from odoo import models, fields


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    date_operation = fields.Date(
        string="Fecha de Operación",
        help="Fecha de operación del documento."
    )

    def _select(self):
        res = super(AccountInvoiceReport, self)._select()
        res += """
            , sub.date_operation as date_operation"""
        return res

    def _sub_select(self):
        res = super(AccountInvoiceReport, self)._sub_select()
        res += """
            , ai.date_operation AS date_operation"""
        return res
