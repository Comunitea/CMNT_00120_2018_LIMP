##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos. All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the Affero GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the Affero GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    manager_id = fields.Many2one(
        default=lambda r: r.env.user.context_responsible_id.id
        or r.env.user.employee_ids
        and r.env.user.employee_ids[0].id
    )


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    manager_id = fields.Many2one(
        default=lambda r: r.env.user.context_responsible_id.id
        or r.env.user.employee_ids
        and r.env.user.employee_ids[0].id
    )


class AccountAnalyticDistribution(models.Model):

    _inherit = "account.analytic.distribution"

    manager_id = fields.Many2one(
        default=lambda r: r.env.user.context_responsible_id.id
        or r.env.user.employee_ids
        and r.env.user.employee_ids[0].id
    )


class AccountAnalyticAccount(models.Model):

    _inherit = "account.analytic.account"

    manager_id = fields.Many2one(
        default=lambda r: r._context.get(
            "c_manager_id",
            r.env.user.context_responsible_id.id
            or r.env.user.employee_ids
            and r.env.user.employee_ids[0].id,
        )
    )


class AccountAnalyticLine(models.Model):

    _inherit = "account.analytic.line"

    manager_id = fields.Many2one(
        default=lambda r: r._context.get(
            "c_manager_id",
            r.env.user.context_responsible_id.id
            or r.env.user.employee_ids
            and r.env.user.employee_ids[0].id,
        )
    )
