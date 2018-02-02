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

from osv import osv, fields
import tools

class account_invoice_report_custom(osv.osv):

    _name = "account.invoice.report.custom"
    _auto = False
    _rec_name = 'date'

    _columns = {
        'date': fields.date('Date', readonly=True),
        'year': fields.char('Year', size=4, readonly=True),
        'day': fields.char('Day', size=128, readonly=True),
        'month': fields.selection([('01','January'), ('02','February'), ('03','March'), ('04','April'),
            ('05','May'), ('06','June'), ('07','July'), ('08','August'), ('09','September'),
            ('10','October'), ('11','November'), ('12','December')], 'Month', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'product_qty':fields.float('Qty', readonly=True),
        'uom_name': fields.char('Reference UoM', size=128, readonly=True),
        'payment_term': fields.many2one('account.payment.term', 'Payment Term', readonly=True),
        'period_id': fields.many2one('account.period', 'Force Period', domain=[('state','<>','done')], readonly=True),
        'fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position', readonly=True),
        'currency_id': fields.many2one('res.currency', 'Currency', readonly=True),
        'categ_id': fields.many2one('product.category','Category of Product', readonly=True),
        'journal_id': fields.many2one('account.journal', 'Journal', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'price_total': fields.float('Total Without Tax', readonly=True),
        'price_total_tax': fields.float('Total With Tax', readonly=True),
        'currency_rate': fields.float('Currency Rate', readonly=True),
        'nbr':fields.integer('# of Lines', readonly=True),
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
            ],'Type', readonly=True),
        'state': fields.selection([
            ('draft','Draft'),
            ('proforma','Pro-forma'),
            ('proforma2','Pro-forma'),
            ('open','Open'),
            ('paid','Done'),
            ('cancel','Cancelled')
            ], 'Invoice State', readonly=True),
        'date_due': fields.date('Due Date', readonly=True),
        'address_contact_id': fields.many2one('res.partner.address', 'Contact Address Name', readonly=True),
        'address_invoice_id': fields.many2one('res.partner.address', 'Invoice Address Name', readonly=True),
        'account_id': fields.many2one('account.account', 'Account',readonly=True),
        'partner_bank_id': fields.many2one('res.partner.bank', 'Bank Account',readonly=True),
        'residual': fields.float('Total Residual', readonly=True),
        'privacy': fields.selection([('public', 'Public'), ('private', 'Private')], 'Privacy', readonly=True),
        'delegation_id': fields.many2one('res.delegation', 'Delegation', readonly=True),
        'department_id': fields.many2one('hr.department', 'Department', readonly=True),
        'manager_id': fields.many2one('hr.employee', 'Responsible', readonly=True, domain=[('responsible', '=', True)]),
        'no_quality': fields.boolean('Scont', readonly=True)
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'account_invoice_report_custom')
        cr.execute("""
            create or replace view account_invoice_report_custom as (
                 select min(ail.id) as id,
                    ai.date_invoice as date,
                    to_char(ai.date_invoice, 'YYYY') as year,
                    to_char(ai.date_invoice, 'MM') as month,
                    ai.date_invoice as day,
                    ail.product_id,
                    ai.partner_id as partner_id,
                    ai.delegation_id,
                    ai.department_id,
                    ai.manager_id,
                    ai.payment_term as payment_term,
                    ai.period_id as period_id,
                    (case when u.uom_type not in ('reference') then
                        (select name from product_uom where uom_type='reference' and active and category_id=u.category_id LIMIT 1)
                    else
                        u.name
                    end) as uom_name,
                    ai.currency_id as currency_id,
                    ai.journal_id as journal_id,
                    ai.fiscal_position as fiscal_position,
                    ai.company_id as company_id,
                    count(ail.*) as nbr,
                    ai.type as type,
                    aa.privacy,
                    ai.state,
                    pt.categ_id,
                    ai.date_due as date_due,
                    ai.address_contact_id as address_contact_id,
                    ai.address_invoice_id as address_invoice_id,
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
                left join product_uom u on (u.id=ail.uos_id)
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
                    ai.payment_term,
                    ai.period_id,
                    u.name,
                    ai.currency_id,
                    ai.journal_id,
                    ai.fiscal_position,
                    ai.company_id,
                    ai.type,
                    ai.state,
                    aa.privacy,
                    pt.categ_id,
                    ai.date_due,
                    ai.address_contact_id,
                    ai.address_invoice_id,
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


account_invoice_report_custom()
