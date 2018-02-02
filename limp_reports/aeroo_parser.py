##############################################################################
#
# Copyright (c) 2008-2011 Alistek Ltd (http://www.alistek.com) All Rights Reserved.
#                    General contacts <info@alistek.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This module is GPLv3 or newer and incompatible
# with OpenERP SA "AGPL + Private Use License"!
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from report import report_sxw
from report.report_sxw import rml_parse

#~ import lorem
#~ import random

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_valorization':self._get_valorization,
            'get_invoice':self._get_invoice,
            'get_total_qty':self._get_total_qty,
            'get_total_qty2':self._get_total_qty2,
            'get_ins':self._get_ins,
            'get_ins_total_qty':self._get_ins_total_qty,
            'get_outs':self._get_outs,
            'get_outs_total_qty':self._get_outs_total_qty
        })

    def _get_valorization(self):
        dic={}
        domain = [('date','<=',str(self.localcontext['data']['form']['year']) + '-12-31'),
        ('date','>=',str(self.localcontext['data']['form']['year']) + '-01-01'),('memory_include', '=', True),('stock_picking_id', '!=', False)]
        ids = self.pool.get('valorization.lines').search(self.cr,self.uid,domain)

        for obj in self.pool.get('valorization.lines').browse(self.cr,self.uid,ids):
            if obj.ler_code_id and not obj.ler_code_id.cpa:
                if obj.ler_code_id not in dic:
                    dic[obj.ler_code_id] = obj.qty
                else:
                    dic[obj.ler_code_id] += obj.qty
        res = []
        for k in dic.keys():
            res.append((k,dic[k]))
        return res

    def _get_invoice(self,cpa):
        dic={}
        domain = [('date','<=',str(self.localcontext['data']['form']['year']) + '-12-31'),
        ('date','>=',str(self.localcontext['data']['form']['year']) + '-01-01')]
        ids = self.pool.get('invoice.lines').search(self.cr,self.uid,domain)
        #import ipdb; ipdb.set_trace()
        for obj in self.pool.get('invoice.lines').browse(self.cr,self.uid,ids):
            if eval(cpa):
                check = obj.ler_code_id and obj.ler_code_id.cpa
            else:
                check = obj.ler_code_id and not obj.ler_code_id.cpa
            if check:
                if obj.ler_code_id not in dic:
                    dic[obj.ler_code_id] = obj.quantity
                else:
                    dic[obj.ler_code_id] += obj.quantity
        res = []
        for k in dic.keys():
            res.append((k,dic[k]))
        return res

    def _get_total_qty(self):
        domain = [('date','<=',str(self.localcontext['data']['form']['year']) + '-12-31'),
        ('date','>=',str(self.localcontext['data']['form']['year']) + '-01-01'),('memory_include', '=', True),('stock_picking_id', '!=', False)]
        ids = self.pool.get('valorization.lines').search(self.cr,self.uid,domain)
        #import ipdb; ipdb.set_trace()
        total_qty = 0.0
        for obj in self.pool.get('valorization.lines').browse(self.cr,self.uid,ids):
            if obj.ler_code_id and not obj.ler_code_id.cpa:
                total_qty += obj.qty
        return total_qty

    def _get_total_qty2(self):
        domain = [('date','<=',str(self.localcontext['data']['form']['year']) + '-12-31'),
        ('date','>=',str(self.localcontext['data']['form']['year']) + '-01-01')]
        ids = self.pool.get('invoice.lines').search(self.cr,self.uid,domain)
        #import ipdb; ipdb.set_trace()
        total_qty = 0.0
        for obj in self.pool.get('invoice.lines').browse(self.cr,self.uid,ids):
            if obj.ler_code_id and not obj.ler_code_id.cpa:
                total_qty += obj.quantity
        return total_qty

    def _get_ins(self,ler):
        res=[]
        domain = [('date','<=',str(self.localcontext['data']['form']['year']) + '-12-31'),
        ('date','>=',str(self.localcontext['data']['form']['year']) + '-01-01'),('memory_include', '=', True),('stock_picking_id', '!=', False)]
        ids = self.pool.get('valorization.lines').search(self.cr,self.uid,domain)
        res = {}
        for obj in self.pool.get('valorization.lines').browse(self.cr,1,ids):
            if obj.ler_code_id.code == ler and not obj.ler_code_id.cpa and obj.building_site_id:
                key = (obj.building_site_id.producer_promoter or "") + (obj.building_site_id.vat_producer or "") + (obj.building_site_id.city_producer or "") + (obj.building_site_id.province_producer or "")
                if res.get(key, False):
                    res[key][1] += obj.qty
                else:
                    res[key] = [obj.building_site_id, obj.qty]
            elif obj.ler_code_id.code == ler and not obj.ler_code_id.cpa:
                if res.get("X", False):
                    res[obj.building_site_id][1] += obj.qty
                else:
                    res["X"] = [obj.building_site_id, obj.qty]

        res = [(res[x][0],res[x][1]) for x in res]
        res.sort(lambda x,y: cmp(x[0].producer_promoter or "",y[0].producer_promoter or ""))
        return res

    def _get_ins_total_qty(self,ler):
        res=0
        domain = [('date','<=',str(self.localcontext['data']['form']['year']) + '-12-31'),
        ('date','>=',str(self.localcontext['data']['form']['year']) + '-01-01'),('memory_include', '=', True),('stock_picking_id', '!=', False)]
        ids = self.pool.get('valorization.lines').search(self.cr,self.uid,domain)
        #import ipdb; ipdb.set_trace()
        for obj in self.pool.get('valorization.lines').browse(self.cr,self.uid,ids):
            if obj.ler_code_id.code == ler and not obj.ler_code_id.cpa:
                res += obj.qty
        return res

    def _get_outs(self,cpa,ler):
        res=[]
        domain = [('date','<=',str(self.localcontext['data']['form']['year']) + '-12-31'),
        ('date','>=',str(self.localcontext['data']['form']['year']) + '-01-01')]
        ids = self.pool.get('invoice.lines').search(self.cr,self.uid,domain)
        res = {}
        for obj in self.pool.get('invoice.lines').browse(self.cr,self.uid,ids):
            if eval(cpa):
                check = obj.ler_code_id and obj.ler_code_id.cpa
            else:
                check = obj.ler_code_id and not obj.ler_code_id.cpa
            if check:
                if obj.ler_code_id.code == ler:
                    if res.get(obj.partner_id, False):
                        res[obj.partner_id][1] += obj.quantity
                    else:
                        res[obj.partner_id] = [obj, obj.quantity]
        res = [(x,res[x][0].city,res[x][0].state_id.name,res[x][1]) for x in res]
        res.sort(lambda x,y: cmp(x[0].name,y[0].name))
        return res

    def _get_outs_total_qty(self,cpa,ler):
        res=0
        domain = [('date','<=',str(self.localcontext['data']['form']['year']) + '-12-31'),
        ('date','>=',str(self.localcontext['data']['form']['year']) + '-01-01')]
        ids = self.pool.get('invoice.lines').search(self.cr,self.uid,domain)
        #import ipdb; ipdb.set_trace()
        for obj in self.pool.get('invoice.lines').browse(self.cr,self.uid,ids):
            if eval(cpa):
                check = obj.ler_code_id and obj.ler_code_id.cpa
            else:
                check = obj.ler_code_id and not obj.ler_code_id.cpa
            if check:
                if obj.ler_code_id.code == ler:
                    res += obj.quantity
        return res


