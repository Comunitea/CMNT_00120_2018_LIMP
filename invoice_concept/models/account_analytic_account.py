##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
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

from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import calendar
from dateutil.rrule import rrule, rruleset, DAILY


class AccountAnalyticAccount(models.Model):
    """Add concepts field to analytic account"""

    _inherit = "account.analytic.account"

    concept_ids = fields.One2many(
        "account.analytic.invoice.concept.rel", "analytic_id", "Concepts"
    )
    group_concepts = fields.Boolean(
        "Group concepts", help="Groups concepts at invoice"
    )
    group_products = fields.Boolean(
        "Group products", help="Groups products at invoice"
    )
    group_products_each_invoice = fields.Boolean(
        "One for invoice", help="Groups products, one for invoice"
    )
    invoiceable = fields.Boolean("Invoiceable")

    def _invoice_hook(self, invoice_id, end_date):
        return self

    def _create_invoice(self, end_date):
        """creates an invoice to an analytic account"""
        self.ensure_one()
        end_date = datetime.strptime(
            fields.Date.to_string(end_date) + " 23:59:59", "%Y-%m-%d %H:%M:%S"
        )
        vals = {
            "name": self.name,
            "origin": self.name,
            "type": "out_invoice",
            "account_id": self.partner_id.property_account_receivable_id.id,
            "partner_id": self.partner_id.id,
            "partner_shipping_id": self.address_id and self.address_id.id,
            "address_tramit_id": self.address_tramit_id
            and self.address_tramit_id.id,
            "payment_term_id": self.partner_id.property_payment_term_id
            and self.partner_id.property_payment_term_id.id
            or False,
            "payment_mode_id": self.partner_id.customer_payment_mode_id and
            self.partner_id.customer_payment_mode_id.id or False,
            "fiscal_position_id": self.partner_id.
            property_account_position_id.id,
            "company_id": self.company_id.id,
            "analytic_id": self.id,
            "date_invoice": self._context.get("invoice_date", False),
            "department_id": self.department_id
            and self.department_id.id
            or False,
        }
        if self._context.get("journal_id", False):
            vals["journal_id"] = int(self._context["journal_id"])

        invoice = self.env["account.invoice"].create(vals)
        self._invoice_hook(invoice, end_date)
        return invoice

    def _process_concept_name(self, concept_rel, date):
        self.ensure_one()
        return concept_rel.concept_id.process_name(
            description=concept_rel.name, date=date
        )

    def _invoice_line_hook(self, concept, invoice_line, end_date):
        return True

    def close_analytic(self):
        self.write({"state": "close"})
        return True

    def create_concept_invoice_line(self, concept, invoice_id, end_date):
        concept_product = concept.concept_id.product_id
        account_id = (
            concept_product.product_tmpl_id.property_account_income_id.id
        )
        if not account_id:
            account_id = (
                concept_product.categ_id.property_account_income_categ_id.id
            )
        # se rellena con la fecha de última factura o
        # la fecha de alta de la cuenta
        start_date = (
            concept.last_invoice_date
            and datetime.strptime(
                fields.Date.to_string(concept.last_invoice_date) +
                " 00:00:00", "%Y-%m-%d %H:%M:%S"
            )
            + relativedelta(days=+1)
            or datetime.strptime(
                fields.Date.to_string(self.date_start) + " 00:00:00",
                "%Y-%m-%d %H:%M:%S"
            )
        )
        # fecha en la que se está facturando
        end_date = datetime.strptime(
            fields.Date.to_string(end_date) + " 23:59:59",
            "%Y-%m-%d %H:%M:%S"
        )
        # fecha de baja de la cuenta analítica o fecha de facturación
        end_date = (
            (
                self.date
                and datetime.strptime(
                    fields.Date.to_string(self.date) + " 23:59:59",
                    "%Y-%m-%d %H:%M:%S"
                )
                < end_date
            )
            and datetime.strptime(fields.Date.to_string(self.date) +
                                  " 23:59:59", "%Y-%m-%d %H:%M:%S")
            or end_date
        )

        except_months = concept._get_except_months()[concept.id]
        if end_date.month in except_months:
            return False

        rset = rruleset()
        if except_months:
            rset.exrule(
                rrule(
                    DAILY,
                    dtstart=start_date,
                    until=end_date,
                    bymonth=except_months,
                )
            )
        rset.rrule(rrule(DAILY, dtstart=start_date, until=end_date))
        months = list(set([(x.year, x.month) for x in list(rset)]))
        amount = 0.0
        if concept.freq == "q":
            days = 90
        else:
            days = 30
        duration = 0
        for month in months:
            days_in_month = calendar.monthrange(month[0], month[1])[1]
            first_month_day = datetime.strptime(
                str(month[0]) + "-" + str(month[1]).zfill(2) + "-01",
                "%Y-%m-%d",
            )
            last_month_day = datetime.strptime(
                str(month[0])
                + "-"
                + str(month[1]).zfill(2)
                + "-"
                + str(days_in_month),
                "%Y-%m-%d",
            )
            rset_month = rset.between(
                first_month_day, last_month_day, inc=True
            )
            month_days = len(list(rset_month))
            if month_days == days_in_month:
                duration += 30
            else:
                duration += month_days
        amount += (duration * concept.amount) / days
        if (
            self.date
            and datetime.strptime(fields.Date.to_string(self.date) +
                                  " 23:59:59", "%Y-%m-%d %H:%M:%S")
            <= end_date
        ):
            self.close_analytic()

        if not amount and concept.amount:
            return False
        invoice_line = self.env["account.invoice.line"].create(
            {
                "name": self._process_concept_name(concept, end_date),
                "origin": self.name,
                "invoice_id": invoice_id.id,
                "uom_id": concept_product.uom_id
                and concept_product.uom_id.id
                or False,
                "product_id": concept_product.id,
                "account_id": self.partner_id.property_account_position_id.
                map_account(account_id),
                "price_unit": amount,
                "discount": 0.0,
                "quantity": 1.0,
                "invoice_line_tax_ids": [
                    (
                        6,
                        0,
                        self.partner_id.property_account_position_id.map_tax(
                            concept_product.taxes_id
                        ).ids,
                    )
                ],
                "account_analytic_id": self.id,
            }
        )

        res = self._invoice_line_hook(concept, invoice_line, end_date)
        return res and invoice_line

    @api.model
    def __group_by_product_lines(self, ref_line, grouped_lines):
        subtotal = ref_line.price_unit
        note = ref_line.name + "\n"
        for line in grouped_lines:
            subtotal += line.price_unit
            note += line.name + "\n"
        ref_line.write(
            {
                "price_unit": round(subtotal, 2),
                "name": ref_line.product_id.description_sale
                or ref_line.product_id.name,
                "note": note,
            }
        )
        return True

    @api.multi
    def run_invoice_cron_manual(self):

        analytic_ids = self.env[
            "account.analytic.account"
        ]  # list of visited analytic accounts
        created_invoices = self.env[
            "account.invoice"
        ]  # list of created invoices

        if self._context.get("end_date", False):
            end_date = self._context["end_date"]
        else:
            day, days = calendar.monthrange(
                int(time.strftime("%Y")), int(time.strftime("%m"))
            )
            end_date = time.strftime("%Y-%m-") + str(days)

        for analytic_account in self:
            child_concepts_ids = self.env[
                "account.analytic.invoice.concept.rel"
            ]  # list of childs in first level
            analytic_invoices = self.env["account.invoice"]
            child_ids = analytic_account.child_ids
            for child in child_ids:
                child_concepts_ids |= child.concept_ids
            if analytic_account not in analytic_ids:
                if analytic_account.group_concepts and (
                    analytic_account.concept_ids or child_concepts_ids
                ):
                    invoice = analytic_account._create_invoice(end_date)
                    created_invoices |= invoice
                    analytic_invoices |= invoice
                    for concept in analytic_account.concept_ids:
                        res = analytic_account.create_concept_invoice_line(
                            concept, invoice, end_date
                        )
                        if res:
                            concept.write({"last_invoice_date": end_date})

                    analytic_ids |= (
                        analytic_account  # visited analytic account
                    )

                    for analytic_child_obj in child_ids:
                        if analytic_child_obj in analytic_ids:
                            # remove his related invoice because it's
                            # invoice line
                            related_invoices = self.env[
                                "account.invoice"
                            ].search(
                                [("analytic_id", "=", analytic_child_obj.id),
                                 ('state', '=', 'draft')]
                            )  # obtain all related invoices with this account
                            toremove_related_invoices = (
                                created_invoices & related_invoices
                            )  # computes repeated invoice in two lists
                            if toremove_related_invoices:
                                for rec in toremove_related_invoices:
                                    created_invoices -= rec
                                toremove_related_invoices.unlink()
                                analytic_ids -= analytic_child_obj

                        for (
                            child_concept
                        ) in (
                            analytic_child_obj.concept_ids
                        ):  # goes around child concepts
                            # creates invoice line for each child concept
                            res = analytic_child_obj.\
                                create_concept_invoice_line(child_concept,
                                                            invoice, end_date)
                            if res:
                                child_concept.write(
                                    {"last_invoice_date": end_date}
                                )
                        analytic_ids |= (
                            analytic_child_obj  # set account as visited
                        )
                elif (
                    analytic_account.concept_ids or child_concepts_ids
                ):  # if exists concepts buy they don't group and
                    # it isn't visited
                    invoice = analytic_account._create_invoice(
                        end_date
                    )  # invoice by concept
                    created_invoices |= invoice
                    analytic_invoices |= invoice
                    for concept in analytic_account.concept_ids:
                        res = analytic_account.create_concept_invoice_line(
                            concept, invoice, end_date
                        )  # invoice line by conept
                        if res:
                            concept.write({"last_invoice_date": end_date})
                    analytic_ids |= analytic_account

                if analytic_account.group_products:
                    for inv in analytic_invoices:
                        dicc = {}
                        for line in inv.invoice_line_ids:
                            if line.product_id.id not in dicc:
                                dicc[line.product_id.id] = []
                            dicc[line.product_id.id].append(line)

                        for key_id in dicc:
                            to_delete_line_ids = self.env[
                                "account.invoice.line"
                            ]
                            if len(dicc[key_id]) > 1:
                                ref_line = dicc[key_id][0]
                                for line in dicc[key_id]:
                                    if line.id != ref_line.id:
                                        to_delete_line_ids |= line

                                self.__group_by_product_lines(
                                    ref_line, to_delete_line_ids
                                )
                                new_name = self.env[
                                    "account.analytic.invoice.concept"
                                ].process_name(
                                    description=ref_line.name,
                                    date=datetime.strptime(
                                        end_date, "%Y-%m-%d"
                                    ),
                                )
                                ref_line.write({"name": new_name})
                                to_delete_line_ids.unlink()

                        if analytic_account.group_products_each_invoice:
                            if len(inv.invoice_line_ids) > 1:
                                line_ref = inv.invoice_line_ids[0]
                                for line in inv.invoice_line_ids:
                                    if line.id != line_ref.id:
                                        new_inv = inv.copy(
                                            default={
                                                "invoice_line_ids": False,
                                                "date_invoice":
                                                inv.date_invoice,
                                            }
                                        )
                                        created_invoices |= new_inv
                                        line.write({"invoice_id": new_inv.id})

            to_delete_invoices = self.env["account.invoice"]

            for invoice in created_invoices:
                if not invoice.invoice_line_ids:
                    to_delete_invoices |= invoice
                else:
                    invoice.compute_taxes()

            created_invoices = created_invoices - to_delete_invoices
            to_delete_invoices.unlink()
        return created_invoices

    @api.model
    def run_invoice(self):
        # gets analytic account to eval
        analytic_accounts = self.search(
            [
                ("state", "=", "open"),
                ("partner_id", "!=", False),
                ("invoiceable", "=", True),
                ("date_start", "<", self._context["end_date"]),
            ],
            order="create_date",
        )
        analytic_accounts.run_invoice_cron_manual()
        return True
