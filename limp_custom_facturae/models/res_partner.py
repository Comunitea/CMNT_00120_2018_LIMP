# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class ResPartner(models.Model):

    _inherit = 'res.partner'

    dir3 = fields.Char('DIR3', size=10,
                       help="Field required for Face facturae format")
    sef = fields.Char('SEF', size=10)
