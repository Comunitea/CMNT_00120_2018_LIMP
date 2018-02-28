# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 Pexego Sistemas Informáticos. All Rights Reserved
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
from odoo import models, fields


class AccountAnalyticDistributionRule(models.Model):

    _inherit = 'account.analytic.distribution.rule'

    delegation_id = fields.Many2one(
        'res.delegation', 'Delegation', required=True,
        default=lambda r: r.env.user.context_delegation_id.id)
    department_id = fields.Many2one('hr.department', 'Department',
                                    required=True)
    manager_id = fields.Many2one(
        'hr.employee', 'Responsible', required=True,
        domain=[('responsible', '=', True)],
        default=lambda r: r.env.user.employee_ids and
        r.env.user.employee_ids[0].id or False)
    fix_amount = fields.Float(digits=(12, 2), required=True)

    # 'department_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context).context_department_id.id,  MIGRACION: El campo context_department_id no existe