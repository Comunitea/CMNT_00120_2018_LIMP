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

import base64
import datetime
from odoo import models, fields
import xlrd
import StringIO
import calendar
import time
from openerp.tools import ustr

def string_format(value):
    if isinstance(value, float):
        value = str(int(value))
    else:
        str(value)

    return value

def float_format(value):
    if isinstance(value, (str, unicode)):
        value = float(value.replace(',','.'))
    else:
        value = float(value)

    return value

class DistributionCostsImport(models.TransientModel):

    _name = "distribution.costs.import"

    name = fields.Char('Name',size=64,required=True)
    month = fields.Selection([
        ('1','January'), ('2','February'),
        ('3','March'), ('4','April'),
        ('5','May'), ('6','June'),
        ('7','July'), ('8','August'),
        ('9','September'), ('10','October'),
        ('11','November'), ('12','December')],'Month')
    file = fields.Binary('File',required=True)
    year = fields.Integer('Year', required=True, default=lambda r: int(time.strftime("%Y")))

    def import_distribution_costs(self):
        obj = self
        year = str(obj.year)
        month = ''
        file = base64.b64decode(obj.file)
        data = xlrd.open_workbook(file_contents=StringIO.StringIO(file).read(), encoding_override="utf-8")
        sh = data.sheet_by_index(0)
        cost_fixed = 0 #suma de precios fijos
        cost_price_hour = 0 # suma de horas con precio hora
        cost_contract = 0 #suma de coste c on contrato
        cost_contract_ss = 0 #suma de coste seguriodad social

        record = {}
        weeks = 4.416666667 # 53/12
        dates = []
        timesheets = []

        remuneration_obj = self.env['remuneration']

        journal_id = self.env['account.analytic.tag'].search([('name', '=', 'Timesheet Journal')])
        social_journal_id = self.env['account.analytic.tag'].search([('name', '=', 'Seguridad Social')])
        sueldos_journal_id = self.env['account.analytic.tag'].search([('name', '=', 'Sueldos')])
        general_account_id_ss = self.env['account.account'].search([('code','=',"64200000")])
        general_account_id_suelsala = self.env['account.account'].search([('code','=',"64000000")])
        visited_rows = []
        for line in range(1, sh.nrows): #nos recorremos el fichero
            row = sh.row_values(line)

            if row[3] and len(row[3]) == 7 and row[8] and row[3] not in visited_rows:
                visited_rows.append(row[3])
                contracts = {}
                with_contract = 0 #coste con contrato total
                ss_total = 0 # total importe seguridad social
                #with_ss_contract = 0 # total horas seguridad social en contratos
                #ss_total_timesheet = 0 # total horas ss en partes
                ss_total_hours = 0 # total horas seguridad social
                #with_contract_timesheet = 0 #horas de los parte de trabajo
                #with_contract_contract = 0 #horas de contratos
                fixed = 0 #costes fijos
                with_price_hour = 0 #coste con precio hora
                n = 1
                record = {
                    'ref_employee': row[3] and string_format(row[3]) or row[3],
                    'month': row[8] and string_format(row[8]) or row[8],
                    'ss_company': row[10] and float_format(row[10]) or 0.0, #total seguridad social
                    'total_accrued': row[12] and float_format(row[12]) or 0.0, #total bruto
                    'ss_injury_benefit': row[14] and float_format(row[14]) or 0.0, # total seguridad social accidente
                    'ss_sickness_benefit': row[16] and float_format(row[16]) or 0.0, # total seguridad social enferemedad
                    }


                while (sh.row_values(line+n))[3] == "" or (sh.row_values(line+n))[3] == row[3]:
                    ### MARTA (30.09.2014 11:49): Añadido 'or' debido a que si había dos registros con el código del mismo trabajador antes de crear el segundo apunte eliminaba el primero. ###
                    if (sh.row_values(line+n))[10]:
                        record['ss_company'] += float_format((sh.row_values(line+n))[10])
                    if (sh.row_values(line+n))[12]:
                        record['total_accrued'] += float_format((sh.row_values(line+n))[12])
                    if (sh.row_values(line+n))[14]:
                        record['ss_injury_benefit'] += float_format((sh.row_values(line+n))[14])
                    if (sh.row_values(line+n))[16]:
                        record['ss_sickness_benefit'] += float_format((sh.row_values(line+n))[16])
                    n = n + 1

                if not month:
                    if len(record['month']) == 1:
                        month = "0"+record['month']
                    else:
                        month = record['month']
                ss_total = 0
                if record['ss_company']:# coste seguridad social
                    ss_total += record['ss_company']
                if record['ss_injury_benefit']:
                    ss_total -= record['ss_injury_benefit'] # le restamos la seguridad social por accidente
                if record['ss_sickness_benefit']:
                    ss_total -= record['ss_sickness_benefit'] # le resptamos la seguridad social por enfermedad

                if record['month'] and obj.month == record['month'] and year:
                    first_day, last_day = calendar.monthrange(int(year),int(month))
                    id=self.env['hr.employee'].search([('glasof_code','=',record['ref_employee'])]) #buscamos al empleado
                    if id:
                        hr_employee_obj = id[0]

                        first_day, last_day = calendar.monthrange(int(year),int(month)) #obtenemos el último días del mes
                        #obtenemos las remuneraciones del empleado dentro del mes importado
                        remunerations = remuneration_obj.search([('employee_id','=', hr_employee_obj.id),'|',('date_to','>=',year+"-"+month+"-01"),('date_to','=',False),('date','<=',year+"-"+month+"-"+str(last_day)),'|',('parent_id', '=', False),('parent_id.employee_id','!=',hr_employee_obj.id)])
                        #obtenemos los parte de horas del empleado dentro del mes importado
                        timesheets = self.env['timesheet'].search([('employee_id','=', hr_employee_obj.id),('date','>=',year+"-"+month+"-01"),('date','<=',year+"-"+month+"-"+str(last_day)),('done','=',True)])
                        config = {}
                        if remunerations:
                            #nos recorremos las remuneraciones rellenando un diccionario con la forma {'cuenta analítica': [lista de remuneraciones]}
                            for remun_obj in remunerations:
                                remuneration_periods = remun_obj.get_periods_remuneration(year+"-"+month+"-01", year+"-"+month+"-"+str(last_day))
                                for period in remuneration_periods:
                                    start_date, end_date = period.split('#')
                                    for remu in remuneration_obj.browse(remuneration_periods[period]):
                                        code = ""
                                        if remu.analytic_account_id:
                                            code = str(remu.analytic_account_id.id)
                                        elif remu.analytic_distribution_id:
                                            code = "D" + str(remu.analytic_distribution_id.id)
                                        else:
                                            continue

                                        start_datetime = datetime.datetime.strptime((start_date + ' 00:00:00'),"%Y-%m-%d %H:%M:%S")
                                        end_datetime = datetime.datetime.strptime((end_date + ' 00:00:00'),"%Y-%m-%d %H:%M:%S")
                                        days = (end_datetime - start_datetime).days
                                        days_diff = 0
                                        #calculamos el número de días en el periodo
                                        if end_date[8:10] == str(last_day):
                                            days_diff = 30 - int(end_date[8:10]) + 1
                                        else:
                                            days_diff = 1
                                        days += days_diff

                                        # cargamos la información en un diccionario del tipo {'id_remuneracion': {'id_cuenta-fixed': total_fijo, 'id_cuenta-efectivo': total_efectivo,
                                        # 'id_cuenta-with-contract': total_dias, 'id_cuenta-with_price_hour': total_con_precio_hora}
                                        if not config.get(str(remu.id)):
                                            config[str(remu.id)] = {}
                                        # si tiene cantidad fija
                                        if remu.with_fix_qty:
                                            fixed_old = (remu.quantity*days)/30 # proporción correspondiente a lso días en el periodo ej. (100*5)/30
                                            fixed += fixed_old # sumamos el fijo de esta remuneración al fijo total
                                            if not config[str(remu.id)].get(str(code)+'-fixed'):
                                                config[str(remu.id)].update({str(code)+'-fixed': fixed_old})
                                            else:
                                                config[str(remu.id)][str(code)+'-fixed'] += fixed_old

                                        if remu.with_contract:
                                            rule3 = (weeks * days)/30.0 # proporción de días en el periodo
                                            with_contact_old = remu.contract_hours * rule3
                                            with_contract += with_contact_old # sumamos la proporción de días de la remuneración al total con contrato
                                            #with_contract_contract += with_contact_old # sumamos la proporción de días de la remuneración al total con contrato y precio hora
                                            if not config[str(remu.id)].get(str(code)+'-with_contract'):
                                                config[str(remu.id)].update({str(code)+'-with_contract': with_contact_old})
                                            else:
                                                config[str(remu.id)][str(code)+'-with_contract'] += with_contact_old

                                            rule3 = (weeks * days)/30.0
                                            with_contract_ss_old = remu.ss_hours * rule3 # proporción de horas de seguridad social en el periodo
                                            ss_total_hours += with_contract_ss_old #sumamos las horas al total horas con seguridad social
                                            #with_ss_contract += with_contract_ss_old # sumamos la proporción de días de la remuneración al total con contrato y precio hora
                                            if not config[str(remu.id)].get(str(code)+'-with_ss_contract'):
                                                config[str(remu.id)].update({str(code)+'-with_ss_contract': with_contract_ss_old})
                                            else:
                                                config[str(remu.id)][str(code)+'-with_ss_contract'] += with_contract_ss_old

                                        if remu.with_hour_price:
                                            rule3 = (weeks * days)/30.0
                                            with_price_hour_old = remu.price * (remu.hour_price_hours * rule3) #precio_hora por proporción del total de horas de la remuneración
                                            with_price_hour += with_price_hour_old
                                            if not config[str(remu.id)].get(str(code)+'-with_price_hour'):
                                                config[str(remu.id)].update({str(code)+'-with_price_hour': with_price_hour_old})
                                            else:
                                                config[str(remu.id)][str(code)+'-with_price_hour'] += with_price_hour_old

                        if timesheets:
                            #nos recorremos los partes de horas y seguimos añadienod al mismo diccionario datos con la forma {'id_parte+t' {'id_cuenta-fixed': total fijo, 'id_cuenta-effective': total_efectivo, 'id_cuenta-with_contract': total horas contrato}
                            for obj_time in timesheets:
                                if obj_time.analytic_id:
                                    config[str(obj_time.id)+"t"] = {}
                                    #si hay cantidad fija, la sumamos a la cantidad fija total
                                    if obj_time.fix_qty:
                                        fixed += obj_time.fix_qty
                                        config[str(obj_time.id)+"t"].update({str(obj_time.analytic_id.id)+'-fixed': obj_time.fix_qty})
                                    if obj_time.contract:
                                        with_contract += obj_time.hours # sumamos a las horas totales las horas con contrato en el parte de horas
                                        #with_contract_timesheet += obj_time.hours # sumamos a las horas en parte las horas con contrato del parte
                                        config[str(obj_time.id)+"t"].update({str(obj_time.analytic_id.id)+"-with_contract": obj_time.hours})
                                    if obj_time.ss_hours:
                                        ss_total_hours += obj_time.ss_hours #sumamos las horas al total horas con seguridad social
                                        #ss_total_timesheet += obj_time.ss_hours
                                        config[str(obj_time.id)+"t"].update({str(obj_time.analytic_id.id)+"-with_ss_contract": obj_time.ss_hours})

                        if journal_id and general_account_id_ss and general_account_id_suelsala and config and (fixed or with_contract or with_price_hour):
                            for remuneration in config:
                                if remuneration.isdigit(): # si es una remuneración
                                    for configuration in config[remuneration]:

                                        type = (configuration.split("-"))[1] # tipo del importe
                                        code = (configuration.split("-"))[0]
                                        analytic_objs = []

                                        analytic = code.isdigit() and int(code) or False # id de cuenta analítica
                                        if analytic:
                                            analytic_objs = self.env['account.analytic.account'].browse([analytic])

                                        distribution = not code.isdigit() and int(code[1:]) or False
                                        if distribution:
                                            distribution_obj = self.env['account.analytic.distribution'].browse(distribution)
                                            analytic_objs = distribution_obj.rule_ids

                                        valor = config[remuneration][configuration] # importe a apuntar

                                        for analytic_obj in analytic_objs:
                                            if distribution:
                                                new_valor = analytic_obj.percent and valor * (analytic_obj.percent / 100) or analytic_obj.fix_amount
                                            else:
                                                new_valor = valor

                                            if not type in ("with_contract","with_ss_contract") and new_valor: # si no es con contrato y hay importe
                                                ids_delete = self.env['account.analytic.line'].search(
                                                [('remuneration_id','=',int(remuneration)),('account_id','=', analytic or analytic_obj.analytic_account_id.id),
                                                ('name','=',ustr(obj.name)+u"("+type+u")/ "+month+u"/"+year+u"/ "+ hr_employee_obj.name),
                                                ('department_id','=',analytic_obj.department_id and analytic_obj.department_id.id or False),
                                                ('delegation_id','=',analytic_obj.delegation_id and analytic_obj.delegation_id.id or False),
                                                ('manager_id','=',analytic_obj.manager_id and analytic_obj.manager_id.id or False)]) # se borrar todos los apunets ya existenetes con el mismo formato para no duplicar
                                                if ids_delete:
                                                    ids_delete.unlink()
                                                    ids_delete = []

                                                vals = {
                                                    'amount': -(new_valor),
                                                    'name':  ustr(obj.name)+u"("+type+u")/ "+month+u"/"+year+u"/ "+ hr_employee_obj.name,
                                                    'tag_ids': [(4, journal_id[0].id)],
                                                    'remuneration_id': int(remuneration),
                                                    'account_id': analytic or analytic_obj.analytic_account_id.id,
                                                    'general_account_id': general_account_id_suelsala[0].id,
                                                    'date': ""+year+"/"+month+"/"+str(calendar.monthrange(int(year),int(month))[1]),
                                                    'department_id': analytic_obj.department_id and analytic_obj.department_id.id or False,
                                                    'delegation_id': analytic_obj.delegation_id and analytic_obj.delegation_id.id or False,
                                                    'manager_id': analytic_obj.manager_id and analytic_obj.manager_id.id or False,
                                                    'employee_id' : hr_employee_obj.id,
                                                    'company_id': self.env.user.company_id.id
                                                    }
                                                self.env['account.analytic.line'].create(vals) # se crear un apunte según el tipo y el importe
                                            elif type == "with_contract" and new_valor: # si es con contrato y hay importe
                                                ids_delete = self.env['account.analytic.line'].search(
                                                [('remuneration_id','=',int(remuneration)),('account_id','=',analytic or analytic_obj.analytic_account_id.id),
                                                ('name','=',ustr(obj.name)+u"("+type+u")/ "+month+u"/"+year+u"/ "+ hr_employee_obj.name),
                                                ('department_id','=',analytic_obj.department_id and analytic_obj.department_id.id or False),
                                                ('delegation_id','=',analytic_obj.delegation_id and analytic_obj.delegation_id.id or False),
                                                ('manager_id','=',analytic_obj.manager_id and analytic_obj.manager_id.id or False)]) # evitamos suplicados
                                                if ids_delete:
                                                    ids_delete.unlink()
                                                    ids_delete = []
                                                cost_fixed = record['total_accrued'] - fixed # restamos del total bruto la cantidad fija, obteniendo el coste no fijo
                                                cost_price_hour = cost_fixed - with_price_hour # restamos del coste que nos queda el coste por precio hora
                                                remu_total_cost = (cost_price_hour*new_valor)/with_contract # ontenemos el número de horas de la remuneración sobre el total de horas que tb incluye las horas por parte
                                                #cost_contract = (remu_total_cost*valor)/with_contract_contract # repartimos la proporción del coste del contrato según las horas
                                                vals = {
                                                    'amount': -(remu_total_cost),
                                                    'name':  ustr(obj.name)+u"("+type+u")/ "+month+u"/"+year+u"/ "+ hr_employee_obj.name,
                                                    'tag_ids': [(4, journal_id[0].id)],
                                                    'remuneration_id': int(remuneration),
                                                    'account_id': analytic or analytic_obj.analytic_account_id.id,
                                                    'general_account_id': general_account_id_suelsala[0].id,
                                                    'date': ""+year+"/"+month+"/"+str(calendar.monthrange(int(year),int(month))[1]),
                                                    'department_id': analytic_obj.department_id and analytic_obj.department_id.id or False,
                                                    'delegation_id': analytic_obj.delegation_id and analytic_obj.delegation_id.id or False,
                                                    'manager_id': analytic_obj.manager_id and analytic_obj.manager_id.id or False,
                                                    'employee_id' : hr_employee_obj.id,
                                                    'company_id': self.env.user.company_id.id
                                                    }
                                                self.env['account.analytic.line'].create(vals) # creakos el apunte de con contrato
                                            elif new_valor and ss_total: # si hay seguridad social a repartir
                                                ids_delete = self.env['account.analytic.line'].search(
                                                [('remuneration_id','=',int(remuneration)),('account_id','=',analytic or analytic_obj.analytic_account_id.id),
                                                ('name','=',ustr(obj.name)+u"/ "+month+u"/"+year+u"/ "+ hr_employee_obj.name),
                                                ('department_id','=',analytic_obj.department_id and analytic_obj.department_id.id or False),
                                                ('delegation_id','=',analytic_obj.delegation_id and analytic_obj.delegation_id.id or False),
                                                ('manager_id','=',analytic_obj.manager_id and analytic_obj.manager_id.id or False)]) # evitamos suplicados
                                                if ids_delete:
                                                    ids_delete.unlink()
                                                    ids_delete = []
                                                remu_total_cost_ss = (ss_total*new_valor)/ss_total_hours # obtenemos el número de horas de la remuneración respecto a las horas totales
                                                #cost_contract_ss = (remu_total_cost_ss*valor)/with_ss_contract # repartimos la proporción del coste de ss según las horas
                                                vals = {
                                                        'amount': -(remu_total_cost_ss),
                                                        'name':  ustr(obj.name)+u"/ "+month+u"/"+year+u"/ "+ hr_employee_obj.name,
                                                        'tag_ids': [(4, social_journal_id[0].id)],
                                                        'remuneration_id': int(remuneration),
                                                        'account_id': analytic or analytic_obj.analytic_account_id.id,
                                                        'general_account_id': general_account_id_ss[0].id,
                                                        'date': ""+year+"/"+month+"/"+str(calendar.monthrange(int(year),int(month))[1]),
                                                        'department_id': analytic_obj.department_id and analytic_obj.department_id.id or False,
                                                        'delegation_id': analytic_obj.delegation_id and analytic_obj.delegation_id.id or False,
                                                        'manager_id': analytic_obj.manager_id and analytic_obj.manager_id.id or False,
                                                        'employee_id' : hr_employee_obj.id,
                                                        'company_id': self.env.user.company_id.id
                                                        }
                                                self.env['account.analytic.line'].create(vals)
                                else: # si es un parte de horas
                                    for configuration in config[remuneration]:
                                        type = (configuration.split("-"))[1]
                                        analytic = int((configuration.split("-"))[0])
                                        analytic_obj = self.env['account.analytic.account'].browse(analytic)
                                        valor = config[remuneration][configuration]
                                        timesheet_obj_id = self.env['timesheet'].browse(int(remuneration[:-1]))
                                        if type not in ("with_contract","with_ss_contract") and valor: # si no es con contrato y hay importe
                                            ids_delete = self.env['account.analytic.line'].search(
                                            [('timesheet_id','=',int(remuneration[:-1])),('account_id','=',int(analytic)),
                                            ('name','=',ustr(obj.name)+u" ("+type+u")/ "+month+u"/"+year+u"/ "+ hr_employee_obj.name)]) #borramos los duplicados
                                            if ids_delete:
                                                ids_delete.unlink()
                                                ids_delete = []
                                            vals = {
                                                'amount': -(valor),
                                                'name':  ustr(obj.name)+u" ("+type+u")/ "+month+u"/"+year+u"/ "+ hr_employee_obj.name,
                                                'tag_ids': [(4, journal_id[0].id)],
                                                'timesheet_id': int(remuneration[:-1]),
                                                'account_id': analytic,
                                                'general_account_id': general_account_id_suelsala[0].id,
                                                'date': ""+year+"/"+month+"/"+str(calendar.monthrange(int(year),int(month))[1]),
                                                'department_id': timesheet_obj_id.department_id and timesheet_obj_id.department_id.id or (analytic_obj.department_id and analytic_obj.department_id.id or False),
                                                'delegation_id': timesheet_obj_id.delegation_id and timesheet_obj_id.delegation_id.id or (analytic_obj.delegation_id and analytic_obj.delegation_id.id or False),
                                                'manager_id': timesheet_obj_id.responsible_id and timesheet_obj_id.responsible_id.id or (analytic_obj.manager_id and analytic_obj.manager_id.id or False),
                                                'employee_id' : hr_employee_obj.id,
                                                'company_id': self.env.user.company_id.id
                                                }
                                            self.env['account.analytic.line'].create(vals)
                                        elif type == "with_contract" and valor:
                                            ids_delete = self.env['account.analytic.line'].search(
                                            [('timesheet_id','=',int(remuneration[:-1])),('account_id','=',int(analytic)),
                                            ('name','=',ustr(obj.name)+u" ("+type+u")/ "+month+u"/"+year+u"/ "+ hr_employee_obj.name)]) # borramos duplicados
                                            if ids_delete:
                                                ids_delete.unlink()
                                                ids_delete = []
                                            cost_fixed = record['total_accrued'] - fixed # restamos del total el importe fijo
                                            cost_price_hour = cost_fixed - with_price_hour # retsmoa el importe por rpecio hora
                                            timesheet_total_cost = (cost_price_hour*valor)/with_contract # calculamso la proporción a repartir según las horas de l parte sobre las totales
                                            #cost_contract = (timesheet_total_cost*valor)/with_contract_timesheet
                                            vals = {
                                                'amount': -(timesheet_total_cost),
                                                'name':  ustr(obj.name)+u" ("+type+u")/ "+month+u"/"+year+u"/ "+ hr_employee_obj.name,
                                                'tag_ids': [(4, journal_id[0].id)],
                                                'timesheet_id': int(remuneration[:-1]),
                                                'account_id': analytic,
                                                'general_account_id': general_account_id_suelsala[0].id,
                                                'date': ""+year+"/"+month+"/"+str(calendar.monthrange(int(year),int(month))[1]),
                                                'department_id': timesheet_obj_id.department_id and timesheet_obj_id.department_id.id or (analytic_obj.department_id and analytic_obj.department_id.id or False),
                                                'delegation_id': timesheet_obj_id.delegation_id and timesheet_obj_id.delegation_id.id or (analytic_obj.delegation_id and analytic_obj.delegation_id.id or False),
                                                'manager_id': timesheet_obj_id.responsible_id and timesheet_obj_id.responsible_id.id or (analytic_obj.manager_id and analytic_obj.manager_id.id or False),
                                                'employee_id' : hr_employee_obj.id,
                                                'company_id': self.env.user.company_id.id
                                                }

                                            self.env['account.analytic.line'].create(vals)
                                        elif valor and ss_total: # si hay seguridad social
                                            ids_delete = self.env['account.analytic.line'].search(
                                            [('timesheet_id','=',int(remuneration[:-1])),('account_id','=',int(analytic)),
                                            ('name','=',ustr(obj.name)+u"/ "+month+u"/"+year+u"/ "+ hr_employee_obj.name)]) # borramos duplicados
                                            if ids_delete:
                                                ids_delete.unlink()
                                                ids_delete = []
                                            timesheet_total_cost_ss = (ss_total*valor)/ss_total_hours # obtenemos el coste respecto ala shoras del parte copntra las totales
                                            #cost_contract_ss = (timesheet_total_cost_ss*valor)/ss_total_timesheet # calculamos el coste proporcionado a las horas
                                            vals = {
                                                    'amount': -(timesheet_total_cost_ss),
                                                    'name':  ustr(obj.name)+u"/ "+month+u"/"+year+u"/ "+ hr_employee_obj.name,
                                                    'tag_ids': [(4, social_journal_id[0].id)],
                                                    'timesheet_id': int(remuneration[:-1]),
                                                    'account_id': analytic,
                                                    'general_account_id': general_account_id_ss[0].id,
                                                    'date': ""+year+"/"+month+"/"+str(calendar.monthrange(int(year),int(month))[1]),
                                                    'department_id': timesheet_obj_id.department_id and timesheet_obj_id.department_id.id or (analytic_obj.department_id and analytic_obj.department_id.id or False),
                                                    'delegation_id': timesheet_obj_id.delegation_id and timesheet_obj_id.delegation_id.id or (analytic_obj.delegation_id and analytic_obj.delegation_id.id or False),
                                                    'manager_id': timesheet_obj_id.responsible_id and timesheet_obj_id.responsible_id.id or (analytic_obj.manager_id and analytic_obj.manager_id.id or False),
                                                    'employee_id' : hr_employee_obj.id,
                                                    'company_id': self.env.user.company_id.id
                                                    }
                                            self.env['account.analytic.line'].create(vals)
        return {'type': 'ir.actions.act_window_close'}
