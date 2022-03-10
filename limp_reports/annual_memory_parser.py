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
from odoo.addons.report_py3o.models.py3o_report import py3o_report_extender


def _get_valorization(self):
    dic = {}
    domain = [
        ("date", "<=", str(self.year) + "-12-31"),
        ("date", ">=", str(self.year) + "-01-01"),
        ("memory_include", "=", True),
        ("stock_picking_id", "!=", False),
        ("manager_partner_id", 'in', self.manager_partner_ids.ids),
        ("company_id", "=", self.company_id.id),
    ]
    objs = self.env["valorization.lines"].search(domain)

    for obj in objs:
        if obj.ler_code_id and not obj.ler_code_id.cpa:
            if obj.ler_code_id not in dic:
                dic[obj.ler_code_id] = obj.qty
            else:
                dic[obj.ler_code_id] += obj.qty
    res = []
    for k in dic.keys():
        res.append((k, dic[k]))
    return res


def _get_invoice(self, cpa):
    dic = {}
    domain = [
        ("date", "<=", str(self.year) + "-12-31"),
        ("date", ">=", str(self.year) + "-01-01"),
        ("manager_partner_id", 'in', self.manager_partner_ids.ids),
        ("company_id", "=", self.company_id.id),
    ]

    for obj in self.env["invoice.lines"].search(domain):
        if cpa:
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
        res.append((k, dic[k]))
    return res


def _get_total_qty(self):
    domain = [
        ("date", "<=", str(self.year) + "-12-31"),
        ("date", ">=", str(self.year) + "-01-01"),
        ("memory_include", "=", True),
        ("stock_picking_id", "!=", False),
        ("manager_partner_id", 'in', self.manager_partner_ids.ids),
        ("company_id", "=", self.company_id.id),
    ]
    total_qty = 0.0
    for obj in self.env["valorization.lines"].search(domain):
        if obj.ler_code_id and not obj.ler_code_id.cpa:
            total_qty += obj.qty
    return total_qty


def _get_total_qty2(self):
    domain = [
        ("date", "<=", str(self.year) + "-12-31"),
        ("date", ">=", str(self.year) + "-01-01"),
        ("manager_partner_id", 'in', self.manager_partner_ids.ids),
        ("company_id", "=", self.company_id.id),
    ]
    total_qty = 0.0
    for obj in self.env["invoice.lines"].search(domain):
        if obj.ler_code_id and not obj.ler_code_id.cpa:
            total_qty += obj.quantity
    return total_qty


def _get_ins(self, ler):
    res = []
    domain = [
        ("date", "<=", str(self.year) + "-12-31"),
        ("date", ">=", str(self.year) + "-01-01"),
        ("memory_include", "=", True),
        ("stock_picking_id", "!=", False),
        ("manager_partner_id", 'in', self.manager_partner_ids.ids),
        ("company_id", "=", self.company_id.id),
    ]
    res = {}
    for obj in self.env["valorization.lines"].sudo().search(domain):
        if (
            obj.ler_code_id.code == ler
            and not obj.ler_code_id.cpa
            and obj.building_site_id
        ):
            key = (
                (obj.building_site_id.producer_promoter or "")
                + (obj.building_site_id.vat_producer or "")
                + (obj.building_site_id.city_producer or "")
                + (obj.building_site_id.province_producer or "")
            )
            if res.get(key, False):
                res[key][1] += obj.qty
            else:
                res[key] = [obj.building_site_id, obj.qty]
        elif obj.ler_code_id.code == ler and not obj.ler_code_id.cpa:
            if res.get("X", False):
                res[obj.building_site_id][1] += obj.qty
            else:
                res["X"] = [obj.building_site_id, obj.qty]
    res = [(res[x][0], res[x][1]) for x in res]
    res.sort(key=lambda x: x[0].producer_promoter or "")
    return res


def _get_ins_total_qty(self, ler):
    res = 0
    domain = [
        ("date", "<=", str(self.year) + "-12-31"),
        ("date", ">=", str(self.year) + "-01-01"),
        ("memory_include", "=", True),
        ("manager_partner_id", 'in', self.manager_partner_ids.ids),
        ("stock_picking_id", "!=", False),
        ("company_id", "=", self.company_id.id),
    ]
    for obj in self.env["valorization.lines"].search(domain):
        if obj.ler_code_id.code == ler and not obj.ler_code_id.cpa:
            res += obj.qty
    return res


def _get_outs(self, cpa, ler):
    res = []
    domain = [
        ("date", "<=", str(self.year) + "-12-31"),
        ("date", ">=", str(self.year) + "-01-01"),
        ("manager_partner_id", 'in', self.manager_partner_ids.ids),
        ("company_id", "=", self.company_id.id),
    ]
    res = {}
    for obj in self.env["invoice.lines"].search(domain):
        if cpa:
            check = obj.ler_code_id and obj.ler_code_id.cpa
        else:
            check = obj.ler_code_id and not obj.ler_code_id.cpa
        if check:
            if obj.ler_code_id.code == ler:
                if res.get(obj.partner_id.commercial_partner_id, False):
                    res[obj.partner_id.commercial_partner_id][1] += obj.quantity
                else:
                    res[obj.partner_id.commercial_partner_id] = [obj,
                                                                 obj.quantity]
    res = [
        (x, res[x][0].city, res[x][0].state_id.name, res[x][1]) for x in res
    ]
    res.sort(key=lambda x: x[0].commercial_partner_id.name)
    return res


def _get_outs_total_qty(self, cpa, ler):
    res = 0
    domain = [
        ("date", "<=", str(self.year) + "-12-31"),
        ("date", ">=", str(self.year) + "-01-01"),
        ("manager_partner_id", 'in', self.manager_partner_ids.ids),
        ("company_id", "=", self.company_id.id),
    ]
    for obj in self.env["invoice.lines"].search(domain):
        if cpa:
            check = obj.ler_code_id and obj.ler_code_id.cpa
        else:
            check = obj.ler_code_id and not obj.ler_code_id.cpa
        if check:
            if obj.ler_code_id.code == ler:
                res += obj.quantity
    return res


@py3o_report_extender("limp_reports.aeroo_annual_memory_id")
def annual_memory(report_xml, localcontext):
    localcontext.update(
        {
            "get_valorization": _get_valorization,
            "get_invoice": _get_invoice,
            "get_total_qty": _get_total_qty,
            "get_total_qty2": _get_total_qty2,
            "get_ins": _get_ins,
            "get_ins_total_qty": _get_ins_total_qty,
            "get_outs": _get_outs,
            "get_outs_total_qty": _get_outs_total_qty,
        }
    )
