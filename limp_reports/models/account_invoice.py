from odoo import models, _, fields
from odoo.tools import format_date
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    grupo_limp_partner_id = fields.Many2one("res.partner", string="Grupo Limp", default=24613)

    # def action_invoice_open(self):
    #     if self.journal_id and 'Scont' not in self.journal_id.name:
    #         if not self.invoice_line_ids.filtered(lambda l: l.invoice_line_tax_ids):
    #             raise UserError(_("You must select a tax for each invoice line."))
    #     return super(AccountInvoice, self).action_invoice_open()

    def get_expiration_dates_list(self, padding, signed):
        self.ensure_one()
        expiration_dates = []
        if self.move_id:
            move_lines = self.env["account.move.line"].search([
                ('move_id', '=', self.move_id.id),
                ('account_id.internal_type', 'in', ['payable', 'receivable']),
                ('date_maturity', "!=", False)
            ], order="date_maturity asc")
            for line in move_lines:
                expiration_dates.append('{}'.format(
                    format_date(self.env, line.date_maturity)))
        return expiration_dates
