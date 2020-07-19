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
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
import calendar


class AccountBalanceByDepartmentXls(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, objs):
        def merge_dicts(*dict_args):
            result = {}
            for dictionary in dict_args:
                result.update(dictionary)
            return result

        year = str(data["year"])
        cell_styles = {
            "far_values": {"pattern": 1, "bg_color": "light_yellow"},
            "very_far_values": {"pattern": 1, "bg_color": "yellow"},
            "very_very_far_values": {"pattern": 1, "bg_color": "red"},
            "target_label": {"pattern": 1, "bg_color": "#CCFFCC"},
            "target_label_font": {
                "font_color": "red",
                "bold": True,
                "font_size": 8,
            },
            "journals_months": {
                "font_color": "#000080",
                "bold": True,
                "font_size": 8,
            },
            "average_real": {"pattern": 1, "bg_color": "#CCCCFF"},
            "average_real_font": {
                "font_color": "#000080",
                "bold": True,
                "font_size": 8,
            },
            "average_real_font": {
                "font_color": "#000080",
                "bold": True,
                "font_size": 8,
            },
            "bordered": {"border": True},
            "bold": {"bold": True, "font_size": 8},
        }

        domain = []
        report_name = u""
        if data.get("delegation_id", False):
            domain.append(("delegation_id", "=", data["delegation_id"][0]))
            report_name += (
                self.env["res.delegation"]
                .browse(data["delegation_id"][0])
                .name
            )
        if data.get("privacy", False):
            domain.append(("account_id.privacy", "=", data["privacy"]))
            report_name += (
                u" " + data["privacy"] == "public"
                and u"Sector público"
                or u"Sector Privado"
            )
        report_name += u" " + str(data["year"])

        months = [
            ("01", "ENERO"),
            ("02", "FEBRERO"),
            ("03", "MARZO"),
            ("04", "ABRIL"),
            ("05", "MAYO"),
            ("06", "JUNIO"),
            ("07", "JULIO"),
            ("08", "AGOSTO"),
            ("09", "SEPTIEMBRE"),
            ("10", "OCTUBRE"),
            ("11", "NOVIEMBRE"),
            ("12", "DICIEMBRE"),
        ]
        sheet = workbook.add_worksheet("1")
        sheet.set_landscape()

        sheet.merge_range(0, 0, 0, 9, report_name)

        cell_format = workbook.add_format(
            merge_dicts(
                cell_styles["target_label"],
                cell_styles["target_label_font"],
                cell_styles["bordered"],
            )
        )
        sheet.merge_range(2, 0, 2, 1, "DEPARTAMENTOS", cell_format)

        cell_format = workbook.add_format(
            merge_dicts(
                cell_styles["journals_months"], cell_styles["bordered"]
            )
        )
        for month in months:
            sheet.write(2, 1 + int(month[0]), month[1], cell_format)

        cell_format = workbook.add_format(
            merge_dicts(
                cell_styles["average_real"],
                cell_styles["average_real_font"],
                cell_styles["bordered"],
            )
        )
        sheet.write(2, 14, "MEDIA", cell_format)
        sheet.write(2, 15, "% REAL", cell_format)

        departments = self.env["hr.department"].search([], order="name")
        row_pos = 3
        for department in departments:
            months_with_results = 0
            avergare_percent = 0.0
            cell_format = workbook.add_format(
                merge_dicts(
                    cell_styles["journals_months"], cell_styles["bordered"]
                )
            )
            sheet.write(row_pos, 0, department.name, cell_format)
            expense_amount_total = 0.0
            income_amount_total = 0.0
            for month in months:
                first_day = year + "-" + month[0] + "-01"
                last_day = (
                    year
                    + "-"
                    + month[0]
                    + "-"
                    + str(calendar.monthrange(int(year), int(month[0]))[1])
                )

                filter_domain = [
                    ("department_id", "=", department.id),
                    ("date", ">=", first_day),
                    ("date", "<=", last_day),
                ] + domain
                expense_amount = sum(
                    self.env["account.analytic.line"]
                    .search(filter_domain + [("amount", "<", 0)])
                    .mapped("amount")
                )
                income_amount = sum(
                    self.env["account.analytic.line"]
                    .search(filter_domain + [("amount", ">", 0)])
                    .mapped("amount")
                )
                expense_amount = -expense_amount
                expense_amount_total += expense_amount
                income_amount_total += income_amount
                if income_amount:
                    percent = round(
                        ((income_amount - expense_amount) * 100.0)
                        / income_amount,
                        2,
                    )
                    months_with_results += 1
                else:
                    percent = 0
                avergare_percent += percent
                cell_format = workbook.add_format(
                    merge_dicts(cell_styles["bold"], cell_styles["bordered"])
                )
                sheet.write(row_pos, 1 + int(month[0]), percent, cell_format)

            average_percent = round(
                avergare_percent / (months_with_results or 1.0), 2
            )
            cell_format = workbook.add_format(
                merge_dicts(cell_styles["bold"], cell_styles["bordered"])
            )
            sheet.write(row_pos, 14, average_percent, cell_format)

            real_percent = round(
                ((income_amount_total - expense_amount_total) * 100.0)
                / (income_amount_total or 1.0),
                2,
            )
            sheet.write(row_pos, 15, real_percent, cell_format)
            row_pos += 1


AccountBalanceByDepartmentXls(
    "report.analytic_balance_by_department_xls",
    "analytic.balance.by.department.wzd",
)
