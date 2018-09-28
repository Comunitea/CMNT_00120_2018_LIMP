# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
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


from report import report_sxw
from report.report_sxw import rml_parse
import calendar
from datetime import datetime
import time
from dateutil import rrule
import tools
from tools.translate import _

MONTHS = {
    '1': _("Enero"),
    '2': _("Febrero"),
    '3': _("Marzo"),
    '4': _("Abril"),
    '5': _("Mayo"),
    '6': _("Junio"),
    '7': _("Julio"),
    '8': _('Agosto'),
    '9': _("Septiembre"),
    '10': _("Octubre"),
    '11': _("Noviembre"),
    '12': _("Diciembre")
}

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.amount_total = 0.0
        # self.normal_hours = 0.0
        # self.holidays_hours = 0.0
        # self.sunday_hours = 0.0
        # self.saturday_afternoon_hours = 0.0
        self.contract_line_hours = {}
        self.contract_line_except_hours = {}
        self.contract_line_orig_hours = {}
        self.contract_line_exceptions = {}
        self.contract_line_mediums_days = {}
        self.concept_amounts = {}
        self.mediums = {}
        self.localcontext.update({
            'get_concepts_by_contract':self._get_concepts_by_contract,
            'get_contract_lines':self._get_contract_lines,
            'get_detail':self._get_detail,
            'get_total_details':self._get_total_details,
            'get_date_str': self._get_date_str,
            'get_amount_total': self._get_total_amount,
            'get_month_name': self._get_month_name,
            'get_periods': self._get_periods,
            'get_contract_line_hours': self._get_contract_line_hours,
            'get_contract_line_except_hours': self._get_contract_line_except_hours,
            'get_contract_line_orig_hours': self._get_contract_line_orig_hours,
        })

    def _get_concepts_by_contract(self, contract):
        start_date = datetime(self.localcontext['data']['form']['year'],int(self.localcontext['data']['form']['month']),1).strftime("%Y-%m-%d")
        end_date = datetime(self.localcontext['data']['form']['year'],int(self.localcontext['data']['form']['month']),calendar.monthrange(int(self.localcontext['data']['form']['year']), int(self.localcontext['data']['form']['month']))[1]).strftime("%Y-%m-%d")
        concepts = []
        visted_concepts = []
        for line in contract.home_help_line_ids:
            if line.state in ['open', 'close'] and line.date_start <= end_date and (line.date == False or line.date >= start_date):
                for concept in line.concept_ids:
                    if concept.concept_id.id not in visted_concepts:
                        concepts.append((concept.concept_id, concept.name))
                        visted_concepts.append(concept.concept_id.id)
        for line in contract.cleaning_line_ids:
            if line.state in ['open', 'close'] and line.date_start <= end_date and (line.date == False or line.date >= start_date):
                for concept in line.concept_ids:
                    if concept.concept_id.id not in visted_concepts:
                        concepts.append((concept.concept_id, concept.name))
                        visted_concepts.append(concept.concept_id.id)

        return list(concepts)

    def _get_contract_lines(self, contract, concept):
        start_date = datetime(self.localcontext['data']['form']['year'],int(self.localcontext['data']['form']['month']),1).strftime("%Y-%m-%d")
        end_date = datetime(self.localcontext['data']['form']['year'],int(self.localcontext['data']['form']['month']),calendar.monthrange(int(self.localcontext['data']['form']['year']), int(self.localcontext['data']['form']['month']))[1]).strftime("%Y-%m-%d")
        # self.normal_hours = 0.0
        # self.holidays_hours = 0.0
        # self.sunday_hours = 0.0
        if not self.concept_amounts.get(concept, False):
                self.concept_amounts[concept] = {'NH': {},
                                                 'FH': {},
                                                 'STH': {},
                                                 'SUH': {}}

        # self.saturday_afternoon_hours = 0.0
        lines = []
        analytic_concept_ids = self.pool.get('account.analytic.invoice.concept.rel').search(self.cr, self.uid, [('concept_id', '=', concept.id),('analytic_id', 'child_of', contract.analytic_account_id.id)])
        analytic_ids = [x.analytic_id.id for x in self.pool.get('account.analytic.invoice.concept.rel').browse(self.cr, self.uid, analytic_concept_ids)]
        lines.extend(self.pool.get('limp.contract.line.home.help').browse(self.cr, self.uid, self.pool.get('limp.contract.line.home.help').search(self.cr, self.uid, [('analytic_acc_id', 'in', analytic_ids),('state', 'in', ['open','close']),('date_start', '<=', end_date),'|',('date', '=', False),('date', '>=', start_date)])))
        #lines.extend(self.pool.get('limp.contract.line.cleaning').browse(self.cr, self.uid, self.pool.get('limp.contract.line.cleaning').search(self.cr, self.uid, [('analytic_acc_id', 'in', analytic_ids),('state', 'in', ['open','close']),('date_start', '<=', end_date),'|',('date', '=', False),('date', '>=', start_date)])))
        lines.sort(lambda x,y: cmp((x.customer_contact_id and x.customer_contact_id.name or x.address_id.name) + (x.customer_contact_id and x.customer_contact_id.first_name or x.address_id.first_name),(y.customer_contact_id and y.customer_contact_id.name or y.address_id.name)  + (y.customer_contact_id and y.customer_contact_id.first_name or y.address_id.first_name)))
        return lines

    def _get_contract_line_hours(self, contract_line):
        return self.contract_line_hours.get(contract_line.id, 0.0)

    def _get_contract_line_except_hours(self, contract_line):
        return self.contract_line_hours.get(contract_line.id, 0.0)

    def _get_contract_line_orig_hours(self, contract_line):
        if not contract_line.invoice_limit_hours:
            return self.contract_line_orig_hours.get(contract_line.id, 0.0)
        else:
            return contract_line.invoice_limit_hours

    def _get_detail(self, contract_line, concept, start_date, occupations_ids):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime(self.localcontext['data']['form']['year'],int(self.localcontext['data']['form']['month']),calendar.monthrange(int(self.localcontext['data']['form']['year']), int(self.localcontext['data']['form']['month']))[1])
        res = []
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        contract_line = self.pool.get('limp.contract.line.home.help').browse(self.cr, self.uid, contract_line.id)
        line_concept = self.pool.get('account.analytic.invoice.concept.rel').search(self.cr, self.uid, [('concept_id', '=', concept.id),('analytic_id', '=', contract_line.analytic_acc_id.id)])
        if line_concept:
            line_concept = self.pool.get('account.analytic.invoice.concept.rel').browse(self.cr, self.uid, line_concept[0])

            normal_amount = line_concept.amount
            saturday_afternoon_amount = line_concept.saturday_afternoon_amount and line_concept.saturday_afternoon_amount or 0.0
            holiday_amount = line_concept.holyday_amount and line_concept.holyday_amount or 0.0
            sunday_amount = line_concept.sunday_amount and line_concept.sunday_amount or float(holiday_amount)
            if not self.concept_amounts[concept]['NH'].get(str(normal_amount)):
                self.concept_amounts[concept]['NH'][str(normal_amount)] = 0.0
            if saturday_afternoon_amount and not self.concept_amounts[concept]['STH'].get(str(saturday_afternoon_amount)):
                self.concept_amounts[concept]['STH'][str(saturday_afternoon_amount)] = 0.0
            if holiday_amount and not self.concept_amounts[concept]['FH'].get(str(holiday_amount)):
                self.concept_amounts[concept]['FH'][str(holiday_amount)] = 0.0
            if sunday_amount and not self.concept_amounts[concept]['SUH'].get(str(sunday_amount)):
                self.concept_amounts[concept]['SUH'][str(sunday_amount)] = 0.0

            WEEKEND_RULE = "FREQ=WEEKLY;BYDAY=SU;INTERVAL=1;UNTIL=" + end_date.strftime("%Y%m%dT%H%M%S")
            exceptions = []
            if line_concept._get_except_months()[line_concept.id]:
                EXCEPT_MONTHS_RULE = "FREQ=DAILY;BYMONTH=" + ",".join([str(x) for x in line_concept._get_except_months()[line_concept.id]]) + ";INTERVAL=1;UNTIL=" + end_date.strftime("%Y%m%dT%H%M%S")
                rset2 = rrule.rrulestr(EXCEPT_MONTHS_RULE, dtstart=start_date, forceset=True)
                exceptions = map(lambda x:x.strftime('%Y-%m-%d'), rset2._iter())

            rset1 = rrule.rrulestr(WEEKEND_RULE, dtstart=start_date, forceset=True) #search weekend date in the period
            weekends = map(lambda x:x.strftime('%Y-%m-%d'), rset1._iter())

            MONDAY_RULE = "FREQ=WEEKLY;BYDAY=MO;INTERVAL=1;UNTIL=" + end_date.strftime("%Y%m%dT%H%M%S")
            rset1 = rrule.rrulestr(MONDAY_RULE, dtstart=start_date, forceset=True)
            mondays = map(lambda x:x.strftime('%Y-%m-%d'), rset1._iter())

            TUESDAY_RULE = "FREQ=WEEKLY;BYDAY=TU;INTERVAL=1;UNTIL=" + end_date.strftime("%Y%m%dT%H%M%S")
            rset1 = rrule.rrulestr(TUESDAY_RULE, dtstart=start_date, forceset=True)
            tuesdays = map(lambda x:x.strftime('%Y-%m-%d'), rset1._iter())

            WEDNESDAY_RULE = "FREQ=WEEKLY;BYDAY=WE;INTERVAL=1;UNTIL=" + end_date.strftime("%Y%m%dT%H%M%S")
            rset1 = rrule.rrulestr(WEDNESDAY_RULE, dtstart=start_date, forceset=True)
            wednesdays = map(lambda x:x.strftime('%Y-%m-%d'), rset1._iter())

            THURDAY_RULE = "FREQ=WEEKLY;BYDAY=TH;INTERVAL=1;UNTIL=" + end_date.strftime("%Y%m%dT%H%M%S")
            rset1 = rrule.rrulestr(THURDAY_RULE, dtstart=start_date, forceset=True)
            thursdays = map(lambda x:x.strftime('%Y-%m-%d'), rset1._iter())

            FRIDAY_RULE = "FREQ=WEEKLY;BYDAY=FR;INTERVAL=1;UNTIL=" + end_date.strftime("%Y%m%dT%H%M%S")
            rset1 = rrule.rrulestr(FRIDAY_RULE, dtstart=start_date, forceset=True)
            fridays = map(lambda x:x.strftime('%Y-%m-%d'), rset1._iter())

            SATURDAY_RULE = "FREQ=WEEKLY;BYDAY=SA;INTERVAL=1;UNTIL=" + end_date.strftime("%Y%m%dT%H%M%S")
            rset1 = rrule.rrulestr(SATURDAY_RULE, dtstart=start_date, forceset=True)
            saturdays = map(lambda x:x.strftime('%Y-%m-%d'), rset1._iter())

            duration = 0.0
            holiday_duration = 0.0
            sunday_duration = 0.0
            saturday_afternoon_duration = 0.0
            except_duration = 0.0
            orig_duration = 0.0
            total_hours = 0.0
            diff_exceptions = 0.0
            concepts = {}
            visited_days = []
            medium_day_duration = 0.0
            holidays = []


            exc_days = []
            #occupations_ids = self.pool.get('account.analytic.occupation').search(self.cr, self.uid, [('analytic_account_id', '=', contract_line.analytic_acc_id.id), ('date', '>=', start_date.strftime("%Y-%m-%d")), ('date', '<=', end_date.strftime("%Y-%m-%d")), ('state', 'in', ['active', 'replacement'])])
            if occupations_ids:
                occupation = self.pool.get('account.analytic.occupation').read(self.cr, self.uid, occupations_ids[0], ['employee_id', 'date', 'location_id', 'state_id', 'region_id'])
                tmp_start_date = start_date.strftime("%Y-%m-%d")
                tmp_end_date = end_date.strftime("%Y-%m-%d")
                for holiday in self.pool.get('hr.holiday').get_holidays_dates(self.cr, self.uid, [occupation['employee_id'][0]], occupation.get('location_id', False) and occupation['location_id'][0] or False, occupation.get('state_id', False) and occupation['state_id'][0] or False, occupation.get('region_id', False) and occupation['region_id'][0] or False)[occupation['employee_id'][0]]:
                    if holiday >= tmp_start_date and holiday <= tmp_end_date:
                        holidays.append(holiday)
            for occupation in self.pool.get('account.analytic.occupation').read(self.cr, self.uid, occupations_ids, ['employee_id', 'date', 'location_id', 'state_id', 'region_id', 'mo', 'tu', 'we', 'th', 'fr', 'sa', 'su', 'rrule_type', 'parent_occupation_id', 'duration', 'to_invoice', 'recurrency', 'value_diff']):

                oc_medium_day = []
                occupation_date = occupation['date'][:10]
                hours, minutes, seconds = occupation['date'][11:].split(":")
                occupation_hour = int(hours) + (((int(minutes) * 60.0 + int(seconds)) / 60.0) / 60.0)
                #holidays = self.pool.get('hr.holiday').get_holidays_dates(self.cr, self.uid, [occupation['employee_id'][0]], occupation.get('location_id', False) and occupation['location_id'][0] or False, occupation.get('state_id', False) and occupation['state_id'][0] or False, occupation.get('region_id', False) and occupation['region_id'][0] or False)[occupation['employee_id'][0]]
                if occupation_date >= start_date.strftime("%Y-%m-%d") and occupation_date <= end_date.strftime("%Y-%m-%d") and occupation_date not in exceptions:
                    #check if it's holiday, checkingh if it's weekend or it's in employee holiday calendars
                    valid = False
                    occupation_duration = self.pool.get('account.analytic.occupation').get_duration_to_invoice(self.cr, self.uid, occupation['id'])
                    dateocu = occupation['date'][:10]
                    dateocustart = dateocu + ' 00:00:00'
                    dateocustop = dateocu + ' 23:59:59'
                    oc_medium_day = []
                    if occupation['recurrency'] == True:
                        oc_medium_day = self.pool.get('account.analytic.occupation').search(self.cr, self.uid, [('id','in', [x.id for x in contract_line.occupation_ids]), ('date','>=',dateocustart), ('date','<=',dateocustop), ('recurrency', '=', False)])
                        if oc_medium_day:
                            if not self.contract_line_mediums_days.get(contract_line.id, False):
                                self.contract_line_mediums_days[contract_line.id] = set()
                            if occupation['id'] not in list(self.contract_line_mediums_days[contract_line.id]):
                                oc_medium_day = [oc_medium_day[0]]
                                for d in oc_medium_day:
                                    self.contract_line_mediums_days[contract_line.id].add(d)
                                    if not self.mediums.get(d):
                                        self.mediums[d] = occupation['duration']
                                    else:
                                        self.mediums[d] += occupation['duration']
                                    #self.pool.get('account.analytic.occupation').write(self.cr, self.uid, d, {'value_diff': occupation['duration']})

                                self.contract_line_mediums_days[contract_line.id].add(occupation['id'])
                                #exc_days.append(tools.ustr(dateocu) + u" 1 Día * " + tools.ustr(occupation_duration) + u" Hrs" )

                    if occupation_date in weekends:
                        name = occupation_duration and u"GDomingos" or u"GDomingos (NF)"
                        if sunday_amount:
                            if occupation_duration:
                                sunday_duration += occupation_duration
                                total_hours += occupation_duration
                            valid = True
                    elif occupation_date in holidays:
                        name = occupation_duration and u"HFestivos" or u"HFestivos (NF)"
                        if holiday_amount:
                            if occupation_duration:
                                holiday_duration += occupation_duration
                                total_hours += occupation_duration
                            valid = True
                    elif occupation_date in mondays:
                        name = occupation_duration and u"ALunes" or u"ALunes (NF)"
                        if occupation_duration:
                            duration += occupation_duration
                            total_hours += occupation_duration

                        valid = True
                    elif occupation_date in tuesdays:
                        name = occupation_duration and u"BMartes" or u"BMartes (NF)"
                        if occupation_duration:
                            duration += occupation_duration
                            total_hours += occupation_duration
                        valid = True
                    elif occupation_date in wednesdays:
                        name = occupation_duration and u"CMiércoles" or u"CMiércoles (NF)"
                        if occupation_duration:
                            duration += occupation_duration
                            total_hours += occupation_duration
                        valid = True
                    elif occupation_date in thursdays:
                        name = occupation_duration and u"DJueves" or u"DJueves (NF)"
                        if occupation_duration:
                            duration += occupation_duration
                            total_hours += occupation_duration
                        valid = True
                    elif occupation_date in fridays:
                        name = occupation_duration and u"EViernes" or u"EViernes (NF)"
                        if occupation_duration:
                            duration += occupation_duration
                            total_hours += occupation_duration
                        valid = True
                    elif occupation_date in saturdays:
                        name = occupation_duration and u"FSábados" or u"FSábados (NF)"
                        if occupation_duration:
                            if occupation_hour >= user.company_id.afternoon_time and saturday_afternoon_amount:
                                saturday_afternoon_duration += occupation_duration
                            else:
                                duration += occupation_duration
                            total_hours += occupation_duration
                        valid = True

                    if occupation.get('parent_occupation_id', False):
                        parent_occupation = self.pool.get('account.analytic.occupation').browse(self.cr, self.uid, occupation['parent_occupation_id'][0])
                        if occupation.get('to_invoice', False):
                            diff_exceptions += (parent_occupation.duration - occupation['duration'])
                        if parent_occupation.rrule_type == 'monthly':
                            except_duration += occupation['duration']
                            orig_duration += parent_occupation.duration
                    else:
                        parent_occupation = False

                    if not parent_occupation and occupation_duration and occupation['rrule_type'] == 'monthly':
                        except_duration += occupation_duration
                        orig_duration += occupation_duration

                    if contract_line.invoice_limit_hours and not contract_line.invoice_by_high and ((contract_line.invoice_limit_hours - diff_exceptions) < total_hours):
                        rest = total_hours - (contract_line.invoice_limit_hours - diff_exceptions)
                        if occupation_date in weekends and sunday_amount:
                            sunday_duration -= rest
                            total_hours -= rest
                        elif occupation_date in holidays and holiday_amount:
                            holiday_duration -= rest
                            total_hours -= rest
                        elif occupation_date in saturdays and saturday_afternoon_amount and saturday_afternoon_duration >= user.company_id.afternoon_time:
                            saturday_afternoon_duration -= rest
                            total_hours -= rest
                        elif occupation_date not in weekends and occupation_date not in holidays:
                            duration -= rest
                            total_hours -= rest

                    if valid and occupation['rrule_type'] != 'monthly' and not contract_line.invoice_limit_hours and (not parent_occupation or parent_occupation.rrule_type != 'monthly'):

                        if name and not oc_medium_day:
                            if concepts.get(name, False):
                                if occupation['id'] in self.mediums:
                                    concepts[name][0] += (occupation_duration or occupation['duration']) + self.mediums[occupation['id']]
                                    del self.mediums[occupation['id']]
                                else:
                                    concepts[name][0] += (occupation_duration or occupation['duration'])
                                if occupation_date not in visited_days:
                                    concepts[name][1] += 1
                                    visited_days.append(occupation_date)
                            else:
                                if occupation['id'] in self.mediums:
                                    concepts[name] = [(occupation_duration or occupation['duration']) + self.mediums[occupation['id']], 1]
                                    del self.mediums[occupation['id']]
                                else:
                                    concepts[name] = [(occupation_duration or occupation['duration']), 1]
                                visited_days.append(occupation_date)

            if contract_line.invoice_limit_hours and contract_line.invoice_by_high:
                hours_limit = contract_line.invoice_limit_hours - diff_exceptions
                if total_hours > hours_limit:
                    to_remove_hours = total_hours - hours_limit
                    if duration >= to_remove_hours:
                        duration -= to_remove_hours
                    else:
                        to_remove_hours -= duration
                        duration = 0.0
                        if saturday_afternoon_duration >= to_remove_hours:
                            saturday_afternoon_duration -= to_remove_hours
                        else:
                            to_remove_hours -= saturday_afternoon_duration
                            saturday_afternoon_duration = 0.0
                            if sunday_duration >= to_remove_hours:
                                sunday_duration -= to_remove_hours
                            else:
                                to_remove_hours -= sunday_duration
                                sunday_duration = 0.0
                                if holiday_duration >= to_remove_hours:
                                    holiday_duration -= to_remove_hours
                                else:
                                    holiday_duration = 0.0
                                    duration = 0.0
                                    saturday_afternoon_duration = 0.0
                                    sunday_duration = 0.0

            invoice_limit_hours = contract_line.invoice_limit_hours - diff_exceptions
            if contract_line.invoice_limit_hours and invoice_limit_hours > total_hours:
                suma = invoice_limit_hours - total_hours
                duration += suma

            for sconcept in sorted(concepts.iterkeys()):
                res.append((sconcept[1:], tools.ustr(concepts[sconcept][1]) + u" Días * " + tools.ustr(round(concepts[sconcept][0] / concepts[sconcept][1], 2)) + u" Hrs / Día = " + tools.ustr(round(concepts[sconcept][0], 2)) + " Hrs"))

            #~ if exc_days:
                #~ for x in exc_days:
                    #~ res.append((u"Excepción: ", x))
            # self.normal_hours += round(duration, 2)
            if normal_amount:
                self.concept_amounts[concept]['NH'][str(normal_amount)] += duration
            # self.sunday_hours += round(sunday_duration, 2)
            if sunday_amount:
                self.concept_amounts[concept]['SUH'][str(sunday_amount)] += sunday_duration
            # self.holidays_hours += round(holiday_duration, 2)
            if holiday_amount:
                self.concept_amounts[concept]['FH'][str(holiday_amount)] += holiday_duration
            # self.saturday_afternoon_hours += round(saturday_afternoon_duration, 2)
            if saturday_afternoon_amount:
                self.concept_amounts[concept]['STH'][str(saturday_afternoon_amount)] += saturday_afternoon_duration
            if self.contract_line_hours.get(contract_line.id, False):
                self.contract_line_hours[contract_line.id] += (duration + sunday_duration + holiday_duration + saturday_afternoon_duration)
            else:
                self.contract_line_hours[contract_line.id] = duration + sunday_duration + holiday_duration + saturday_afternoon_duration

            if self.contract_line_except_hours.get(contract_line.id, False):
                self.contract_line_except_hours[contract_line.id] += except_duration
            else:
                self.contract_line_except_hours[contract_line.id] = except_duration

            if self.contract_line_orig_hours.get(contract_line.id, False):
                self.contract_line_orig_hours[contract_line.id] += orig_duration
            else:
                self.contract_line_orig_hours[contract_line.id] = orig_duration

            if self.contract_line_exceptions.get(contract_line.id, False):
                self.contract_line_exceptions[contract_line.id] += diff_exceptions
            else:
                self.contract_line_exceptions[contract_line.id] = diff_exceptions
        return res


    def _get_total_details(self, concept, contract):
        res = []
        dic = {}
        total = 0.0
        for key in self.concept_amounts[concept]:
            for amount in self.concept_amounts[concept][key]:
                if self.concept_amounts[concept][key][amount]:
                    if key == "NH":
                        res.append((u"Días Laborales", tools.ustr(self.concept_amounts[concept][key][amount]) + u" HRS * " + amount + u" € / H = " + tools.ustr(round(self.concept_amounts[concept][key][amount] * float(amount),2)) + u" + I.V.A"))
                    elif key == "STH":
                        res.append((u"Sábados Tarde", tools.ustr(self.concept_amounts[concept][key][amount]) + u" HRS * " + amount + u" € / H = " + tools.ustr(round(self.concept_amounts[concept][key][amount] * float(amount),2)) + u" + I.V.A"))
                    elif key == "SUH":
                        res.append((u"Domingos", tools.ustr(self.concept_amounts[concept][key][amount]) + u" HRS * " + amount + u" € / H = " + tools.ustr(round(self.concept_amounts[concept][key][amount] * float(amount),2)) + u" + I.V.A"))
                    elif key == "FH":
                        res.append((u"Festivos", tools.ustr(self.concept_amounts[concept][key][amount]) + u" HRS * " + amount + u" € / H = " + tools.ustr(round(self.concept_amounts[concept][key][amount] * float(amount),2)) + u" + I.V.A"))
                    total += round(self.concept_amounts[concept][key][amount] * float(amount),2)

        #~ line_concept = self.pool.get('account.analytic.invoice.concept.rel').search(self.cr, self.uid, [('concept_id', '=', concept.id),('analytic_id', 'child_of', contract.analytic_account_id.id)])
        #~ if line_concept:
            #~ line_concept = self.pool.get('account.analytic.invoice.concept.rel').browse(self.cr, self.uid, line_concept[0])
            #~ res.append((u"Días Laborales", tools.ustr(self.normal_hours) + u" HRS * " + tools.ustr(line_concept.amount) + u" € / H = " + tools.ustr(round(self.normal_hours * line_concept.amount,2)) + u" + I.V.A"))
            #~ total += self.normal_hours * line_concept.amount
