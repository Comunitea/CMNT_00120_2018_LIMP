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
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class LimpContractLineWaste(models.Model):
    _name = "limp.contract.line.waste"
    _description = "Limpergal's contract lines for waste"
    _inherits = {'limp.contract.line': "contract_line_id", 'account.analytic.account': 'analytic_acc_id'}

    contract_line_id = fields.Many2one('limp.contract.line', 'Contract line', readonly=True, required=True, ondelete="cascade")
    analytic_acc_id = fields.Many2one('account.analytic.account', 'Analytic account', readonly=True, required=True, ondelete="cascade")
    picking_line_ids = fields.One2many('stock.service.picking', 'contract_line_id', 'Pickings')
    delegation_id = fields.Many2one(default=lambda r: r._context.get('c_delegation_id', self.env.user.context_delegation_id.id))

    def open_line(self):
        return self.write({'state': 'open'})

    def reopen_line(self):
        return self.write({'state': 'open'})

    @api.model
    def create(self, vals):
        if vals.get('contract_id', False):
            contract = self.env['limp.contract'].browse(vals['contract_id'])
            partner = self.env['res.partner'].browse(vals['partner_id'])
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
                partner_address = self.env['res.partner'].browse(partner.address_get()['default'])
                if not vals.get('state_id', False):
                    vals['state_id'] = partner_address.state_id.id
                if not vals.get('location_id', False):
                    vals['location_id'] = partner_address.location_id.id
        else:
            raise UserError(_('Not contract defined for this line'))

        return super(LimpContractLineWaste, self).create(vals)

    def unlink(self):
        for line in self:
            if line.state not in ('draft','cancelled'):
                raise UserError(_("Only contract lines in draft or cancelled states can be deleted."))
        res = super(LimpContractLineHomeHelp, self).unlink()
        self.mapped('contract_line_id').unlink()
        self.mapped('analytic_acc_id').unlink()
        return res


class StockServicePicking(models.Model):

    _inherit = "stock.service.picking"

    contract_line_id = fields.Many2one('limp.contract.line.waste', 'Contract line')

    @api.model
    def create(self, vals):
        if vals.get('contract_line_id', False):
            line = self.env['limp.contract.line.waste'].browse(vals['contract_line_id'])
            vals['analytic_acc_id'] = line.analytic_acc_id and line.analytic_acc_id.id or False
        return super(stock_service_picking, self).create(vals)
