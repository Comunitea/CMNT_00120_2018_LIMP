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

import time
from osv import fields,osv
from tools.translate import _

WARNING_MESSAGE = [
                   ('no-message','No Message'),
                   ('warning','Warning'),
                   ('block','Blocking Message')
                   ]


WARNING_HELP = _('Selecting the "Warning" option will notify user with the message, Selecting "Blocking Message" will throw an exception with the message and block the flow. The Message has to be written in the next field.')

class product_template(osv.osv):

    _inherit = "product.template"

    _columns = {
        'department_id': fields.many2one('hr.department', 'Department')
    }

product_template()

class product_product(osv.osv):
    _inherit = 'product.product'
    _columns = {
         'picking_warn': fields.selection(WARNING_MESSAGE, 'Picking Warning',
                                          help=WARNING_HELP),
         'picking_warn_msg' : fields.text('Message for Picking'),
         'tax_product': fields.boolean('Tax product'),
         'biocide_type': fields.char('Biocide type', size=150),
         'active_matter_percent': fields.float('Active Mater (%)',
                                               digits=(16, 3)),
         'registration_no': fields.char('Registration no.', size=150),
         'application_method': fields.char('Application method', size=150),
         'dosis': fields.float('Dosis (%)', digits=(16, 3)),
         'security_term': fields.char('Security term', size=150)
     }

    _defaults = {
         'picking_warn' : lambda *a: 'no-message',
    }

product_product()
