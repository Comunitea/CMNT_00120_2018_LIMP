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
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from openerp.addons import decimal_precision as dp


class ServicePickingStockMove(models.Model):

    _name = "service.picking.stock.move"
    _description = "Model between stock_move and analytic_account"
    _rec_name = "move_id"

    def _get_default_location(self):
        if self._context.get('employee_id', False):
            employee = self.env['hr.employee'].browse(self._context.get('employee_id', False))
        else:
            employee = self.env.user.employee_ids[0]
        return employee.location_id.id

    employee_id = fields.Many2one('hr.employee', 'Manager', required=True, states={'second':[('readonly',True)]}, default=lambda r: r._context.get('employee_id', self.env.user.employee_ids[0].id))
    location_id = fields.Many2one('stock.location', 'Location', required=True, states={'second':[('readonly',True)]}, default=_get_default_location)
    product_id = fields.Many2one('product.product', 'Product', required=True, states={'second':[('readonly',True)]})
    product_qty = fields.Float('Quantity', required=True, digits=dp.get_precision('Product UoM'), states={'second':[('readonly',True)]}, default=1.0)
    move_id = fields.Many2one('stock.move', 'Move', readonly=True)
    service_picking_id = fields.Many2one('stock.service.picking', 'Service picking')
    state = fields.Selection([('first', 'First'), ('second', 'Second')], 'State', readonly=True, default='first')

    @api.model
    def create(self, vals):
        res = super(ServicePickingStockMove, self).create(vals)

        if not res.employee_id.location_id:
            raise UserError(_('Employee must have an associated location !'))
        if not res.employee_id.company_id:
            raise UserError(_('Employee must have an associated company !'))
        if not res.employee_id.company_id.partner_id.property_stock_customer or res.employee_id.company_id.partner_id.property_stock_customer.usage != 'customer':
            raise UserError(_('Company must have set an output customer location in its partner form !'))
        if not res.service_picking_id.analytic_acc_id:
            raise UserError(_('It should cover the analytical mind. But, you can not target the corresponding movements !'))

        move_obj = self.env['stock.move'].create(
            {
                'product_id': res.product_id.id,
                'product_qty': res.product_qty,
                'product_uom': res.product_id.uom_id.id,
                'origin': res.service_picking_id.analytic_acc_id.name,
                'location_id': res.location_id.id,
                'location_dest_id': res.employee_id.company_id.partner_id.property_stock_customer.id,
                'name': res.service_picking_id.analytic_acc_id.name + u": Out " + res.product_id.name,
                'company_id': res.employee_id.company_id.id,
                'partner_id': res.employee_id.company_id.partner_id.id})

        move_obj.action_confirm()
        move_obj.force_assign()
        move_obj.action_done()

        tag_ids = self.env['account.analytic.tag'].search([('name', '=', 'Material')])
        if not tag_ids:
            raise UserError(_("Cannot find analytic tag 'Material'!"))

        a = res.product_id.product_tmpl_id.property_account_expense.id
        if not a:
            a = res.product_id.categ_id.property_account_expense_categ.id
            if not a:
                raise UserError(_('No product and product category expense property account defined on the related product.\nFill these on product form.'))

        self.env['account.analytic.line'].create(
            {
                'amount': -(res.product_id.standard_price * res.product_qty),
                'name': res.service_picking_id.analytic_acc_id.name + u": Out " + res.product_id.name,
                'company_id': res.employee_id.company_id.id,
                'product_id': res.product_id.id,
                'tag_ids': [(4, tag_ids[0])],
                'account_id': res.service_picking_id.analytic_acc_id.id,
                'general_account_id': a
            })

        res.write({'state': 'second', 'move_id': move_id})
        return res

    @api.multi
    def unlink(self):
        raise UserError(_('Cannot delete any record.'))
