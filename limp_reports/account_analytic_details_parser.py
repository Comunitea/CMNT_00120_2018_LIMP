# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos. All Rights Reserved
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

import time
from report import report_sxw

class account_analytic_details(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_analytic_details, self).__init__(cr, uid, name, context=context)
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        self.journals_sumarize = {}
        self.localcontext.update( {
            'time': time,
            'get_balance': self._get_balance,
            'get_real_percent': self._get_real_percent,
            'get_journals': self._get_journals,
            'get_childs': self._get_childs,
            'lang': user.context_lang,
            'get_summarize': self._get_summarize,
            'get_employees': self._get_employees,
            'get_analytic_type': self._get_analytic_type
        })

    def _get_domain(self, acc, data):
        account_ids = self.pool.get('account.analytic.account').search(self.cr, self.uid, [('id', 'child_of', [acc.id])])
        where = "date >= '%s' and date <= '%s' and account_id in (%s) and company_id = %s" % (data['date1'], data['date2'], ",".join(str(x) for x in account_ids), str(acc.company_id.id))
        if data.get('delegation_id', False):
            where += " and delegation_id = %s" % str(data['delegation_id'])
        if data.get('department_id', False):
            where += " and department_id = %s" % str(data['department_id'])
        if data.get('manager_id', False):
            where += " and manager_id = %s" % str(data['manager_id'])
        if data.get('without_pickings', False):
            not_valid_accounts = []
            for acc in self.pool.get('account.analytic.account').browse(self.cr, self.uid, account_ids):
                if acc.is_picking_in_contract:
                    not_valid_accounts.append(acc.id)
            if not_valid_accounts:
                where += " and account_id not in (%s)" % ",".join(str(x) for x in not_valid_accounts)

        return where

    def _get_balance(self, account, data):
        domain = self._get_domain(account, data)
        self.cr.execute("select sum(amount),count(*) from account_analytic_line where %s" % domain)
        data = self.cr.fetchone()
        balance = data[0]
        count = data[1]
        if balance > 0:
            res = True
        else:
            res = False
        return balance,res,count

    def _get_real_percent(self, account, data):
        balance,sign,count = self._get_balance(account, data)
        domain = self._get_domain(account, data)
        journal_ids = self.pool.get('account.analytic.journal').search(self.cr, self.uid, [('type', '=', 'sale')])
        domain += " and journal_id in (%s)" % ",".join(str(x) for x in journal_ids)
        self.cr.execute("select sum(amount) from account_analytic_line where %s" % domain)
        invoiced_amount = self.cr.fetchone()[0]
        if invoiced_amount:
            return (balance * 100.0) / invoiced_amount
        else:
            return 0.0

    def _get_journals(self, account, data, child=False):
        domain = self._get_domain(account, data)
        res = []
        for journal_id in self.pool.get('account.analytic.journal').search(self.cr, self.uid, [], order="name asc"):
            journal = self.pool.get('account.analytic.journal').browse(self.cr, self.uid, journal_id, context=self.localcontext)
            self.cr.execute("select sum(amount) from account_analytic_line where %s" % domain + " and journal_id = %s" % str(journal.id))
            balance = self.cr.fetchone()[0]
            if balance:
                res.append((journal.name, balance, journal))
                if not child:
                    if not self.journals_sumarize.get(journal.name):
                        self.journals_sumarize[journal.name] = balance
                    else:
                        self.journals_sumarize[journal.name] += balance
        return res

    def _get_employees(self, account, journal, data):
        res = []
        domain = self._get_domain(account, data)
        domain += " and journal_id = %s" % str(journal.id)
        self.cr.execute("select distinct employee_id from account_analytic_line where %s" % domain)
        employee_data = self.cr.fetchall()
        employee_ids = [x[0] for x in employee_data]
        for employee_id in employee_ids:
            employee = False
            if employee_id:
                employee = self.pool.get('hr.employee').browse(self.cr, self.uid, employee_id)
                name = employee.name
                self.cr.execute("select sum(amount) from account_analytic_line where %s" % domain + " and employee_id = %s" % str(employee.id))
            else:
                name = "Sin empleado"
                self.cr.execute("select sum(amount) from account_analytic_line where %s" % domain + " and employee_id is null")
            balance = self.cr.fetchone()[0]
            if balance:
                res.append((name, balance, employee))
        return res

    def _get_analytic_type(self, account, journal, employee, data):
        res = []
        domain = self._get_domain(account, data)
        domain += " and journal_id = %s" % str(journal.id)
        if employee:
            domain += " and employee_id = %s" % str(employee.id)
        else:
            domain += " and employee_id is null"
        self.cr.execute("select distinct type_analytic from account_analytic_line where %s" % domain)
        type_data = self.cr.fetchall()
        type_names = [x[0] for x in type_data]
        for type_n in type_names:
            if type_n:
                name = type_n
                self.cr.execute("select sum(amount) from account_analytic_line where %s" % domain + " and type_analytic = '%s'" % type_n)
            else:
                name = "Sin tipo"
                self.cr.execute("select sum(amount) from account_analytic_line where %s" % domain + " and type_analytic is null")
            balance = self.cr.fetchone()[0]
            if balance:
                res.append((name, balance))
        return res

    def _get_childs(self, account):
        child_ids = self.pool.get('account.analytic.account').search(self.cr, self.uid, [('id', 'child_of', [account.id])])
        child_ids = list(set(child_ids) - set([account.id]))
        return [x for x in self.pool.get('account.analytic.account').browse(self.cr, self.uid, child_ids)]

    def _get_summarize(self):
        res = []
        expenses = 0.0
        incomes = 0.0
        for journal in self.journals_sumarize:
            if self.journals_sumarize[journal] < 0:
                expenses += self.journals_sumarize[journal]
            else:
                incomes += self.journals_sumarize[journal]
            res.append((journal, self.journals_sumarize[journal], u"€"))

        balance = incomes + expenses
        if balance:
            percent = (balance * 100.0) / (incomes or 1.0)
        else:
            percent = 0.0
        res.append(("% Real", percent, u"%"))
        return res

report_sxw.report_sxw('report.account.analytic.account.details.report', 'account.analytic.account', 'addons/limp_reports/report/analytic_account_details.rml',parser=account_analytic_details, header="internal")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

