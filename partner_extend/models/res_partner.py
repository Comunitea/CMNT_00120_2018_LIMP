# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, api, fields


class ResPartner(models.Model):

    _inherit = "res.partner"

    is_company=fields.Boolean(default=True)

    @api.model
    def _commercial_fields(self):
        res = super(ResPartner, self)._commercial_fields()
        res.remove('vat')
        return res

    @api.multi
    def name_get(self):
        result = []
        orig_name = dict(super(ResPartner, self).name_get())
        for partner in self:
            name = orig_name[partner.id]
            if not partner.is_company:
                addr = "%s %s %s %s" % \
                    ((partner.name == '/' and
                      partner.commercial_partner_id.name or
                      (partner.name or '')),
                     partner.street or '', partner.zip or '',
                     partner.city or '')
                name = addr.strip()
            result.append((partner.id, name))
        return result
