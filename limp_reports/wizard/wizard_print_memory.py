from odoo import models, fields
import time


class WizardPrintMemory(models.TransientModel):

    _name = "wizard.print.memory"

    year = fields.Integer(
        "Year", required=True, default=lambda r: int(time.strftime("%Y"))
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        default=lambda r: r.env.user.company_id.id,
    )
    manager_partner_ids = fields.\
        Many2many("res.partner", string="Managers", required=True,
                  domain=[('destination_manager', '=', True)])

    def print_report(self):
        report = self.env['ir.actions.report'].search(
            [('report_name', '=', "annual_memory")], limit=1)
        data = {"year": self.year,
                "company_id": self.company_id.id,
                "manager_partner_ids": self.manager_partner_ids.ids,
                'doc_ids': report.ids}
        return report.report_action(self)
