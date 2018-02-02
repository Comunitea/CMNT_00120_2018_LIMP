# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Pexego Sistemas Informáticos. All Rights Reserved
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

_ir_translation_name = 'analytic_balance.xls'

class analytic_balance(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(analytic_balance, self).__init__(cr, uid, name, context=context)
        move_obj = self.pool.get('account.analytic.line')
        self.context = context
        self.localcontext.update({
            'datetime': datetime,
        })

class account_balance_xls(report_xls):

    def __init__(self, name, table, rml=False, parser=False, header=True, store=False):
        super(account_balance_xls, self).__init__(name, table, rml, parser, header, store)

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

    def _get_value(self, value, positive=False, negative=False):
        if value and value < 100:
            if positive:
                return ('number', 100.0 - value)
            else:
                return ('text', "")
        elif value and value > 100:
            if negative:
                return ('number', value - 100.0)
            else:
                return ('text', "")
        else:
            return ('text', "")

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
        if data.get('department_id', False):
            domain.append(('department_id', '=', data['department_id']))
        if data.get('manager_id', False):
            domain.append(('manager_id', '=', data['manager_id']))
        if data.get('privacy', False):
            account_ids = self.pool.get('account.analytic.account').search(self.cr, self.uid, [('privacy', '=', data['privacy'])])
            domain.append(('account_id', 'child_of', account_ids))

        months = [('01','ENERO'),('02','FEBRERO'),('03','MARZO'),('04','ABRIL'),('05','MAYO'),('06','JUNIO'),('07','JULIO'),('08','AGOSTO'),('09','SEPTIEMBRE'),('10','OCTUBRE'),('11','NOVIEMBRE'),('12','DICIEMBRE')]
        report_name = (data.get('department_id', False) and  self.pool.get('hr.department').browse(self.cr, self.uid, data['department_id'], context=_p).name or u"")
        report_name += u" " + (data.get('delegation_id', False) and  self.pool.get('res.delegation').browse(self.cr, self.uid, data['delegation_id'], context=_p).name or u"")
        report_name += u" " + self.pool.get('account.fiscalyear').browse(self.cr, self.uid, data['fiscalyear_id'], context=_p).name
        report_name += u" " + (data.get('manager_id', False) and  self.pool.get('hr.employee').browse(self.cr, self.uid, data['manager_id'], context=_p).name or u"")
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
        c_specs = [('journal_id', 2, 2, 'text',  'OBJETIVOS', None, fstyle)]
        fstyle = xlwt.easyxf(cell_styles['journals_months'] + cell_styles['bordered'])
        for month in months:
            c_specs.append(('month_' + month[0], 1, 0, 'text', month[1], None, fstyle))
        fstyle = xlwt.easyxf(cell_styles['average_real'] + cell_styles['average_real_font'] + cell_styles['bordered'])
        c_specs.append(('average', 1, 0, 'text',  'MEDIA', None, fstyle))
        c_specs.append(('real_percent', 1, 0, 'text',  '% REAL', None, fstyle))

        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rh_cell_style)

        fstyle = xlwt.easyxf(cell_styles['journals_months'] + cell_styles['bordered'])
        c_specs = [
            ('journal_id', 2, 2, 'text', u"Facturación", None, fstyle),
        ]
        sale_journal_ids = self.pool.get('account.analytic.journal').search(self.cr, self.uid, [('type', '=', 'sale')])
        fiscal_year = self.pool.get('account.fiscalyear').browse(self.cr, self.uid, data['fiscalyear_id'], context=_p)
        year = fiscal_year.code
        amount = 0.0
        months_with_results = 0
        fstyle = xlwt.easyxf(cell_styles['bold'] + cell_styles['bordered'])
        month_invoice_amouonts = {}
        for month in months:
            first_day =  year + "-" + month[0] + "-01"
            last_day = year + "-" + month[0] + "-" + str(calendar.monthrange(int(year),int(month[0]))[1])
            filter_domain = [('journal_id', 'in', sale_journal_ids),('date', '>=', first_day),('date', '<=',last_day)] + domain
            unit_amount = sum([x.amount for x in self.pool.get('account.analytic.line').browse(self.cr, self.uid, self.pool.get('account.analytic.line').search(self.cr, self.uid, filter_domain), context=_p)])
            month_invoice_amouonts[month[0]] = unit_amount
            if unit_amount:
                months_with_results += 1
            amount += unit_amount
            c_specs.append(('month_' + month[0], 1, 0, 'number', unit_amount, None, fstyle))
        c_specs.append(('average', 1, 0, 'number', round(amount / (months_with_results or 1.0), 2), None, fstyle))
        c_specs.append(('real_percent', 1, 0, 'number', round(amount / (months_with_results or 1.0), 2), None, fstyle))

        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rh_cell_style)

        expense_journal_ids = self.pool.get('account.analytic.journal').search(self.cr, self.uid, [('type', '!=', 'sale')], context=_p)
        filter_domain = [('journal_id', 'in', expense_journal_ids),('date', '>=', fiscal_year.date_start),('date', '<=', fiscal_year.date_stop)] + domain
        total_expense = sum([x.amount for x in self.pool.get('account.analytic.line').browse(self.cr, self.uid, self.pool.get('account.analytic.line').search(self.cr, self.uid, filter_domain), context=_p)])
        total_expense = -total_expense
        expense_percent = round((total_expense * 100.0) / (amount or 1.0), 2)

        column_percent = {}


        journal_obj_ids = sorted(self.pool.get('account.analytic.journal').browse(self.cr, self.uid, expense_journal_ids, context=_p), key=lambda x: x.name)
        for journal in journal_obj_ids:
            target = False
            if data.get('target_ids', []):
                target_ids = self.pool.get('account.analytic.target').search(self.cr, self.uid, [('id', 'in', data['target_ids']),('analytic_journal_id', '=', journal.id)])
                if target_ids:
                    target = target_ids[0]
            fstyle = xlwt.easyxf(cell_styles['journals_months'] + cell_styles['bordered'])
            c_specs = [('journal_id', 1, 0, 'text', journal.name, None, fstyle)]
            fstyle = xlwt.easyxf(cell_styles['target_label'] + cell_styles['bordered'] + cell_styles['bold'])
            if target:
                target = self.pool.get('account.analytic.target').browse(self.cr, self.uid, target, context=_p)
                c_specs.append(('target', 1, 0, 'number', target.target_percent, None, fstyle))
                if not column_percent.get('target', False):
                    column_percent['target'] = 0.0
                column_percent['target'] += target.target_percent
            else:
                c_specs.append(('target', 1, 0, 'number', 0.0, None, fstyle))
                if not column_percent.get('target', False):
                    column_percent['target'] = 0.0
            avergare_percent = 0.0
            amount = 0.0
            fstyle = xlwt.easyxf(cell_styles['bold'] + cell_styles['bordered'])
            for month in months:
                first_day =  year + "-" + month[0] + "-01"
                last_day = year + "-" + month[0] + "-" + str(calendar.monthrange(int(year),int(month[0]))[1])

                filter_domain = [('journal_id', '=', journal.id),('date', '>=', first_day),('date', '<=',last_day)] + domain
                unit_amount = sum([x.amount for x in self.pool.get('account.analytic.line').browse(self.cr, self.uid, self.pool.get('account.analytic.line').search(self.cr, self.uid, filter_domain), context=_p)])
                unit_amount = -unit_amount
                if month_invoice_amouonts[month[0]]:
                    percent = round((unit_amount * 100.0) / month_invoice_amouonts[month[0]], 2)
                else:
                    percent = 0
                avergare_percent += percent
                amount += unit_amount
                if not column_percent.get('month_' + month[0], False):
                    column_percent['month_' + month[0]] = 0.0
                column_percent['month_' + month[0]] += percent
                c_specs.append(('month_' + month[0], 1, 0, 'number', percent, None, fstyle))

            average_percent = round(avergare_percent / (months_with_results or 1.0), 2)
            fstyle = False
            target_percent = target and target.target_percent or 0.0

            if average_percent > target_percent:
                diff = average_percent - target_percent
                if diff > 1.5:
                    fstyle = xlwt.easyxf(cell_styles['very_very_far_values'] + cell_styles['bold'] + cell_styles['bordered'])
                elif diff > 1.0:
                    fstyle = xlwt.easyxf(cell_styles['very_far_values'] + cell_styles['bold'] + cell_styles['bordered'])
                elif diff >= 0.5:
                    fstyle = xlwt.easyxf(cell_styles['far_values'] + cell_styles['bold'] + cell_styles['bordered'])
            if fstyle:
                c_specs.append(('average', 1, 0, 'number', average_percent, None, fstyle))
            else:
                fstyle = xlwt.easyxf(cell_styles['bold'] + cell_styles['bordered'])
                c_specs.append(('average', 1, 0, 'number', average_percent, None, fstyle))
            if not column_percent.get('average', False):
                column_percent['average'] = 0.0
            column_percent['average'] += average_percent

            real_percent = round((amount * expense_percent) / (total_expense or 1.0), 2)
            fstyle = False
            if real_percent > target_percent:
                diff = real_percent - target_percent
                if diff > 1.5:
                    fstyle = xlwt.easyxf(cell_styles['very_very_far_values'] + cell_styles['bold'] + cell_styles['bordered'])
                elif diff > 1.0:
                    fstyle = xlwt.easyxf(cell_styles['very_far_values'] + cell_styles['bold'] + cell_styles['bordered'])
                elif diff >= 0.5:
                    fstyle = xlwt.easyxf(cell_styles['far_values'] + cell_styles['bold'] + cell_styles['bordered'])
            if fstyle:
                c_specs.append(('real_percent', 1, 0, 'number', real_percent, None, fstyle))
            else:
                fstyle = xlwt.easyxf(cell_styles['bold'] + cell_styles['bordered'])
                c_specs.append(('real_percent', 1, 0, 'number', real_percent, None, fstyle))
            if not column_percent.get('real_percent', False):
                column_percent['real_percent'] = 0.0
            column_percent['real_percent'] += real_percent

            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rh_cell_style)

        fstyle = xlwt.easyxf(cell_styles['journals_months'] + cell_styles['bordered'])
        c_specs = [('journal_id', 1, 0, 'text', "GANANCIA", None, fstyle)]
        fstyle = xlwt.easyxf(cell_styles['target_label_font'] + cell_styles['bordered'])
        c_specs2 = [('journal_id', 1, 0, 'text', "PÉRDIDA", None, fstyle)]
        fstyle = xlwt.easyxf(cell_styles['target_label'] + cell_styles['bordered'] + cell_styles['bold'])
        ctype, value = self._get_value(column_percent['target'], positive=True)
        c_specs.append(('target', 1, 0, ctype, value, None, fstyle))
        fstyle = xlwt.easyxf(cell_styles['target_label_font'] + cell_styles['bordered'])
        ctype, value = self._get_value(column_percent['target'], negative=True)
        c_specs2.append(('target', 1, 0, ctype, value, None, fstyle))

        for month in months:
            fstyle = xlwt.easyxf(cell_styles['bold'] + cell_styles['bordered'])
            ctype, value = self._get_value(column_percent['month_' + month[0]], positive=True)
            c_specs.append(('month_' + month[0], 1, 0, ctype, value, None, fstyle))
            ctype, value = self._get_value(column_percent['month_' + month[0]], negative=True)
            fstyle = xlwt.easyxf(cell_styles['target_label_font'] + cell_styles['bordered'])
            c_specs2.append(('month_' + month[0], 1, 0, ctype, value, None, fstyle))

        fstyle = xlwt.easyxf(cell_styles['bold'] + cell_styles['bordered'])
        ctype, value = self._get_value(column_percent['average'], positive=True)
        c_specs.append(('average', 1, 0, ctype, value, None, fstyle))
        ctype, value = self._get_value(column_percent['average'], negative=True)
        fstyle = xlwt.easyxf(cell_styles['target_label_font'] + cell_styles['bordered'])
        c_specs2.append(('average', 1, 0, ctype, value, None, fstyle))
        ctype, value = self._get_value(column_percent['real_percent'], positive=True)
        fstyle = xlwt.easyxf(cell_styles['bold'] + cell_styles['bordered'])
        c_specs.append(('real_percent', 1, 0, ctype, value, None, fstyle))
        ctype, value = self._get_value(column_percent['real_percent'], negative=True)
        fstyle = xlwt.easyxf(cell_styles['target_label_font'] + cell_styles['bordered'])
        c_specs2.append(('real_percent', 1, 0, ctype, value, None, fstyle))

        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rh_cell_style)

        row_data = self.xls_row_template(c_specs2, [x[0] for x in c_specs2])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rh_cell_style)

account_balance_xls('report.analytic_balance_xls',
    'analytic.balance',
    parser=analytic_balance)
