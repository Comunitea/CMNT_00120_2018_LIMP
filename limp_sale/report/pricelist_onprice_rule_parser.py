# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$ omar@pexego.es
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from report import report_sxw
from osv import osv
import pooler
from tools.translate import _
class product_pricelist(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(product_pricelist, self).__init__(cr, uid, name, context=context)
        self.quantity=[]
        self.user = uid
        currency_obj = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id
        self.localcontext.update({
            'time': time,
            'get_state': self._get_state,
            'get_categories': self._get_categories,
            'get_price': self._get_price,
            'get_titles': self._get_titles,
            'currency_name': currency_obj.name,
            'currency_symbol': currency_obj.symbol
        })

    def _get_titles(self,form):
        lst = []
        vals = {}
        qtys = 1

        for i in range(1,6):
            if form['qty'+str(i)]!=0:
                vals['qty'+str(qtys)] = str(form['qty'+str(i)]) + ' units'
            qtys += 1
        lst.append(vals)
        return lst

    def _set_quantity(self,form):
        for i in range(1,6):
            q = 'qty%d'%i
            if form[q] >0 and form[q] not in self.quantity:
                self.quantity.append(form[q])
            else:
                self.quantity.append(0)
        return True

    def _get_state(self, state_id):
        pool = pooler.get_pool(self.cr.dbname)
        state_data = pool.get('res.country.state').read(self.cr, self.uid, [state_id], ['name'], context=self.localcontext)[0]
        return state_data['name']

    def _get_categories(self, products,form):
        cat_ids=[]
        res=[]
        state = form['state_id']
        self._set_quantity(form)
        pool = pooler.get_pool(self.cr.dbname)
        pro_ids=[]
        for product in products:
            pro_ids.append(product.id)
            if product.categ_id.id not in cat_ids:
                cat_ids.append(product.categ_id.id)

        cats = pool.get('product.category').name_get(self.cr, self.uid, cat_ids, context=self.localcontext)
        if not cats:
            return res
        for cat in cats:
            product_ids=pool.get('product.product').search(self.cr, self.uid, [('id', 'in', pro_ids), ('categ_id', '=', cat[0])], context=self.localcontext)
            products = []
            for product in pool.get('product.product').read(self.cr, self.uid, product_ids, ['name', 'code'], context=self.localcontext):
                val = {
                     'id':product['id'],
                     'name':product['name'],
                     'code':product['code']
                }
                i = 1
                for qty in self.quantity:
                    if qty == 0:
                        val['qty'+str(i)] = 0.0
                    else:
                        val['qty'+str(i)]=self._get_price(state, product['id'], qty, form['price_list'])
                    i += 1
                products.append(val)
            res.append({'name':cat[1],'products': products})
        return res

    def _get_price(self, state_id, product_id, qty, pricelist=False):
        sale_price_digits = self.get_digits(dp='Sale Price')
        pool = pooler.get_pool(self.cr.dbname)
        product = pool.get('product.product').browse(self.cr, self.uid, product_id)

        price = product.list_price
        rules = product.price_rule_ids
        global_rules = [x for x in rules if not x.province]
        state_rules = [x for x in rules if x.province and x.province.id == state_id]
        for rule in state_rules or global_rules:
            if qty >= rule.range:
                price = rule.price
            
        if pricelist:
            pricelist_price = self.pool.get('product.pricelist').apply_pricelist_to_price(self.cr, self.uid, [pricelist], price, product_id, qty)
            if pricelist_price:
                price = pricelist_price

        price = self.formatLang(price, digits=sale_price_digits)

        return price

report_sxw.report_sxw('report.product.pricelist.onprice.rule','product.product','addons/limp_sale/report/product_pricelist_onprice_rule.rml',parser=product_pricelist)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

