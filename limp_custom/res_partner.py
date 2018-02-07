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
import time
from openerp.osv import osv, fields
from openerp.tools.translate import _

WARNING_MESSAGE = [
                   ('no-message','No Message'),
                   ('warning','Warning'),
                   ('block','Blocking Message')
                   ]


WARNING_HELP = _('Selecting the "Warning" option will notify user with the message, Selecting "Blocking Message" will throw an exception with the message and block the flow. The Message has to be written in the next field.')

'''class res_partner_address(osv.osv):
    _inherit = "res.partner.address"
    _columns = {
        'type': fields.selection( [ ('default','Default'),('invoice','Invoice'), ('delivery','Delivery'), ('contact','Contact'), ('management_plant', 'Management plant'), ('other','Other'), ('tramit', 'Tramit')],'Address Type', help="Used to select automatically the right address according to the context in sales and purchases documents."),
        'attention_of': fields.char('A/A', size=255)
    }
res_partner_address()'''

class res_partner(osv.osv):
    _inherit = "res.partner"

    def _partner_byref_search(self, cr, uid, obj, name, args, context=None):
        ids = []
        if args:
            property_ids = self.pool.get('ir.property').search(cr, uid, [('name','=','ref'),('value_text','ilike',args[0][2])])
            for property_obj in self.pool.get('ir.property').browse(cr, uid, property_ids):
                if property_obj.res_id:
                    ids.append(property_obj.res_id.id)

        ids = [('id', 'in', ids)]
        return ids

    def _get_with_ref(self, cr, uid, ids, name, args, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids, context=context):
            if partner.ref:
                res[partner.id] = True
            else:
                res[partner.id] = False
        return res

    def _search_with_ref(self, cr, uid, obj, name, args, context=None):
        ids = []
        partner_ids = []
        if args:
            property_ids = self.pool.get('ir.property').search(cr, uid, [('name','=','ref'),('value_text','!=',False)])
            for property_obj in self.pool.get('ir.property').browse(cr, uid, property_ids):
                if property_obj.res_id:
                    partner_ids.append(property_obj.res_id.id)

            if args[0][2]:
                ids = [('id', 'in', list(set(partner_ids)))]
            else:
                ids = [('id', 'not in', list(set(partner_ids)))]
        return ids


    _columns = {
        'picture': fields.binary('Logo',filters='*.png,*.jpg,*.gif'),
        'add_info': fields.boolean('Aditional Info'),
        'picking_warn_type' : fields.selection(WARNING_MESSAGE,'Picking warning', help=WARNING_HELP),
        'picking_warn_message' : fields.text('Message for Picking'),
        'ref': fields.property('res.partner',
            type='char',
            string='Reference',
            method=True,
            view_load=True,
            required=False,
            fnct_search=_partner_byref_search),
        'with_ref': fields.function(_get_with_ref, method=True, string="With ref", readonly=True, type="boolean", fnct_search=_search_with_ref)
     }

    _defaults = {
         'picking_warn_type' : lambda *a: 'no-message',
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({'contract_ids': []})

        return super(res_partner, self).copy(cr, uid, id, default, context)

res_partner()

class res_partner_bank(osv.osv):

    _inherit = "res.partner.bank"

    _columns = {
        'active': fields.boolean('Active')
    }

    _defaults = {
        'active': lambda *a: True
    }

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


res_partner_bank()
