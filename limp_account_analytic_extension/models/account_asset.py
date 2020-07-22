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
        "account.analytic.distribution", "Analytic distribution"
    )

#TODO: Migrar
# ~ class AccountAssetDepreciationLine(models.Model):

    # ~ _inherit = "account.asset.depreciation.line"

    # ~ def create_move(self, post_move=True):
        # ~ res = super(AccountAssetDepreciationLine, self).create_move(post_move)

        # ~ for move in self.env["account.move"].browse(res):
            # ~ for line in move.line_ids:
                # ~ if line.asset_id and line.asset_id.analytic_distribution_id:
                    # ~ line.write(
                        # ~ {
                            # ~ "analytic_distribution_id": line.asset_id.analytic_distribution_id.id
                        # ~ }
                    # ~ )
        # ~ return res
