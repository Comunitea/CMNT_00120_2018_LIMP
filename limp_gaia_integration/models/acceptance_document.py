# Copyright 2021 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields, exceptions
import time


class AcceptanceDocument(models.Model):

    _inherit = "acceptance.document"

    waste_name = fields.Char("Waste name")
    product_id = fields.Many2one("product.product", "Producto")
    producer_promoter_id = fields.Many2one("res.partner", "Producer/Promoter")
    doc_date = fields.Date("Date", default=fields.Date.today)
    operator_partner_id = fields.\
        Many2one("res.partner", "Operator",
                 default=lambda self: self.env.user.company_id.partner_id.id)

    manager_partner_id = fields.Many2one("res.partner", "Manager")
    net_weight = fields.Float("Net (T.)", required=True, digits=(12, 3))
    manager_id = fields.Many2one(
        "hr.employee", "Responsible", domain=[("responsible", "=", True)]
    )
    operation_type = fields.\
        Selection([('D01', 'D01'), ('D02', 'D02'), ('D03', 'D03'),
                   ('D04', 'D04'), ('D05', 'D05'), ('D06', 'D06'),
                   ('D07', 'D07'), ('D08', 'D08'), ('D09', 'D09'),
                   ('D10', 'D10'), ('D11', 'D11'), ('D12', 'D12'),
                   ('D13', 'D13'), ('D14', 'D14'), ('D15', 'D15'),
                   ('R01', 'R01'), ('R02', 'R02'), ('R03', 'R03'),
                   ('R04', 'R04'), ('R05', 'R05'), ('R06', 'R06'),
                   ('R07', 'R07'), ('R08', 'R08'), ('R09', 'R09'),
                   ('R10', 'R10'), ('R11', 'R11'), ('R12', 'R12'),
                   ('R13', 'R13'), ('R14', 'R14'), ('R15', 'R15')],
                  "Operation type")
    dangerous_motive = fields.\
        Selection([('HP1', 'HP1 Explosivo'), ('HP2', 'HP2 Comburente'),
                   ('HP3', 'HP3 Inflamable'),
                   ('HP4', 'HP4 Irritante-Irritación cutánea y lesiones '
                    'oculares'), ('HP5', 'HP5 Toxicidad especifica en '
                    'determinados órganos (STOT en su sigla ingles) - '
                    'Toxicidad por aspiración'),
                   ('HP6', 'HP6 Tóxicidad aguda'), ('HP7', 'HP7 Carcinógeno'),
                   ('HP8', 'HP8 Corrosivo'), ('HP9', 'HP9 Infeccioso'),
                   ('HP10', 'HP10 Tóxico para la reproducción'),
                   ('HP11', 'HP11 Mutágeno'),
                   ('HP12', 'HP12 Liberación de un gas de toxicidad aguda'),
                   ('HP13', 'HP13 Sensibilizante'), ('HP14', 'HP14 Ecotóxico'),
                   ('HP15', 'HP15 Residuos que pueden presentar una de las '
                    'caractarísticas de peligrosidad antes mencionadas que el '
                    'residuo original no presentaba directamente')],
                  "Dangerous Motive")

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res.number == "/":
            seq_id = self.env["ir.sequence"].search(
                [
                    (
                        "prefix",
                        "=",
                        "DA30"
                        + res.operator_partner_id.nima_no
                        + time.strftime("%Y"),
                    ),
                    ("code", "=", "da_document"),
                ]
            )
            if not seq_id:
                seq_id = self.env["ir.sequence"].create(
                    {
                        "prefix": "DA30"
                        + res.operator_partner_id.nima_no
                        + time.strftime("%Y"),
                        "code": "da_document",
                        "padding": 7,
                        "name": "Treatment contract seq. "
                        + res.operator_partner_id.nima_no,
                        "company_id": False,
                    }
                )
            else:
                seq_id = seq_id[0]

            seq = seq_id.next_by_id()
            res.number = seq
        return res

    @api.multi
    def check_NT_data(self):
        for pick in self:
            pick.operator_partner_id.check_gaia("operador")
            pick.operator_partner_id.\
                get_authorization_id(pick.waste_id, ['N', 'G'])

            pick.producer_promoter_id.check_gaia("productor")
            code = pick.producer_promoter_id.\
                get_authorization_id(pick.waste_id, ['P', 'G'])
            if code.authorization_type[0] == 'G':
                pick.producer_promoter_id.\
                    get_authorization_id(pick.waste_id, ['E'])

            pick.manager_partner_id.check_gaia("gestor")
            pick.manager_partner_id.\
                get_authorization_id(pick.waste_id, ['G'])
            pick.manager_partner_id.\
                get_authorization_id(pick.waste_id, ['E'])

            if not pick.operation_type and not pick.\
                    waste_id.operation_type:
                raise exceptions.UserError("No se ha establecido el tipo"
                                           " de operación en el residuo")
            if pick.waste_id.dangerous and not pick.dangerous_motive \
                    and not pick.waste_id.dangerous_motive:
                raise exceptions.\
                    UserError("No se ha establecido el motivo de "
                              "peligrosidad en el residuo")

    @api.onchange('building_site_id')
    def onchange_building_site_id(self):
        if self.building_site_id:
            self.producer_promoter_id = self.building_site_id.\
                producer_promoter_id

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.waste_id = self.product_id.ler_code_id
            self.waste_name = self.product_id.name

    @api.onchange('waste_id')
    def onchange_waste_id(self):
        if self.waste_id:
            self.operation_type = self.waste_id.operation_type
            self.dangerous_motive = self.waste_id.dangerous_motive
