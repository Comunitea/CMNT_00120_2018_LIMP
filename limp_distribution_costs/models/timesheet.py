##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Marta Vázquez Rodríguez$
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
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class Timesheet(models.Model):
    _name = "timesheet"

    name = fields.Char(
        "Name",
        size=12,
        default=lambda self: self.env["ir.sequence"].next_by_code("timesheet"),
    )
    date = fields.Date("Date", required=True)
    employee_id = fields.Many2one("hr.employee", "Employee", required=True)
    analytic_id = fields.Many2one(
        "account.analytic.account", "Analytic account"
    )
    hours = fields.Float("Hours", digits=(12, 2), required=True)
    contract = fields.Boolean("Contract")
    fix_qty = fields.Float("Fix Qty.", digits=dp.get_precision("Account"))
    quantity = fields.Float("Qty.", digits=dp.get_precision("Account"))
    extra_hours = fields.Float("Extra Hours", digits=(4, 2))
    price_hours = fields.Float("Price Hours", digits=(4, 2))
    effective = fields.Float("Effective", digits=(4, 2))
    done = fields.Boolean("Done")
    paid = fields.Boolean("Paid")
    paid_date = fields.Date("Paid date")
    ss_hours = fields.Float("SS hours", digits=(4, 2))
    ss_no_hours = fields.Float("No ss hours", digits=(4, 2))
    total_hours = fields.Float(compute="_compute_total_hours", store=True)
    company_id = fields.Many2one(
        "res.company",
        "Company",
        readonly=True,
        default=lambda r: r._context.get(
            "company_id", r.env.user.company_id.id
        ),
    )
    pending_qty = fields.Float(
        "Quantity to Distribute",
        digits=(12, 2),
        compute="_compute_pending_qty",
    )
    pending_distribute_qty = fields.Float(
        "Pending Quantity", digits=(12, 2), compute="_compute_pending_qty"
    )
    delegation_id = fields.Many2one("res.delegation", "Delegation")
    department_id = fields.Many2one("hr.department", "Department")
    responsible_id = fields.Many2one(
        "hr.employee", "Responsible", domain=[("responsible", "=", True)]
    )
    description = fields.Char("Description", size=255)
    old = fields.Boolean("Old")
    employee_delegation_id = fields.Many2one(
        "res.delegation", "Employee Delegation"
    )
    employee_department_id = fields.Many2one(
        "hr.department", "Employee Department"
    )
    # create_uid': fields.many2one('res.users', 'Creator', readonly=True)

    @api.depends("ss_hours", "ss_no_hours")
    def _compute_total_hours(self):
        for tsobj in self:
            tsobj.total_hours = tsobj.ss_hours + tsobj.ss_no_hours

    @api.depends(
        "extra_hours",
        "price_hours",
        "hours",
        "quantity",
        "effective",
        "fix_qty",
    )
    def _compute_pending_qty(self):
        for tsobj in self:
            pending_qty = (
                (tsobj.extra_hours * tsobj.price_hours)
                + (tsobj.hours * tsobj.price_hours)
                + tsobj.quantity
            )
            tsobj.pending_qty = pending_qty
            tsobj.pending_distribute_qty = (
                pending_qty - tsobj.effective - tsobj.fix_qty
            )

    @api.onchange("fix_qty")
    def onchange_fix_qty(self):
        if not self.pending_distribute_qty:
            self.paid = True
            self.done = True
        else:
            self.paid = False
            self.done = False

    @api.onchange("hours")
    def onchange_hours(self):
        if self.hours:
            self.contract = True
            self.done = True
            self.paid = True
        else:
            self.contract = False
            self.done = False
            self.paid = False

    @api.onchange("analytic_id")
    def on_change_analytic_id(self):
        if not self.analytic_id:
            self.delegation_id = False
            self.department_id = False
            self.responsible_id = False
        else:
            self.delegation_id = self.analytic_id.delegation_id.id
            self.department_id = self.analytic_id.department_id.id
            self.responsible_id = self.analytic_id.manager_id.id

    @api.model
    def create(self, vals):
        if vals.get("hours", 0.0) and not vals.get("paid", False):
            vals["paid"] = True
            vals["contract"] = True
            vals["done"] = True
        if (
            vals.get("fix_qty", False)
            and vals.get("done", False)
            and not vals.get("paid", False)
        ):
            vals["paid"] = True
            vals["contract"] = True
        if vals.get("paid", False):
            vals["paid_date"] = fields.Date.today()
        if vals.get("hours", 0.0) and not vals.get("ss_hours", 0.0):
            vals["ss_hours"] = vals["hours"]
        if vals.get("employee_id", False):
            employee_id = self.env["hr.employee"].browse(vals["employee_id"])
            vals["employee_delegation_id"] = employee_id.delegation_id.id
            vals["employee_department_id"] = employee_id.department_id.id

        return super(Timesheet, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get("hours", 0.0) and not vals.get("paid", False):
            vals["paid"] = True
            vals["contract"] = True
            vals["done"] = True
        if (
            vals.get("fix_qty", False)
            and vals.get("done", False)
            and not vals.get("paid", False)
        ):
            vals["paid"] = True
            vals["contract"] = True
        if vals.get("paid", False) and not vals.get("paid_date", False):
            vals["paid_date"] = fields.Date.today()
        if vals.get("hours", 0.0) and not vals.get("ss_hours", 0.0):
            vals["ss_hours"] = vals["hours"]
        if vals.get("employee_id", False):
            employee_id = self.env["hr.employee"].browse(vals["employee_id"])
            vals["employee_delegation_id"] = employee_id.delegation_id.id
            vals["employee_department_id"] = employee_id.department_id.id
        for line in self:
            if "hours" in vals and not vals["hours"] and line.hours:
                vals["contract"] = False
                vals["paid"] = False
                vals["done"] = False
                vals["paid_date"] = False

        return super(Timesheet, self).write(vals)

    @api.multi
    def unlink(self):
        if self.env.user.id != 1:
            for tim in self:
                if tim.create_uid.id != self.env.user.id:
                    raise UserError(
                        _("Error"),
                        _(
                            "Cannot delete this timesheet, "
                            "because you are not the creator or admin."
                        ),
                    )
        return super(Timesheet, self).unlink()
