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


class AccountAsset(models.Model):

    _inherit = "account.asset"

    analytic_distribution_id = fields.Many2one(
        "account.analytic.tag", "Analytic distribution",
        domain=[('active_analytic_distribution', '=', True)]
    )


class AccountAssetLine(models.Model):

    _inherit = "account.asset.line"

    def _setup_move_line_data(self, depreciation_date, account, ml_type, move):
        res = super()._setup_move_line_data(depreciation_date, account,
                                            ml_type, move)
        asset = self.asset_id
        if ml_type == 'expense' and asset.analytic_distribution_id:
            if res.get('analytic_account_id'):
                del res['analytic_account_id']
            res['analytic_tag_ids'] = \
                [(6, 0, [asset.analytic_distribution_id.id])]
        return res