#~
            #~ sunday_concept_ids = self.pool.get('account.analytic.invoice.concept.rel').search(self.cr, self.uid, [('analytic_id', 'child_of' , contract.analytic_account_id.id), ('concept_id', '=', concept.id),
                                    #~ ('sunday_amount','!=',0.0)])
            #~ if not sunday_concept_ids:
                #~ sunday_concept_ids = self.pool.get('account.analytic.invoice.concept.rel').search(self.cr, self.uid, [('analytic_id', 'child_of', contract.analytic_account_id.id), ('concept_id', '=', concept.id),
                                    #~ ('holyday_amount', '!=', 0.0)])
            #~ if self.sunday_hours and sunday_concept_ids:
                #~ line_concept = self.pool.get('account.analytic.invoice.concept.rel').browse(self.cr, self.uid, sunday_concept_ids[0])
                #~ res.append((u"Domingos", tools.ustr(self.sunday_hours) + u" HRS * " + tools.ustr((line_concept.sunday_amount or line_concept.holyday_amount)) + u" € / H = " + tools.ustr(round(self.sunday_hours * (line_concept.sunday_amount or line_concept.holyday_amount),2)) + u" + I.V.A"))
                #~ total += self.sunday_hours * (line_concept.sunday_amount or line_concept.holyday_amount)
