# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class AccountAnalyticTag(models.Model):

    _inherit = 'account.analytic.tag'

    show_in_report = fields.Boolean()
