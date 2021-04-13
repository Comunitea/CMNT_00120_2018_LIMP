# Copyright 2021 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields, exceptions
import time


class StockPicking(models.Model):

    _inherit = "stock.picking"

    operator_partner_id = fields.Many2one("res.partner", "Operator",
                                          default=lambda self: self.env.user.
                                          company_id.partner_id.id)
    nt_doc_id = fields.Many2one("prior.transfer.documentation", "NT")
    dcs_no = fields.Char("DCS no.", size=26, copy=False, readonly=True)

    @api.multi
    def check_DI_data(self):
        for pick in self:
            if not pick.move_lines.mapped('product_id.ler_code_id'):
                raise exceptions.UserError("Los residuos a transladar no "
                                           "están definidos")
            pick.operator_partner_id.check_gaia("operador")
            pick.operator_partner_id.\
                get_authorization_id(pick.move_lines.
                                     mapped('product_id.ler_code_id'), ['N'])

            pick.picking_type_id.warehouse_id.partner_id.\
                check_gaia("productor")
            pick.picking_type_id.warehouse_id.partner_id.\
                get_authorization_id(pick.move_lines.
                                     mapped('product_id.ler_code_id'),
                                     ['P', 'G'])

            pick.carrier_id.check_gaia("transportista")
            pick.carrier_id.\
                get_authorization_id(pick.move_lines.
                                     mapped('product_id.ler_code_id'),
                                     ['T'])

            pick.company_id.partner_id.check_gaia("gestor")
            pick.company_id.partner_id.\
                get_authorization_id(pick.move_lines.
                                     mapped('product_id.ler_code_id'),
                                     ['E', 'G'])

    @api.multi
    def action_done(self):
        for pick in self:
            if not pick.dcs_no and pick.picking_type_code == 'outgoing' and \
                    pick.memory_include:
                seq_id = self.env["ir.sequence"].search(
                    [
                        (
                            "prefix",
                            "=",
                            "DCS30"
                            + pick.operator_partner_id.nima_no
                            + time.strftime("%Y"),
                        ),
                        ("code", "=", "waste_delivery_proof"),
                    ]
                )
                if not seq_id:
                    seq_id = self.env["ir.sequence"].create(
                        {
                            "prefix": "DCS30"
                            + pick.operator_partner_id.nima_no
                            + time.strftime("%Y"),
                            "code": "waste_delivery_proof",
                            "padding": 7,
                            "name": "Waste delivery proof "
                            + pick.company_id.name,
                            "company_id": False,
                        }
                    )
                else:
                    seq_id = seq_id[0]

                seq = seq_id.next_by_id()
                pick.dcs_no = seq
                pick.check_DI_data()
                #TODO: Crear envío a Gaia
        return super().action_done()
