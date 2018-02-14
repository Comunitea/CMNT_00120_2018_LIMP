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
from openerp import models, fields, api, _
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

def daterange(start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    for n in range(int((end_date - start_date).days + 1)):
        yield datetime.strftime(start_date + timedelta(n),"%Y-%m-%d")

def base_calendar_id2real_id(base_calendar_id=None, with_date=False):
    """
    This function converts virtual event id into real id of actual event
    @param base_calendar_id: Id of calendar
    @param with_date: If value passed to this param it will return dates based on value of withdate + base_calendar_id
    """

    if base_calendar_id and isinstance(base_calendar_id, (str, unicode)):
        res = base_calendar_id.split('-')

        if len(res) >= 2:
            real_id = res[0]
            if with_date:
                real_date = time.strftime("%Y-%m-%d %H:%M:%S", \
                                 time.strptime(res[1], "%Y%m%d%H%M%S"))
                start = datetime.strptime(real_date, "%Y-%m-%d %H:%M:%S")
                end = start + timedelta(hours=with_date)
                return (int(real_id), real_date, end.strftime("%Y-%m-%d %H:%M:%S"))
            return int(real_id)

    return base_calendar_id and int(base_calendar_id) or base_calendar_id

class remuneration(models.Model):
    _name = "remuneration"
    _description = "Remunerations"

    def _compute_total_hours(self):
        pass
        '''MIGRACION: Solo se cambia la firma a nueva api
        if context is None:
            context = {}
        res = {}
        for remu in self.browse(cr, uid, ids):
            res[remu.id] = remu.ss_hours + remu.ss_no_hours

        return res'''

    name = fields.Char(size=8, readonly=True, default=lambda r: r.env['ir.sequence'].get('remuneration'))
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    incidence = fields.Boolean('Incidence')
    date = fields.Date('Date', required=True)
    incidence_id_tp = fields.Many2one('incidence', 'Type', default=lambda r: r.env['incidence'].search([('code', '=', 'def')])[0] or False)
    absence_id_tp = fields.Many2one('absence', 'Type absence')
    date_to = fields.Date('Date to')
    with_contract = fields.Boolean('With contract')
    contract_hours = fields.Float('Hours', digits=(12, 2))
    with_hour_price = fields.Boolean('With hour price')
    hour_price_hours = fields.Float('Hours', digits=(12, 2))
    with_fix_qty = fields.Boolean()
    price = fields.Float(digits=(12, 2))
    quantity = fields.Float(digits=(12, 2))
    analytic_account_id = fields.Many2one('account.analytic.account', 'Account')
    state = fields.Selection(related='analytic_account_id.state')
    # selection=[('draft','Draft'),('open','Open'), ('pending','Pending'),('cancelled', 'Cancelled'),('close','Closed'),('template', 'Template')]

    parent_id = fields.Many2one('remuneration', 'Parent remuneration', readonly=True, select=True)
    child_ids = fields.One2many('remuneration', 'parent_id', string='Childs remunerations', readonly=True)
    department_id = fields.Many2one("hr.department", "Department", default=lambda r: r._context.get('department_id', False))
    location_id = fields.Many2one('city.council', 'Council')
    effective = fields.Float(digits=(12, 2))
    ss_hours = fields.Float('SS hours', digits=(4, 2))
    ss_no_hours = fields.Float('No ss hours', digits=(4, 2))
    total_hours = fields.Float(compute='_compute_total_hours')
    analytic_distribution_id = fields.Many2one('account.analytic.plan.instance', 'Analytic Distribution')
    company_id = fields.Many2one('res.company', 'Company', required=False, default=lambda r: r.env.user.company_id.id)
    old = fields.Boolean('Old')
    notes = fields.Text('Notes')

    @api.multi
    def get_periods_remuneration(self, remuneration_id, start_date, end_date):
        pass
        '''MIGRACION: Solo firma
        res = {}
        days_to_cover = []
        days_covered = set()
        rem_obj = self.browse(cr, uid, remuneration_id)
        if (rem_obj.date_to >= start_date or rem_obj.date_to == False) and rem_obj.date <= end_date:
            for single_date in daterange(start_date, end_date):
                days_to_cover.append(single_date)
            child_rem_ids = self.search(cr, uid, ['|',('date_to','>=',start_date),('date_to','=',False),('date','<=',end_date),('parent_id','=',rem_obj.id),('employee_id', '=', rem_obj.employee_id.id)])
            if child_rem_ids:
                for child_rem in self.browse(cr, uid, child_rem_ids):
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
                    elif child_rem.date >= start_date and child_rem.date <= end_date  and not child_rem.date_to:
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
                    if day not in days_covered and day >= rem_obj.date and (not rem_obj.date_to or day <= rem_obj.date_to):
                        if not start_day:
                            start_day = day
                            end_day = day
                        else:
                            end_day = day
                    elif day in days_covered and start_day and end_day:
                        key = start_day + "#" + end_day
                        res[key] = [rem_obj.id]
                        start_day = False
                        end_day = False
                if start_day and end_day:
                    key = start_day + "#" + end_day
                    res[key] = [rem_obj.id]
            else:
                if start_date <= rem_obj.date:
                    start_date = rem_obj.date
                if rem_obj.date_to and end_date >= rem_obj.date_to:
                    end_date = rem_obj.date_to
                key = start_date + "#" + end_date
                res[key] = [rem_obj.id]
        return res'''


    @api.multi
    def action_open(self):
        return self.write({'state': 'open'})

    @api.model
    def check_is_absence(self, id=False, vals={}):
        pass
        '''MIGRACION: Solo firma
        if vals.get('incidence_id_tp', False):
            incidence_obj = self.pool.get('incidence').browse(cr,uid, vals['incidence_id_tp'])
            if incidence_obj.is_absence == True:
                if not vals.get('absence_id_tp', False):
                    raise osv.except_osv(_('Error'), _('As the incidence of absence type must complete the type of absence !'))

        if id:
            for remuneration_id in self.browse(cr, uid, id):
                if remuneration_id.incidence == True and remuneration_id.incidence_id_tp.is_absence == True and not vals.get('absence_id_tp', False):
                    raise osv.except_osv(_('Error'), _('As the incidence of absence type must complete the type of absence !'))

        return True'''

    @api.model
    def create(self, vals):

        '''MIGRACION: Solo firma
        if context is None: context = {}

        if vals.get('incidence',False):
            if vals.get('incidence_id_tp', False) or vals.get('absence_id_tp', False):
                self.check_is_absence(cr, uid, False, vals, context=context)
        if vals.get('analytic_account_id', False):
            account = self.pool.get('account.analytic.account').browse(cr, uid, vals['analytic_account_id'])
            if not vals.get('department_id', False):
                vals['department_id'] = account.department_id and account.department_id.id or False
            if not vals.get('location_id', False):
                vals['location_id'] = account.location_id and account.location_id.id or False'''

        return super(remuneration, self).create(vals)

    @api.multi
    def write(self, vals):
        """When writing a end date in the remuneration, updating the child"""
        '''MIGRACION: Solo firma
        if context is None: context = {}
        if not vals:
            return True
        if isinstance(ids, (int, long)):
            ids = [ids]
        if vals.get('incidence', False):
            if vals.get('incidence_id_tp', False) or vals.get('incidence_id_tp', False) or not vals.get('incidence_id_tp', False):
                self.check_is_absence(cr, uid, ids, vals, context=context)
        if vals.get('date_to', False):
            for remuneration_id in self.browse(cr, uid, ids):
                for child in remuneration_id.child_ids:
                    if child.date_to == False:
                        self.write(cr,uid,[child.id],{'date_to': vals['date_to']})'''
#~ CODIGO YA COMENTADO ANTES DE MIGRACION
                #~ occupation_ids = self.pool.get('account.analytic.occupation').search(cr, uid, [('analytic_account_id', '=', remuneration_id.analytic_account_id.id),('state', 'in', ['active','incidence','replaced','replacement']), ('date', '<=',  vals['date_to']), ('date', '>=', remuneration_id.date), ('employee_id', '=', remuneration_id.employee_id.id)])
#~
                #~ if occupation_ids:
                    #~ occupation_ids = map(lambda x: base_calendar_id2real_id(x), occupation_ids)
                    #~ occupation_ids = list(set(occupation_ids))
                    #~ for occupation_id in self.pool.get('account.analytic.occupation').read(cr, uid, occupation_ids, ['end_date', 'end_type']):
                        #~ if occupation_id['end_date'] == False or occupation_id['end_date'] > vals['date_to']:
                            #~ self.pool.get('account.analytic.occupation').write(cr,uid,[occupation_id['id']],{'end_type': 'end_date','end_date': vals['date_to']})

            #~ if remuneration_id.incidence == True and remuneration_id.absence_id_tp <> False:
                #~ date = remuneration_id.date + " 00:00:00"
                #~ end_date = (datetime.strptime(date, "%Y-%m-%d %H:%M:%S") + relativedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
                #~
                #~ occupation_ids2 = self.pool.get('account.analytic.occupation').search(cr, uid, [('state', '=', 'active'),('end_type', '=', 'end_date'),('end_date', '=', end_date),('employee_id', '=', remuneration_id.employee_id.id)])
                #~ if occupation_ids2:
                    #~ dat_to = vals['date_to'] + occupation_id['date'][10:]
                    #~ date_to = (datetime.strptime(dat_to, "%Y-%m-%d %H:%M:%S") + relativedelta(days=+1)).strftime("%Y-%m-%d %H:%M:%S")
                    #~ for occupation_id in self.pool.get('account.analytic.occupation').read(cr, uid, occupation_ids2, ['end_date','duration','date_deadline', 'end_type', 'remuneration_id']):
                        #~ if occupation_id['remuneration_id']:
                            #~ if occupation_id['remuneration_id']:
                                #~ remuneration_obj = self.browse(cr,uid,occupation_id['remuneration_id'][0])
                                #~
                                #~ if not remuneration_obj.date_to:
                                    #~ self.pool.get('account.analytic.occupation').copy(cr, uid, occupation_id['id'], default={'date': date_to,
                                                                                                    #~ 'end_date': False,
                                                                                                    #~ 'end_type': 'forever',
                                                                                                    #~ 'state': 'active',
                                                                                                    #~ 'to_invoice' : False,
                                                                                                    #~ 'duration': occupation_id['duration'] ,
                                                                                                    #~ 'parent_occupation_id': occupation_id['id'],
                                                                                                    #~ 'date_deadline': ((datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S")) + relativedelta(hours=+occupation_id['duration'])).strftime("%Y-%m-%d %H:%M:%S")
                                                                                                    #~ }, context=context)
                                #~
                                #~ elif remuneration_obj.date_to > dat_to:
                                    #~ new_id = self.pool.get('account.analytic.occupation').copy(cr, uid, occupation_id['id'], default={'date': date_to,
                                                                                                    #~ 'state': 'active',
                                                                                                    #~ 'to_invoice' : False,
                                                                                                    #~ 'duration': occupation_id['duration'] ,
                                                                                                    #~ 'parent_occupation_id': occupation_id['id'],
                                                                                                    #~ 'date_deadline': ((datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S")) + relativedelta(hours=+occupation_id['duration'])).strftime("%Y-%m-%d %H:%M:%S"),
                                                                                                    #~ 'remuneration_id': remuneration_obj.id
                                                                                                    #~ }, context=context)
                                    #~ self.pool.get('account.analytic.occupation').write(cr, uid, [new_id], {'end_date': remuneration_obj.date_to,
                                                                                                        #~ 'end_type': 'end_date',})


        return super(remuneration, self).write(vals)

    @api.one
    def copy_data(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        if not context:
            context = {}
        if context.get('is_contract', False):
            rem = self.browse(cr, uid, id)
            if rem.parent_id or rem.date_to:
                return {}
        default.update({'parent_id': False, 'date_to': False, 'child_ids': [(6,0,[])]})
        return super(remuneration, self).copy_data(cr, uid, id, default, context)

    @api.multi
    def make_child_inc_remuneration(self, vals):
        pass
        '''MIGRACION: Solo firma
        if context is None:
            context = {}
        visited_occupations = []
        if ids:
            remuneration_objs = self.pool.get('remuneration').browse(cr,uid,ids,context=context)
            distribute_bt_remuneration = False
            total_hours = 0.0
            total_ss_hours = 0.0
            total_noss_hours = 0.0
            if vals.get('distribute_bt_remuneration', False):
                distribute_bt_remuneration = True
                total_ss_hours = sum([x.ss_hours for x in remuneration_objs])
                total_noss_hours = sum([x.ss_no_hours for x in remuneration_objs])
                total_hours = (total_ss_hours + total_noss_hours)

            for line_remuneration in remuneration_objs:
                end_date = vals['date_to'] and vals['date_to'] + " 23:59:59" or False

                date = vals['date'] + " 00:00:00"

                employee_id = line_remuneration.employee_id.id
                analytic_account_id = line_remuneration.analytic_account_id.id
                parent_id = line_remuneration.id

                if vals.get('conditions', False) != 'equal_condition' and not distribute_bt_remuneration:
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
                    with_fix_qty =  vals['with_fix_qty']
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
                    child_remuneration_id =  self.pool.get('remuneration').create(cr,uid,{'employee_id': employee_id,
                            'date': vals['date'],
                            'analytic_account_id': analytic_account_id,
                            'parent_id': parent_id,
                            'incidence_id_tp': vals['incidence_id_tp'] or False,
                            'absence_id_tp': vals['absence_id_tp'] or False,
                            'date_to': vals['date_to'] or False,
                            'with_contract' : with_contract,
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
                            })'''
#~ COMENTADO ANTES DE MIGRACION
                #~ if end_date:
                    #~ occupation_ids = self.pool.get('account.analytic.occupation').search(cr, uid, [('analytic_account_id','=',analytic_account_id),('state', 'in', ['active','replacement']), ('date', '<=', end_date), ('date', '>=', date), ('employee_id', '=', employee_id)])
                #~ else:
                    #~ occupation_ids = self.pool.get('account.analytic.occupation').search(cr, uid, [('analytic_account_id','=',analytic_account_id),('state', 'in', ['active','replacement']), ('date', '>=', date), ('employee_id', '=', employee_id)])
                #~ if occupation_ids:
                    #~ occupation_ids = map(lambda x: base_calendar_id2real_id(x), occupation_ids)
                    #~ occupation_ids = list(set(occupation_ids))
#~
                    #~ for occupation in self.pool.get('account.analytic.occupation').read(cr, uid, occupation_ids, ['date', 'date_deadline', 'end_date', 'rrule', 'duration', 'state', 'end_type']):
#~
                        #~ real_id = occupation['id']
                        #~ if isinstance(real_id, (unicode, str)) and len(real_id.split('-')) > 1:
                            #~ real_id = int(real_id.split('-')[0])
                        #~ if real_id not in visited_occupations:
                            #~ visited_occupations.append(real_id)
                            #~ if occupation.get('rrule'): #is recurrent instance
#~
                                #~ new_id = self.pool.get('account.analytic.occupation').copy(cr, uid, real_id, default={'date': (occupation['date'] > date) and occupation['date'] or date[:10] + occupation['date'][10:],
                                                                                                                                #~ 'duration': occupation['duration'],
                                                                                                                                #~ 'date_deadline': (occupation['date'] > date) and ((datetime.strptime(occupation['date'], "%Y-%m-%d %H:%M:%S")) + relativedelta(hours=+occupation['duration'])).strftime("%Y-%m-%d %H:%M:%S") or (datetime.strptime(date[:10] + occupation['date'][10:], "%Y-%m-%d %H:%M:%S") + relativedelta(hours=+occupation['duration'])).strftime("%Y-%m-%d %H:%M:%S"),
                                                                                                                                #~ 'state': 'incidence',
                                                                                                                                #~ 'to_invoice' : False,
                                                                                                                                #~ 'remuneration_id': child_remuneration_id,
                                                                                                                                #~ 'parent_occupation_id': real_id}, context=context)
                                #~ self.pool.get('account.analytic.occupation').write(cr, uid, [new_id], {
                                        #~ 'end_date': end_date and ((occupation.get('end_date') and occupation['end_date'] <  end_date) and occupation['end_date'] or end_date) or (occupation.get('end_date') and occupation['end_date'] or False) or False,
                                        #~ 'end_type': end_date and 'end_date' or ((occupation.get('end_type') and occupation['end_type'] == 'end_date') and 'end_date' or 'forever'),
                                #~ })
                                #~ if end_date and occupation.get('end_date') and occupation['end_date'] >  end_date:
                                    #~ new_id = self.pool.get('account.analytic.occupation').copy(cr, uid, real_id, default={'date': (datetime.strptime(end_date[:10] + occupation['date'][10:], "%Y-%m-%d %H:%M:%S") + relativedelta(days=+1)).strftime("%Y-%m-%d %H:%M:%S") or False,
                                                                                                                                #~ 'duration': occupation['duration'],
                                                                                                                                #~ 'date_deadline': (datetime.strptime(end_date[:10] + occupation['date'][10:], "%Y-%m-%d %H:%M:%S") + relativedelta(days=+1) + relativedelta(hours=+occupation['duration'])).strftime("%Y-%m-%d %H:%M:%S") or False,
                                                                                                                                #~ 'state': occupation['state'],
                                                                                                                                #~ 'to_invoice' : False,
                                                                                                                                #~ 'remuneration_id': child_remuneration_id,
                                                                                                                                #~ 'parent_occupation_id': real_id}, context=context),
                                    #~ self.pool.get('account.analytic.occupation').write(cr, uid, [new_id], {
                                        #~ 'end_date': (occupation.get('end_type') == 'end_date') and occupation['end_date'] or False,
                                                                                                                                #~ 'end_type': (occupation.get('end_type') == 'end_date') and 'end_date' or 'forever',
                                    #~ })
#~
                                #~ elif end_date:
                                    #~ if not occupation.get('end_date') or (occupation.get('end_type') and occupation['end_type'] == 'forever'):
                                        #~ self.pool.get('account.analytic.occupation').copy(cr, uid, real_id, default={'date': (datetime.strptime(end_date[:10] + occupation['date'][10:], "%Y-%m-%d %H:%M:%S") + relativedelta(days=+1)).strftime("%Y-%m-%d %H:%M:%S") or False,
                                                                                                                                #~ 'end_type':'forever',
                                                                                                                                #~ 'end_date': False,
                                                                                                                                #~ 'duration': occupation['duration'],
                                                                                                                                #~ 'date_deadline': (datetime.strptime(end_date[:10] + occupation['date'][10:], "%Y-%m-%d %H:%M:%S") + relativedelta(days=+1) + relativedelta(hours=+occupation['duration'])).strftime("%Y-%m-%d %H:%M:%S") or False,
                                                                                                                                #~ 'state': occupation['state'],
                                                                                                                                #~ 'to_invoice' : False,
                                                                                                                                #~ 'remuneration_id': child_remuneration_id,
                                                                                                                                #~ 'parent_occupation_id': real_id}, context=context),
#~
#~
                                #~ if (occupation['date'][:10] + date[10:]) > (datetime.strptime(date, "%Y-%m-%d %H:%M:%S") + relativedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S"):
                                    #~ self.pool.get('account.analytic.occupation').unlink(cr, uid, [real_id], context=context)
                                #~ else:
                                    #~ self.pool.get('account.analytic.occupation').write(cr, uid, real_id, {'remuneration_id': line_remuneration.id, 'end_date': (datetime.strptime(date, "%Y-%m-%d %H:%M:%S") + relativedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S"), 'end_type': 'end_date'})
                            #~ else:
                                #~ self.pool.get('account.analytic.occupation').write(cr, uid, real_id, {'state': 'incidence'})


            # return visited_occupations MIGRACION:


class Incidence(models.Model):

    _inherit = "incidence"


    remuneration_ids = fields.One2many('remuneration', 'incidence_id_tp', 'Remunerations', readonly=True)


class Absence(models.Model):

    _inherit = "absence"

    remuneration_ids = fields.One2many('remuneration', 'absence_id_tp', 'Remunerations', readonly=True)
