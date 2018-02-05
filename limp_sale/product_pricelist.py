# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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

from openerp import models, fields
import time
from tools.translate import _

class product_pricelist(models.Model):

    _inherit = "product.pricelist"

    def apply_pricelist_to_price(self, cr, uid, ids, price, product_id, qty, context=None):
        if context is None: context = {}

        date = time.strftime('%Y-%m-%d')
        if 'date' in context:
            date = context['date']

        def _create_parent_category_list(id, lst):
            if not id:
                return []
            parent = product_category_tree.get(id)
            if parent:
                lst.append(parent)
                return _create_parent_category_list(parent, lst)
            else:
                return lst

        product_obj = self.pool.get('product.product')
        product_category_obj = self.pool.get('product.category')

        product_pricelist_version_obj = self.pool.get('product.pricelist.version')

        pricelist_version_ids = list(set(ids))
        plversions_search_args = [
            ('pricelist_id', 'in', pricelist_version_ids),
            '|',
            ('date_start', '=', False),
            ('date_start', '<=', date),
            '|',
            ('date_end', '=', False),
            ('date_end', '>=', date),
        ]

        plversion_ids = product_pricelist_version_obj.search(cr, uid, plversions_search_args)
        if len(pricelist_version_ids) != len(plversion_ids):
            msg = _("At least one pricelist has no active version !\nPlease create or activate one.")
            raise osv.except_osv(_('Warning !'), msg)

        if product_id:
            product = product_obj.browse(cr, uid, product_id, context=context)
            product_category_ids = product_category_obj.search(cr, uid, [])
            product_categories = product_category_obj.read(cr, uid, product_category_ids, ['parent_id'])
            product_category_tree = dict([(item['id'], item['parent_id'][0]) for item in product_categories if item['parent_id']])

            for pricelist_id in pricelist_version_ids:
                tmpl_id = product.product_tmpl_id and product.product_tmpl_id.id or False

                categ_id = product.categ_id and product.categ_id.id or False
                categ_ids = _create_parent_category_list(categ_id, [categ_id])
                if categ_ids:
                        categ_where = '(categ_id IN (' + ','.join(map(str, categ_ids)) + '))'
                else:
                    categ_where = '(categ_id IS NULL)'

                cr.execute(
                    'SELECT i.*, pl.currency_id '
                    'FROM product_pricelist_item AS i, '
                        'product_pricelist_version AS v, product_pricelist AS pl '
                    'WHERE (product_tmpl_id IS NULL OR product_tmpl_id = %s) '
                        'AND (product_id IS NULL OR product_id = %s) '
                        'AND (' + categ_where + ' OR (categ_id IS NULL)) '
                        'AND price_version_id = %s '
                        'AND (min_quantity IS NULL OR min_quantity <= %s) '
                        'AND i.price_version_id = v.id AND v.pricelist_id = pl.id '
                    'ORDER BY sequence',
                    (tmpl_id, product_id, plversion_ids[0], qty))
                res1 = cr.dictfetchall()
                for res in res1:
                    if res:
                        if price is not False:
                            price_limit = price

                            price = price * (1.0+(res['price_discount'] or 0.0))
                            if res['price_round']:
                                price = round(price / res['price_round']) * res['price_round']
                            price += (res['price_surcharge'] or 0.0)
                            if res['price_min_margin']:
                                price = max(price, price_limit+res['price_min_margin'])
                            if res['price_max_margin']:
                                price = min(price, price_limit+res['price_max_margin'])
                            break

                    else:
                        # False means no valid line found ! But we may not raise an
                        # exception here because it breaks the search
                        price = False

        return price


product_pricelist()
