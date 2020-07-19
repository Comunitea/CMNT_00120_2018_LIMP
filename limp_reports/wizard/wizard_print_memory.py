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

    def print_report(self):
        datas = {"year": self.year, "company_id": self.company_id.id}
        return {
            "type": "ir.actions.report",
            "report_name": "annual_memory",
            "datas": datas,
        }
