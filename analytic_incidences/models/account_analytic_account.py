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
from odoo import models, fields


class AccountAnalyticAccount(models.Model):
    """Adds remuneration fiels to analytic account's columns"""

    _inherit = "account.analytic.account"

    remuneration_ids = fields.One2many('remuneration', 'analytic_account_id',
                                       'Remunerations')
    active_remuneration_ids = fields.One2many(
        'remuneration', 'analytic_account_id', 'Active remunerations',
        domain=[('old', '=', False)])
    inactive_remuneration_ids = fields.One2many(
        'remuneration', 'analytic_account_id', 'Unactive remunerations',
        domain=[('old', '=', True)])
