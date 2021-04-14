# Copyright 2021 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields, exceptions
import time


class PriorTransferDocumentation(models.Model):

    _name = "prior.transfer.documentation"
    _description = "(NT) Prior transfer documentation"

    producer_promoter_id = fields.Many2one("res.partner", "Producer/Promoter",
                                           required=True)
    operator_partner_id = fields.\
        Many2one("res.partner", "Operator", required=True,
                 default=lambda self: self.env.user.company_id.partner_id.id)

    manager_partner_id = fields.\
        Many2one("res.partner", "Manager", required=True)
    name = fields.Char("Number", default="/", required=True)
    freq = fields.Selection([("DIARIA", "Diaria"), ("SEMANAL", "Semanal"),
                             ("QUINCENAL", "Quincenal"),
                             ("MENSUAL", "Mensual"),
                             ("TRIMESTRAL", "Trimestral"),
                             ("SEMESTRAL", "Semestral"), ("ANUAL", "Anual"),
                             ("OTROS", "Otros")], "Frequency", required=True,
                            default="MENSUAL")
    line_ids = fields.One2many("prior.transfer.documentation.line",
                               "nt_id", "Lines")
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        default=lambda r: r.env.user.company_id.id,
    )
    start_date = fields.Date("Start date", required=True)
    end_date = fields.Date("End date", required=True)
    notification_date = fields.Date("Notification date", required=True,
                                    default=fields.Date.today)

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res.name == "/":
            seq_id = self.env["ir.sequence"].search(
                [
                    (
                        "prefix",
                        "=",
                        "NT30"
                        + res.operator_partner_id.nima_no
                        + time.strftime("%Y"),
                    ),
                    ("code", "=", "nt_document"),
                ]
            )
            if not seq_id:
                seq_id = self.env["ir.sequence"].create(
                    {
                        "prefix": "NT30"
                        + res.operator_partner_id.nima_no
                        + time.strftime("%Y"),
                        "code": "nt_document",
                        "padding": 7,
                        "name": "Prior transfer documentation seq. "
                        + res.company_id.name,
                        "company_id": False,
                    }
                )
            else:
                seq_id = seq_id[0]

            seq = seq_id.next_by_id()
            pick.name = seq
        return res

    @api.multi
    def check_NT_data(self):
        for pick in self:
            if not pick.line_ids.mapped('waste_id'):
                raise exceptions.UserError("Los residuos a transladar no "
                                           "están definidos")
            pick.operator_partner_id.check_gaia("operador")
            pick.operator_partner_id.\
                get_authorization_id(pick.line_ids.
                                     mapped('waste_id'), ['N'])

            pick.producer_promoter_id.check_gaia("productor")
            code = pick.producer_promoter_id.\
                get_authorization_id(pick.line_ids.
                                     mapped('waste_id'), ['P', 'G'])
            if code.authorization_type[0] == 'G':
                pick.producer_promoter_id.\
                    get_authorization_id(pick.line_ids.
                                         mapped('waste_id'), ['E'])

            pick.manager_partner_id.check_gaia("gestor")
            pick.manager_partner_id.\
                get_authorization_id(pick.line_ids.
                                     mapped('waste_id'), ['G'])
            pick.manager_partner_id.\
                get_authorization_id(pick.line_ids.
                                     mapped('waste_id'), ['E'])
            for waste in pick.line_ids.mapped('waste_id'):
                if not waste.operation_type:
                    raise exceptions.UserError("No se ha establecido el tipo"
                                               " de operación en el residuo")
                if waste.dangerous and not waste.dangerous_motive:
                    raise exceptions.\
                        UserError("No se ha establecido el motivo de "
                                  "peligrosidad en el residuo")


class PriorTransferDocumentationLine(models.Model):

    _name = "prior.transfer.documentation.line"
    _description = "(NT) Prior transfer documentation line"

    waste_id = fields.Many2one("waste.ler.code", "LER", required=True)
    name = fields.Char("Waste name", required=True)
    nt_id = fields.Many2one("prior.transfer.documentation", "NT")
    net_weight = fields.Float("Net (T.)", required=True, digits=(12, 3))
    volume = fields.Float("Volume (m³)", required=True, digits=(12, 3))
    no_compute = fields.Boolean("No compute")

    @api.onchange("net_weight")
    def onchange_net_weight(self):
        if self.no_compute or not self.waste_id:
            return

        if self.waste_id.density:
            self.product_qty = round(self.net_weight /
                                     self.waste_id.density, 2)
            self.volume = round(self.net_weight / self.waste_id.density, 2)

    @api.onchange("volume")
    def onchange_volume(self):
        if self.no_compute or not self.waste_id:
            return
        self.product_qty = self.volume
        if self.waste_id.density:
            self.net_weight = round(self.volume * self.waste_id.density, 2)
