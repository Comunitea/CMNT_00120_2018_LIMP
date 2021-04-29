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
    manager_id = fields.Many2one(
        "hr.employee",
        "Responsible",
        domain=[("responsible", "=", True)],
        default=lambda r: r._context.get(
            "c_manager_id",
            r.env.user.employee_ids and r.env.user.employee_ids[0].id or False,
        ),
        index=True
    )

    @api.multi
    def check_DI_data(self):
        for pick in self:
            if not pick.move_lines.mapped('product_id.ler_code_id'):
                raise exceptions.UserError("Los residuos a transladar no "
                                           "están definidos")
            pick.operator_partner_id.check_gaia("operador")
            pick.operator_partner_id.\
                get_authorization_id(pick.move_lines.
                                     mapped('product_id.ler_code_id'),
                                     ['N', 'G'])

            pick.picking_type_id.warehouse_id.partner_id.\
                check_gaia("productor")
            code = pick.picking_type_id.warehouse_id.partner_id.\
                get_authorization_id(pick.move_lines.
                                     mapped('product_id.ler_code_id'),
                                     ['P', 'G'])
            if code.authorization_type[0] == 'G':
                pick.picking_type_id.warehouse_id.partner_id.\
                    get_authorization_id(pick.move_lines.
                                         mapped('product_id.ler_code_id'),
                                         ['E'])

            pick.carrier_id.check_gaia("transportista")
            pick.carrier_id.\
                get_authorization_id(pick.move_lines.
                                     mapped('product_id.ler_code_id'),
                                     ['T'])

            pick.company_id.partner_id.check_gaia("gestor")
            pick.company_id.partner_id.\
                get_authorization_id(pick.move_lines.
                                     mapped('product_id.ler_code_id'),
                                     ['G'])
            pick.company_id.partner_id.\
                get_authorization_id(pick.move_lines.
                                     mapped('product_id.ler_code_id'),
                                     ['E'])
            for waste in pick.move_lines.mapped('product_id.ler_code_id'):
                if not waste.operation_type:
                    raise exceptions.UserError("No se ha establecido el tipo"
                                               " de operación en el residuo")
                if waste.dangerous and not waste.dangerous_motive:
                    raise exceptions.\
                        UserError("No se ha establecido el motivo de "
                                  "peligrosidad en el residuo")

    @api.multi
    def action_create_di(self):
        for pick in self:
            if not pick.dcs_no and pick.picking_type_code == 'outgoing' and \
                    pick.memory_include:
                pick.check_DI_data()
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
                #TODO: Crear envío a Gaia
        return True


class StockMove(models.Model):

    _inherit = "stock.move"

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

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super().onchange_product_id()
        if self.product_id:
            self.operation_type = self.product_id.ler_code_id.operation_type
            self.dangerous_motive = self.product_id.ler_code_id.\
                dangerous_motive
        return res
