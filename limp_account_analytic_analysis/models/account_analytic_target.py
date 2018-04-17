# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Pexego Sistemas Informáticos. All Rights Reserved
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
import time


class AccountAnalyticTarget(models.Model):
    _name = "account.analytic.target"
    _rec_name = "year"
    _order = "year desc"

    analytic_tag_id = fields.Many2one('account.analytic.tag', 'Tag')
    year = fields.Integer(default=lambda r: int(time.strftime('%Y')))
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda r: r.env.user.company_id.id)
    delegation_id = fields.Many2one('res.delegation', 'Delegation')
    department_id = fields.Many2one('hr.department', 'Department')
    manager_id = fields.Many2one('hr.employee', 'Responsible', domain=[('responsible', '=', True)])
    target_percent = fields.Float('Percent target', digits=(5,2), required=True)
