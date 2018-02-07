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

"""Adds new fields to analytics accounts"""

from openerp.osv import osv, fields
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil import rrule
from openerp.addons.decimal_precision import decimal_precision as dp
import time
import calendar

class account_analytic_account(osv.osv):
    """Adds new fields to analytics accounts"""

    _inherit = "account.analytic.account"
    _order = "partner_name asc,name asc"

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=80):
        """allows search by center name too"""
        if args is None: args=[]
        if context is None: context={}
        ids = []

        if name:
            partner_ids = self.pool.get('res.partner').search(cr, user, [('name', operator, name)], limit=limit, context=context)
            if partner_ids:
                ids = self.search(cr, user,[('partner_id', 'in', partner_ids)]+ args, limit=limit, context=context)
            ids += self.search(cr, user, [('name', operator, name)]+ args, limit=limit, context=context)
            ids = list(set(ids))
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)

        result = self.name_get(cr, user, ids, context)
        return result

    def name_get(self, cr, uid, ids, context=None):
        """return other name if it is contract line"""
        if context is None:
            context = {}
        if not ids:
            return []
        res = []

        for obj in self.browse(cr, uid, ids, context=context):
            name = ""
            if obj.partner_id:
                name = obj.partner_id.name
                home_help_lines = self.pool.get('limp.contract.line.home.help').search(cr, uid, [('analytic_acc_id', '=', obj.id)])
                if home_help_lines:
                    line = self.pool.get('limp.contract.line.home.help').browse(cr, uid, home_help_lines[0])
                    if line.customer_contact_id:
                        name += u" " + line.customer_contact_id.name
                    else:
                        name += u""
                else:
                    name += u" " + (obj.address_id.name or u"")
                name += u" " + (obj.description or u"")
            else:
                name = obj.name
            res.append((obj.id, name))

        return res

    def _get_concept_amount(self, cr, uid, concept_ids):
        """return fix amount for set of concepts"""
        amount = 0.0
        for line in self.pool.get('account.analytic.invoice.concept.rel').browse(cr, uid, concept_ids):
            if not line.per_hours:
                if line.freq == 'q':
                    amount += line.amount * 4
                else:
                    except_months = line._get_except_months()
                    amount += line.amount * (12 - len(except_months[line.id]))

        return amount

    def _get_total_amount(self, cr, uid, ids, field_name, arg, context=None):
        """adds all fix amount in contract"""
        res = {}
        for account in self.browse(cr, uid, ids):
            amount = self._get_concept_amount(cr, uid, [x.id for x in account.concept_ids])

            res[account.id] = amount

        return res

    def _get_is_contract(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        #dist_contract_ids = self.pool.get('limp.contract').search(cr, uid, [('analytic_distribution_id', '!=', False)])
        #contract_line_ids = self.pool.get('limp.contract.line').search(cr, uid, [('contract_id', 'in', dist_contract_ids)])
        for account in ids:
            #contract_ids = self.pool.get('limp.contract').search(cr, uid, [('analytic_account_id', '=', account),('analytic_distribution_id', '=', False)])
            contract_ids = self.pool.get('limp.contract').search(cr, uid, [('analytic_account_id', '=', account)])
            #clean_line_ids = self.pool.get('limp.contract.line.cleaning').search(cr, uid, [('analytic_acc_id', '=', account),('contract_line_id', 'in', contract_line_ids)])
            #home_help_line_ids = self.pool.get('limp.contract.line.home.help').search(cr, uid, [('analytic_acc_id', '=', account),('contract_line_id', 'in', contract_line_ids)])
            #res[account] = (contract_ids or clean_line_ids or home_help_line_ids) and True or False
            res[account] = contract_ids and True or False

        return res

    def _search_is_contract(self, cr, uid, obj, name, args, context=None):
        ids = []

        #all_contract_ids = self.pool.get('limp.contract').search(cr, uid, [('analytic_distribution_id', '=', False)])
        all_contract_ids = self.pool.get('limp.contract').search(cr, uid, [])
        #dist_contract_ids = self.pool.get('limp.contract').search(cr, uid, [('analytic_distribution_id', '!=', False)])
        #contract_line_ids = self.pool.get('limp.contract.line').search(cr, uid, [('contract_id', 'in', dist_contract_ids)])
        #clean_line_ids = self.pool.get('limp.contract.line.cleaning').search(cr, uid, [('contract_line_id', 'in', contract_line_ids)])
        #home_help_line_ids = self.pool.get('limp.contract.line.home.help').search(cr, uid, [('contract_line_id', 'in', contract_line_ids)])
        for data in self.pool.get('limp.contract').read(cr, uid, all_contract_ids, ['analytic_account_id']):
            if data['analytic_account_id']:
                ids.append(data['analytic_account_id'][0])
        #~ for data in self.pool.get('limp.contract.line.cleaning').read(cr, uid, clean_line_ids, ['analytic_acc_id']):
            #~ if data['analytic_acc_id']:
                #~ ids.append(data['analytic_acc_id'][0])
        #~ for data in self.pool.get('limp.contract.line.home.help').read(cr, uid, home_help_line_ids, ['analytic_acc_id']):
            #~ if data['analytic_acc_id']:
                #~ ids.append(data['analytic_acc_id'][0])
        if args and args[0][2]:
            ids = [('id', 'in', list(set(ids)))]
        else:
            ids = [('id', 'not in', list(set(ids)))]

        return ids

    def _get_is_picking(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for account in ids:
            picking_ids = self.pool.get('stock.service.picking').search(cr, uid, [('analytic_acc_id', '=', account),('contract_id', '=', False)])
            res[account] = picking_ids and True or False

        return res

    def _search_is_picking(self, cr, uid, obj, name, args, context=None):
        ids = []

        all_picking_ids = self.pool.get('stock.service.picking').search(cr, uid, [])
        for data in self.pool.get('stock.service.picking').read(cr, uid, all_picking_ids, ['analytic_acc_id', 'contract_id']):
            if data['analytic_acc_id'] and not data['contract_id']:
                ids.append(data['analytic_acc_id'][0])
        if args and args[0][2]:
            ids = [('id', 'in', list(set(ids)))]
        else:
            ids = [('id', 'not in', list(set(ids)))]

        return ids

    def _get_is_picking_contract(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for account in ids:
            picking_ids = self.pool.get('stock.service.picking').search(cr, uid, [('analytic_acc_id', '=', account),('contract_id', '!=', False),('maintenance', '=', False)])
            res[account] = picking_ids and True or False

        return res

    def _get_invoice_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for account in self.browse(cr, uid, ids):
            res[account.id] = self.pool.get('account.invoice').search(cr, uid, [('analytic_id', 'in', [account.id] + [x.id for x in account.child_ids])])

        return res

    def _search_is_picking_contract(self, cr, uid, obj, name, args, context=None):
        ids = []

        all_picking_ids = self.pool.get('stock.service.picking').search(cr, uid, [])
        for data in self.pool.get('stock.service.picking').read(cr, uid, all_picking_ids, ['analytic_acc_id', 'contract_id', 'maintenance']):
            if data['analytic_acc_id'] and data['contract_id'] and not data['maintenance']:
                ids.append(data['analytic_acc_id'][0])
        if args and args[0][2]:
            ids = [('id', 'in', list(set(ids)))]
        else:
            ids = [('id', 'not in', list(set(ids)))]

        return ids

    _columns = {
        'invoice_ids': fields.function(_get_invoice_ids, method =True, type="one2many", relation='account.invoice', string='Invoices', readonly=True),
        'state_id': fields.many2one('res.country.state', 'Province'),
        'location_id': fields.many2one('city.council', 'Council'),
        'concept_amount': fields.function(_get_total_amount, method=True, string="Concepts amount", readonly=True, type="float", digits_compute=dp.get_precision('Account')),
        'address_invoice_id': fields.many2one('res.partner', 'Address invoice'),
        'address_id': fields.many2one('res.partner', 'Address'),
        'region_id': fields.many2one('res.country.region', 'Autonomous'),
        'privacy': fields.selection([('public', 'Public'), ('private', 'Private')], 'Privacy'),
        'is_contract': fields.function(_get_is_contract, method=True, fnct_search=_search_is_contract, type="boolean", readonly=True, string="Is contract"),
        'is_picking': fields.function(_get_is_picking, method=True, fnct_search=_search_is_picking, type="boolean", readonly=True, string="Is picking"),
        'is_picking_in_contract': fields.function(_get_is_picking_contract, method=True, fnct_search=_search_is_picking_contract, type="boolean", readonly=True, string="Is picking in contract"),
        'invoice_limit_hours': fields.float('Invoice limit hours', digits=(7, 2)),
        'invoice_by_high': fields.boolean('Invoice by high'),
        'analytic_distribution_id': fields.many2one('account.analytic.plan.instance','Analytic Distribution'),
        'address_tramit_id': fields.many2one('res.partner', "Tramit address"),
        'partner_name': fields.related('partner_id', 'name', type="char", size=256, readonly=True, store=True, string="Partner name")
    }

    _defaults = {
        'state': lambda *a: 'draft',
        'privacy': lambda *a: 'private',
        'invoice_by_high': True
    }

    def _process_concept_name(self, cr, uid, concept_rel, analytic, date, context=None):
        """Add new replacements"""
        if context is None: context = {}

        name = super(account_analytic_account, self)._process_concept_name(cr, uid, concept_rel, analytic, date, context=context)
        name = name.replace('%(customer)s', analytic.partner_id.name)

        home_help_lines = self.pool.get('limp.contract.line.home.help').search(cr, uid, [('analytic_acc_id', '=', analytic.id)])
        if home_help_lines:
            contact = self.pool.get('limp.contract.line.home.help').browse(cr, uid, home_help_lines[0]).customer_contact_id
            if contact:
                name = name.replace('%(contact)s', contact.first_name  + u" " + contact.name)

        cleaning_lines = self.pool.get('limp.contract.line.cleaning').search(cr, uid, [('analytic_acc_id', '=', analytic.id)])
        if cleaning_lines:
            ## MARTA (01.10.2014 09:46) Daba error cuando el objecto no tenía dirección configurada o,
            ## bien la dirección no tenía nombre. ##
            line_cleaning_obj = self.pool.get('limp.contract.line.cleaning').browse(cr, uid, cleaning_lines[0])
            if line_cleaning_obj.address_id and line_cleaning_obj.address_id.name:
                name = name.replace('%(center)s', line_cleaning_obj.address_id.name)

        return name

    def _invoice_hook(self, cr, uid, analytic, invoice_id, end_date, context=None):
        """fills fields with contract data"""
        if context is None: context = {}

        super(account_analytic_account, self)._invoice_hook(cr, uid, analytic, invoice_id, end_date, context=context)

        line = False
        vals = {}

        home_help_lines = self.pool.get('limp.contract.line.home.help').search(cr, uid, [('analytic_acc_id', '=', analytic.id)])
        if home_help_lines:
            line = self.pool.get('limp.contract.line.home.help').browse(cr, uid, home_help_lines[0])

        cleaning_lines = self.pool.get('limp.contract.line.cleaning').search(cr, uid, [('analytic_acc_id', '=', analytic.id)])
        if cleaning_lines:
            line = self.pool.get('limp.contract.line.cleaning').browse(cr, uid, cleaning_lines[0])

        if line:
            vals = {
                'payment_term': line.contract_id.payment_term_id and line.contract_id.payment_term_id.id or (analytic.partner_id.property_payment_term and analytic.partner_id.property_payment_term.id or False),
                'payment_type': line.contract_id.payment_type_id and line.contract_id.payment_type_id.id or (analytic.partner_id.payment_type_customer and analytic.partner_id.payment_type_customer.id or False),
                'invoice_header': line.contract_id.invoice_header,
                'partner_bank_id': (line.contract_id.payment_type_id and line.contract_id.payment_type_id.suitable_bank_types) and (line.contract_id.bank_account_id and line.contract_id.bank_account_id.id or (analytic.partner_id.bank_ids and analytic.partner_id.bank_ids[0].id or False)) or False
            }
            if line.contract_id.address_invoice_id:
                vals.update({'address_invoice_id': line.contract_id.address_invoice_id.id})
            if line.contract_id.address_id:
                vals.update({'address_contact_id': line.contract_id.address_id.id})
            if line.contract_id.address_tramit_id:
                vals.update({'address_tramit_id': line.contract_id.address_tramit_id.id})

            if line.contract_id.include_pickings:
                picking_ids = self.pool.get('stock.service.picking').search(cr, uid, [('contract_id','=',line.contract_id.id),('invoice_line_ids', '=', False),('state','=','closed'),('invoice_type','!=', 'noinvoice'),('retired_date', '<=', end_date)])
                wzd = self.pool.get('add.to.invoice').create(cr, uid, {'invoice_id': invoice_id})
                self.pool.get('add.to.invoice').add_to_invoice(cr, uid, [wzd], context={'active_ids': picking_ids})

        else:
            contracts = self.pool.get('limp.contract').search(cr, uid, [('analytic_account_id', '=', analytic.id)])
            if contracts:
                contract = self.pool.get('limp.contract').browse(cr, uid, contracts[0])
                vals = {
                    'payment_term': contract.payment_term_id and contract.payment_term_id.id or (analytic.partner_id.property_payment_term and analytic.partner_id.property_payment_term.id or False),
                    'payment_type': contract.payment_type_id and contract.payment_type_id.id or (analytic.partner_id.payment_type_customer and analytic.partner_id.payment_type_customer.id or False),
                    'contract_id': contract.id,
                    'invoice_header': contract.invoice_header,
                    'partner_bank_id': (contract.payment_type_id and contract.payment_type_id.suitable_bank_types) and (contract.bank_account_id and contract.bank_account_id.id or (analytic.partner_id.bank_ids and analytic.partner_id.bank_ids[0].id or False)) or False
                }
                if contract.address_invoice_id:
                    vals.update({'address_invoice_id': contract.address_invoice_id.id})
                if contract.address_id:
                    vals.update({'address_contact_id': contract.address_id.id})
                if contract.address_tramit_id:
                    vals.update({'address_tramit_id': contract.address_tramit_id.id})

                if contract.include_pickings:
                    picking_ids = self.pool.get('stock.service.picking').search(cr, uid, [('contract_id','=',contract.id),('invoice_line_ids', '=', False),('state','=','closed'),('invoice_type','!=', 'noinvoice'),('retired_date', '<=', end_date)])
                    wzd = self.pool.get('add.to.invoice').create(cr, uid, {'invoice_id': invoice_id})
                    self.pool.get('add.to.invoice').add_to_invoice(cr, uid, [wzd], context={'active_ids': picking_ids})

        vals.update({'delegation_id': analytic.delegation_id and analytic.delegation_id.id or False})
        self.pool.get('account.invoice').write(cr, uid, [invoice_id], vals, context=context)

        return

    def _get_duration(self, cr, uid, analytic, concept, end_date):
        """returns an add of occupations duration in analytic account in currently month"""
        analytic_obj = self.pool.get('account.analytic.account').browse(cr, uid, analytic)
        start_date = concept.last_invoice_date and datetime.strptime(concept.last_invoice_date + " 00:00:00", "%Y-%m-%d %H:%M:%S") + relativedelta(days=+1) or datetime.strptime(analytic_obj.date_start + " 00:00:00", "%Y-%m-%d %H:%M:%S")
        day, days = calendar.monthrange(end_date.year, end_date.month)
        user = self.pool.get('res.users').browse(cr, uid, uid)
        #end_date = datetime.now()
        SUNDAY_RULE = "FREQ=WEEKLY;BYDAY=SU;INTERVAL=1;UNTIL=" + end_date.strftime("%Y%m%dT%H%M%S")
        SATURDAY_RULE = "FREQ=WEEKLY;BYDAY=SA;INTERVAL=1;UNTIL=" + end_date.strftime("%Y%m%dT%H%M%S")
        exceptions = []
        if concept._get_except_months()[concept.id]:
            EXCEPT_MONTHS_RULE = "FREQ=DAILY;BYMONTH=" + ",".join([str(x) for x in concept._get_except_months()[concept.id]]) + ";INTERVAL=1;UNTIL=" + end_date.strftime("%Y%m%dT%H%M%S")
            rset2 = rrule.rrulestr(EXCEPT_MONTHS_RULE, dtstart=start_date, forceset=True)
            exceptions = map(lambda x:x.strftime('%Y-%m-%d'), rset2._iter())

        rset1 = rrule.rrulestr(SUNDAY_RULE, dtstart=start_date, forceset=True) #search sunday date in the period
        rset3 = rrule.rrulestr(SATURDAY_RULE, dtstart=start_date, forceset=True) #search saturday date in the period
        sundays = map(lambda x:x.strftime('%Y-%m-%d'), rset1._iter())
        saturdays = map(lambda x:x.strftime('%Y-%m-%d'), rset3._iter())

        duration = 0.0
        holiday_duration = 0.0
        sunday_duration = 0.0
        saturday_duration = 0.0
        diff_exceptions = 0.0
        total_hours = 0.0
        holidays = []
        occupations_ids = self.pool.get('account.analytic.occupation').search(cr, uid, [('analytic_account_id', '=', analytic), ('date', '>=', start_date.strftime("%Y-%m-%d")), ('date', '<=', end_date.strftime("%Y-%m-%d")), ('state', 'in', ['active', 'replacement'])])
        if occupations_ids:
            occupation = self.pool.get('account.analytic.occupation').read(cr, uid, occupations_ids[0], ['employee_id', 'date', 'location_id', 'state_id', 'region_id'])
            tmp_start_date = start_date.strftime("%Y-%m-%d")
            tmp_end_date = end_date.strftime("%Y-%m-%d")
            for holiday in self.pool.get('hr.holiday').get_holidays_dates(cr, uid, [occupation['employee_id'][0]], occupation.get('location_id', False) and occupation['location_id'][0] or False, occupation.get('state_id', False) and occupation['state_id'][0] or False, occupation.get('region_id', False) and occupation['region_id'][0] or False)[occupation['employee_id'][0]]:
                if holiday >= tmp_start_date and holiday <= tmp_end_date:
                    holidays.append(holiday)
        for occupation in self.pool.get('account.analytic.occupation').read(cr, uid, occupations_ids, ['employee_id', 'date', 'location_id', 'state_id', 'region_id', 'parent_occupation_id', 'to_invoice']):
            occupation_date = occupation['date'][:10]
            hours, minutes, seconds = occupation['date'][11:].split(":")
            occupation_hour = int(hours) + (((int(minutes) * 60.0 + int(seconds)) / 60.0) / 60.0)
            #holidays = self.pool.get('hr.holiday').get_holidays_dates(cr, uid, [occupation['employee_id'][0]], occupation.get('location_id', False) and occupation['location_id'][0] or False, occupation.get('state_id', False) and occupation['state_id'][0] or False, occupation.get('region_id', False) and occupation['region_id'][0] or False)[occupation['employee_id'][0]]
            if occupation.get('parent_occupation_id', False):
                parent_occ = self.pool.get('account.analytic.occupation').browse(cr, uid, occupation['parent_occupation_id'][0])
            else:
                parent_occ = False

            if occupation_date >= start_date.strftime("%Y-%m-%d") and occupation_date <= end_date.strftime("%Y-%m-%d") and occupation_date not in exceptions:
                #check if it's holiday, checkingh if it's weekend or it's in employee holiday calendars
                occupation_duration = self.pool.get('account.analytic.occupation').get_duration_to_invoice(cr, uid, occupation['id'])

                if occupation_date in sundays:
                    if concept.sunday_amount or concept.holyday_amount:
                        sunday_duration += occupation_duration
                        total_hours += occupation_duration
                elif occupation_date in holidays:
                    if concept.holyday_amount:
                        holiday_duration += occupation_duration
                        total_hours += occupation_duration
                elif occupation_date in saturdays and occupation_hour >= user.company_id.afternoon_time:
                    saturday_duration += occupation_duration
                    total_hours += occupation_duration
                else:
                    duration += occupation_duration
                    total_hours += occupation_duration

                if parent_occ and occupation.get('to_invoice', False):
                    diff_exceptions += (parent_occ.duration - occupation_duration)

                if analytic_obj.invoice_limit_hours and not analytic_obj.invoice_by_high and (analytic_obj.invoice_limit_hours - diff_exceptions) < total_hours:
                    rest = total_hours - (analytic_obj.invoice_limit_hours - diff_exceptions)
                    if occupation_date in sundays and sunday_concept_ids:
                        sunday_duration -= rest
                        total_hours -= rest
                    elif occupation_date in holidays and holiday_concept_ids:
                        holiday_duration -= rest
                        total_hours -= rest
                    elif occupation_date in saturdays and occupation_hour >= user.company_id.afternoon_time:
                        saturday_duration -= rest
                        total_hours -= rest
                    else:
                        duration -= rest
                        total_hours -= rest

        if analytic_obj.invoice_limit_hours and analytic_obj.invoice_by_high:
            hours_limit = analytic_obj.invoice_limit_hours - diff_exceptions
            if total_hours > hours_limit:
                to_remove_hours = total_hours - hours_limit
                if duration >= to_remove_hours:
                    duration -= to_remove_hours
                else:
                    to_remove_hours -= duration
                    duration = 0.0
                    if saturday_duration >= to_remove_hours:
                        saturday_duration -= to_remove_hours
                    else:
                        to_remove_hours -= saturday_duration
                        saturday_duration = 0.0
                        if sunday_duration >= to_remove_hours:
                            sunday_duration -= to_remove_hours
                        else:
                            to_remove_hours -= sunday_duration
                            sunday_duration = 0.0
                            if holiday_duration >= to_remove_hours:
                                holiday_duration -= to_remove_hours
                            else:
                                holiday_duration = 0.0
                                duration = 0.0
                                saturday_duration = 0.0
                                sunday_duration = 0.0

        invoice_limit_hours = analytic_obj.invoice_limit_hours - diff_exceptions
        if analytic_obj.invoice_limit_hours and invoice_limit_hours > total_hours:
            suma = invoice_limit_hours - total_hours
            duration += suma
        return duration, holiday_duration, sunday_duration, saturday_duration

    def __group_by_product_lines(self, cr, uid, ref_line, grouped_lines):
        res = super(account_analytic_account, self).__group_by_product_lines(cr, uid, ref_line, grouped_lines)
        ref_line = self.pool.get('account.invoice.line').browse(cr, uid, ref_line.id)

        total_hours = (ref_line.hours or 0.0)
        for line in self.pool.get('account.invoice.line').browse(cr, uid, grouped_lines):
            total_hours += (line.hours or 0.0)
        if total_hours:
            ref_line.write({'hours': total_hours,'name': ref_line.name + u" " + str(total_hours)})
        return res

    def _invoice_line_hook(self, cr, uid, analytic, concept, invoice_line, end_date, context=None):
        """manage invoice concepts per hours"""
        if context is None: context = {}
        super(account_analytic_account, self)._invoice_line_hook(cr, uid, analytic, concept, invoice_line, end_date, context=context)

        duration = 0.0
        holy_duration = 0.0
        sunday_duration = 0.0
        saturday_duration = 0.0

        if concept.per_hours:
            contract_ids = self.pool.get('limp.contract').search(cr, uid, [('analytic_account_id', '=', analytic.id)])
            if contract_ids: #if it's a contract
                for contract in self.pool.get('limp.contract').browse(cr, uid, contract_ids):
                    for home_line in contract.home_help_line_ids:
                        duration_draft, holy_duration_draft, sunday_duration_draft, saturday_duration_draft = self._get_duration(cr, uid, home_line.analytic_acc_id.id, concept, end_date)
                        duration += duration_draft
                        holy_duration += holy_duration_draft
                        sunday_duration += sunday_duration_draft
                        saturday_duration += saturday_duration_draft
                    for cleaning_line in contract.cleaning_line_ids:
                        duration_draft, holy_duration_draft, sunday_duration_draft, saturday_duration_draft = self._get_duration(cr, uid, cleaning_line.analytic_acc_id.id, concept, end_date)
                        duration += duration_draft
                        holy_duration += holy_duration_draft
                        sunday_duration += sunday_duration_draft
                        saturday_duration += saturday_duration_draft
            else:
                duration_draft, holy_duration_draft, sunday_duration_draft, saturday_duration_draft = self._get_duration(cr, uid, analytic.id, concept, end_date)
                duration += duration_draft
                holy_duration += holy_duration_draft
                sunday_duration += sunday_duration_draft
                saturday_duration += saturday_duration_draft

            if duration or holy_duration or sunday_duration or saturday_duration:
                if not concept.holyday_amount:
                    holy_duration = 0.0
                if not concept.sunday_amount and not concept.holyday_amount:
                    sunday_duration = 0.0
                duration = duration
                holy_duration = holy_duration
                sunday_duration = sunday_duration
                saturday_duration = saturday_duration

                inv_line = self.pool.get('account.invoice.line').browse(cr,uid,invoice_line)
                self.pool.get('account.invoice.line').write(cr, uid, [invoice_line],
                                                            {'price_unit': duration * concept.amount + holy_duration * concept.holyday_amount + sunday_duration * (concept.sunday_amount or concept.holyday_amount) + saturday_duration * (concept.saturday_afternoon_amount or concept.amount),
                                                             'name':inv_line.name.replace('%(hours)s',str(duration + holy_duration + sunday_duration + saturday_duration)),
                                                             'hours': duration + holy_duration + sunday_duration + saturday_duration})
            else:
                self.pool.get('account.invoice.line').unlink(cr, uid, [invoice_line])
                return False

        if analytic.analytic_distribution_id:
            self.pool.get('account.invoice.line').write(cr, uid, [invoice_line],
                                                        {'account_analytic_id': False,
                                                         'analytics_id': analytic.analytic_distribution_id.id})


        return True

    def _create_invoice(self, cr, uid, analytic, end_date, context=None):
        """creates an invoice to an analytic account"""
        if context is None: context = {}

        res = super(account_analytic_account, self)._create_invoice(cr, uid, analytic, end_date, context=context)

        self.pool.get('account.invoice').write(cr, uid, [res], {
                'user_id': analytic.manager_id and analytic.manager_id.user_id and analytic.manager_id.user_id.id or uid,
                'manager_id': analytic.manager_id and analytic.manager_id.id or False
                })


        return res

    def create(self, cr, uid, vals, context=None):
        if context is None: context = {}
        res = super(account_analytic_account, self).create(cr, uid, vals, context=context)
        if vals.get('parent_id', False):
            contract_ids = self.pool.get('limp.contract').search(cr, uid, [('analytic_account_id', '=', vals['parent_id'])])
            if contract_ids:
                parent = self.browse(cr, uid, vals['parent_id'])
                self.write(cr, uid, [res], {'privacy': parent.privacy})
        return res

    def write(self, cr, uid, ids, vals, context=None):
        if context is None: context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if vals.get('privacy', False):
            for contract in self.browse(cr, uid, ids):
                contract_ids = self.pool.get('limp.contract').search(cr, uid, [('analytic_account_id', '=', contract.id)])
                if contract_ids and contract.privacy != vals['privacy']:
                    self.write(cr, uid, [x.id for x in contract.child_ids], {'privacy': vals['privacy']})
        res = super(account_analytic_account, self).write(cr, uid, ids, vals, context=context)
        if vals.get('parent_id', False):
            contract_ids = self.pool.get('limp.contract').search(cr, uid, [('analytic_account_id', '=', vals['parent_id'])])
            if contract_ids:
                parent = self.browse(cr, uid, vals['parent_id'])
                self.write(cr, uid, ids, {'privacy': parent.privacy})

        return res

account_analytic_account()
