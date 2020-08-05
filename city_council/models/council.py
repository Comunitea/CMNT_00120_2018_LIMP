##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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


class CityCouncil(models.Model):

    _name = "city.council"

    name = fields.Char("Council", required=True)
    zip_ids = fields.One2many("res.city", "council_id", "Zipcodes")


class ResCity(models.Model):

    _inherit = "res.city"

    council_id = fields.Many2one("city.council", "Council")


class AccountAnalyticAccount(models.Model):

    _inherit = "account.analytic.account"

    location_id = fields.Many2one("city.council", "Council")
