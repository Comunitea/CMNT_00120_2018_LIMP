# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class AccountJournal(models.Model):

    _inherit = 'account.journal'

    analytic_tag_id = fields.Many2one('account.analytic.tag', 'Tag')
