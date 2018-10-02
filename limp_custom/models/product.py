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
from odoo import models, fields , _

WARNING_MESSAGE = [
                   ('no-message','No Message'),
                   ('warning','Warning'),
                   ('block','Blocking Message')
                   ]


WARNING_HELP = _('Selecting the "Warning" option will notify user with the message, Selecting "Blocking Message" will throw an exception with the message and block the flow. The Message has to be written in the next field.')

class ProductTemplate(models.Model):

    _inherit = "product.template"

    department_id = fields.Many2one('hr.department', 'Department')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    picking_warn = fields.Selection(WARNING_MESSAGE, 'Picking Warning',
                                      help=WARNING_HELP, default='no-message')
    picking_warn_msg = fields.Text('Message for Picking')
