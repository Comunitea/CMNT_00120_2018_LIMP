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


class LimpContractTask(models.Model):

    _name = "limp.contract.task"
    _description = "Limpergal contract tasks"

    _order = "sequence asc"

    name = fields.Char('Name', size=256, required=True)
    department_id = fields.Many2one('hr.department', 'Department', required=True)
    parent_id = fields.Many2one('limp.contract.task', 'Parent Task')
    sequence = fields.Integer('Sequence', default=0)
    company_id = fields.Many2one('res.company', 'Company')
    center_type_id = fields.Many2one("limp.center.type", "Center type")

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion('parent_id'):
            raise ValueError(_('Error ! You cannot create recursive categories.'))
