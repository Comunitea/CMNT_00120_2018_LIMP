##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
#    $Javier Colmenero Fernández$
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
from odoo import models, fields, _
from odoo.exceptions import UserError
import os
from mako.template import Template
from mako.lookup import TemplateLookup
import base64
from odoo.tools import config


class ExportAccountToGlasof(models.TransientModel):

    _name = "export.account.to.glasof"

    file_xdiario = fields.Binary("File xDiario", readonly=True)
    xdiario_name = fields.Char("Xdiario name", size=40, readonly=True)
    file_xsubcta = fields.Binary("File xSubCta", readonly=True)
    xsubcta_name = fields.Char("xSubCta name", size=40, readonly=True)
    state = fields.Selection(
        [("no_export", "No Export"), ("export", "Exported")],
        "State",
        readonly=True,
        default="no_export",
    )
    account_length = fields.Integer(
        "Account length", required=True, default=11
    )
    no_department = fields.Boolean("No department")

    def format_acc_number(self, num, ref):
        total_len = self.account_length
        var_len = total_len - len(ref)
        res = ""
        if var_len > len(num):
            res = num.ljust(var_len, "0")
        else:
            res = num[: len(num) - (len(num) - var_len)]
        res += ref
        return res

    def format_normal_account(
        self, account, delegation=False, department=False
    ):
        nd = self.no_department
        total_len = self.account_length
        parent_len = 4
        rjust_len = (
            total_len
            - parent_len
            - ((delegation and not nd) and len(delegation.code) or 0)
            - ((department and not nd) and len(department.code) or 0)
        )
        if len(account.code) <= total_len:
            if account.code.startswith("6") or account.code.startswith("7"):
                new_account_code = (
                    account.code[:parent_len]
                    + ((delegation and not nd) and delegation.code or "")
                    + account.code[parent_len:].rjust(rjust_len, "0")
                    + ((department and not nd) and department.code or "")
                )
            else:
                new_account_code = (
                    account.code[:parent_len]
                    + "".rjust(total_len - len(account.code), "0")
                    + account.code[parent_len:]
                )
            if len(new_account_code) > total_len:
                raise osv.except_osv(
                    _("Error"),
                    _(
                        "New account code compound of departement and delegation code is bigger than selected account size."
                    ),
                )
            return new_account_code
        else:
            raise osv.except_osv(
                _("Error"),
                _(
                    "Selected account size smaller than the size of real accounts"
                ),
            )

    def export_account_moves(self):
        errors_list = set()
        tmp_path = os.path.abspath(os.path.dirname(__file__)) + "/templates/"
        objects = self.env["account.move"].browse(
            self._context.get("active_ids", [])
        )
        move_lines = []
        acc_numbers = {}
        for move in objects:
            for line in move.line_ids:
                if line.partner_id and (
                    line.account_id.code.startswith("40")
                    or line.account_id.code.startswith("41")
                    or line.account_id.code.startswith("43")
                ):
                    if not line.partner_id.ref:
                        errors_list.add(
                            _(
                                "The partner %s has not field ref. Please fill this field and try again."
                            )
                            % line.partner_id.name
                        )
                    else:
                        acc_numbers[line.id] = self.format_acc_number(
                            line.account_id.code, line.partner_id.ref
                        )
                else:
                    acc_numbers[line.id] = self.format_normal_account(
                        line.account_id, line.delegation_id, line.department_id
                    )
                move_lines.append(line)
        if errors_list:
            raise UserError("\n\n".join(list(errors_list)))
        move_lines = sorted(
            move_lines,
            key=lambda x: (x.move_id.id, x.partner_id.id, x.account_id.code),
        )
        mylookup = TemplateLookup(
            input_encoding="utf-8",
            output_encoding="utf-8",
            encoding_errors="replace",
        )
        tmp = Template(
            filename=tmp_path + "xdiario_template.txt",
            lookup=mylookup,
            default_filters=["decode.utf8"],
        )
        doc = tmp.render_unicode(
            objects=move_lines,
            acc_numbers=acc_numbers,
            env=self.env,
            formatAccount=self.format_acc_number,
        ).encode("utf-8", "replace")

        partners = set()
        acc_numbers = {}
        for move in objects:
            for line in move.line_ids:
                receiv_acc = (
                    line.partner_id.property_account_receivable_id.code
                )
                pay_acc = line.partner_id.property_account_payable_id.code
                move_acc = line.account_id.code
                if move_acc in [pay_acc, receiv_acc]:
                    if not line.partner_id.ref:
                        raise UserError(
                            _(
                                "The partner %s has not field ref. Please fill this field and try again."
                            )
                            % line.partner_id.name
                        )

                    acc_numbers[line.partner_id.id] = self.format_acc_number(
                        move_acc, line.partner_id.ref
                    )
                    partners.add(line.partner_id)

        tmp = Template(
            filename=tmp_path + "xsubcta_template.txt",
            lookup=mylookup,
            default_filters=["decode.utf8"],
        )
        doc2 = tmp.render_unicode(
            objects=partners, acc_numbers=acc_numbers, env=self.env
        ).encode("utf-8", "replace")

        xdiario_base64 = base64.b64encode(doc)
        xsubcta_base64 = base64.b64encode(doc2)
        self.write(
            {
                "file_xdiario": xdiario_base64,
                "file_xsubcta": xsubcta_base64,
                "state": "export",
                "xdiario_name": "xDiario.txt",
                "xsubcta_name": "xSubCta.txt",
            }
        )

        return {"type": "ir.actions.do_nothing"}
