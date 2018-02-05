# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 Pexego Sistemas Informáticos. All Rights Reserved
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

from openerp import models, fields

class update_last_invoice_date(models.TransientModel):

    _name = "update.last.invoice.date"

    _columns = {
        'new_date': fields.date('New date', required=True)
    }

    def update_date(self, cr, uid, ids, context=None):
        if context is None: context = {}

        contract_ids = context.get('active_ids', [])
        obj = self.browse(cr, uid, ids[0])

        if contract_ids:
            for contract in self.pool.get('limp.contract').browse(cr, uid, contract_ids):
                if contract.active and contract.state not in ['close', 'cancelled']:
                    for concept in contract.analytic_account_id.concept_ids:
                        concept.write({'last_invoice_date': obj.new_date})

                    for home_line in contract.home_help_line_ids:
                        if home_line.state != 'cancelled' and (home_line.state != 'close' or home_line.date > obj.new_date):
                            for concept in home_line.analytic_acc_id.concept_ids:
                                if home_line.date_start >= obj.new_date:
                                    concept.write({'last_invoice_date': False})
                                else:
                                    concept.write({'last_invoice_date': obj.new_date})
                            if home_line.state == 'close':
                                home_line.reopen_line()
                    for clean_line in contract.cleaning_line_ids:
                        if clean_line.state != 'cancelled' and (clean_line.state != 'close' or clean_line.date > obj.new_date):
                            for concept in clean_line.analytic_acc_id.concept_ids:
                                if clean_line.date_start >= obj.new_date:
                                    concept.write({'last_invoice_date': False})
                                else:
                                    concept.write({'last_invoice_date': obj.new_date})
                            if clean_line.state == 'close':
                                clean_line.reopen_line()

        return {'type': 'ir.actions.act_window_close'}

update_last_invoice_date()
