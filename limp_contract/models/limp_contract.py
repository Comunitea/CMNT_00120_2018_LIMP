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
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from openerp.addons import decimal_precision as dp
from datetime import datetime


class LimpContract(models.Model):

    _name = 'limp.contract'
    _description = "Limpergal Contracts"
    _inherit = ['mail.thread']
    _inherits = {'account.analytic.account': "analytic_account_id"}

    prorogation_date = fields.Date('Prorogation date', help="Estimate prorogation date")
    prorogation_end_date = fields.Date('Prorogation end date', help="Prorogation end date")
    prorogation_notes = fields.Text('Notes')
    request_prorogation_date = fields.Date('Req. prorogation date')
    upamount_date = fields.Date('Upamount date', help="Estimate up amount date")
    request_upamount_date = fields.Date('Req. upamount date')
    amount = fields.Float('Total annual amount', digits=dp.get_precision('Account'), compute='_compute_contract_total_amount')
    monthly_amount = fields.Float('Monthly amount', digits=dp.get_precision('Account'), compute='_compute_contract_total_amount')
    periodicity = fields.Selection([('m', 'Monthy'), ('q', 'Quarterly'), ('b', 'Biannual'), ('a', 'Annual'), ('ph', 'Per hours')], 'Periodicity', default='m')
    bank_account_id = fields.Many2one('res.partner.bank', 'Bank account', help="Income bank account")
    analytic_account_id = fields.Many2one('account.analytic.account', 'Account', readonly=True, required=True, ondelete="cascade")
    state = fields.Selection([('draft', 'Draft'), ('wait_signature', 'Waiting signature'), ('open', 'Opened'), ('close', 'Closed'), ('cancelled', 'Cancelled')], 'State', readonly=True, default='draft')
    active = fields.Boolean('Active', default=True)
    seq_lines_id = fields.Many2one('ir.sequence', 'Sequence', readonly=True)
    home_help_line_ids = fields.One2many('limp.contract.line.home.help', 'contract_id', 'Home help lines', states={'cancelled':[('readonly',True)], 'close':[('readonly',True)]})
    cleaning_line_ids = fields.One2many('limp.contract.line.cleaning', 'contract_id', 'Cleaning lines', states={'cancelled':[('readonly',True)], 'close':[('readonly',True)]})
    stock_service_picking_ids = fields.One2many('stock.service.picking', 'contract_id', 'Picking lines', states={'cancelled':[('readonly',True)], 'close':[('readonly',True)]}, domain=[('picking_type','=','wastes')])
    stock_sporadic_service_picking_ids = fields.One2many('stock.service.picking', 'contract_id', 'Sporadic picking lines', states={'cancelled':[('readonly',True)], 'close':[('readonly',True)]}, domain=[('picking_type','=','sporadic')])
    payment_term_id = fields.Many2one('account.payment.term', 'Payment term')
    payment_type_id = fields.Many2one('account.payment.mode', 'Payment type') # MIGRACION: Movido a payment.mode
    contact_id = fields.Many2one('res.partner', 'Contact')
    note = fields.Text('Description')
    include_pickings = fields.Boolean('Include pickings')
    signature_date = fields.Date('Signature date', readonly=True)
    contract_note_ids = fields.One2many('limp.contract.note', 'contract_id', 'Notes')
    invoice_header = fields.Char('Invoice header', size=128)
    contract_duration = fields.Char('Contract duration', size=128)
    contract_end_date = fields.Date('End date')
    invoice_count = fields.Integer(string='# of Invoices', compute='_compute_invoiced', readonly=True)
    upamount_history_count = fields.Integer(string='# of upamount_history', compute='_compute_upamount_history_count', readonly=True)
    home_help_lines_count = fields.Integer(string='# of home_help_lines', compute='_compute_home_help_lines_count', readonly=True)
    cleaning_lines_count = fields.Integer(string='# of cleaning_lines', compute='_compute_cleaning_lines_count', readonly=True)
    waste_lines_count = fields.Integer(string='# of waste', compute='_compute_waste_lines_count', readonly=True)
    service_picking_lines_count = fields.Integer(string='# of serv. pickings', compute='_compute_service_picking_lines_count', readonly=True)
    active_remuneration_lines_count = fields.Integer(string='# of remunerations', compute='_compute_active_remuneration_lines_count', readonly=True)
    contract_note_count = fields.Integer(string='# of notes', compute='_compute_contract_note_count', readonly=True)
    analytic_moves_count = fields.Integer(string='# of consummtions', compute='_compute_analytic_moves_count', readonly=True)
    maintenance_task_count = fields.Integer(string='# of maintenance tasks', compute='_compute_maintenance_task_count', readonly=True)
    timesheet_count = fields.Integer(string='# of timesheets', compute='_compute_timesheet_count', readonly=True)


    def get_same_contract_accounts(self, extra_domain = []):
        self.ensure_one()
        contract_tag = self.tag_ids.filtered('contract_tag').id
        if contract_tag:
            accounts = self.env['account.analytic.account'].search(
                [('tag_ids', '=', contract_tag),
                 ('id', '!=', self.analytic_account_id.id)] + extra_domain)
            if accounts:
                return accounts
        return self.env['account.analytic.account']

    def _compute_contract_total_amount(self):
        for contract in self:
            amount = 0.0
            if contract.state == 'open':
                amount += sum([x.total_amount for x in contract.concept_ids])
            for home_help_line in contract.home_help_line_ids:
                if home_help_line.state == 'open':
                    amount += sum([x.total_amount for x in home_help_line.concept_ids])
            for cleaning_line in contract.cleaning_line_ids:
                if cleaning_line.state == 'open':
                    amount += sum([x.total_amount for x in cleaning_line.concept_ids])
            contract.amount = amount
            contract.monthly_amount = round(amount / 12.0, 2)

    def invoice_run(self):
        id_invoice = []
        invoice_ids = self.env['account.invoice']
        for obj in self:
            contract_tag = obj.tag_ids.filtered('contract_tag')
            if obj.analytic_account_id and obj.state == 'open':
                child_ids = self.env['account.analytic.account'].search(
                    [('state', '=', 'open'), ('partner_id', '!=', False),
                    ('invoiceable', '=', True),
                    ('tag_ids', 'in', [contract_tag.id]),
                    ('date_start', '<', self._context['end_date'])],
                    order='create_date')
                child_ids += obj.analytic_account_id
                invoice_ids += child_ids.run_invoice_cron_manual()

        if invoice_ids:
            action = self.env.ref('account.action_invoice_tree1').read()[0]
            if action:
                action['domain'] = "[('id','in', ["+','.join(map(str, invoice_ids.ids))+"])]"
                action["nodestroy"] = True
                return action
        return True

    @api.model
    def create(self, vals):
        vals['is_contract'] = True
        vals['name'] = self.env['ir.sequence'].get_by_delegation('limp.contract.seq', vals['delegation_id'])
        vals['tag_ids'] = [(0, 0, {'name': vals['name'], 'contract_tag': True})]
        # obtains contract lines sequence id and copy default to assign new sequence for this contract lines
        seq_id = self.env['ir.sequence'].search_by_delegation('limp.contract.line.seq', vals['delegation_id'])
        if seq_id:
            vals['seq_lines_id'] = self.env['ir.sequence'].browse(seq_id).copy({'number_next': 1}).id
        vals['invoiceable'] = True
        new_id = super(LimpContract, self).create(vals)
        new_id.write({'state': 'draft'}) # TODO: por qué no pasarlo en vals?
        return new_id

    def write(self, vals):
        res = super(LimpContract, self).write(vals)
        for contract in self:
            if vals.get('state', False) and vals['state'] in ['open', 'close', 'cancelled']:
                contract.home_help_line_ids.filtered(lambda r: r.state in ['open','draft']).write({'state': vals['state']})
                contract.cleaning_line_ids.filtered(lambda r: r.state in ['open','draft']).write({'state': vals['state']})
                contract.analytic_account_id.state = vals['state']

            if vals.get('date', False):
                contract.home_help_line_ids.filtered(lambda r: r.date == False).write({'date': vals['date']})
                contract.cleaning_line_ids.filtered(lambda r: r.date == False).write({'date': vals['date']})
                contract.remuneration_ids.filtered(lambda r: not r.date_to).sudo().write({'date_to': vals['date']})

            if vals.get('date_start',False):
                contract.home_help_line_ids.write({'date_start': vals['date_start']})
                contract.cleaning_line_ids.write({'date_start': vals['date_start']})
                contract.remuneration_ids.sudo().write({'date': vals['date_start']})

            if vals.get('privacy',False):
                contract.home_help_line_ids.write({'privacy': vals['privacy']})
                contract.cleaning_line_ids.write({'privacy': vals['privacy']})
        return res

    def unlink(self):
        """delete associated analytic account"""
        account_to_delete = self.env['account.analytic.account']
        for contract in self:
            if contract.state not in ('draft','cancelled'):
                raise UserError(_("Only contracts in draft or cancelled states can be deleted."))
            account_to_delete += contract.get_same_contract_accounts()

        res = super(LimpContract, self).unlink()
        account_to_delete.unlink()
        return res

    def copy(self, default=None):
        if default is None:
            default = {}
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
        return super(LimpContract, self.sudo().with_context(is_contract=True)).copy(default)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            partner_obj = self.partner_id
            payment_type = partner_obj.customer_payment_mode_id and partner_obj.customer_payment_mode_id or False
            self.payment_type_id = payment_type and payment_type.id or False
            self.payment_term_id = partner_obj.property_payment_term_id and partner_obj.property_payment_term_id.id or False
            self.address_id = partner_obj.address_get(['contact'])['contact']
            self.address_invoice_id = partner_obj.address_get(['invoice'])['invoice']
            self.bank_account_id = (payment_type and payment_type.suitable_bank_types and partner_obj.bank_ids) and partner_obj.bank_ids[0].id or False

    def act_confirm(self):
        return self.write({'state': 'wait_signature'})

    def act_cancel(self):
        return self.write({'state': 'cancelled'})

    def act_reopen(self):
        for contract in self:
            line_ids = contract.get_same_contract_accounts(extra_domain=[('date', '=', contract.date)])
            line_ids.write({'date': False, 'state': 'open'})
        self.write({'state': 'open', 'date': False})
        return

    def act_draft(self):
        return self.write({'state': 'draft'})

    def act_close(self):
        for contract in self:
            if not contract.date or contract.date > fields.Date.today():
                raise UserError(_("Cannot close the contract without a final date less or equal today."))
        return self.write({'state': 'close'})

    def _compute_invoiced(self):
        for contract in self:
            contract.invoice_count = len(contract.invoice_ids)

    def action_view_invoices(self):
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        action['domain'] = "[('id','in', ["+','.join(map(str, self.invoice_ids._ids))+"])]"
        return action

    def _compute_upamount_history_count(self):
        for contract in self:
            contract.upamount_history_count = len(contract.upamount_history_ids)

    def action_view_upamount_history(self):
        action = self.env.ref('limp_contract.upamount_history_action').read()[0]
        action['domain'] = "[('id','in', ["+','.join(map(str, self.upamount_history_ids._ids))+"])]"
        return action

    def _compute_home_help_lines_count(self):
        for contract in self:
            contract.home_help_lines_count = len(contract.home_help_line_ids)

    def action_view_home_help_lines(self):
        action = self.env.ref('limp_contract.action_limp_contract_home_help_line').read()[0]
        action['context'] = str({
            'c_manager_id' : self.manager_id.id,
            'default_partner_id' : self.partner_id.id,
            'default_tag_ids' : [(4, x.id) for x in self.tag_ids],
            'c_delegation_id' : self.delegation_id.id,
            'default_company_id' : self.company_id.id,
            'c_department_id' : self.department_id.id,
            'default_contract_id': self.id})
        action['domain'] = "[('id','in', ["+','.join(map(str, self.home_help_line_ids._ids))+"])]"
        return action

    def _compute_cleaning_lines_count(self):
        for contract in self:
            contract.cleaning_lines_count = len(contract.cleaning_line_ids)

    def action_view_cleaning_lines(self):
        action = self.env.ref('limp_contract.action_limp_contract_cleaning_line').read()[0]
        action['context'] = str({
            'c_manager_id' : self.manager_id.id,
            'default_partner_id' : self.partner_id.id,
            'default_tag_ids' : [(4, x.id) for x in self.tag_ids],
            'c_delegation_id' : self.delegation_id.id,
            'default_company_id' : self.company_id.id,
            'c_department_id' : self.department_id.id,
            'default_contract_id': self.id})
        action['domain'] = "[('id','in', ["+','.join(map(str, self.cleaning_line_ids._ids))+"])]"
        return action

    def _compute_waste_lines_count(self):
        for contract in self:
            contract.waste_lines_count = len(contract.stock_service_picking_ids)

    def action_view_waste_lines(self):
        action = self.env.ref('limp_service_picking.service_pickings_action').read()[0]
        action['context'] = str({
           'default_tag_ids' : [(4, x.id) for x in self.tag_ids],
           'default_picking_type': 'wastes', 'type': 'wastes',
           'form_view_ref': 'limp_service_picking.stock_service_picking_form',
           'default_delegation_id' : self.delegation_id.id,
           'default_partner_id': self.partner_id.id,
           'default_manager_id': self.manager_id.id,
           'default_address_invoice_id': self.address_invoice_id.id,
           'default_address_id': self.address_id.id,
           'default_ccc_account_id': self.bank_account_id.id,
           'default_payment_type': self.payment_type_id.id,
           'default_payment_term': self.payment_term_id.id,
           'default_privacy': self.privacy,
           'default_address_tramit_id': self.address_tramit_id.id,
           'default_contract_id': self.id,
        })
        action['domain'] = "[('id','in', ["+','.join(map(str, self.stock_service_picking_ids._ids))+"])]"
        return action

    def _compute_service_picking_lines_count(self):
        for contract in self:
            contract.service_picking_lines_count = len(contract.stock_sporadic_service_picking_ids)

    def action_view_sporadic_service_picking(self):
        action = self.env.ref('limp_service_picking.sporadic_service_pickings_action').read()[0]
        action['context'] = str({
           'default_tag_ids' : [(4, x.id) for x in self.tag_ids],
           'default_picking_type': 'sporadic', 'type': 'sporadic',
           'form_view_ref': 'limp_service_picking.stock_service_picking_form',
           'default_delegation_id' : self.delegation_id.id,
           'default_partner_id': self.partner_id.id,
           'default_manager_id': self.manager_id.id,
           'default_address_invoice_id': self.address_invoice_id.id,
           'default_address_id': self.address_id.id,
           'default_ccc_account_id': self.bank_account_id.id,
           'default_payment_type': self.payment_type_id.id,
           'default_payment_term': self.payment_term_id.id,
           'default_privacy': self.privacy,
           'default_address_tramit_id': self.address_tramit_id.id,
           'default_contract_id': self.id,

        })
        action['domain'] = "[('id','in', ["+','.join(map(str, self.stock_sporadic_service_picking_ids._ids))+"])]"
        return action

    def _compute_active_remuneration_lines_count(self):
        for contract in self:
            contract.active_remuneration_lines_count = len(contract.active_remuneration_ids)

    def action_view_active_remuneration(self):
        action = self.env.ref('analytic_incidences.action_remuneration').read()[0]
        action['context'] = str({
            'default_analytic_account_id': self.analytic_account_id.id

        })
        action['domain'] = "[('id','in', ["+','.join(map(str, self.active_remuneration_ids._ids))+"])]"
        return action

    def _compute_contract_note_count(self):
        for contract in self:
            contract.contract_note_count = len(contract.contract_note_ids)

    def action_view_contract_note(self):
        action = self.env.ref('limp_contract.limp_contract_note_action').read()[0]
        action['context'] = str({
            'default_contract_id': self.id

        })
        action['domain'] = "[('id','in', ["+','.join(map(str, self.contract_note_ids._ids))+"])]"
        return action

    def _compute_analytic_moves_count(self):
        for contract in self:
            contract.analytic_moves_count = len(contract.analytic_move_ids)

    def action_view_analytic_moves(self):
        action = self.env.ref('analytic_material_costs.analytic_stock_move_concepts').read()[0]
        action['context'] = str({
            'employee_id': self.manager_id.id,
            'default_analytic_account_id': self.analytic_account_id.id

        })
        action['domain'] = "[('id','in', ["+','.join(map(str, self.analytic_move_ids._ids))+"])]"
        return action

    def _compute_maintenance_task_count(self):
        for contract in self:
            contract.maintenance_task_count = len(contract.maintenance_task_ids)

    def action_view_maintenance_task(self):
        action = self.env.ref('limp_contract.maintenance_task_action').read()[0]
        action['context'] = str({
            'default_contract_id': self.analytic_account_id.id

        })
        action['domain'] = "[('id','in', ["+','.join(map(str, self.maintenance_task_ids._ids))+"])]"
        return action

    def _compute_timesheet_count(self):
        for contract in self:
            contract.timesheet_count = len(contract.active_employee_ids)

    def action_view_timesheet(self):
        action = self.env.ref('limp_distribution_costs.action_timesheet').read()[0]
        action['context'] = str({ # TODO: AÑADIR RESPONSABLE
            'default_delegation_id': self.delegation_id.id,
            'default_department_id': self.department_id.id,
            'default_analytic_id': self.analytic_account_id.id,
        })
        action['domain'] = "[('id','in', ["+','.join(map(str, self.active_employee_ids._ids))+"])]"
        return action
