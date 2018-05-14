# -*- coding: utf-8 -*-
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
from odoo import models, fields, _

WARNING_MESSAGE = [
                   ('no-message','No Message'),
                   ('warning','Warning'),
                   ('block','Blocking Message')
                   ]


WARNING_HELP = _('Selecting the "Warning" option will notify user with the message, Selecting "Blocking Message" will throw an exception with the message and block the flow. The Message has to be written in the next field.')


class ResPartner(models.Model):
    _inherit = "res.partner"

    picture = fields.Binary('Logo',filters='*.png,*.jpg,*.gif')
    add_info = fields.Boolean('Aditional Info')
    picking_warn_type = fields.Selection(WARNING_MESSAGE, 'Picking warning', help=WARNING_HELP, default='no-message')
    picking_warn_message = fields.Text('Message for Picking')
    ref = fields.Char('Reference', company_dependent=True)
    attention_of = fields.Char('A/A', size=255)
    type = fields.Selection(selection_add=[('management_plant', 'Management plant'), ('tramit', 'Tramit')])
    first_name = fields.Char('First Name', size=64, required=True)
    colege_num = fields.Char('Colege number', size=64)


class ResPartnerBank(models.Model):

    _inherit = "res.partner.bank"

    active = fields.Boolean('Active', default=True)

    def onchange_iban(self, cr, uid, ids, iban):
        res = {'value': {}}
        if iban:
            country = iban[:2]
            country_obj = self.pool.get('res.country')
            country_ids = country_obj.search(cr, uid, [('code', '=', country)])
            if country_ids:
                res['value']['acc_country_id'] = country_ids[0]
            else:
                raise osv.except_osv(_('Error!'),_(u'There isn\'t a country starting with %s' % country))

            bank = iban[4:8]
            bank_obj = self.pool.get('res.bank')
            bank_ids = bank_obj.search(cr, uid, [('code', '=', bank),('country', '=', country_ids)])
            if bank_ids:
                res['value']['bank'] = bank_ids[0]
            else:
                raise osv.except_osv(_('Error!'),_(u'There isn\'t this bank in this country'))

        return res
