# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
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
from datetime import datetime, timedelta


class Remuneration(models.Model):
    _name = "remuneration"
    _description = "Remunerations"

    name = fields.Char(
        size=8, readonly=True,
        default=lambda r: r.env['ir.sequence'].get('remuneration'))
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    incidence = fields.Boolean()
    date = fields.Date(required=True)
    incidence_id_tp = fields.Many2one(
        'incidence', 'Type',
        default=lambda r: r.env['incidence'].search(
            [('code', '=', 'def')])[0] or False)
    absence_id_tp = fields.Many2one('absence', 'Type absence')
    date_to = fields.Date()
    with_contract = fields.Boolean()
    contract_hours = fields.Float('Hours', digits=(12, 2))
    with_hour_price = fields.Boolean()
    hour_price_hours = fields.Float('Hours', digits=(12, 2))
    with_fix_qty = fields.Boolean()
    price = fields.Float(digits=(12, 2))
    quantity = fields.Float(digits=(12, 2))
    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Account')

    parent_id = fields.Many2one(
        'remuneration', 'Parent remuneration', readonly=True, index=True)
    child_ids = fields.One2many(
        'remuneration', 'parent_id', string='Childs remunerations',
        readonly=True)
    department_id = fields.Many2one(
        "hr.department", "Department",
        default=lambda r: r._context.get('department_id', False))
    location_id = fields.Many2one('city.council', 'Council')
    effective = fields.Float(digits=(12, 2))
    ss_hours = fields.Float('SS hours', digits=(4, 2))
    ss_no_hours = fields.Float('No ss hours', digits=(4, 2))
    total_hours = fields.Float(compute='_compute_total_hours')
    analytic_distribution_id = fields.Many2one(
        'account.analytic.distribution', 'Analytic Distribution')
    company_id = fields.Many2one(
        'res.company', 'Company', required=False,
        default=lambda r: r.env.user.company_id.id)
    old = fields.Boolean()
    notes = fields.Text()


    def _compute_total_hours(self):
        for remu in self:
            remu.total_hours = remu.ss_hours + remu.ss_no_hours

    def get_periods_remuneration(self, start_date, end_date):
        def daterange(start_date, end_date):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            for n in range(int((end_date - start_date).days + 1)):
                yield datetime.strftime(start_date + timedelta(n), "%Y-%m-%d")
        res = {}
        days_to_cover = []
        days_covered = set()
        if (self.date_to >= start_date or self.date_to) and self.date <= end_date:
            for single_date in daterange(start_date, end_date):
                days_to_cover.append(single_date)
            child_rem_ids = self.search(
                ['|', ('date_to', '>=', start_date), ('date_to', '=', False),
                 ('date', '<=', end_date), ('parent_id', '=', self.id),
                 ('employee_id', '=', self.employee_id.id)])
            for child_rem in child_rem_ids:
                key = False
                if child_rem.date <= start_date and child_rem.date_to and child_rem.date_to <= end_date:
                    key = start_date + "#" + child_rem.date_to
                elif child_rem.date < start_date and child_rem.date_to and child_rem.date_to > end_date:
                    key = start_date + "#" + end_date
                elif child_rem.date >= start_date and child_rem.date_to and child_rem.date_to <= end_date:
                    key = child_rem.date + "#" + child_rem.date_to
                elif child_rem.date >= start_date and child_rem.date_to and child_rem.date_to > end_date:
                    key = child_rem.date + "#" + end_date
                elif child_rem.date <= start_date and not child_rem.date_to:
                    key = start_date + "#" + end_date
                elif child_rem.date >= start_date and child_rem.date <= end_date and not child_rem.date_to:
                    key = child_rem.date + "#" + end_date

                if key:
                    period_start, period_end = key.split('#')
                    for single_date in daterange(period_start, period_end):
                        days_covered.add(single_date)

                    if res.get(key, False):
                        res[key].append(child_rem.id)
                    else:
                        res[key] = [child_rem.id]

            if days_covered:
                days_covered = list(days_covered)
                days_to_cover = sorted(days_to_cover)
                days_covered = sorted(days_covered)
                start_day = False
                end_day = False
                for day in days_to_cover:
                    if day not in days_covered and day >= self.date and (not self.date_to or day <= self.date_to):
                        if not start_day:
                            start_day = day
                            end_day = day
                        else:
                            end_day = day
                    elif day in days_covered and start_day and end_day:
                        key = start_day + "#" + end_day
                        res[key] = [self.id]
                        start_day = False
                        end_day = False
                if start_day and end_day:
                    key = start_day + "#" + end_day
                    res[key] = [self.id]
            else:
                if start_date <= self.date:
                    start_date = self.date
                if self.date_to and end_date >= self.date_to:
                    end_date = self.date_to
                key = start_date + "#" + end_date
                res[key] = [self.id]
        return res

    @api.model
    def check_is_absence(self, id=False, vals={}):
        if vals.get('incidence_id_tp', False):
            incidence_obj = self.env['incidence'].browse(vals['incidence_id_tp'])
            if incidence_obj.is_absence:
                if not vals.get('absence_id_tp', False):
                    raise UserError(_('As the incidence of absence type must complete the type of absence !'))

        if self:
            for remuneration_id in self:
                if remuneration_id.incidence and \
                        remuneration_id.incidence_id_tp.is_absence \
                        and not vals.get('absence_id_tp', False):
                    raise UserError(_('As the incidence of absence type must complete the type of absence !'))

        return True

    @api.model
    def create(self, vals):
        if vals.get('incidence', False):
            if vals.get('incidence_id_tp', False) or vals.get('absence_id_tp', False):
                self.check_is_absence(vals)
        if vals.get('analytic_account_id', False):
            account = self.env['account.analytic.account'].browse(vals['analytic_account_id'])
            if not vals.get('department_id', False):
                vals['department_id'] = account.department_id and account.department_id.id or False
            if not vals.get('location_id', False):
                vals['location_id'] = account.location_id and account.location_id.id or False
        return super(Remuneration, self).create(vals)

    @api.multi
    def write(self, vals):
        if not vals:
            return True
        if vals.get('incidence', False):
            if vals.get('incidence_id_tp', False) or vals.get('incidence_id_tp', False) or not vals.get('incidence_id_tp', False):
                self.check_is_absence(vals)
        if vals.get('date_to', False):
            for remuneration_id in self:
                for child in remuneration_id.child_ids:
                    if not child.date_to:
                        child.write({'date_to': vals['date_to']})
        return super(Remuneration, self).write(vals)

    @api.multi
    def copy_data(self, default=None):
        default = dict(default or [])
        if self._context.get('is_contract', False):
            if self.parent_id or self.date_to:
                return {}
        default.update({'parent_id': False, 'date_to': False, 'child_ids': [(6, 0, [])]})
        return super(Remuneration, self).copy_data(default)

    @api.multi
    def make_child_inc_remuneration(self, vals):
        distribute_bt_remuneration = False
        total_hours = 0.0
        total_ss_hours = 0.0
        total_noss_hours = 0.0
        if vals.get('distribute_bt_remuneration', False):
            distribute_bt_remuneration = True
            total_ss_hours = sum([x.ss_hours for x in self])
            total_noss_hours = sum([x.ss_no_hours for x in self])
            total_hours = (total_ss_hours + total_noss_hours)

        for line_remuneration in self:

            employee_id = line_remuneration.employee_id.id
            analytic_account_id = line_remuneration.analytic_account_id.id
            parent_id = line_remuneration.id

            if vals.get('conditions', False) != 'equal_condition' and not \
                    distribute_bt_remuneration:
                with_contract = vals['with_contract']
                contract_hours = vals['contract_hours']
                with_hour_price = vals['with_hour_price']
                hour_price_hours = vals['hour_price_hours']
                with_fix_qty = vals['with_fix_qty']
                price = vals['price']
                quantity = vals['quantity']
                ss_hours = vals['ss_hours']
                ss_no_hours = vals['ss_no_hours']
                effective = vals['effective']
            elif vals.get('conditions', False) != 'equal_condition':
                remu_hours = line_remuneration.ss_no_hours + line_remuneration.ss_hours
                with_contract = vals['with_contract']
                contract_hours = (vals['contract_hours'] * remu_hours) / (total_hours or 1.0)
                with_hour_price = vals['with_hour_price']
                hour_price_hours = (vals['hour_price_hours'] * remu_hours) / (total_hours or 1.0)
                with_fix_qty = vals['with_fix_qty']
                price = vals['price']
                quantity = (vals['quantity'] * remu_hours) / (total_hours or 1.0)
                ss_hours = (vals['ss_hours'] * line_remuneration.ss_hours) / (total_ss_hours or 1.0)
                ss_no_hours = (vals['ss_no_hours'] * line_remuneration.ss_no_hours) / (total_noss_hours or 1.0)
                effective = (vals['effective'] * remu_hours) / (total_hours or 1.0)
            else:
                with_contract = line_remuneration.with_contract
                contract_hours = line_remuneration.contract_hours
                with_hour_price = line_remuneration.with_hour_price
                hour_price_hours = line_remuneration.hour_price_hours
                with_fix_qty = line_remuneration.with_fix_qty
                price = line_remuneration.price
                quantity = line_remuneration.quantity
                ss_hours = line_remuneration.ss_hours
                ss_no_hours = 0.0
                effective = 0.0

            if vals.get('date'):
                self.env['remuneration'].create({
                    'employee_id': employee_id,
                    'date': vals['date'],
                    'analytic_account_id': analytic_account_id,
                    'parent_id': parent_id,
                    'incidence_id_tp': vals['incidence_id_tp'] or False,
                    'absence_id_tp': vals['absence_id_tp'] or False,
                    'date_to': vals['date_to'] or False,
                    'with_contract': with_contract,
                    'contract_hours': contract_hours,
                    'with_hour_price': with_hour_price,
                    'hour_price_hours': hour_price_hours,
                    'with_fix_qty': with_fix_qty,
                    'ss_no_hours': ss_no_hours,
                    'ss_hours': ss_hours,
                    'price': price,
                    'quantity': quantity,
                    'effective': effective,
                    'incidence': True,
                })


class Incidence(models.Model):

    _inherit = "incidence"

    remuneration_ids = fields.One2many(
        'remuneration', 'incidence_id_tp', 'Remunerations', readonly=True)


class Absence(models.Model):

    _inherit = "absence"

    remuneration_ids = fields.One2many(
        'remuneration', 'absence_id_tp', 'Remunerations', readonly=True)
