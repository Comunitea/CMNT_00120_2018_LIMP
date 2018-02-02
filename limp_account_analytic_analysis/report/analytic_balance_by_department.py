# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Comunitea Servicios Tecnológicos
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

import xlwt
from openerp.addons.report_xls.report_xls import report_xls
from datetime import datetime
import calendar
from report import report_sxw

_ir_translation_name = 'analytic_balance_by_department.xls'

class analytic_balance_by_department(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(analytic_balance_by_department, self).__init__(cr, uid, name, context=context)
        self.context = context
        self.localcontext.update({
            'datetime': datetime,
        })

class analytic_balance_by_department_xls(report_xls):

    def __init__(self, name, table, rml=False, parser=False, header=True, store=False):
        super(analytic_balance_by_department_xls, self).__init__(name, table, rml, parser, header, store)

        _xs = self.xls_styles
        rh_cell_format = _xs['bold'] + _xs['borders_all']
        # lines
        aml_cell_format = _xs['borders_all']
        self.aml_cell_style = xlwt.easyxf(aml_cell_format)
        self.aml_cell_style_center = xlwt.easyxf(aml_cell_format +
                                                 _xs['center'])
        self.aml_cell_style_date = xlwt.easyxf(aml_cell_format +
                                               _xs['left'],
                                               num_format_str=report_xls.date_format)
        self.aml_cell_style_decimal = xlwt.easyxf(aml_cell_format +
                                                  _xs['right'],
                                                  num_format_str=report_xls.decimal_format)

        self.rh_cell_style = xlwt.easyxf(rh_cell_format)

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        cell_styles = {
        'far_values': 'pattern: pattern solid, fore_color light_yellow;',
        'very_far_values': 'pattern: pattern solid, fore_color yellow;',
        'very_very_far_values': 'pattern: pattern solid, fore_color red;',
        'target_label': 'pattern: pattern solid, fore_color light_green;',
        'target_label_font': 'font: colour red, bold on, height 160;',
        'journals_months': 'font: colour dark_blue, bold on, height 160;',
        'average_real': 'pattern: pattern solid, fore_color ice_blue;',
        'average_real_font': 'font: colour dark_blue, bold on, height 160;',
        'bordered': 'border: top thin, right thin, bottom thin, left thin;',
        'bold': 'font: bold on, height 160;'
        }

        domain = []

        if data.get('delegation_id', False):
            domain.append(('delegation_id', '=', data['delegation_id']))
        if data.get('privacy', False):
            account_ids = self.pool.get('account.analytic.account').search(self.cr, self.uid, [('privacy', '=', data['privacy'])])
            domain.append(('account_id', 'child_of', account_ids))

        months = [('01','ENERO'),('02','FEBRERO'),('03','MARZO'),('04','ABRIL'),('05','MAYO'),('06','JUNIO'),('07','JULIO'),('08','AGOSTO'),('09','SEPTIEMBRE'),('10','OCTUBRE'),('11','NOVIEMBRE'),('12','DICIEMBRE')]
        report_name = (data.get('delegation_id', False) and  self.pool.get('res.delegation').browse(self.cr, self.uid, data['delegation_id'], context=_p).name or u"")
        report_name += u" " + self.pool.get('account.fiscalyear').browse(self.cr, self.uid, data['fiscalyear_id'], context=_p).name
        report_name += u" " + (data.get('privacy', False) and (data['privacy'] == 'public' and u'Sector público' or u'Sector Privado') or u"")
        ws = wb.add_sheet("1")
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        c_specs = [
            ('report_name', 10, 10, 'text', report_name),
        ]

        row_data = self.xls_row_template(c_specs, ['report_name'])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        row_pos += 1
        fstyle = xlwt.easyxf(cell_styles['target_label'] + cell_styles['target_label_font'] + cell_styles['bordered'])
        c_specs = [('department_id', 2, 2, 'text',  'DEPARTAMENTOS', None, fstyle)]
        fstyle = xlwt.easyxf(cell_styles['journals_months'] + cell_styles['bordered'])
        for month in months:
            c_specs.append(('month_' + month[0], 1, 0, 'text', month[1], None, fstyle))
        fstyle = xlwt.easyxf(cell_styles['average_real'] + cell_styles['average_real_font'] + cell_styles['bordered'])
        c_specs.append(('average', 1, 0, 'text',  'MEDIA', None, fstyle))
        c_specs.append(('real_percent', 1, 0, 'text',  '% REAL', None, fstyle))
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rh_cell_style)

        sale_journal_ids = self.pool.get('account.analytic.journal').search(self.cr, self.uid, [('type', '=', 'sale')], context=_p)
        fiscal_year = self.pool.get('account.fiscalyear').browse(self.cr, self.uid, data['fiscalyear_id'], context=_p)
        year = fiscal_year.code
        filter_domain = [('journal_id', 'in', sale_journal_ids),('date', '>=', fiscal_year.date_start),('date', '<=', fiscal_year.date_stop)] + domain
        total_income = sum([x.amount for x in self.pool.get('account.analytic.line').browse(self.cr, self.uid, self.pool.get('account.analytic.line').search(self.cr, self.uid, filter_domain), context=_p)])

        expense_journal_ids = self.pool.get('account.analytic.journal').search(self.cr, self.uid, [('type', '!=', 'sale')], context=_p)
        filter_domain = [('journal_id', 'in', expense_journal_ids),('date', '>=', fiscal_year.date_start),('date', '<=', fiscal_year.date_stop)] + domain
        total_expense = sum([x.amount for x in self.pool.get('account.analytic.line').browse(self.cr, self.uid, self.pool.get('account.analytic.line').search(self.cr, self.uid, filter_domain), context=_p)])
        total_expense = -total_expense
        expense_percent = round((total_expense * 100.0) / (total_income or 1.0), 2)

        department_ids = self.pool.get('hr.department').search(self.cr, self.uid, [], context=_p)
        department_ids = sorted(self.pool.get('hr.department').browse(self.cr, self.uid, department_ids, context=_p), key=lambda x: x.name)
        for department in department_ids:
            months_with_results = 0
            avergare_percent = 0.0
            fstyle = xlwt.easyxf(cell_styles['journals_months'] + cell_styles['bordered'])
            c_specs = [('department_id', 2, 2, 'text', department.name, None, fstyle)]
            expense_amount_total = 0.0
            income_amount_total = 0.0
            for month in months:
                first_day =  year + "-" + month[0] + "-01"
                last_day = year + "-" + month[0] + "-" + str(calendar.monthrange(int(year),int(month[0]))[1])

                filter_domain = [('department_id', '=', department.id),('date', '>=', first_day),('date', '<=',last_day)] + domain
                expense_amount = sum([x.amount for x in self.pool.get('account.analytic.line').browse(self.cr, self.uid, self.pool.get('account.analytic.line').search(self.cr, self.uid, filter_domain + [('journal_id', 'in', expense_journal_ids)]), context=_p)])
                income_amount = sum([x.amount for x in self.pool.get('account.analytic.line').browse(self.cr, self.uid, self.pool.get('account.analytic.line').search(self.cr, self.uid, filter_domain + [('journal_id', 'in', sale_journal_ids)]), context=_p)])
                expense_amount = -expense_amount
                expense_amount_total += expense_amount
                income_amount_total += income_amount
                if income_amount:
                    percent = round(((income_amount - expense_amount) * 100.0) / income_amount, 2)
                    months_with_results += 1
                else:
                    percent = 0
                avergare_percent += percent
                fstyle = xlwt.easyxf(cell_styles['bold'] + cell_styles['bordered'])
                c_specs.append(('month_' + month[0], 1, 0, 'number', percent, None, fstyle))

            average_percent = round(avergare_percent / (months_with_results or 1.0), 2)

            fstyle = xlwt.easyxf(cell_styles['bold'] + cell_styles['bordered'])
            c_specs.append(('average', 1, 0, 'number', average_percent, None, fstyle))

            real_percent = round(((income_amount_total - expense_amount_total) * 100.0) / (income_amount_total or 1.0), 2)
            fstyle = xlwt.easyxf(cell_styles['bold'] + cell_styles['bordered'])
            c_specs.append(('real_percent', 1, 0, 'number', real_percent, None, fstyle))

            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rh_cell_style)


analytic_balance_by_department_xls('report.analytic_balance_by_department_xls',
    'analytic.balance.by.department.wzd',
    parser=analytic_balance_by_department)
