# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) Comunitea Servicios Informáticos. All Rights Reserved
#    #Carlos Lombardía Rodríguez carlos@comunitea.com#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the Affero GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the Affero GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api, _

class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    type_analytic = fields.Char('Type', compute='_compute_type_analytic', store=True)
    privacy = fields.Selection([('public', 'Public'), ('private', 'Private')],
                               'Privacy', related='account_id.privacy',
                               readonly=True)

    @api.depends('remuneration_id', 'timesheet_id')
    def _compute_type_analytic(self):
        for line in self:
            if line.remuneration_id:
                line.type_analytic = line.remuneration_id.incidence_id_tp.name
            elif line.timesheet_id:
                line.type_analytic = _("Timesheet")
            else:
                line.type_analytic = False
