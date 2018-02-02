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

"""Wizard to replace employee of selected remunerations"""

from osv import osv, fields
from tools.translate import _
import time
from datetime import datetime
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
class employee_replacement_wzd(osv.osv_memory):
    """Wizard to replace employee of selected remuneratons"""

    _name = "employee.replacement.wzd"

    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Substitute'),
        'conditions': fields.selection([('equal_condition', 'Equal conditions'), ('diff_condition', 'Different conditions')], 'Conditions', required=True),
        'with_contract': fields.boolean('With contract'),
        'contract_hours': fields.float('Hours', digits=(12,2)),
        'with_hour_price': fields.boolean('With hour price'),
        'hour_price_hours': fields.float('Hours', digits=(12,2)),
        'with_fix_qty': fields.boolean('With fix qty'),
        'price': fields.float('Price',digits=(12,2)),
        'quantity': fields.float('Quantity',digits=(12,2)),
        'ss_hours': fields.float('SS hours', digits=(4,2)),
        'ss_no_hours': fields.float('No ss hours', digits=(4,2)),
        'effective': fields.float('Effective', digits=(12,2)),
        'distribute_bt_remuneration': fields.boolean('Distribute between remunerations', help="Distribute quantities between all selected remuneration proportionally to original hours")
    }

    _defaults = {
        'equal_condition': True,
        'price': 0.0,
        'quantity': 0.0,
        'hour_price_hours': 0.0,
        'contract_hours': 0.0,
        'conditions': 'equal_condition'
    }

    def open_search(self, cr, uid, ids, context=None):
        """Opens search repalcements view"""
        if context is None: context = {}


        remuneration_ids = context.get('active_ids', [])
        if remuneration_ids:
            remuneration_obj = self.pool.get('remuneration').browse(cr, uid, remuneration_ids[0])


        result = self.pool.get('ir.model.data')._get_id(cr, uid, 'analytic_incidences', 'action_search_employee_replacement')
        id = self.pool.get('ir.model.data').read(cr, uid, [result], ['res_id'])[0]['res_id']
        result = self.pool.get('ir.actions.act_window').read(cr, uid, [id])[0]

        result['context'] = str({'location': remuneration_ids and remuneration_obj.location_id and remuneration_obj.location_id.id or False,
                                'department': (remuneration_ids and remuneration_obj.department_id) and remuneration_obj.department_id.id or False,
                                'employee_id': (remuneration_ids and remuneration_obj.employee_id) and remuneration_obj.employee_id.id or False
                                })

        result.update({'target': 'new',
                        'nodestroy': True})

        return result

    def action_replace(self, cr, uid, ids, context=None):
        """Replace employee of active occupations by employee in wizard"""
        if context is None: context = {}

        obj = self.browse(cr, uid, ids[0])
        if not obj.employee_id:
            raise osv.except_osv(_('Error!'),_("You must set substitute"))
        remuneration_ids = context.get('active_ids', [])

        if remuneration_ids:
            remuneration_objs = self.pool.get('remuneration').browse(cr, uid, remuneration_ids)
            total_ss_hours = sum([x.ss_hours for x in remuneration_objs])
            total_noss_hours = sum([x.ss_no_hours for x in remuneration_objs])
            total_hours = (total_ss_hours + total_noss_hours)

            for line_remuneration in remuneration_objs:
                if line_remuneration.incidence == False:
                    raise osv.except_osv(_('Error!'), _('You must set remuneration as based of incidence for replacing employee'))

                if obj.conditions != 'equal_condition' and not obj.distribute_bt_remuneration:
                    with_contract = obj.with_contract
                    contract_hours = obj.contract_hours
                    with_hour_price = obj.with_hour_price
                    hour_price_hours = obj.hour_price_hours
                    with_fix_qty = obj.with_fix_qty
                    price = obj.price
                    quantity = obj.quantity
                    ss_hours = obj.ss_hours
                    ss_no_hours = obj.ss_no_hours
                    effective = obj.effective
                elif obj.conditions != 'equal_condition':
                    remu_hours = line_remuneration.ss_no_hours + line_remuneration.ss_hours
                    with_contract = obj.with_contract
                    contract_hours = (obj.contract_hours * remu_hours) / (total_hours or 1.0)
                    with_hour_price = obj.with_hour_price
                    hour_price_hours = (obj.hour_price_hours * remu_hours) / (total_hours or 1.0)
                    with_fix_qty = obj.with_fix_qty
                    price = obj.price
                    quantity = (obj.quantity * remu_hours) / (total_hours or 1.0)
                    ss_hours = (obj.ss_hours * line_remuneration.ss_hours) / (total_ss_hours or 1.0)
                    ss_no_hours = (obj.ss_no_hours * line_remuneration.ss_no_hours) / (total_noss_hours or 1.0)
                    effective = (obj.effective * remu_hours) / (total_hours or 1.0)
                else:
                    with_contract = line_remuneration.with_contract
                    contract_hours = line_remuneration.contract_hours
                    with_hour_price = line_remuneration.with_hour_price
                    hour_price_hours = line_remuneration.hour_price_hours
                    with_fix_qty = line_remuneration.with_fix_qty
                    price = line_remuneration.price
                    quantity = line_remuneration.quantity
                    ss_hours = line_remuneration.ss_hours
                    ss_no_hours = line_remuneration.ss_no_hours
                    effective = line_remuneration.effective

                action_model,type_incidence_id = self.pool.get('ir.model.data').get_object_reference(cr,uid,'analytic_incidences','incidence_replacement')
                child_remuneration_id =  self.pool.get('remuneration').create(cr,uid,{'employee_id': obj.employee_id.id,
                        'date': line_remuneration.date,
                        'analytic_account_id': line_remuneration.analytic_account_id.id,
                        'parent_id': line_remuneration.id,
                        'incidence_id_tp': type_incidence_id,
                        'date_to': line_remuneration.date_to or False,
                        'with_contract' : with_contract,
                        'contract_hours': contract_hours,
                        'with_hour_price': with_hour_price,
                        'hour_price_hours': hour_price_hours,
                        'ss_hours': ss_hours,
                        'ss_no_hours': ss_no_hours,
                        'with_fix_qty': with_fix_qty,
                        'price': price,
                        'quantity': quantity,
                        'effective': effective,
                        'incidence': True,
                        })
                #import ipdb; ipdb.set_trace()
                #~ if line_remuneration.date_to:
                    #~ occupation_ids = self.pool.get('account.analytic.occupation').search(cr, uid, [('state', 'in', ['incidence']), ('date', '<=',  line_remuneration.date_to), ('date', '>=', line_remuneration.date), ('employee_id', '=', line_remuneration.employee_id.id)])
                #~ else:
                    #~ occupation_ids = self.pool.get('account.analytic.occupation').search(cr, uid, [('state', 'in', ['incidence']), ('date', '>=', line_remuneration.date), ('employee_id', '=', line_remuneration.employee_id.id)])
