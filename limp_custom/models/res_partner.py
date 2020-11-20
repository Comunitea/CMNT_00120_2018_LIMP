##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Marta Vázquez Rodríguez$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields,  api, _, exceptions


class ResPartner(models.Model):
    _inherit = "res.partner"

    picture = fields.Binary("Logo", filters="*.png,*.jpg,*.gif")
    add_info = fields.Boolean("Aditional Info")
    ref = fields.Char("Reference", company_dependent=True)
    attention_of = fields.Char("A/A", size=255)
    type = fields.Selection(
        selection_add=[
            ("management_plant", "Management plant"),
            ("tramit", "Tramit"),
        ]
    )
    organo_gestor_desc = fields.Char('Órgano gestor desc.')
    unidad_tramitadora_desc = fields.Char('Unidad tramitadora desc.')
    oficina_contable_desc = fields.Char('Oficina contable desc.')
    organo_proponente_desc = fields.Char('Órgano proponente desc.',)

    @api.constrains('facturae', 'vat', 'state_id', 'country_id')
    def check_facturae(self):
        for record in self:
            if record.facturae:
                if not record.vat and not record.parent_id:
                    raise exceptions.ValidationError(_('Vat must be defined'))
                if not record.country_id:
                    raise exceptions.ValidationError(
                        _('Country must be defined'))
                if record.country_id.code_alpha3 == 'ESP':
                    if not record.state_id:
                        raise exceptions.ValidationError(
                            _('State must be defined'))
