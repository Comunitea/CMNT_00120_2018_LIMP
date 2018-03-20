# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
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
from odoo.addons import decimal_precision as dp

class LimpContractUpamountHistory(models.Model):

    _name = "limp.contract.upamount.history"
    _description = "Contract upamount history"
    _order = "date desc"

    name = fields.Char('Description', size=255, required=True)
    upamount_percent = fields.Float('Upamount percent', digits=(12,3), required=True, readonly=True)
    previous_amount = fields.Float('Previous amount', digits=dp.get_precision('Account'), required=True, readonly=True)
    new_amount = fields.Float('New amount', digits=dp.get_precision('Account'), required=True, readonly=True)
    date = fields.Date('Date', required=True, default=fields.Date.today)
    contract_id = fields.Many2one('limp.contract', 'Contract', required=True)


class LimpContract(models.Model):
    _inherit = 'limp.contract'

    upamount_history_ids = fields.One2many('limp.contract.upamount.history', 'contract_id', 'Upamounts history')
