# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _


class AssociateCouncilBetterZipWizard(models.TransientModel):

    _name = "associate.council.better.zip.wizard"

    def associate(self):
        for zip in self.env["res.better.zip"].search([]):
            council_ids = self.env["city.council"].search(
                ["name", "=", zip.city]
            )
            if not council_ids:
                council_ids = self.env["city.council"].create(
                    {"name": zip.city}
                )
            zip.write({"council_id": council_ids[0]})
        return {"type": "ir.actions.act_window_close"}
