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
from odoo import models, fields


class ResCompany(models.Model):

    _inherit = "res.company"

    jasper_report_header = fields.Text(
        "Jasper report header",
        help="Text to write in jasper reports header.",
        translate=True,
    )
    jasper_report_footer = fields.Text(
        "Jasper report footer",
        help="Text to write in jasper reports footer.",
        translate=True,
    )
    signature_image = fields.Binary("Signature")
