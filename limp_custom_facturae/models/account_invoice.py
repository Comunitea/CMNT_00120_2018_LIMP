# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    address_tramit_id = fields.Many2one('res.partner', "Tramit address")
