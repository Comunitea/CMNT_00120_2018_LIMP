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
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
import calendar


class AccountBalanceXls(ReportXlsx):

    def _get_value(self, value, positive=False, negative=False):
        if value and value < 100:
            if positive:
                return 100.0 - value
            else:
                return ""
        elif value and value > 100:
            if negative:
                return value - 100.0
            else:
                return ""
        else:
            return ""

    def generate_xlsx_report(self, workbook, data, objs):
        def merge_dicts(*dict_args):
            result = {}
            for dictionary in dict_args:
                result.update(dictionary)
            return result
        cell_styles = {
            'far_values': {'pattern': 1, 'bg_color': 'light_yellow'},
            'very_far_values': {'pattern': 1, 'bg_color': 'yellow'},
            'very_very_far_values': {'pattern': 1, 'bg_color': 'red'},
            'target_label': {'pattern': 1, 'bg_color': '#CCFFCC'},
            'target_label_font':
                {'font_color': 'red', 'bold': True, 'font_size': 8},
            'journals_months':
                {'font_color': '#000080', 'bold': True, 'font_size': 8},
            'average_real': {'pattern': 1, 'bg_color': '#CCCCFF'},
            'average_real_font':
                {'font_color': '#000080', 'bold': True, 'font_size': 8},
            'average_real_font':
                {'font_color': '#000080', 'bold': True, 'font_size': 8},
            'bordered': {'border': True},
            'bold': {'bold': True, 'font_size': 8}
        }

        domain = []
        report_name = u""
        if data.get('delegation_id', False):
            domain.append(('delegation_id', '=', data['delegation_id'][0]))
            report_name += self.env['res.delegation'].browse(
                data['delegation_id'][0]).name
        if data.get('department_id', False):
            domain.append(('department_id', '=', data['department_id'][0]))
            report_name += u" " + self.env['hr.department'].browse(
                data['department_id'][0]).name
        if data.get('manager_id', False):
            domain.append(('manager_id', '=', data['manager_id'][0]))
            report_name += u" " + self.env['hr.employee'].browse(
                data['manager_id'][0]).name
        if data.get('privacy', False):
            domain.append(('account_id.privacy', '=', data['privacy']))
            report_name += u" " + data['privacy'] == 'public' and \
                u'Sector público' or u'Sector Privado'
        report_name += u" " + str(data['year'])

        months = [('01', 'ENERO'), ('02', 'FEBRERO'), ('03', 'MARZO'),
                  ('04', 'ABRIL'), ('05', 'MAYO'), ('06', 'JUNIO'),
                  ('07', 'JULIO'), ('08', 'AGOSTO'), ('09', 'SEPTIEMBRE'),
                  ('10', 'OCTUBRE'), ('11', 'NOVIEMBRE'), ('12', 'DICIEMBRE')]

        sheet = workbook.add_worksheet('1')
        sheet.set_landscape()

        sheet.merge_range(0, 0, 0, 9, report_name)

        cell_format = workbook.add_format(
            merge_dicts(cell_styles['target_label'],
                        cell_styles['target_label_font'],
                        cell_styles['bordered']))
        sheet.merge_range(2, 0, 2, 1, 'OBJETIVOS', cell_format)

        cell_format = workbook.add_format(
            merge_dicts(cell_styles['journals_months'],
                        cell_styles['bordered']))
        for month in months:
            sheet.write(2, 1 + int(month[0]), month[1], cell_format)
        cell_format = workbook.add_format(
            merge_dicts(cell_styles['average_real'],
                        cell_styles['average_real_font'],
                        cell_styles['bordered']))
        sheet.write(2, 14, 'MEDIA', cell_format)
        sheet.write(2, 15, '% REAL', cell_format)

        cell_format = workbook.add_format(
            merge_dicts(cell_styles['journals_months'],
                        cell_styles['bordered']))
        sheet.merge_range(3, 0, 3, 1, u'Facturación', cell_format)

        year = str(data['year'])
        amount = 0.0
        months_with_results = 0
        cell_format = workbook.add_format(
            merge_dicts(cell_styles['bold'],  cell_styles['bordered']))
        month_invoice_amouonts = {}
        for month in months:
            first_day = year + "-" + month[0] + "-01"
            last_day = year + "-" + month[0] + "-" \
                + str(calendar.monthrange(int(year), int(month[0]))[1])
            filter_domain = [
                ('amount', '>', 0),
                ('date', '>=', first_day), ('date', '<=', last_day)] + domain
            unit_amount = sum(
                self.env['account.analytic.line'].search(
                    filter_domain).mapped('amount'))
            month_invoice_amouonts[month[0]] = unit_amount
            if unit_amount:
                months_with_results += 1
            amount += unit_amount
            sheet.write(3, 1 + int(month[0]), unit_amount, cell_format)
        sheet.write(3, 14,
                    round(amount / (months_with_results or 1.0), 2),
                    cell_format)
        sheet.write(3, 15,
                    round(amount / (months_with_results or 1.0), 2),
                    cell_format)

        row_pos = 4

        tags = self.env['account.analytic.tag'].search(
            [('show_in_report', '=', True)])
        first_day = year + "-01-01"
        last_day = year + "-12-" + str(calendar.monthrange(int(year), 12)[1])
        filter_domain = [
            ('tag_ids', 'in', tags.ids),
            ('date', '>=', first_day),
            ('date', '<=', last_day)] + domain
        total_expense = sum(self.env['account.analytic.line'].search(
            filter_domain).mapped('amount'))
        total_expense = -total_expense
        expense_percent = round((total_expense * 100.0) / (amount or 1.0), 2)

        column_percent = {}

        for tag in tags:
            target = False
            if data.get('target_ids', []):
                target_ids = self.env['account.analytic.target'].search(
                    [('id', 'in', data['target_ids']),
                     ('analytic_tag_id', '=', tag.id)])
                if target_ids:
                    target = target_ids[0]

            cell_format = workbook.add_format(
                merge_dicts(cell_styles['journals_months'],
                            cell_styles['bordered']))
            sheet.write(row_pos, 0, tag.name, cell_format)
            cell_format = workbook.add_format(
                merge_dicts(cell_styles['target_label'],
                            cell_styles['bordered'],
                            cell_styles['bold']))

            if target:
                sheet.write(row_pos, 1, target.target_percent, cell_format)
                if not column_percent.get('target', False):
                    column_percent['target'] = 0.0
                column_percent['target'] += target.target_percent
            else:
                sheet.write(row_pos, 1, 0.0, cell_format)
                if not column_percent.get('target', False):
                    column_percent['target'] = 0.0
            avergare_percent = 0.0
            amount = 0.0
            cell_format = workbook.add_format(
                merge_dicts(cell_styles['bold'],
                            cell_styles['bordered']))

            for month in months:
                first_day = year + "-" + month[0] + "-01"
                last_day = year + "-" + month[0] + "-" \
                    + str(calendar.monthrange(int(year), int(month[0]))[1])
                filter_domain = [
                    ('tag_ids', 'in', tag.ids),
                    ('date', '>=', first_day),
                    ('date', '<=', last_day)] + domain
                unit_amount = sum(
                    self.env['account.analytic.line'].search(
                        filter_domain).mapped('amount'))
                unit_amount = -unit_amount
                if month_invoice_amouonts[month[0]]:
                    percent = round(
                        (unit_amount * 100.0) /
                        month_invoice_amouonts[month[0]], 2)
                else:
                    percent = 0
                avergare_percent += percent
                amount += unit_amount
                if not column_percent.get('month_' + month[0], False):
                    column_percent['month_' + month[0]] = 0.0
                column_percent['month_' + month[0]] += percent
                sheet.write(row_pos, 1 + int(month[0]), percent, cell_format)

            average_percent = round(
                avergare_percent / (months_with_results or 1.0), 2)
            cell_format = workbook.add_format(
                merge_dicts(cell_styles['bold'],
                            cell_styles['bordered']))
            target_percent = target and target.target_percent or 0.0

            if average_percent > target_percent:
                diff = average_percent - target_percent
                if diff > 1.5:
                    cell_format = workbook.add_format(
                        merge_dicts(cell_styles['very_very_far_values'],
                                    cell_styles['bold'],
                                    cell_styles['bordered']))
                elif diff > 1.0:
                    cell_format = workbook.add_format(
                        merge_dicts(cell_styles['very_far_values'],
                                    cell_styles['bold'],
                                    cell_styles['bordered']))
                elif diff >= 0.5:
                    cell_format = workbook.add_format(
                        merge_dicts(cell_styles['far_values'],
                                    cell_styles['bold'],
                                    cell_styles['bordered']))
            sheet.write(row_pos, 14, average_percent, cell_format)
            if not column_percent.get('average', False):
                column_percent['average'] = 0.0
            column_percent['average'] += average_percent

            real_percent = round(
                (amount * expense_percent) / (total_expense or 1.0), 2)
            cell_format = workbook.add_format(
                merge_dicts(cell_styles['bold'],
                            cell_styles['bordered']))
            if real_percent > target_percent:
                diff = real_percent - target_percent
                if diff > 1.5:
                    cell_format = workbook.add_format(
                        merge_dicts(cell_styles['very_very_far_values'],
                                    cell_styles['bold'],
                                    cell_styles['bordered']))
                elif diff > 1.0:
                    cell_format = workbook.add_format(
                        merge_dicts(cell_styles['very_far_values'],
                                    cell_styles['bold'],
                                    cell_styles['bordered']))
                elif diff >= 0.5:
                    cell_format = workbook.add_format(
                        merge_dicts(cell_styles['far_values'],
                                    cell_styles['bold'],
                                    cell_styles['bordered']))
            sheet.write(row_pos, 15, real_percent, cell_format)
            if not column_percent.get('real_percent', False):
                column_percent['real_percent'] = 0.0
            column_percent['real_percent'] += real_percent
            row_pos += 1

        cell_format = workbook.add_format(
            merge_dicts(cell_styles['journals_months'],
                        cell_styles['bordered']))
        sheet.write(row_pos, 0, 'GANANCIAS', cell_format)
        sheet.write(row_pos + 1, 0, u'PÉRDIDA', cell_format)

        cell_format = workbook.add_format(
            merge_dicts(cell_styles['target_label'],
                        cell_styles['bordered'],
                        cell_styles['bold']))
        value = self._get_value(column_percent['target'], positive=True)
        sheet.write(row_pos, 1, value, cell_format)
        cell_format = workbook.add_format(
            merge_dicts(cell_styles['target_label_font'],
                        cell_styles['bordered']))
        value = self._get_value(column_percent['target'], negative=True)
        sheet.write(row_pos + 1, 1, value, cell_format)

        for month in months:
            cell_format = workbook.add_format(
                merge_dicts(cell_styles['bold'],
                            cell_styles['bordered']))
            value = self._get_value(
                column_percent['month_' + month[0]], positive=True)
            sheet.write(row_pos, 1 + int(month[0]), value, cell_format)
            cell_format = workbook.add_format(
                merge_dicts(cell_styles['target_label_font'],
                            cell_styles['bordered']))
            value = self._get_value(
                column_percent['month_' + month[0]], negative=True)
            sheet.write(row_pos + 1, 1 + int(month[0]), value, cell_format)

        cell_format = workbook.add_format(
            merge_dicts(cell_styles['bold'],
                        cell_styles['bordered']))
        value = self._get_value(column_percent['average'], positive=True)
        sheet.write(row_pos, 14, value, cell_format)
        cell_format = workbook.add_format(
            merge_dicts(cell_styles['target_label_font'],
                        cell_styles['bordered']))
        value = self._get_value(column_percent['average'], negative=True)
        sheet.write(row_pos + 1, 14, value, cell_format)

        cell_format = workbook.add_format(
            merge_dicts(cell_styles['bold'],
                        cell_styles['bordered']))
        value = self._get_value(column_percent['real_percent'], positive=True)
        sheet.write(row_pos, 15, value, cell_format)
        cell_format = workbook.add_format(
            merge_dicts(cell_styles['target_label_font'],
                        cell_styles['bordered']))
        value = self._get_value(column_percent['real_percent'], negative=True)
        sheet.write(row_pos + 1, 15, value, cell_format)

AccountBalanceXls('report.analytic_balance_xls', 'analytic.balance')
