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
from odoo.addons import decimal_precision as dp


class LimpContractLineHomeHelp(models.Model):

    _name = "limp.contract.line.home.help"
    _description = "Limpergal's contract lines for home help"
    _inherits = {'limp.contract.line': "contract_line_id", 'account.analytic.account': 'analytic_acc_id'}

    contract_line_id = fields.Many2one('limp.contract.line', 'Contract line', readonly=True, required=True, ondelete="cascade")
    customer_contact_id = fields.Many2one('res.partner', 'User', required=True)
    beneficiary_amount = fields.Float('Beneficiary amount', digits=dp.get_precision('Account'))
    check_amount = fields.Float('Check amount', digits=dp.get_precision('Account'))
    administration_amount = fields.Float('Administration amount', digits=dp.get_precision('Account'))
    partner_social_worker_id = fields.Many2one('res.partner', 'Partner social worker')
    analytic_acc_id = fields.Many2one('account.analytic.account', 'Analytic account', readonly=True, required=True, ondelete="cascade")
    social_worker_id = fields.Many2one('hr.employee', 'Social worker')

    def open_line(self):
        return self.write({'state': 'open'})

    def reopen_line(self):
        return self.write({'state': 'open'})

    def copy(self, default=None):
        if default is None:
            default = {}
        default.update({
            'state': 'draft',
            'date': False,
            'parent_id': False,
            'line_ids': [],
            'employee_ids': [],
            'active_employee_ids': [],
            'inactive_employee_ids': [],
            'report_employee_ids': []
        })
        return super(LimpContractLineHomeHelp, self.sudo()).copy(default)

    def copy_data(self, default=None):
        if not default:
            default = {}
        if self._context.get('is_contract', False):
            if self.date:
                return {}
        default.update({
            'state': 'draft',
            'date': False,
            'parent_id': False,
            'line_ids': [],
            'employee_ids': [],
            'active_employee_ids': [],
            'inactive_employee_ids': [],
            'report_employee_ids': []
        })
        return super(LimpContractLineHomeHelp, self).copy_data(default)

    @api.onchange('customer_contract_id')
    def onchange_customer_contact_id(self):
        """when changing customer contact set state_if field"""
        if self.customer_contact_id:
            contact_obj = self.env['res.partner'].browse(self.customer_contact_id)
            if contact_obj.job_id and contact_obj.job_id.address_id and contact_obj.job_id.address_id.state_id:
                self.state_id = contact_obj.job_id.address_id.state_id.id
            if contact_obj.job_id and contact_obj.job_id.address_id and contact_obj.job_id.address_id.location:
                self.location_id = contact_obj.job_id.address_id.location.id
            if contact_obj.job_id and contact_obj.job_id.address_id and contact_obj.job_id.address_id.region:
                self.region_id = contact_obj.job_id.address_id.region.id
            if contact_obj.job_id and contact_obj.job_id.address_id and contact_obj.job_id.address_id.council_id:
                self.location_id = contact_obj.job_id.address_id.council_id.id

    @api.model
    def create(self, vals):
        if vals.get('contract_id', False):
            contract = self.env['limp.contract'].browse(vals['contract_id'])
            if contract.seq_lines_id:
                num = contract.seq_lines_id.next_by_id()
                vals['name'] = contract.name + u" - " + num
                vals['num'] = num
                if not vals.get('delegation_id', False):
                    vals['delegation_id'] = contract.delegation_id.id
                if not vals.get('department_id', False):
                    vals['department_id'] = contract.department_id.id
                if not vals.get('company_id', False):
                    vals['company_id'] = contract.company_id.id
                if not vals.get('tag_ids', False):
                    vals['tag_ids'] = [(4, x.id) for x in contract.tag_ids]
        else:
            raise UserError(_('Not contract defined for this line'))
        vals['invoiceable'] = True
        return super(LimpContractLineHomeHelp, self).create(vals)

    def write(self, vals):
        res = super(LimpContractLineHomeHelp, self).write(vals)

        if vals.get('date', False) or vals.get('date_start', False):
            all_remuneration_ids = self.mapped('remuneration_ids')
            remuneration_ids_wo_dateto = self.mapped('remuneration_ids').filtered(lambda r: not r.date_to)

            if all_remuneration_ids:
                if vals.get('date_start', False):
                    all_remuneration_ids.sudo().write({'date': vals['date_start']})
                if vals.get('date', False) and remuneration_ids_wo_dateto:
                    remuneration_ids_wo_dateto.sudo().write({'date_to': vals['date']})
        if vals.get('state', False) and vals['state'] in ('open', 'close', 'cancelled'):
            for line in self:
                line.analytic_acc_id.state = vals['state']
        return res

    def unlink(self):
        for line in self:
            if line.state not in ('draft','cancelled'):
                raise UserError(_("Only contract lines in draft or cancelled states can be deleted."))
        res = super(LimpContractLineHomeHelp, self).unlink()
        self.mapped('contract_line_id').unlink()
        self.mapped('analytic_acc_id').unlink()
        return res
