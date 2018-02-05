# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
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

"""Base model to manage Limpergal's contracts"""

from openerp import models, fields
import decimal_precision as dp
from tools.translate import _
from datetime import datetime

class limp_contract(models.Model):
    """Base model to manage Limpergal's contracts"""

    _name = 'limp.contract'
    _description = "Limpergal Contracts"
    _inherits = {'account.analytic.account': "analytic_account_id"}

    def _get_last_invoice_date(self, cr, uid, ids, field_name, arg, context=None):
        if context is None: context =  {}
        res = {}

        for contract in self.browse(cr, uid, ids):
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('analytic_id', '=', contract.id)], order="date_invoice desc", limit=1)
            if invoice_ids:
                res[contract.id] = self.pool.get('account.invoice').browse(cr, uid, invoice_ids[0]).date_invoice
            else:
                res[contract.id] = False

        return res

    def _get_contract_total_amount(self, cr, uid, ids, field_name, arg, context=None):
        """adds all fix amount in contract"""
        res = {}
        for contract in self.browse(cr, uid, ids):
            amount = 0.0
            res[contract.id] = {}
            if contract.state == 'open':
                amount += self.pool.get('account.analytic.account')._get_concept_amount(cr, uid, [x.id for x in contract.concept_ids])
            for home_help_line in contract.home_help_line_ids:
                if home_help_line.state == 'open':
                    amount += self.pool.get('account.analytic.account')._get_concept_amount(cr, uid, [x.id for x in home_help_line.concept_ids])
            for cleaning_line in contract.cleaning_line_ids:
                if cleaning_line.state == 'open':
                    amount += self.pool.get('account.analytic.account')._get_concept_amount(cr, uid, [x.id for x in cleaning_line.concept_ids])
            #for waste_line in contract.waste_line_ids:
            #    amount += waste_line.amount

            res[contract.id]['amount'] = amount
            res[contract.id]['monthly_amount'] = round(amount / 12.0, 2)

        return res

    _columns = {
        'prorogation_date': fields.date('Prorogation date', help="Estimate prorogation date"),
        'prorogation_end_date': fields.date('Prorogation end date', help="Prorogation end date"),
        'prorogation_notes': fields.text('Notes'),
        'request_prorogation_date': fields.date('Req. prorogation date'),
        'upamount_date': fields.date('Upamount date', help="Estimate up amount date"),
        'request_upamount_date': fields.date('Req. upamount date'),
        'amount': fields.function(_get_contract_total_amount, type="float", method=True, string='Total annual amount', digits_compute=dp.get_precision('Account'), readonly=True, multi="amount"),
        'monthly_amount': fields.function(_get_contract_total_amount, type="float", method=True, string='Monthly amount', digits_compute=dp.get_precision('Account'), readonly=True, multi="amount"),
        'periodicity': fields.selection([('m', 'Monthy'), ('q', 'Quarterly'), ('b', 'Biannual'), ('a', 'Annual'), ('ph', 'Per hours')], 'Periodicity'),
        'bank_account_id': fields.many2one('res.partner.bank', 'Bank account', help="Income bank account"),
        'last_invoice_date': fields.function(_get_last_invoice_date, method=True, string="Last invoice date", readonly=True, type="date"),
        'offered_hours': fields.float('Offered hours'),
        'hours_per_week': fields.float('Hours per week'),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Account', readonly=True, required=True, ondelete="cascade"),
        'state': fields.selection([('draft', 'Draft'), ('wait_signature', 'Waiting signature'), ('open', 'Opened'), ('close', 'Closed'), ('cancelled', 'Cancelled')], 'State', readonly=True),
        'active': fields.boolean('Active'),
        'seq_lines_id': fields.many2one('ir.sequence', 'Sequence', readonly=True),
        'home_help_line_ids': fields.one2many('limp.contract.line.home.help', 'contract_id', 'Home help lines', states={'cancelled':[('readonly',True)], 'close':[('readonly',True)]}),
        'cleaning_line_ids': fields.one2many('limp.contract.line.cleaning', 'contract_id', 'Cleaning lines', states={'cancelled':[('readonly',True)], 'close':[('readonly',True)]}),
#        'waste_line_ids': fields.one2many('limp.contract.line.waste', 'contract_id', 'Waste lines', states={'cancelled':[('readonly',True)], 'close':[('readonly',True)]}),
        'stock_service_picking_ids': fields.one2many('stock.service.picking', 'contract_id', 'Picking lines', states={'cancelled':[('readonly',True)], 'close':[('readonly',True)]}, domain=[('picking_type','=','wastes')]),
        'stock_sporadic_service_picking_ids': fields.one2many('stock.service.picking', 'contract_id', 'Sporadic picking lines', states={'cancelled':[('readonly',True)], 'close':[('readonly',True)]}, domain=[('picking_type','=','sporadic')]),
        'payment_term_id': fields.many2one('account.payment.term', 'Payment term'),
        'payment_type_id': fields.many2one('payment.type', 'Payment type'),
        'contact_id': fields.many2one('res.partner', 'Contact'),
        'note': fields.text('Description'),
        'include_pickings': fields.boolean('Include pickings'),
        'signature_date': fields.date('Signature date', readonly=True),
        'contract_note_ids': fields.one2many('limp.contract.note', 'contract_id', 'Notes'),
        'invoice_header': fields.char('Invoice header', size=128),
        'contract_duration': fields.char('Contract duration', size=128),
        'contract_end_date': fields.date('End date'),
    }

    _defaults = {
        'periodicity': lambda *a: 'm',
        'state': lambda *a: 'draft',
        'active': lambda *a: True,
    }

    def invoice_run(self, cr, uid, ids=False, context=None):
        if context is None: context = {}
        id_invoice = []
        invoice_ids = []
        for obj in self.browse(cr, uid, ids):
            if obj.analytic_account_id and obj.state == 'open':
                child_ids = self.pool.get('account.analytic.account').search(cr, uid, [('state', '=', 'open'), ('partner_id', '!=', False), ('invoiceable', '=', True), ('parent_id', '=', obj.analytic_account_id.id), ('date_start', '<', context['end_date'])], order='create_date')
                invoice_ids = self.pool.get('account.analytic.account').run_invoice_cron_manual(cr, uid, child_ids + [obj.analytic_account_id.id], context=context)
        if invoice_ids:
            action_model,action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', "action_invoice_tree1")
            if action_model:
                action_pool = self.pool.get(action_model)
                action = action_pool.read(cr, uid, action_id, context=context)
                action['domain'] = "[('id','in', ["+','.join(map(str,invoice_ids))+"])]"
                action["nodestroy"] = True
                return action
        return True

    def create(self, cr, uid, vals, context=None):
        """Creates contract sequence and contract lines sequence"""

        if context is None: context = {}
        vals['name'] = self.pool.get('ir.sequence').get_by_delegation(cr, uid, 'limp.contract.seq', vals['delegation_id'])

        # obtains contract lines sequence id and copy default to assign new sequence for this contract lines
        seq_id = self.pool.get('ir.sequence').search_by_delegation(cr, uid, 'limp.contract.line.seq', vals['delegation_id'])
        if seq_id:
            vals['seq_lines_id'] = self.pool.get('ir.sequence').copy(cr, uid, seq_id, {'number_next': 1})

        vals['invoiceable'] = True

        new_id = super(limp_contract, self).create(cr, uid, vals, context=context)
        self.write(cr, uid, [new_id], {'state': 'draft'})

        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        """updates all contract lines if state = close"""
        if context is None: context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = super(limp_contract, self).write(cr, uid, ids, vals, context=context)
        if vals.get('state', False) and vals['state'] in ['open', 'close', 'cancelled']:
            for contract in self.browse(cr, uid, ids):
                if contract.home_help_line_ids:
                    self.pool.get('limp.contract.line.home.help').write(cr, uid, [x.id for x in contract.home_help_line_ids if x.state == 'open'], {'state': vals['state']})
                if contract.cleaning_line_ids:
                    self.pool.get('limp.contract.line.cleaning').write(cr, uid, [x.id for x in contract.cleaning_line_ids if x.state == 'open'], {'state': vals['state']})
