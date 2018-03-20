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


class AccountAnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    _order = 'name desc'

    delegation_id = fields.Many2one(
        'res.delegation', 'Delegation', change_default=1,
        default=lambda r: r._context.get('delegation_id',
                                         r.env.user.context_delegation_id.id))
    manager_id = fields.Many2one(
        'hr.employee', 'Responsible', domain=[('responsible', '=', True)],
        default=lambda r: r._context.get('c_manager_id',
                                         r.env.user.employee_ids and
                                         r.env.user.employee_ids[0].id or
                                         False))
    department_id = fields.Many2one(
        default=lambda r: r._context.get('c_department_id', r._context.get('context_department_id', r.env.user.context_department_id.id)))


class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    delegation_id = fields.Many2one(
        'res.delegation', 'Delegation',
        default=lambda r: r.env.user.context_delegation_id.id)
    manager_id = fields.Many2one(
        'hr.employee', 'Responsible',
        domain=[('responsible', '=', True)],
        default=lambda r: r._context.get(
            'c_manager_id', r.env.user.employee_ids and
            r.env.user.employee_ids[0].id or False))
    move_id = fields.Many2one(
        'account.move.line', 'Move Line', ondelete='cascade', index=True)
    employee_id = fields.Many2one('hr.employee', 'Employee')
    partner_id = fields.Many2one('res.partner', 'Partner')
