# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
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

"""Add concepts field to analytic account"""

from openerp.osv import osv, fields
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
# import netsvc MIGRACION: Comentado
import calendar
from dateutil.rrule import *

def intersect(la, lb):
    """intersects between two list returning equal values"""
    l = filter(lambda x: x in lb, la)
    return l

class account_analytic_account(osv.osv):
    """Add concepts field to analytic account"""

    _inherit = "account.analytic.account"

    _columns = {
        'concept_ids': fields.one2many('account.analytic.invoice.concept.rel', 'analytic_id', 'Concepts'),
        'group_concepts': fields.boolean('Group concepts', help="Groups concepts at invoice"),
        'group_products': fields.boolean('Group products', help="Groups products at invoice"),
        'group_products_each_invoice': fields.boolean('One for invoice', help="Groups products, one for invoice"),
        'invoiceable': fields.boolean('Invoiceable', help="Visibility to invoce cron")
    }

    def _get_ids_hook(self, cr, uid, ids, context=None):
        """hook to manage ids list to process"""
        if context is None: context = {}

        return ids

    def _invoice_hook(self, cr, uid, analytic, invoice_id, end_date, context=None):
        """hook to manage invoice creation"""
        if context is None: context = {}

        return

    def _create_invoice(self, cr, uid, analytic, end_date, context=None):
        """creates an invoice to an analytic account"""
        if context is None: context = {}

        end_date = datetime.strptime(end_date + " 23:59:59","%Y-%m-%d %H:%M:%S")

        vals = {
            'name': analytic.name,
            'origin': analytic.name,
            'type': 'out_invoice',
            'account_id': analytic.partner_id.property_account_receivable.id,
            'partner_id': analytic.partner_id.id,
            'address_contact_id': analytic.address_id and analytic.address_id.id or ((analytic.parent_id and analytic.parent_id.address_id) and analytic.parent_id.address_id.id or False),
            'address_invoice_id': analytic.address_invoice_id and analytic.address_invoice_id.id or ((analytic.parent_id and analytic.parent_id.address_invoice_id) and analytic.parent_id.address_invoice_id.id or False),
            'payment_term': analytic.partner_id.property_payment_term and analytic.partner_id.property_payment_term.id or False,
            'fiscal_position': analytic.partner_id.property_account_position.id,
            'company_id': analytic.company_id.id,
            'analytic_id': analytic.id,
            'date_invoice': context.get('invoice_date', False),
            'department_id': analytic.department_id and analytic.department_id.id or False
        }

        if context.get('journal_id', False):
            vals['journal_id'] = context["journal_id"]

        invoice_id = self.pool.get('account.invoice').create(cr, uid, vals)

        self._invoice_hook(cr, uid, analytic, invoice_id, end_date, context=context)

        return invoice_id

    def _process_concept_name(self, cr, uid, concept_rel, analytic, date, context=None):
        """hook to process concept name"""
        if context is None: context = {}

        return self.pool.get('account.analytic.invoice.concept').process_name(concept_rel.concept_id, description=concept_rel.name, date=date)

    def _invoice_line_hook(self, cr, uid, analytic, concept, invoice_line, end_date, context=None):
        """hook to manage invoice line creation"""
        if context is None: context = {}

        return True

    def close_analytic(self, cr, uid, analytic):
        analytic.write({'state': 'close'})

        return True

    def create_concept_invoice_line(self, cr, uid, analytic, concept, invoice_id, end_date, context=None):
        """creates an invoice line for concept in args"""
        if context is None: context = {}
        account_id = concept.concept_id.product_id.product_tmpl_id.property_account_income.id
        if not account_id:
            account_id = concept.concept_id.product_id.categ_id.property_account_income_categ.id

        # se rellena con la fecha de última factura o la fecha de alta de la cuenta
        start_date = concept.last_invoice_date and datetime.strptime(concept.last_invoice_date + " 00:00:00", "%Y-%m-%d %H:%M:%S") + relativedelta(days=+1) or datetime.strptime(analytic.date_start + " 00:00:00", "%Y-%m-%d %H:%M:%S")
        # fecha en la que se está facturando
        end_date = datetime.strptime(end_date + " 23:59:59","%Y-%m-%d %H:%M:%S")
        # fecha de baja de la cuenta analítica o fecha de facturación
        end_date = (analytic.date and datetime.strptime(analytic.date + " 23:59:59","%Y-%m-%d %H:%M:%S") < end_date) and datetime.strptime(analytic.date + " 23:59:59","%Y-%m-%d %H:%M:%S") or end_date

        if end_date.month in concept._get_except_months()[concept.id]:
            return False

        except_months = concept._get_except_months()[concept.id]
        rset = rruleset()
        if except_months:
            rset.exrule(rrule(DAILY,dtstart=start_date,until=end_date,bymonth=except_months))
        rset.rrule(rrule(DAILY,dtstart=start_date,until=end_date))
        months = list(set([(x.year,x.month) for x in list(rset)]))
        amount = 0.0
        if concept.freq == 'q':
            days = 90
        else:
            days = 30
        duration = 0
        for month in months:
            days_in_month = calendar.monthrange(month[0], month[1])[1]
            first_month_day = datetime.strptime(str(month[0]) + "-" + str(month[1]).zfill(2) + "-01", "%Y-%m-%d")
            last_month_day = datetime.strptime(str(month[0]) + "-" + str(month[1]).zfill(2) + "-" + str(days_in_month), "%Y-%m-%d")
            rset_month = rset.between(first_month_day, last_month_day, inc=True)
            month_days = len(list(rset_month))
            if month_days == days_in_month:
                duration += 30
            else:
                duration += month_days
        amount += (duration * concept.amount) / days

        if analytic.date and datetime.strptime(analytic.date + " 23:59:59","%Y-%m-%d %H:%M:%S") <= end_date:
            self.close_analytic(cr, uid, analytic)

        if not amount and concept.amount:
            return False

        invoice_line = self.pool.get('account.invoice.line').create(cr, uid, {
                'name': self._process_concept_name(cr, uid, concept, analytic, end_date, context=context),
                'origin': analytic.name,
                'invoice_id': invoice_id,
                'uos_id': concept.concept_id.product_id.uos_id and concept.concept_id.product_id.uos_id.id or False,
                'product_id': concept.concept_id.product_id.id,
                'account_id': self.pool.get('account.fiscal.position').map_account(cr, uid, analytic.partner_id.property_account_position, account_id),
                'price_unit': amount,
                'discount': 0.0,
                'quantity': 1.0,
                'invoice_line_tax_id': [(6, 0, self.pool.get('account.fiscal.position').map_tax(cr, uid, analytic.partner_id.property_account_position, concept.concept_id.product_id.taxes_id))],
                'account_analytic_id': analytic.id,
        })

        res = self._invoice_line_hook(cr, uid, analytic, concept, invoice_line, end_date, context=context)
        return res and invoice_line

    def __group_by_product_lines(self, cr, uid, ref_line, grouped_lines):
        subtotal = ref_line.price_unit
        note = ref_line.name + u"\n"
        for line in self.pool.get('account.invoice.line').browse(cr, uid, grouped_lines):
            subtotal += line.price_unit
            note += (line.name + u"\n")
        ref_line.write({'price_unit': round(subtotal,2), 'name' : ref_line.product_id.description_sale or ref_line.product_id.name, 'note': note})
        return True

    def run_invoice_cron_manual(self, cr, uid, ids, context=None):
        if context is None: context = {}

        analytic_ids = [] #list of visited analytic accounts
        created_invoices = [] #list of created invoices

        ids = self._get_ids_hook(cr, uid, ids, context=context)
        if context.get('end_date', False):
            end_date = context['end_date']
        else:
            day, days = calendar.monthrange(int(time.strftime('%Y')), int(time.strftime('%m')))
            end_date = time.strftime('%Y-%m-') + str(days)


        for analytic_obj in self.browse(cr, uid, ids):
            child_concepts_ids = [] #list of childs in first level
            analytic_invoices= []
            for child in analytic_obj.child_ids:
                child_concepts_ids.extend(child.concept_ids)
            if analytic_obj.id not in analytic_ids:
                if analytic_obj.group_concepts and (analytic_obj.concept_ids or child_concepts_ids): # if group concepts and exists concepts
                    invoice = self._create_invoice(cr, uid, analytic_obj, end_date, context=context) #creates an unique invoice to group all concepts
                    created_invoices.append(invoice)
                    analytic_invoices.append(invoice)
                    for concept in analytic_obj.concept_ids:
                        res = self.create_concept_invoice_line(cr, uid, analytic_obj, concept, invoice, end_date, context=context) #an invoice line for each concept
                        if res:
                            concept.write({'last_invoice_date': end_date})

                    analytic_ids.append(analytic_obj.id) #visited analytic account

                    for analytic_child_obj in analytic_obj.child_ids: #goes around child analytic accounts
                        delete = False
                        if analytic_child_obj.id in analytic_ids:
                            #remove his related invoice because it's invoice line
                            related_invoices = self.pool.get('account.invoice').search(cr, uid, [('analytic_id', '=', analytic_child_obj.id)]) #obtain all related invoices with this account
                            toremove_related_invoices = intersect(created_invoices, related_invoices) #computes repeated invoice in two lists
                            if toremove_related_invoices:
                                self.pool.get('account.invoice').unlink(cr, uid, toremove_related_invoices)
                                for rec in toremove_related_invoices:
                                    created_invoices.remove(rec)
                                analytic_ids.remove(analytic_child_obj.id)
                                delete = True

                        for child_concept in analytic_child_obj.concept_ids: #goes around child concepts
                            #if delete or self._check_valid_concept(cr, uid, child_concept, analytic_child_obj):
                            res = self.create_concept_invoice_line(cr, uid, analytic_child_obj, child_concept, invoice, end_date, context=context) #creates an invoice line for each child concept
                            if res:
                                child_concept.write({'last_invoice_date': end_date})

                        analytic_ids.append(analytic_child_obj.id) #set account as visited
                elif analytic_obj.concept_ids or child_concepts_ids: #if exists concepts buy they don't group and it isn't visited
                    for concept in analytic_obj.concept_ids:
                        invoice = self._create_invoice(cr, uid, analytic_obj, end_date, context=context) #invoice by concept
                        created_invoices.append(invoice)
                        analytic_invoices.append(invoice)
                        res = self.create_concept_invoice_line(cr, uid, analytic_obj, concept, invoice, end_date, context=context) #invoice line by conept
                        if res:
                            concept.write({'last_invoice_date': end_date})
                    analytic_ids.append(analytic_obj.id)

                if analytic_obj.group_products:
                    for inv in self.pool.get("account.invoice").browse(cr,uid,analytic_invoices, context=context):
                        dicc = {}
                        for line in inv.invoice_line:
                            if line.product_id.id not in dicc:
                                dicc[line.product_id.id] = []
                            dicc[line.product_id.id].append(line)

                        for key_id in dicc:
                            to_delete_line_ids = []
                            if len(dicc[key_id]) > 1:
                                ref_line = dicc[key_id][0]
                                for line in dicc[key_id]:
                                    if line.id != ref_line.id:
                                        to_delete_line_ids.append(line.id)

                                self.__group_by_product_lines(cr, uid, ref_line, to_delete_line_ids)
                                ref_line = self.pool.get('account.invoice.line').browse(cr, uid, ref_line.id)
                                new_name = self.pool.get('account.analytic.invoice.concept').process_name(False, description=ref_line.name, date=datetime.strptime(end_date, "%Y-%m-%d"))
                                ref_line.write({'name': new_name})
                                self.pool.get('account.invoice.line').unlink(cr,uid,to_delete_line_ids)

                        if analytic_obj.group_products_each_invoice:
                            inv_new_state = self.pool.get("account.invoice").browse(cr,uid,inv.id)
                            if len(inv_new_state.invoice_line) > 1:
                                line_ref = inv_new_state.invoice_line[0]
                                for line in inv_new_state.invoice_line:
                                    if line.id != line_ref.id:
                                        new_inv = self.pool.get('account.invoice').copy(cr, uid, inv_new_state.id, default={'invoice_line': False, 'date_invoice': inv.date_invoice})
                                        created_invoices.append(new_inv)
                                        line.write({'invoice_id': new_inv})

            wf_service = netsvc.LocalService('workflow')
            to_delete_invoices = []

            for invoice in self.pool.get('account.invoice').browse(cr, uid, created_invoices):
                if not invoice.invoice_line:
                    wf_service.trg_validate(uid, 'account.invoice', invoice.id, 'invoice_cancel', cr)
                    to_delete_invoices.append(invoice.id)

            self.pool.get('account.invoice').unlink(cr, uid, to_delete_invoices)

            created_invoices = list(set(created_invoices) - set(to_delete_invoices))

            if created_invoices:
                self.pool.get('account.invoice').button_compute(cr, uid, created_invoices, context=context, set_total=False) #computed created invoices

        return created_invoices

    def run_invoice(self, cr, uid, ids=False, context=None):
        """invoice all concepts in opened and invoiceable analytic accounts"""
        if context is None: context = {}

        #gets analytic account to eval
        ids = self.search(cr, uid, [('state', '=', 'open'), ('partner_id', '!=', False), ('invoiceable', '=', True), ('date_start', '<', context['end_date'])], order='create_date')

        created_invoices = self.run_invoice_cron_manual(cr, uid, ids, context)

        return True


account_analytic_account()
