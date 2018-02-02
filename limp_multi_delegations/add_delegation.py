# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#    $Marta Vázquez Rodríguez$
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
import report

if 'old_set_context' not in dir(report.report_sxw.rml_parse):
    report.report_sxw.rml_parse.old_set_context = report.report_sxw.rml_parse.set_context

def set_context2(self,objects, data, ids, report_type = None):
    self.old_set_context(objects, data, ids, report_type = report_type)
    if objects and len(objects) == 1 and objects[0].exists() and 'delegation_id' in objects[0] and objects[0].delegation_id:
        self.localcontext['delegation'] = objects[0].delegation_id

#override set_context method of class rml_parser
report.report_sxw.rml_parse.set_context = set_context2
