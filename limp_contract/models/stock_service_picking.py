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
from odoo import models, fields, api, _
from datetime import datetime


class StockServicePicking(models.Model):

    _inherit = "stock.service.picking"

    contract_id = fields.Many2one("limp.contract", "Contract")
    workcenter = fields.Char("Workcenter")

    revision_start_date = fields.Date("Revision start date")
    revision_end_date = fields.Date("Revision end date")

    has_extinguisher_revision = fields.Boolean('Has extinguisher revision')
    extinguisher_revision_ids = fields.One2many(
        'extinguisher.revision',
        'stock_service_picking_id',
        'Extinguisher revision'
    )
    extinguisher_revision_correct = fields.Selection([
        ('correct', 'Correct'),
        ('has_anomalies', 'Has anomalies')
    ], 'Extinguisher revision is correct')
    extinguisher_certification_notes = fields.Text('Extinguisher certification notes')

    has_bie_revision = fields.Boolean('Has BIE revision')
    bie_revision_ids = fields.One2many(
        'bie.revision',
        'stock_service_picking_id',
        'Extinguisher revision'
    )
    bie_revision_correct = fields.Selection([
        ('correct', 'Correct'),
        ('has_anomalies', 'Has anomalies')
    ], 'BIE revision is correct')
    bie_certification_notes = fields.Text('BIE certification notes')

    signature_date = fields.Date('Signature date', readonly=False)
    signature_name = fields.Char('Signature name', readonly=True)
    signature_job = fields.Char('Signature job', readonly=True)
    signature_vat = fields.Char('Signature VAT', readonly=True)
    signature_image = fields.Binary('Signature image', readonly=True)

    picking_code = fields.Char(
        "Picking code",
        store=True,
    )

    def custom_format_date(self, date):
        if date:
            return date.strftime("%m/%Y")
        return ""

    def _compute_picking_code(self):
        for record in self:
            if record.state == "closed" and record.build_address_id and record.build_address_id.zip_id and (
                record.has_bie_revision or record.has_extinguisher_revision
            ):
                secuence = self.env["stock.service.picking.sequence"].sudo().search([
                    ("year", "=", record.picking_date.year),
                    ("zip_code", "=", record.build_address_id.zip_id.id)
                ])
                if not secuence:
                    secuence = self.env["stock.service.picking.sequence"].sudo().create({
                        "year": record.picking_date.year,
                        "zip_code": record.build_address_id.zip_id.id,
                        "secuence": 0
                    })

                picking_code = str(record.state_id.code) + str(record.picking_date.year)[1:3] \
                    + secuence.get_next_secuence() + "-" + record.name.split("-")[1]
            else:
                picking_code = False

            record.picking_code = picking_code

    def action_close(self):
        res = super(StockServicePicking, self).action_close()
        self._compute_picking_code()
        return res

    def action_sign(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Signature',
            'res_model': 'service.picking.signature.wzd',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_picking_id': self.id,
            }
        }

    def get_period(self):
        self.ensure_one()
        if self.contract_id.revision_period == "anual":
            return _("ANUAL REVISION")
        else:
            return _("QUARTERLY REVISION")

    @api.onchange('has_extinguisher_revision')
    def _onchange_has_extinguisher_revision(self):
        self.ensure_one()
        if not self.has_extinguisher_revision:
            self.extinguisher_revision_ids = [(5,)]
        else:
            values = []
            for extinguisher in self.contract_id.extinguisher_and_signal_ids:
                values.append((0, 0, {'extinguisher_and_signal_id': extinguisher.id}))

            self.extinguisher_revision_ids = values

    @api.onchange('has_bie_revision')
    def _onchange_has_bie_revision(self):
        self.ensure_one()
        if not self.has_bie_revision:
            self.bie_revision_ids = [(5,)]
        else:
            values = []
            for bie in self.contract_id.bie_and_signal_ids:
                values.append((0, 0, {'bie_and_signal_id': bie.id}))

            self.bie_revision_ids = values

    @api.model
    def create(self, vals):
        if vals.get("contract_id", False):
            contract = self.env["limp.contract"].browse(vals["contract_id"])
            if not vals.get("delegation_id", False):
                vals["delegation_id"] = contract.delegation_id.id
            if not vals.get("department_id", False):
                vals["department_id"] = contract.department_id.id
            if not vals.get("company_id", False):
                vals["company_id"] = contract.company_id.id
            if not vals.get("parent_id", False):
                vals["parent_id"] = contract.analytic_account_id.id
        return super(StockServicePicking, self).create(vals)

    @api.onchange("contract_id")
    def onchange_contract_id(self):
        if self.contract_id:
            contract = self.contract_id
            self.parent_id = contract.analytic_account_id
            self.department_id = contract.department_id
            self.delegation_id = contract.delegation_id
            self.partner_id = contract.partner_id
            self.manager_id = contract.manager_id
            self.address_invoice_id = contract.address_invoice_id
            self.address_id = contract.address_id
            self.ccc_account_id = contract.bank_account_id
            self.payment_type = contract.payment_type_id
            self.payment_term = contract.payment_term_id
            self.privacy = contract.privacy
            self.address_tramit_id = contract.address_tramit_id
            self.type_ddd_ids = [(6, 0, contract.type_ddd_ids.ids)]
            self.parent_id = contract.analytic_account_id.id
            self.used_product_ids = [(6, 0, contract.used_product_ids.ids)]

    def format_date(self, date, date_format):
        import locale
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
        return date.strftime(date_format)


class StockServicePickingSecuence(models.Model):
    _name = "stock.service.picking.sequence"

    secuence = fields.Integer("Secuence", readonly=True, required=True, default=0)
    year = fields.Char("Year", required=True,
                       default=lambda x: str(datetime.now().year))
    zip_code = fields.Char("Zip code", required=True)

    _sql_constraints = [(
        "unique_year_zip_code",
        "unique(year, zip_code)",
        "The combination of year and zip code must be unique",
    )]

    def get_next_secuence(self):
        self.ensure_one()
        self.write({"secuence": self.secuence + 1})
        output = str(self.secuence)
        while len(output) < 4:
            output = "0" + output
        return output
