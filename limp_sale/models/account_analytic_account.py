# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class AccountAnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', default=lambda r: r._context.get('pricelist', False))
