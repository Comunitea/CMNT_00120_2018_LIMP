# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#    $Marta Vázquez Rodríguez$
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

from openerp.osv import osv
from openerp.tools.translate import _

###Se comenta la restricción desde el __init__.py

class service_order_toinvoice(osv.osv_memory):
    _inherit = 'service.order.toinvoice'

    def create_invoice(self, cr, uid, ids, context=None):
        for picking in self.pool.get('stock.service.picking').browse(cr, uid, context['active_ids']):
            if picking.contract_id:
                raise osv.except_osv(_('Error!'),
                    _('Picking %s is part of contract %s. You cannot invoice it  manually.') % (picking.name, picking.contract_id.name))

        return super(service_order_toinvoice, self).create_invoice(cr, uid, ids, context=context)

service_order_toinvoice()
