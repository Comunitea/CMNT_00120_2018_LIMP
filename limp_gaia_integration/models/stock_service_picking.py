# Copyright 2021 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields, exceptions


class StockServicePicking(models.Model):

    _inherit = "stock.service.picking"

    operator_partner_id = fields.Many2one(
        "res.partner",
        "Operator",
        states={
            "closed": [("readonly", True)],
            "cancelled": [("readonly", True)],
        },
        default=lambda self: self.env.user.company_id.partner_id.id
    )
    nt_doc_id = fields.Many2one("prior.transfer.documentation", "NT")
    producer_promoter_id = fields.Many2one("res.partner", "Producer/Promoter")
    dcs_phase = fields.Char("DCS Phase", compute="_get_dcs_phase")

    @api.multi
    def check_DI_data(self):
        for pick in self:
            if not pick.service_picking_valorization_ids.\
                    mapped('product_id.ler_code_id'):
                raise exceptions.UserError("Los residuos a transladar no "
                                           "están definidos")
            pick.operator_partner_id.check_gaia("operador")
            pick.operator_partner_id.\
                get_authorization_id(pick.service_picking_valorization_ids.
                                     mapped('product_id.ler_code_id'), ['N'])

            pick.producer_promoter_id.check_gaia("productor")
            pick.producer_promoter_id.\
                get_authorization_id(pick.service_picking_valorization_ids.
                                     mapped('product_id.ler_code_id'),
                                     ['P', 'G'])

            pick.carrier_id.check_gaia("transportista")
            pick.carrier_id.\
                get_authorization_id(pick.service_picking_valorization_ids.
                                     mapped('product_id.ler_code_id'),
                                     ['T'])

            pick.manager_partner_id.check_gaia("gestor")
            pick.manager_partner_id.\
                get_authorization_id(pick.service_picking_valorization_ids.
                                     mapped('product_id.ler_code_id'),
                                     ['E', 'G'])

    @api.multi
    def _get_dcs_phase(self):
        for pick in self:
            partners = pick.producer_promoter_id.commercial_partner_id.\
                child_ids
            partners |= pick.producer_promoter_id.commercial_partner_id
            partners |= pick.manager_partner_id.commercial_partner_id.child_ids
            partners |= pick.manager_partner_id.commercial_partner_id
            if partners.filtered('create_nima_number'):
                pick.dcs_phase = 'D'
            else:
                pick.dcs_phase = 'R'

    @api.onchange("building_site_id")
    def onchange_building_site_id(self):
        if self.building_site_id:
            if self.building_site_id:
                self.producer_promoter_id = \
                    self.building_site_id.producer_promoter_id.id

        super().onchange_building_site_id()

    def action_close(self):
        res = super().action_close()
        for order in self:
            if order.dcs_no:
                order.check_DI_data()
                #TODO: Crear envío a Gaia

        return res


class ServicePickingValorizationRel(models.Model):
    _inherit = "service.picking.valorization.rel"

    operation_type = fields.\
        Selection([('D01', 'D01'), ('D02', 'D02'), ('D03', 'D03'),
                   ('D04', 'D04'), ('D05', 'D05'), ('D06', 'D06'),
                   ('D07', 'D07'), ('D08', 'D08'), ('D09', 'D09.'),
                   ('D10', 'D10'), ('D11', 'D11'), ('D12', 'D12'),
                   ('D13', 'D13'), ('D14', 'D14'), ('D15', 'D15'),
                   ('R01', 'R01'), ('R02', 'R02'), ('R03', 'R03'),
                   ('R04', 'R04'), ('R05', 'R05'), ('R06', 'R06'),
                   ('R07', 'R07'), ('R08', 'R08'), ('R09', 'R09.'),
                   ('R10', 'R10'), ('R11', 'R11'), ('R12', 'R12'),
                   ('R13', 'R13'), ('R14', 'R14'), ('R15', 'R15')],
                  "Operation type")

    @api.onchange("product_id")
    def onchange_product_id_warning(self):
        res = super().onchange_product_id_warning()
        if self.product_id and self.product_id.ler_code_id:
            self.operation_type = self.product_id.ler_code_id.operation_type
        return res


class WasteLerCode(models.Model):

    _inherit = "waste.ler.code"

    operation_type = fields.\
        Selection([('D01', 'D01'), ('D02', 'D02'), ('D03', 'D03'),
                   ('D04', 'D04'), ('D05', 'D05'), ('D06', 'D06'),
                   ('D07', 'D07'), ('D08', 'D08'), ('D09', 'D09.'),
                   ('D10', 'D10'), ('D11', 'D11'), ('D12', 'D12'),
                   ('D13', 'D13'), ('D14', 'D14'), ('D15', 'D15'),
                   ('R01', 'R01'), ('R02', 'R02'), ('R03', 'R03'),
                   ('R04', 'R04'), ('R05', 'R05'), ('R06', 'R06'),
                   ('R07', 'R07'), ('R08', 'R08'), ('R09', 'R09.'),
                   ('R10', 'R10'), ('R11', 'R11'), ('R12', 'R12'),
                   ('R13', 'R13'), ('R14', 'R14'), ('R15', 'R15')],
                  "Operation type")
    dangerous_motive = fields.\
        Selection([('HP1', 'Explosivo'), ('HP2', 'Comburente'),
                   ('HP3', 'Inflamable'),
                   ('HP4', 'Irritante-Irritación cutánea y lesiones oculares'),
                   ('HP5', 'Toxicidad especifica en determinados órganos '
                    '(STOT en su sigla ingles) - Toxicidad por aspiración'),
                   ('HP6', 'Tóxicidad aguda'), ('HP7', 'Carcinógeno'),
                   ('HP8', 'Corrosivo'), ('HP9', 'Infeccioso'),
                   ('HP10', 'Tóxico para la reproducción'),
                   ('HP11', 'Mutágeno'),
                   ('HP12', 'Liberación de un gas de toxicidad aguda'),
                   ('HP13', 'Sensibilizante'), ('HP14', 'Ecotóxico'),
                   ('HP15', 'Residuos que pueden presentar una de las '
                    'caractarísticas de peligrosidad antes mencionadas que el '
                    'residuo original no presentaba directamente')],
                  "Dangerous Motive")
