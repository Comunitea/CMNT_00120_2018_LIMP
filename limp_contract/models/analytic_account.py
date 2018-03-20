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
from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil import rrule
import time
import calendar


class AccountAnalyticTag(models.Model):
    _inherit = 'account.analytic.tag'

    contract_tag = fields.Boolean()


class AccountAnalyticAccount(models.Model):
    """Adds new fields to analytics accounts"""

    _inherit = "account.analytic.account"
    _order = "partner_name asc,name asc"

    invoice_ids = fields.One2many('account.invoice', 'analytic_id', 'Invoices')
    state_id = fields.Many2one('res.country.state', 'Province')
    concept_amount = fields.Float('Concepts amount', digits=dp.get_precision('Account'), compute='_compute_concept_amount')
    address_invoice_id = fields.Many2one('res.partner', 'Address invoice')
    address_id = fields.Many2one('res.partner', 'Address')
    privacy = fields.Selection([('public', 'Public'), ('private', 'Private')], 'Privacy', default='private')
    is_contract = fields.Boolean('Is contract', compute='_compute_is_contract', search='_search_is_contract')
    is_picking = fields.Boolean('Is picking', compute='_compute_is_picking', search='_search_is_picking')
    is_picking_in_contract = fields.Boolean('Is picking in contract', compute='_compute_is_picking_contract', search='_search_is_picking_contract')
    invoice_limit_hours = fields.Float('Invoice limit hours', digits=(7, 2))
    invoice_by_high = fields.Boolean('Invoice by high', default=True)
    analytic_distribution_id = fields.Many2one('account.analytic.plan.instance','Analytic Distribution')
    address_tramit_id = fields.Many2one('res.partner', "Tramit address")
    partner_name = fields.Char('Partner name', related='partner_id.name', readonly=True, store=True)

    def _get_concept_amount(self, concept_ids):
        # TODO: Eliminar funcion
        raise Exception('use total_amount account.analytic.invoice.concept.rel')

    def _compute_concept_amount(self):
        """adds all fix amount in contract"""
        for account in self:
            account.concept_amount = sum(
                [x.total_amount for x in account.concept_ids])

    def _compute_is_contract(self):
        for account in self:
            contract_ids = self.env['limp.contract'].search(
                [('analytic_account_id', '=', account.id)])
            account.is_contract = contract_ids and True or False

    def _search_is_contract(self, operator, operand):
        ids = []
        all_contract_ids = self.env['limp.contract'].search([])
        for data in all_contract_ids.read(['analytic_account_id']):
            if data['analytic_account_id']:
                ids.append(data['analytic_account_id'][0])
        if operand:
            domain = [('id', 'in', list(set(ids)))]
        else:
            domain = [('id', 'not in', list(set(ids)))]
        return domain

    def _compute_is_picking(self):
        for account in ids:
            picking_ids = self.env['stock.service.picking'].search(
                [('analytic_acc_id', '=', account),
                 ('contract_id', '=', False)])
            self.is_picking = picking_ids and True or False

    def _search_is_picking(self, operator, operand):
        all_picking_ids = self.env['stock.service.picking'].search(
            [('contract_id', '=', False)])
        account_ids = all_picking_ids.mapped('analytic_acc_id.id')
        if operand:
            ids = [('id', 'in', list(set(account_ids)))]
        else:
            ids = [('id', 'not in', list(set(account_ids)))]
        return ids

    def _compute_is_picking_contract(self):
        for account in self:
            picking_ids = self.env['stock.service.picking'].search(
                [('analytic_acc_id', '=', account),
                 ('contract_id', '!=', False),
                 ('maintenance', '=', False)])
            account.is_picking_contract = picking_ids and True or False

    def _search_is_picking_contract(self, operator, operand):
        all_picking_ids = self.env['stock.service.picking'].search(
            [('contract_id', '!=', False), ('maintenance', '=', False)])
        account_ids = all_picking_ids.mapped('analytic_acc_id.id')
        if operand:
            ids = [('id', 'in', list(set(account_ids)))]
        else:
            ids = [('id', 'not in', list(set(account_ids)))]
        return ids

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        ids = []

        if name:
            partners = self.env['res.partner'].search([('name', operator, name)], limit=limit)
            if partners:
                ids = self.search([('partner_id', 'in', partners._ids)]+ args, limit=limit)
            ids += self.search([('name', operator, name)]+ args, limit=limit)
        else:
            ids = self.search(args, limit=limit)
        return ids.name_get()

    def name_get(self):
        res = []

        for obj in self:
            name = ""
            if obj.partner_id:
                name = obj.partner_id.name
                home_help_lines = self.env['limp.contract.line.home.help'].search([('analytic_acc_id', '=', obj.id)])
                if home_help_lines:
                    line = home_help_lines[0]
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

    def _process_concept_name(self, concept_rel, date):
        """Add new replacements"""
        name = super(AccountAnalyticAccount, self)._process_concept_name(concept_rel, date)
        name = name.replace('%(customer)s', self.partner_id.name)

        home_help_lines = self.env['limp.contract.line.home.help'].search([('analytic_acc_id', '=', self.id)])
        if home_help_lines:
            contact = home_help_lines[0].customer_contact_id
            if contact:
                name = name.replace('%(contact)s', contact.first_name  + u" " + contact.name)

        cleaning_lines = self.env['limp.contract.line.cleaning'].search([('analytic_acc_id', '=', self.id)])
        if cleaning_lines:
            line_cleaning_obj = cleaning_lines[0]
            if line_cleaning_obj.address_id and line_cleaning_obj.address_id.name:
                name = name.replace('%(center)s', line_cleaning_obj.address_id.name)
        return name

    def _invoice_hook(self, invoice_id, end_date):
        """fills fields with contract data"""
        self.ensure_one()
        super(AccountAnalyticAccount, self)._invoice_hook(invoice_id, end_date)

        line = False
        vals = {}

        home_help_lines = self.env['limp.contract.line.home.help'].search([('analytic_acc_id', '=', self.id)])
        if home_help_lines:
            line = home_help_lines[0]

        cleaning_lines = self.env['limp.contract.line.cleaning'].search([('analytic_acc_id', '=', self.id)])
        if cleaning_lines:
            line = cleaning_lines[0]

        if line:
            vals = {
                'payment_term': line.contract_id.payment_term_id and line.contract_id.payment_term_id.id or (self.partner_id.property_payment_term and self.partner_id.property_payment_term.id or False),
                'payment_type': line.contract_id.payment_type_id and line.contract_id.payment_type_id.id or (self.partner_id.payment_type_customer and self.partner_id.payment_type_customer.id or False),
                'invoice_header': line.contract_id.invoice_header,
                'partner_bank_id': (line.contract_id.payment_type_id and line.contract_id.payment_type_id.suitable_bank_types) and (line.contract_id.bank_account_id and line.contract_id.bank_account_id.id or (self.partner_id.bank_ids and self.partner_id.bank_ids[0].id or False)) or False
            }
            if line.contract_id.address_invoice_id:
                vals.update({'partner_id': line.contract_id.address_invoice_id.id})
            if line.contract_id.address_id:
                vals.update({'partner_shipping_id': line.contract_id.address_id.id})
            if line.contract_id.address_tramit_id:
                vals.update({'address_tramit_id': line.contract_id.address_tramit_id.id})

            if line.contract_id.include_pickings:
                picking_ids = self.env['stock.service.picking'].search(
                    [('contract_id','=',line.contract_id.id),
                     ('invoice_line_ids', '=', False),
                     ('state','=','closed'),
                     ('invoice_type','!=', 'noinvoice'),
                     ('retired_date', '<=', end_date)])
                wzd = self.env['add.to.invoice'].create({'invoice_id': invoice_id})
                wzd.with_context(active_ids=picking_ids._ids).add_to_invoice()

        else:
            contracts = self.env['limp.contract'].search(
                [('analytic_account_id', '=', self.id)])
            if contracts:
                contract = contracts[0]
                vals = {
                    'payment_term': contract.payment_term_id and contract.payment_term_id.id or (self.partner_id.property_payment_term and self.partner_id.property_payment_term.id or False),
                    'payment_type': contract.payment_type_id and contract.payment_type_id.id or (self.partner_id.payment_type_customer and self.partner_id.payment_type_customer.id or False),
                    'contract_id': contract.id,
                    'invoice_header': contract.invoice_header,
                    'partner_bank_id': (contract.payment_type_id and contract.payment_type_id.suitable_bank_types) and (contract.bank_account_id and contract.bank_account_id.id or (self.partner_id.bank_ids and self.partner_id.bank_ids[0].id or False)) or False
                }
                if contract.address_invoice_id:
                    vals.update({'partner_id': contract.address_invoice_id.id})
                if contract.address_id:
                    vals.update({'partner_shipping_id': contract.address_id.id})
                if contract.address_tramit_id:
                    vals.update({'address_tramit_id': contract.address_tramit_id.id})

                if contract.include_pickings:
                    picking_ids = self.env['stock.service.picking'].search(
                        [('contract_id','=',contract.id),
                         ('invoice_line_ids', '=', False),
                         ('state','=','closed'),
                         ('invoice_type','!=', 'noinvoice'),
                         ('retired_date', '<=', end_date)])
                    wzd = self.env['add.to.invoice'].create({'invoice_id': invoice_id})
                    wzd.with_context(active_ids=picking_ids._ids).add_to_invoice()

        vals.update({'delegation_id': self.delegation_id and self.delegation_id.id or False})
        invoice = self.env['account.invoice'].browse(invoice_id)
        invoice.write(vals)
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
        res = super(AccountAnalyticAccount, self).__group_by_product_lines(cr, uid, ref_line, grouped_lines)
        ref_line = self.pool.get('account.invoice.line').browse(cr, uid, ref_line.id)

        total_hours = (ref_line.hours or 0.0)
        for line in self.pool.get('account.invoice.line').browse(cr, uid, grouped_lines):
            total_hours += (line.hours or 0.0)
        if total_hours:
            ref_line.write({'hours': total_hours,'name': ref_line.name + u" " + str(total_hours)})
        return res

    def _invoice_line_hook(self, concept, invoice_line, end_date):
        super(AccountAnalyticAccount, self)._invoice_line_hook(concept, invoice_line, end_date)
        if self.analytic_distribution_id:
            invoice_line.write(
                {'account_analytic_id': False,
                 'analytics_id': self.analytic_distribution_id.id})
        return True

    def _create_invoice(self, end_date):
        res = super(AccountAnalyticAccount, self)._create_invoice(end_date)

        res.write({
            'user_id': self.manager_id and self.manager_id.user_id and self.manager_id.user_id.id or uid,
            'manager_id': self.manager_id and self.manager_id.id or False})
        return res

    def create(self, vals):
        res = super(AccountAnalyticAccount, self).create(vals)
        contract = res.get_contract()
        if contract:
            res.write({'privacy': contract.privacy})
        return res

    def write(self, vals):
        if vals.get('privacy', False):
            for account in self:
                contract_ids = self.env['limp.contract'].search([('analytic_account_id', '=', account.id)])
                if contract_ids and account.privacy != vals['privacy']:
                    self.get_same_contract_accounts().write({'privacy': vals['privacy']})
        res = super(AccountAnalyticAccount, self).write(vals)
        if vals.get('tag_ids', False):
            contract = self.get_contract()
            if contract:
                self.write({'privacy': contract.privacy})
        return res

    def get_contract(self):
        self.ensure_one()
        contract_tag = self.tag_ids.filtered('contract_tag').id
        if contract_tag:
            contracts = self.env['limp.contract'].search(
                [('tag_ids', '=', contract_tag)])
            if contracts:
                return contracts[0]

    def get_same_contract_accounts(self, extra_domain = []):
        self.ensure_one()
        contract_tag = self.tag_ids.filtered('contract_tag').id
        if contract_tag:
            accounts = self.env['account.analytic.account'].search([('tag_ids', '=', contract_tag), ('id', '!=', self.id)] + extra_domain)
            if accounts:
                return accounts
        return self.env['account.analytic.account']
