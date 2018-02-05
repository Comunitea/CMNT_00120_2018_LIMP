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

"""inherits hr_department to create new relationship from departments to users in many2many behaviour"""

from openerp import models, fields

class hr_department(models.Model):
    """inherits hr_department to create new relationship from departments to users in many2many behaviour"""

    _inherit = "hr.department"

    _columns = {
        'user_ids': fields.many2many('res.users', 'hr_department_users_rel', 'department_id', 'user_id', 'Related users'),
        'code': fields.char('Code', size=8)
    }

hr_department()