#                if contract.waste_line_ids:
#                    self.pool.get('limp.contract.line.waste').write(cr, uid, [x.id for x in contract.waste_line_ids], {'state': vals['state']})
                self.pool.get('account.analytic.account').write(cr, uid, [contract.analytic_account_id.id], {'state': vals['state']})

        if vals.get('date',False):
            for contract in self.browse(cr, uid, ids):
                if contract.home_help_line_ids:
                    self.pool.get('limp.contract.line.home.help').write(cr, uid, [x.id for x in contract.home_help_line_ids if x.date == False], {'date': vals['date']})
                if contract.cleaning_line_ids:
                    self.pool.get('limp.contract.line.cleaning').write(cr, uid, [x.id for x in contract.cleaning_line_ids if x.date == False], {'date': vals['date']})
#                if contract.waste_line_ids:
#                    self.pool.get('limp.contract.line.waste').write(cr, uid, [x.id for x in contract.waste_line_ids], {'date': vals['date']})
                if contract.remuneration_ids:
                    self.pool.get('remuneration').write(cr, 1, [x.id for x in contract.remuneration_ids if not x.date_to], {'date_to': vals['date']})

        if vals.get('date_start',False):
            for contract in self.browse(cr, uid, ids):
                if contract.home_help_line_ids:
                    self.pool.get('limp.contract.line.home.help').write(cr, uid, [x.id for x in contract.home_help_line_ids], {'date_start': vals['date_start']})
                if contract.cleaning_line_ids:
                    self.pool.get('limp.contract.line.cleaning').write(cr, uid, [x.id for x in contract.cleaning_line_ids], {'date_start': vals['date_start']})
                if contract.remuneration_ids:
                    self.pool.get('remuneration').write(cr, 1, [x.id for x in contract.remuneration_ids], {'date': vals['date_start']})

        if vals.get('privacy',False):
            for contract in self.browse(cr, uid, ids):
                if contract.home_help_line_ids:
                    self.pool.get('limp.contract.line.home.help').write(cr, uid, [x.id for x in contract.home_help_line_ids], {'privacy': vals['privacy']})
                if contract.cleaning_line_ids:
                    self.pool.get('limp.contract.line.cleaning').write(cr, uid, [x.id for x in contract.cleaning_line_ids], {'privacy': vals['privacy']})

        return res

    def unlink(self, cr, uid, ids, context=None):
        """delete associated analytic account"""
        account_to_delete = []
        for contract in self.browse(cr, uid, ids, context=context):
            if contract.state not in ('draft','cancelled'):
                raise osv.except_osv(_('Error!'),_("Only contracts in draft or cancelled states can be deleted."))
            account_to_delete.extend(self.pool.get('account.analytic.account').search(cr, uid, [('id', 'child_of', [contract.analytic_account_id.id])]))

        res = super(limp_contract, self).unlink(cr, uid, ids, context=context)
        self.pool.get('account.analytic.account').unlink(cr, uid, account_to_delete, context=context)
        return res

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        if context is None:
            context = {}
        context["is_contract"] = True
        default.update({
            'state': 'draft',
            'date': False,
            'child_ids': [],
            'line_ids': [],
            'contract_note_ids': [],
            'stock_sporadic_service_picking_ids': [],
            'stock_service_picking_ids': [],
            'analytic_move_ids': [],
            'employee_ids': [],
            'active_employee_ids': [],
            'inactive_employee_ids': [],
            'report_employee_ids': []
        })

        return super(limp_contract, self).copy(cr, 1, id, default, context)


    def onchange_partner_id(self, cr, uid, ids, partner_id):
        """gets payment type and payment term from partner"""
        res = {}
        if partner_id:
            partner_obj = self.pool.get('res.partner').browse(cr, uid, partner_id)
            res['value'] = {}
            payment_type = partner_obj.payment_type_customer and partner_obj.payment_type_customer or False
            res['value']['payment_type_id'] = payment_type and payment_type.id or False
            res['value']['payment_term_id'] = partner_obj.property_payment_term and partner_obj.property_payment_term.id or False
            res['value']['address_id'] = self.pool.get('res.partner').address_get(cr, uid, [partner_obj.id], ['contact'])['contact']
            res['value']['address_invoice_id'] = self.pool.get('res.partner').address_get(cr, uid, [partner_obj.id],['invoice'])['invoice']
            res['value']['bank_account_id'] = (payment_type and payment_type.suitable_bank_types and partner_obj.bank_ids) and partner_obj.bank_ids[0].id or False

        return res

    def act_confirm(self, cr, uid, ids, context=None):
        """Set wait_signature state"""
        if context is None: context = {}

        return self.write(cr, uid, ids, {'state': 'wait_signature'})

    def act_cancel(self, cr, uid, ids, context=None):
        """Set cancel state"""
        if context is None: context = {}

        return self.write(cr, uid, ids, {'state': 'cancelled'})

    def act_reopen(self, cr, uid, ids, context=None):
        """Set close state"""
        if context is None: context = {}
        for contract in self.browse(cr, uid, ids):
            line_ids = self.pool.get('account.analytic.account').search(cr, uid, [('parent_id', '=', contract.analytic_account_id.id),('date', '=', contract.date)])
            for line in self.pool.get('account.analytic.account').browse(cr, uid, line_ids):
                for occupation in self.pool.get('account.analytic.occupation').read(cr, uid, [x.id for x in line.occupation_ids], ['end_date']):
                    if occupation['end_date'] == line.date:
                        self.pool.get('account.analytic.occupation').write(cr, uid, [occupation['id']], {'end_type': 'forever', 'end_date': False})
            self.pool.get('account.analytic.account').write(cr, uid, line_ids, {'date': False, 'state': 'open'})
        self.write(cr, uid, ids, {'state': 'open', 'date': False})

        return

    def act_draft(self, cr, uid, ids, context=None):
        """Set cancel state"""
        if context is None: context = {}

        return self.write(cr, uid, ids, {'state': 'draft'})

    def act_close(self, cr, uid, ids, context=None):
        """Set close state"""
        if context is None: context = {}
        for contract in self.browse(cr, uid, ids):
            if not contract.date or contract.date > datetime.today().strftime("%Y-%m-%d"):
                raise osv.except_osv(_('Error!'),_("Cannot close the contract without a final date less or equal today."))

        return self.write(cr, uid, ids, {'state': 'close'})

limp_contract()
