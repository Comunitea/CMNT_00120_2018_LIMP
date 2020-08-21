from odoo import models
from odoo.tools import format_date


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    def get_expiration_dates_list(self, padding, signed):
        self.ensure_one()
        expiration_dates = []
        if self.move_id:
            move_lines = self.env["account.move.line"].\
                search([('move_id', '=', self.move_id.id),
                        ('account_id.internal_type', 'in',
                            ['payable', 'receivable']),
                        ('date_maturity', "!=", False)],
                       order="date_maturity asc")
            for line in move_lines:
                expiration_dates.append('{}'.format(
                    format_date(self.env, line.date_maturity)))
        return expiration_dates
