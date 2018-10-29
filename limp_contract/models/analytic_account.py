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
    is_contract = fields.Boolean('Is contract')
    is_picking = fields.Boolean('Is picking', compute='_compute_is_picking', search='_search_is_picking')
    is_picking_in_contract = fields.Boolean('Is picking in contract', compute='_compute_is_picking_contract', search='_search_is_picking_contract')
    analytic_distribution_id = fields.Many2one('account.analytic.distribution','Analytic Distribution')
    address_tramit_id = fields.Many2one('res.partner', "Tramit address")
    partner_name = fields.Char('Partner name', related='partner_id.name', readonly=True, store=True)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Open'),
         ('pending', 'Pending'),
         ('cancelled', 'Cancelled'),
         ('close', 'Closed'), ('template', 'Template')], required=True,
        default='draft')

    def _compute_concept_amount(self):
        """adds all fix amount in contract"""
        for account in self:
            account.concept_amount = sum(
                [x.total_amount for x in account.concept_ids])

    def _compute_is_picking(self):
        for account in self:
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
                [('analytic_acc_id', '=', account.id),
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
        ids = self.env['account.analytic.account']

        if name:
            partners = self.env['res.partner'].search([('name', operator, name)], limit=limit)
            if partners:
                ids = self.search([('partner_id', 'in', partners._ids)]+ args, limit=limit)
            ids += self.search(['|',('description', operator, name),('name', operator, name)]+ args, limit=limit)
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
                name = name.replace('%(contact)s', contact.name)

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
                'payment_term_id': line.contract_id.payment_term_id and line.contract_id.payment_term_id.id or (self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False),
                'payment_mode_id': line.contract_id.payment_type_id and line.contract_id.payment_type_id.id or (self.partner_id.customer_payment_mode_id and self.partner_id.customer_payment_mode_id.id or False),
                'invoice_header': line.contract_id.invoice_header,
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
                if picking_ids:
                    wzd = self.env['add.to.invoice'].\
                            with_context(active_ids=picking_ids.ids).\
                            create({'invoice_id': invoice_id.id})
                    wzd.with_context(active_ids=picking_ids.ids).add_to_invoice()

        else:
            contracts = self.env['limp.contract'].search(
                [('analytic_account_id', '=', self.id)])
            if contracts:
                contract = contracts[0]
                vals = {
                    'payment_term_id': contract.payment_term_id and contract.payment_term_id.id or (self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False),
                    'payment_mode_id': contract.payment_type_id and contract.payment_type_id.id or (self.partner_id.payment_type_customer_id and self.partner_id.payment_type_customer_id.id or False),
                    'contract_id': contract.id,
                    'invoice_header': contract.invoice_header,
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
                    if picking_ids:
                        wzd = self.env['add.to.invoice'].\
                            with_context(active_ids=picking_ids.ids).\
                            create({'invoice_id': invoice_id.id})
                        wzd.with_context(active_ids=picking_ids.ids).add_to_invoice()

        vals.update({'delegation_id': self.delegation_id and self.delegation_id.id or False})
        invoice_id.write(vals)
        return

    @api.model
    def __group_by_product_lines(self, ref_line, grouped_lines):
        res = super(AccountAnalyticAccount, self).__group_by_product_lines(ref_line, grouped_lines)
        total_hours = (ref_line.hours or 0.0)
        for line in grouped_lines:
            total_hours += (line.hours or 0.0)
        if total_hours:
            ref_line.write({'hours': total_hours,'name': ref_line.name + u" " + str(total_hours)})
        return res

    def _invoice_line_hook(self, concept, invoice_line, end_date):
        super(AccountAnalyticAccount, self)._invoice_line_hook(concept, invoice_line, end_date)
        if self.analytic_distribution_id:
            invoice_line.write(
                {'account_analytic_id': False,
                 'analytic_distribution_id': self.analytic_distribution_id.id})
        return True

    def _create_invoice(self, end_date):
        res = super(AccountAnalyticAccount, self)._create_invoice(end_date)

        res.write({
            'user_id': self.manager_id and self.manager_id.user_id and self.manager_id.user_id.id or self.env.user.id,
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
        if vals.get('state') and vals['state'] in ('open', 'close', 'cancelled'):
            for account in self:
                contract_ids = self.env['limp.contract'].search([('analytic_account_id', '=', account.id),('state', '!=', vals['state'])])
                if contract_ids:
                    contract_ids.write({'state': vals['state']})
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
