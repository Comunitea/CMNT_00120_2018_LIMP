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

from openerp import models, fields

class res_partner_job(models.Model):

    _inherit = "res.partner.job"

    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        data = super(res_partner_job, self).default_get(cr, uid, fields, context=context)
        data2 = self._default_get(cr, uid, fields, context=context)
        data.update(data2)
        for f in data.keys():
            if f not in fields:
                del data[f]
        return data

    def _default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        data = {}
        sequence = 0

        if context.get('lines',[]):
            line_selected = False

            for line_record in context['lines']:
                if not isinstance(line_record, (tuple, list)):
                    line_record_detail = self.read(cr, uid, line_record, ['sequence_contact'])
                else:
                    line_record_detail = line_record[2]

                if line_record_detail['sequence_contact'] and line_record_detail['sequence_contact'] >= sequence:
                    line_selected = line_record_detail
                    sequence = line_record_detail['sequence_contact']

        data["sequence_contact"] = sequence + 1

        return data

res_partner_job()
