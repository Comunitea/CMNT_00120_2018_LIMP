# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Comunitea Servicios Tecnológicos. All Rights Reserved
#    $Omar Castiñeira Saavedra$ omar@pexego.esst
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

import time
from report import report_sxw
from openerp.osv import osv
# import pooler MIGRACION: Comentado
from openerp.tools.translate import _

class frequency_table_parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(frequency_table_parser, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'filter_objs': self._filter_objects
        })

    def _filter_objects(self, objects):
        new_objects = []
        for obj in objects:
            if obj.lu or obj.ma or obj.mi or obj.ju or obj.vi or obj.sa or obj.do or obj.sm or obj.qc or obj.m or obj.bt or obj.tr or obj.ct or obj.st or obj.an or obj.s_n:
                new_objects.append(obj)

        return new_objects

report_sxw.report_sxw('report.sale.order.freq.table','sale.order','addons/limp_sale/report/limp_sale_frequency_table.rml',parser=frequency_table_parser)
