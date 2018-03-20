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

"""new model between stock_move and analytic_account"""

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class AccountAnalyticStockMove(models.Model):
    """new model between stock_move and analytic_account"""

    _name = "account.analytic.stock.move"
    _description = "Model between stock_move and analytic_account"
    _rec_name = "move_id"

    @api.model
    def _get_default_employee_id(self):
        employee_id = False
        if self._context.get('employee_id', False):
            employee_id = self._context['employee_id']
        elif self.env.user.employee_ids:
            employee_id = self.env.user.employee_ids[0].id
        return employee_id

    @api.model
    def _get_default_location_id(self):
        employee = self.env['hr.employee'].browse(self._get_default_employee_id())
        return employee.location_id.id

    employee_id = fields.Many2one('hr.employee', 'Manager', required=True,
                                  states={'second': [('readonly', True)]},
                                  default=_get_default_employee_id)
    location_id = fields.Many2one('stock.location', 'Location', required=True,
                                  states={'second': [('readonly', True)]},
                                  default=_get_default_location_id)
    product_id = fields.Many2one('product.product', 'Product', required=True,
                                 states={'second':[('readonly',True)]})
    product_qty = fields.Float('Quantity', required=True,
                               digits=dp.get_precision('Product UoM'),
                               states={'second': [('readonly', True)]},
                               default=1.0)
    move_id = fields.Many2one('stock.move', 'Move', readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account',
                                          'Analytic')
    state = fields.Selection([('first', 'First'), ('second', 'Second')],
                             'State', readonly=True, default='first')
    date = fields.Date("Date", required=True, default=fields.Date.today)

    @api.model
    def create(self, vals):

        res = super(AccountAnalyticStockMove, self).create(vals)
        user = self.env.user
        if not res.location_id and not res.employee_id.location_id:
            raise UserError(_('Employee must have an associated location !'))
        if not user.company_id.partner_id.property_stock_customer or \
                user.company_id.partner_id.property_stock_customer.usage != 'customer':
            raise UserError(_('Company must have set an output customer location in its partner form !'))
        move = self.env['stock.move'].create(
            {'date': res.date,
             'product_id': res.product_id.id,
             'product_uom_qty': res.product_qty,
             'product_uom': res.product_id.uom_id.id,
             'origin': res.analytic_account_id.name,
             'location_id': res.location_id.id,
             'location_dest_id': user.company_id.partner_id.property_stock_customer.id,
             'name': res.analytic_account_id.name + u": Out " + res.product_id.name,
             'company_id': user.company_id.id,
             'partner_id': user.company_id.partner_id.id})

        move.action_confirm()
        move.force_assign()
        move.action_done()

        material_tag = self.env.ref('analytic_material_costs.material_cost_tag')

        account_id = res.product_id.product_tmpl_id.property_account_expense_id.id
        if not account_id:
            account_id = res.product_id.categ_id.property_account_expense_categ_id.id
            if not account_id:
                raise UserError(
                    _('No product and product category expense property '
                      'account defined on the related product.\nFill these'
                      ' on product form.'))

        self.env['account.analytic.line'].create(
        {
            'amount': -(res.product_id.standard_price * res.product_qty),
            'name': res.analytic_account_id.name + u": Out " + res.product_id.name,
            'company_id': user.company_id.id,
            'product_id': res.product_id.id,
            'tag_ids': [(4, material_tag.id)],
            'account_id': res.analytic_account_id.id,
            'general_account_id': account_id
        })

        res.write({'state': 'second', 'move_id': move.id})

        return res

    @api.multi
    def unlink(self):
        """Avoid delete an analytic entry"""
        raise UserError(_('Cannot delete any record.'))