#~
                #~ if occupation_ids:
                    #~ occupation_ids = map(lambda x: base_calendar_id2real_id(x), occupation_ids)
                    #~ occupation_ids = list(set(occupation_ids))
                    #~ visited_occupations = []
                    #~ for occupation_id in self.pool.get('account.analytic.occupation').read(cr, uid, occupation_ids, ['date', 'date_deadline', 'end_date', 'rrule', 'duration', 'state', 'end_type']):
                        #~ real_id = occupation_id['id']
                        #~ if isinstance(real_id, (unicode, str)) and len(real_id.split('-')) > 1:
                            #~ real_id = int(real_id.split('-')[0])
#~
                        #~ if real_id not in visited_occupations:
                            #~ visited_occupations.append(real_id)
#~
                            #~ default_dict = {'date': occupation_id['date'],
                                            #~ 'date_deadline': occupation_id['date_deadline'],
                                            #~ 'duration': occupation_id['duration'],
                                            #~ 'state': 'replacement',
                                            #~ 'incidence_id': False,
                                            #~ 'to_invoice': False,
                                            #~ 'employee_id': obj.employee_id.id}
#~
                            #~ new_id = self.pool.get('account.analytic.occupation').copy(cr, uid, real_id, default=default_dict, context=context)
                            #~ self.pool.get('account.analytic.occupation').write(cr, uid, new_id, {'end_date': occupation_id.get('end_date') and occupation_id['end_date'] or False,})
                            #~ self.pool.get('account.analytic.occupation').write(cr, uid, real_id, {'state': 'replaced','to_invoice': False})


        return {
        'type': 'ir.actions.act_window_close',
        }

employee_replacement_wzd()