#~
            #~ holiday_concept_ids = self.pool.get('account.analytic.invoice.concept.rel').search(self.cr, self.uid, [('analytic_id', 'child_of' , contract.analytic_account_id.id), ('concept_id', '=', concept.id),
                                    #~ ('holyday_amount', '!=', 0.0)])
            #~ if self.holidays_hours and holiday_concept_ids:
                #~ line_concept = self.pool.get('account.analytic.invoice.concept.rel').browse(self.cr, self.uid, holiday_concept_ids[0])
                #~ res.append((u"Festivos", tools.ustr(self.holidays_hours) + u" HRS * " + tools.ustr(line_concept.holyday_amount) + u" € / H = " + tools.ustr(round(self.holidays_hours * line_concept.holyday_amount,2)) + u" + I.V.A"))
                #~ total += self.holidays_hours * line_concept.holyday_amount
#~
            #~ saturday_afternoon_concept_ids = self.pool.get('account.analytic.invoice.concept.rel').search(self.cr, self.uid, [('analytic_id', 'child_of' , contract.analytic_account_id.id), ('concept_id', '=', concept.id),
                                    #~ ('saturday_afternoon_amount', '!=', 0.0)])
            #~ if self.saturday_afternoon_hours:
                #~ line_concept = self.pool.get('account.analytic.invoice.concept.rel').browse(self.cr, self.uid, saturday_afternoon_concept_ids[0])
                #~ res.append((u"Sábados Tarde", tools.ustr(self.saturday_afternoon_hours) + u" HRS * " + tools.ustr((line_concept.saturday_afternoon_amount or line_concept.amount)) + u" € / H = " + tools.ustr(round(self.saturday_afternoon_hours * (line_concept.saturday_afternoon_amount or line_concept.amount),2)) + u" + I.V.A"))
                #~ total += self.saturday_afternoon_hours * (line_concept.saturday_afternoon_amount or line_concept.amount)

        taxes = self.pool.get('account.tax').compute_all(self.cr, self.uid, concept.product_id.taxes_id, total, 1)

        self.amount_total = round(taxes['total_included'],2)

        return res

    def _get_total_amount(self):
        return self.amount_total

    def _get_date_str(self):
        return self._get_month_name() + u" - " + tools.ustr(str(self.localcontext['data']['form']['year'])[2:])

    def _get_month_name(self):
        return MONTHS[self.localcontext['data']['form']['month']]

    def _get_periods(self, contract_line):
        def_start_date = datetime(self.localcontext['data']['form']['year'],int(self.localcontext['data']['form']['month']),1).strftime("%Y-%m-%d")
        def_end_date = datetime(self.localcontext['data']['form']['year'],int(self.localcontext['data']['form']['month']),calendar.monthrange(int(self.localcontext['data']['form']['year']), int(self.localcontext['data']['form']['month']))[1]).strftime("%Y-%m-%d")
        preres = {}
        contract_line = self.pool.get('limp.contract.line.home.help').browse(self.cr, self.uid, contract_line.id)
        for occupation in contract_line.occupation_ids:
            if occupation.state in ['active', 'replacement'] and (not occupation.end_date or occupation.end_date >= def_start_date) and occupation.date[:10] <= def_end_date and occupation.rrule_type != 'monthly' and (not occupation.parent_occupation_id or occupation.parent_occupation_id.rrule_type != 'monthly') and not contract_line.invoice_limit_hours:
                occupations_ids = self.pool.get('account.analytic.occupation').search(self.cr, self.uid, [('id', '=', occupation.id), ('date', '>=', def_start_date), ('date', '<=', def_end_date)])
                start_date = occupation.date[:10] > def_start_date and occupation.date[:10] or def_start_date
                end_date = (occupation.end_date and occupation.end_date < def_end_date) and occupation.end_date or (not occupation.recurrency and occupation.date_deadline[:10] or def_end_date)
                period_str = start_date + "#" + end_date
                if preres.get(period_str):
                    preres[period_str].extend(occupations_ids)
                else:
                    preres[period_str] = occupations_ids
            elif occupation.state in ['active', 'replacement'] and (not occupation.end_date or occupation.end_date >= def_start_date) and occupation.date[:10] <= def_end_date:
                occupations_ids = self.pool.get('account.analytic.occupation').search(self.cr, self.uid, [('id', '=', occupation.id), ('date', '>=', def_start_date), ('date', '<=', def_end_date)])
                if occupations_ids:
                    period_str = def_start_date + "#" + def_end_date
                    if preres.get(period_str):
                        preres[period_str].extend(occupations_ids)
                    else:
                        preres[period_str] = occupations_ids
        res = []
        for result in preres:
            if preres[result]:
                start_date, end_date = result.split("#")
                res.append((start_date[8:10] + u" al " + end_date[8:10] + u" " + self._get_month_name(), start_date, preres[result]))

        #res.sort(lambda x,y: cmp(int(x[0][6:8]),int(y[0][6:8])) )
        res = sorted(res, key = lambda x : (-len(x[2]), int(x[0][6:8])))
        return res

