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

from openerp import models, fields, api, _
from openerp.addons.decimal_precision import decimal_precision as dp


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

    employee_id = fields.Many2one('hr.employee', 'Manager', required=True, states={'second':[('readonly',True)]}, default=_get_default_employee_id)
    location_id = fields.Many2one('stock.location', 'Location', required=True, states={'second':[('readonly',True)]}, default=_get_default_location_id)
    product_id = fields.Many2one('product.product', 'Product', required=True, states={'second':[('readonly',True)]})
    product_qty = fields.Float('Quantity', required=True, digits_compute=dp.get_precision('Product UoM'), states={'second':[('readonly',True)]}, default=1.0)
    move_id = fields.Many2one('stock.move', 'Move', readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic')
    state = fields.Selection([('first', 'First'), ('second', 'Second')], 'State', readonly=True, default='first')
    date = fields.Date("Date", required=True, default=fields.Date.today)

    @api.model
    def create(self):
        """creates stock_move and add cost in analytic_account"""
        return super(AccountAnalyticStockMove,self).create()
        '''MIGRACION: Solo firma
        if context is None: context = {}

        id = super(account_analytic_stock_move, self).create(cr, uid, vals, context=context)
        obj_id = self.browse(cr, uid, id)
        user = self.pool.get('res.users').browse(cr, uid, uid)

        if not obj_id.location_id and not obj_id.employee_id.location_id:
            raise osv.except_osv(_('Error'), _('Employee must have an associated location !'))
        if not user.company_id.partner_id.property_stock_customer or user.company_id.partner_id.property_stock_customer.usage != 'customer':
            raise osv.except_osv(_('Error'), _('Company must have set an output customer location in its partner form !'))

        move_id = self.pool.get('stock.move').create(cr, uid, {'date': obj_id.date,
                                                    'product_id': obj_id.product_id.id,
                                                    'product_qty': obj_id.product_qty,
                                                    'product_uom': obj_id.product_id.uom_id.id,
                                                    'origin': obj_id.analytic_account_id.name,
                                                    'location_id': obj_id.location_id.id,
                                                    'location_dest_id': user.company_id.partner_id.property_stock_customer.id,
                                                    'name': obj_id.analytic_account_id.name + u": Out " + obj_id.product_id.name,
                                                    'company_id': user.company_id.id,
                                                    'partner_id': user.company_id.partner_id.id})

        move_obj = self.pool.get('stock.move').browse(cr, uid, move_id)
        move_obj.action_confirm()
        move_obj.force_assign()
        move_obj.action_done()

        journal_ids = self.pool.get('account.analytic.journal').search(cr, uid, [('name', '=', 'Material')])
        if not journal_ids:
            raise osv.except_osv(_('Error'), _("Cannot find analytic journal 'Material'!"))

        a = obj_id.product_id.product_tmpl_id.property_account_expense.id
        if not a:
            a = obj_id.product_id.categ_id.property_account_expense_categ.id
            if not a:
                raise osv.except_osv(_('Bad Configuration !'),
                        _('No product and product category expense property account defined on the related product.\nFill these on product form.'))

        self.pool.get('account.analytic.line').create(cr, uid, {
                                                        'amount': -(obj_id.product_id.standard_price * obj_id.product_qty),
                                                        'name': obj_id.analytic_account_id.name + u": Out " + obj_id.product_id.name,
                                                        'company_id': user.company_id.id,
                                                        'product_id': obj_id.product_id.id,
                                                        'journal_id': journal_ids[0],
                                                        'account_id': obj_id.analytic_account_id.id,
                                                        'general_account_id': a
                                                })

        self.write(cr, uid, [id], {'state': 'second', 'move_id': move_id})

        return id'''

    @api.multi
    def unlink(self):
        """Avoid delete an analytic entry"""
        raise exceptions.Warning(_('Error !'), _('Cannot delete any record.'))
