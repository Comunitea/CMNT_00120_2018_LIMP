# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
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
from odoo import models, fields


class AccountInvoiceReportCustom(models.Model):

    _name = "account.invoice.report.custom"
    _auto = False
    _rec_name = 'date'

    date = fields.Date('Date', readonly=True)
    year = fields.Char('Year', size=4, readonly=True)
    day = fields.Char('Day', size=128, readonly=True)
    month = fields.Selection([('01','January'), ('02','February'), ('03','March'), ('04','April'),
        ('05','May'), ('06','June'), ('07','July'), ('08','August'), ('09','September'),
        ('10','October'), ('11','November'), ('12','December')], 'Month', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    product_qty = fields.Float('Qty', readonly=True)
    uom_name = fields.Char('Reference UoM', size=128, readonly=True)
    payment_term_id = fields.Many2one('account.payment.term', 'Payment Term', readonly=True)
    fiscal_position = fields.Many2one('account.fiscal.position', 'Fiscal Position', readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', readonly=True)
    categ_id = fields.Many2one('product.category','Category of Product', readonly=True)
    journal_id = fields.Many2one('account.journal', 'Journal', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    price_total = fields.Float('Total Without Tax', readonly=True)
    price_total_tax = fields.Float('Total With Tax', readonly=True)
    currency_rate = fields.Float('Currency Rate', readonly=True)
    nbr = fields.Integer('# of Lines', readonly=True)
    type = fields.Selection([
        ('out_invoice','Customer Invoice'),
        ('in_invoice','Supplier Invoice'),
        ('out_refund','Customer Refund'),
        ('in_refund','Supplier Refund'),
        ],'Type', readonly=True)
    state = fields.Selection([
        ('draft','Draft'),
        ('proforma','Pro-forma'),
        ('proforma2','Pro-forma'),
        ('open','Open'),
        ('paid','Done'),
        ('cancel','Cancelled')
        ], 'Invoice State', readonly=True)
    date_due = fields.Date('Due Date', readonly=True)
    partner_shipping_id = fields.Many2one('res.partner', 'Shipping Address Name', readonly=True)
    account_id = fields.Many2one('account.account', 'Account',readonly=True)
    partner_bank_id = fields.Many2one('res.partner.bank', 'Bank Account',readonly=True)
    residual = fields.Float('Total Residual', readonly=True)
    privacy = fields.Selection([('public', 'Public'), ('private', 'Private')], 'Privacy', readonly=True)
    delegation_id = fields.Many2one('res.delegation', 'Delegation', readonly=True)
    department_id = fields.Many2one('hr.department', 'Department', readonly=True)
    manager_id = fields.Many2one('hr.employee', 'Responsible', readonly=True, domain=[('responsible', '=', True)])
    no_quality = fields.Boolean('Scont', readonly=True)

    def init(self):
        self._cr.execute("""
            create or replace view account_invoice_report_custom as (
                 select min(ail.id) as id,
                    ai.date_invoice as date,
                    to_char(ai.date_invoice, 'YYYY') as year,
                    to_char(ai.date_invoice, 'MM') as month,
                    ai.date_invoice as day,
                    ail.product_id,
                    ai.partner_id as partner_id,
                    ai.partner_shipping_id as partner_shipping_id,
                    ai.delegation_id,
                    ai.department_id,
                    ai.manager_id,
                    ai.payment_term_id as payment_term_id,
                    ai.period_id as period_id,
                    (case when u.uom_type not in ('reference') then
                        (select name from product_uom where uom_type='reference' and active and category_id=u.category_id LIMIT 1)
                    else
                        u.name
                    end) as uom_name,
                    ai.currency_id as currency_id,
                    ai.journal_id as journal_id,
                    ai.fiscal_position_id as fiscal_position,
                    ai.company_id as company_id,
                    count(ail.*) as nbr,
                    ai.type as type,
                    aa.privacy,
                    ai.state,
                    pt.categ_id,
                    ai.date_due as date_due,
                    ai.account_id as account_id,
                    ai.no_quality as no_quality,
                    ai.partner_bank_id as partner_bank_id,
                    sum(case when ai.type in ('out_refund','in_invoice') then
                         ail.quantity / u.factor * -1
                        else
                         ail.quantity / u.factor
                        end) as product_qty,
                    sum(case when ai.type in ('out_refund','in_invoice') then
                         ail.price_subtotal * -1
                        else
                         ail.price_subtotal
                        end) / cr.rate as price_total,
                    sum(case when ai.type in ('out_refund','in_invoice') then
                         ai.amount_total * -1
                        else
                         ai.amount_total
                         end) / (CASE WHEN
                              (select count(l.id) from account_invoice_line as l
                               left join account_invoice as a ON (a.id=l.invoice_id)
                               where a.id=ai.id) <> 0
                            THEN
                              (select count(l.id) from account_invoice_line as l
                               left join account_invoice as a ON (a.id=l.invoice_id)
                               where a.id=ai.id)
                            ELSE 1
                            END) / cr.rate as price_total_tax,
                    cr.rate as currency_rate,
                    sum((case when ai.type in ('out_refund','in_invoice') then
                      ai.residual * -1
                    else
                      ai.residual
                    end) / (select count(*) from account_invoice_line where invoice_id = ai.id) / cr.rate) as residual
                from account_invoice_line as ail
                left join account_invoice as ai ON (ai.id=ail.invoice_id)
                left join product_product pp on (pp.id=ail.product_id)
                left join product_template pt on (pt.id=pp.product_tmpl_id)
                left join product_uom u on (u.id=ail.uom_id)
                left join account_analytic_account aa on (aa.id = ai.analytic_id),
                res_currency_rate cr
                where cr.id in (select id from res_currency_rate cr2  where (cr2.currency_id = ai.currency_id) and (ail.product_id is null or pp.tax_product != true)
                and ((ai.date_invoice is not null and cr.name <= ai.date_invoice) or (ai.date_invoice is null and cr.name <= NOW())) limit 1)
                group by ail.product_id,
                    ai.date_invoice,
                    ai.id,
                    cr.rate,
                    to_char(ai.date_invoice, 'YYYY'),
                    to_char(ai.date_invoice, 'MM'),
                    ai.date_invoice,
                    ai.partner_id,
                    ai.partner_shipping_id,
                    ai.payment_term_id,
                    ai.period_id,
                    u.name,
                    ai.currency_id,
                    ai.journal_id,
                    ai.fiscal_position_id,
                    ai.company_id,
                    ai.type,
                    ai.state,
                    aa.privacy,
                    pt.categ_id,
                    ai.date_due,
                    ai.account_id,
                    ai.partner_bank_id,
                    ai.amount_total,
                    u.uom_type,
                    u.category_id,
                    ai.delegation_id,
                    ai.department_id,
                    ai.manager_id,
                    ai.no_quality
            )
        """)
