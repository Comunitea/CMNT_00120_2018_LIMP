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

"""Object to register incidences"""

from osv import osv, fields
import decimal_precision as dp
import time

class limp_incidence(osv.osv):
    """Object to register incidences"""

    _name = "limp.incidence"
    _description = "Incidences"

    _columns = {
        'periodicity': fields.selection([('q', 'Quarterly'), ('ex', 'Exception'), ('w', 'Weekly'), ('bm', 'Bimonthly'), ('m', 'Monthly'), ('2m', 'Two months')], 'Frequency'),
        'incidence_date': fields.date('Date', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', required=True),
        'contract_line_id': fields.many2one('limp.contract.line', 'Contract line', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'department_id': fields.many2one("hr.department", 'Department'),
        'delegation_id': fields.many2one('res.delegation', 'Delegation'),
        'department_code': fields.related('department_id', 'code', string="Dep.", type="char", size=8, readonly=True),
        'picking_id': fields.many2one('stock.picking', 'Picking'),
        'employee_id': fields.many2one('hr.employee', 'Worker', required=True),
        'hours': fields.float('Hours'),
        'amount': fields.float('Amount', help="Amount per hours", digits_compute=dp.get_precision('Account'), readonly=True),
        'name': fields.char('Description', size=256, required=True),
        'next_date': fields.date('Next date'),
        'note': fields.text('Notes')
    }

    _defaults = {
        'periodicity': lambda *a: 'ex',
        'incidence_date': lambda *a: time.strftime('%Y-%m-%d'),
        'partner_id': lambda self, cr, uid, context: context.get('partner_id', False),
        'delegation_id': lambda self, cr, uid, context: context.get('delegation_id', False),
        'company_id': lambda self, cr, uid, context: context.get('company_id', False),
        'department_id': lambda self, cr, uid, context: context.get('department_id', False)
    }

limp_incidence()
