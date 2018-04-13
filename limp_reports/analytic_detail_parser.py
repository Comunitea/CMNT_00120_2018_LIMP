# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import time
from odoo import models, api, _
from odoo.tools.misc import formatLang


class AccountAnalyticDetails(models.AbstractModel):
    _name = 'report.limp_reports.account_analytic_details'

    def _get_domain(self, acc, data, force_add=False, with_tag_accounts=False):
        if with_tag_accounts:
            contract_tag = acc.tag_ids.filtered('contract_tag')
            account_ids = self.env['account.analytic.account'].search(
                [('tag_ids', 'in', [contract_tag.id])])
        else:
            account_ids = acc
        where = """date >= '{}' and date <= '{}'
                   and account_id in ({})
                   and company_id = {}""".format(
            data['date1'], data['date2'],
            ",".join(str(x.id) for x in account_ids),
            str(acc.company_id.id))
        if data.get('delegation_id', False):
            where += " and delegation_id = {}".format(
                str(data['delegation_id']))
        if data.get('department_id', False):
            where += " and department_id = {}".format(
                str(data['department_id']))
        if data.get('manager_id', False):
            where += " and manager_id = {}".format(str(data['manager_id']))
        if data.get('without_pickings', False):
            not_valid_accounts = account_ids.filtered(
                lambda r: r.is_picking_in_contract)
            if not_valid_accounts:
                where += " and account_id not in ({})".format(
                    ",".join(str(x.id) for x in not_valid_accounts))
        return where

    def _get_balance(self, account, data, with_tag_accounts=False):
        domain = self._get_domain(
            account, data, with_tag_accounts=with_tag_accounts)
        self._cr.execute(
            """select sum(amount),count(*)
               from account_analytic_line where {}""".format(domain))
        data = self._cr.fetchone()
        balance = data[0] or 0.0
        count = data[1]
        if balance > 0:
            res = True
        else:
            res = False
        return balance, res, count

    def _get_real_percent(self, account, data, with_tag_accounts=False):
        balance, sign, count = self._get_balance(
            account, data, with_tag_accounts=with_tag_accounts)
        domain = self._get_domain(
            account, data, with_tag_accounts=with_tag_accounts)
        domain += " and amount > 0"
        self._cr.execute("""
            select sum(amount)
            from account_analytic_line where {}""".format(domain))
        invoiced_amount = self._cr.fetchone()[0]
        if invoiced_amount:
            return (balance * 100.0) / invoiced_amount
        else:
            return 0.0

    def _get_journals(self, account, data,
                      child=False, with_tag_accounts=False):
        domain = self._get_domain(
            account, data, with_tag_accounts=with_tag_accounts)
        res = []
        self._cr.execute("""
            select sum(amount)
            from account_analytic_line
            where {} and amount > 0""".format(domain))
        balance = self._cr.fetchone()[0]
        if balance:
            res.append((_('Sales'), balance, False))
            if not child:
                if not self.journals_sumarize.get(_('Sales')):
                    self.journals_sumarize[_('Sales')] = balance
                else:
                    self.journals_sumarize[_('Sales')] += balance
        for tag in self.env['account.analytic.tag'].search(
                [('show_in_report', '=', True)]):
            self._cr.execute("""
                select sum(amount)
                from account_analytic_line
                where {} and id in
                (select line_id
                 from account_analytic_line_tag_rel where tag_id={})""".format(
                domain, tag.id))
            balance = self._cr.fetchone()[0]
            if balance:
                res.append((tag.name, balance, tag))
                if not child:
                    if not self.journals_sumarize.get(tag.name):
                        self.journals_sumarize[tag.name] = balance
                    else:
                        self.journals_sumarize[tag.name] += balance
        return res

    def _get_employees(self, account, tag, data, with_tag_accounts=False):
        res = []
        domain = self._get_domain(
            account, data, with_tag_accounts=with_tag_accounts)
        if tag:
            domain += """
                and id in (select line_id
                from account_analytic_line_tag_rel
                where tag_id={})""".format(str(tag.id))
        else:
            domain += " and amount > 0"
        self._cr.execute("""
            select distinct employee_id
            from account_analytic_line where {}""".format(domain))
        employee_data = self._cr.fetchall()
        employee_ids = [x[0] for x in employee_data]
        for employee_id in employee_ids:
            employee = False
            if employee_id:
                employee = self.env['hr.employee'].browse(employee_id)
                name = employee.name
                self._cr.execute("""
                    select sum(amount)
                    from account_analytic_line
                    where {} and employee_id = {}""".format(
                    domain, str(employee.id)))
            else:
                name = "Sin empleado"
                self._cr.execute("""
                    select sum(amount)
                    from account_analytic_line
                    where {} and employee_id is null""".format(domain))
            balance = self._cr.fetchone()[0]
            if balance:
                res.append((name, balance, employee))
        return res

    def _get_analytic_type(self, account, tag, employee, data,
                           with_tag_accounts=False):
        res = []
        domain = self._get_domain(
            account, data, with_tag_accounts=with_tag_accounts)
        if tag:
            domain += """
                and id in (select line_id
                from account_analytic_line_tag_rel
                where tag_id={})""".format(str(tag.id))
        else:
            domain += " and amount > 0"
        if employee:
            domain += " and employee_id = {}".format(str(employee.id))
        else:
            domain += " and employee_id is null"
        self._cr.execute("""
            select distinct type_analytic
            from account_analytic_line where {}""".format(domain))
        type_data = self._cr.fetchall()
        type_names = [x[0] for x in type_data]
        for type_n in type_names:
            if type_n:
                name = type_n
                self._cr.execute("""
                    select sum(amount)
                    from account_analytic_line
                    where {} and type_analytic = '{}'""".format(
                    domain, type_n))
            else:
                name = "Sin tipo"
                self._cr.execute("""
                    select sum(amount)
                    from account_analytic_line
                    where {} and type_analytic is null""".format(domain))
            balance = self._cr.fetchone()[0]
            if balance:
                res.append((name, balance))
        return res

    def _get_childs(self, account):
        contract_tag = account.tag_ids.filtered('contract_tag')
        account_ids = self.env['account.analytic.account'].search(
            [('tag_ids', 'in', [contract_tag.id]), ('id', '!=', account.id)])
        return account_ids

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

    @api.model
    def render_html(self, docids, data=None):
        if not docids:
            docids = self.env.context.get('active_ids', False)
        docs = self.env['account.analytic.account'].browse(docids)
        self.journals_sumarize = {}
        docargs = {
            'data': data['form'],
            'doc_ids': docids,
            'doc_model': 'account.analytic.account',
            'docs': docs,
            'time': time,
            'get_balance': self._get_balance,
            'get_real_percent': self._get_real_percent,
            'get_journals': self._get_journals,
            'get_childs': self._get_childs,
            'lang': self.env.user.lang,
            'get_summarize': self._get_summarize,
            'get_employees': self._get_employees,
            'get_analytic_type': self._get_analytic_type,
            'formatLang': formatLang
        }

        return self.env['report'].render(
            'limp_reports.account_analytic_details', docargs)
