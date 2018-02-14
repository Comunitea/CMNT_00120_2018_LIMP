# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
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
from openerp import models, fields, api


class AnalyticIncidenceWizard(models.TransientModel):

    _name = "analytic.incidence.wizard"

    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    date = fields.Date(required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Account', readonly=True)
    child_ids = fields.Many2one('remuneration','Childs remunerations',readonly=True)
    #'parent_id': fields.one2many('child_ids', 'remuneration', 'Remuneration parent', readonly=True), MIGRACION: Revisar campos
    date_to = fields.Date()
    incidence_id_tp = fields.Many2one('incidence', 'Type')
    absence_id_tp = fields.Many2one('absence', 'Type absence')
    conditions = fields.Selection([('equal_condition', 'Equal conditions'), ('diff_condition', 'Different conditions')], 'Conditions', required=True, default='equal_condition')
    with_contract = fields.Boolean('With contract')
    contract_hours = fields.Float('Hours', digits=(12, 2))
    with_hour_price = fields.Boolean('With hour price')
    hour_price_hours = fields.Float('Hours', digits=(12, 2))
    with_fix_qty = fields.Boolean('With fix qty')
    price = fields.Float(digits=(12, 2))
    quantity = fields.Float('Quantity', digits=(12, 2))
    ss_hours = fields.Float('SS hours', digits=(4, 2))
    ss_no_hours = fields.Float('No ss hours', digits=(4, 2))
    effective = fields.Float('Effective', digits=(12, 2))

    @api.multi
    def make_child_remunerations(self):
        '''MIGRACION: Solo firma
        vals = {}
        if context is None:
            context = {}
        for line_child_remu in self.browse(cr,uid,ids):
            vals = {
                'with_contract': line_child_remu.with_contract,
                'contract_hours': line_child_remu.contract_hours,
                'with_hour_price': line_child_remu.with_hour_price,
                'hour_price_hours': line_child_remu.hour_price_hours,
                'with_fix_qty': line_child_remu.with_fix_qty,
                'price': line_child_remu.price,
                'quantity': line_child_remu.quantity,
                'date': line_child_remu.date,
                'incidence_id_tp': line_child_remu.incidence_id_tp.id,
                'absence_id_tp': line_child_remu.absence_id_tp.id,
                'date_to': line_child_remu.date_to,
                'conditions': line_child_remu.conditions,
                'ss_hours': line_child_remu.ss_hours,
                'ss_no_hours': line_child_remu.ss_no_hours,
                'effective': line_child_remu.effective
                }

            remuneration_ids = context.get('active_ids', [])
            if remuneration_ids:
                visited_occupations = self.pool.get('remuneration').make_child_inc_remuneration(cr,uid,remuneration_ids,vals)

            return {
                'type': 'ir.actions.act_window_close',
            }'''
