# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
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

"""Wizard to increase prices in contracts"""

from osv import osv, fields
from tools.translate import _
from dateutil.relativedelta import relativedelta
from datetime import datetime

class upamount_contract_wzd(osv.osv_memory):
    """Wizard to increase prices in contracts"""

    _name = "upamount.contract.wzd"

    _columns = {
        'upamount_percent': fields.float('Upamount (%)', digits=(12,3), required=True)
    }

    def _reg_upamount(self, cr, uid, ids, upamount_percent, previous_amount, new_amount, name):
        """Resgistries an upamount in history"""
        return self.pool.get('limp.contract.upamount.history').create(cr, uid, {'contract_id': ids[0],
                                                                        'name': name,
                                                                        'upamount_percent': upamount_percent,
                                                                        'previous_amount': previous_amount,
                                                                        'new_amount': new_amount})

    def _update_concepts(self, cr, uid, ids, upamount_percent, contract_id):
        """generic method to update inveoice concepts amounts for ana analytical model"""
        for analytical_acc in self.pool.get('account.analytic.account').browse(cr, uid, ids):
            #analytical invoice concepts
            for concept in analytical_acc.concept_ids:
                vals = {}
                if concept.amount:
                    vals['amount'] = concept.amount + (concept.amount * (upamount_percent / 100.0))
                    self._reg_upamount(cr, uid, [contract_id], upamount_percent, concept.amount, vals['amount'], analytical_acc.name + u" Normal: " + concept.concept_id.name)
                if concept.holyday_amount:
                    vals['holyday_amount'] = concept.holyday_amount + (concept.holyday_amount * (upamount_percent / 100.0))
                    self._reg_upamount(cr, uid, [contract_id], upamount_percent, concept.holyday_amount, vals['holyday_amount'], analytical_acc.name + _(u" Holy: ") + concept.concept_id.name)
                if concept.sunday_amount:
                    vals['sunday_amount'] = concept.sunday_amount + (concept.sunday_amount * (upamount_percent / 100.0))
                    self._reg_upamount(cr, uid, [contract_id], upamount_percent, concept.sunday_amount, vals['sunday_amount'], analytical_acc.name + _(u" Sunday: ") + concept.concept_id.name)
                if concept.saturday_afternoon_amount:
                    vals['saturday_afternoon_amount'] = concept.saturday_afternoon_amount + (concept.saturday_afternoon_amount * (upamount_percent / 100.0))
                    self._reg_upamount(cr, uid, [contract_id], upamount_percent, concept.saturday_afternoon_amount, vals['saturday_afternoon_amount'], analytical_acc.name + _(u" Saturday afternoon: ") + concept.concept_id.name)
                self.pool.get('account.analytic.invoice.concept.rel').write(cr, uid, [concept.id], vals)

        return True

    def upamount_action(self, cr, uid, ids, context=None):
        """Increase amounts for active contracts"""
        if context is None: context = {}

        contract_ids = context.get('active_ids', [])
        obj = self.browse(cr, uid, ids[0])

        if contract_ids:
            for contract in self.pool.get('limp.contract').browse(cr, uid, contract_ids):
                if contract.active and contract.state not in ['close', 'cancelled']:
                    #Annual amount
                    if contract.amount:
                        new_amount = contract.amount + (contract.amount * (obj.upamount_percent / 100.0))
                        self.pool.get('limp.contract').write(cr, uid, [contract.id], {'amount': new_amount})
                        self._reg_upamount(cr, uid, [contract.id], obj.upamount_percent, contract.amount, new_amount, contract.name + _(u": Annual amount"))

                    #contract invoice concepts
                    self._update_concepts(cr, uid, [contract.analytic_account_id.id], obj.upamount_percent, contract.id)

                    for home_line in contract.home_help_line_ids:
                        self._update_concepts(cr, uid, [home_line.analytic_acc_id.id], obj.upamount_percent, contract.id)
                    for clean_line in contract.cleaning_line_ids:
                        self._update_concepts(cr, uid, [clean_line.analytic_acc_id.id], obj.upamount_percent, contract.id)

                    self.pool.get('limp.contract').write(cr, uid, [contract.id], {'upamount_date': (datetime.now() + relativedelta(years=+1)).strftime("%Y-%m-%d")})

        return {'type': 'ir.actions.act_window_close'}

upamount_contract_wzd()
