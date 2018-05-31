# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
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


class AccountAnalyticLine(models.Model):

    _inherit = "account.analytic.line"

    remuneration_id = fields.Many2one('remuneration', 'Remuneration',
                                      readonly=True)
    remuneration_incidence = fields.\
        Boolean(related='remuneration_id.incidence', readonly=True)
    company_id = fields.Many2one("res.company", related=None, string='Company',
                                 readonly=True)
    timesheet_id = fields.Many2one('timesheet', 'Timesheet', readonly=True)
    amount = fields.Float(digits=(16, 4))
