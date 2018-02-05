# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 Omar Castiñeira Savedra (http://www.pexego.es)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the Affero GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the Affero GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields

class res_partner_address(models.Model):

    _inherit = "res.partner.address"

    _columns = {
        'dir3': fields.char('DIR3', size=10, help="Field required for Face facturae format"),
        'sef': fields.char('SEF', size=10)
    }

res_partner_address()

class res_partner_address(models.Model):

    _inherit = "res.partner.address"

    _columns = {
        'type': fields.selection( [ ('default','Default'),('invoice','Invoice'), ('delivery','Delivery'), ('contact','Contact'), ('other','Other'), ('tramit', 'Tramit')],'Address Type', help="Used to select automatically the right address according to the context in sales and purchases documents."),
    }

res_partner_address()
