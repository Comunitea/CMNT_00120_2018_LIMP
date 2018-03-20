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
from odoo import models, fields, api

class IrSequence(models.Model):

    _inherit = "ir.sequence"

    delegation_id = fields.Many2one('res.delegation', 'Delegation')

    @api.model
    def search_by_delegation(self, code, delegation):
        """search sequence by code and delegation"""
        company_id = self.env.user.company_id.id or None

        self.env.cr.execute('''SELECT id
                      FROM ir_sequence
                      WHERE code='%s'
                       AND active=true
                       AND (company_id = %s or company_id is NULL)
                       AND (delegation_id = %s or delegation_id is NULL)
                      ORDER BY company_id, id
                      FOR UPDATE NOWAIT''' % (code, company_id, delegation))
        res = self.env.cr.dictfetchone()

        return res and res['id'] or False

    @api.model
    def get_by_delegation(self, code, delegation):
        """obtains corect sequence by delegation and code"""
        res = self.search_by_delegation(code, delegation)
        if res:
            return self.browse(res).next_by_id()
        return self.next_by_code(code)
