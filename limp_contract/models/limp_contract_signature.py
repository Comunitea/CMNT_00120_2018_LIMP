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
from odoo import models, fields
import time


class limp_contract_signature(models.Model):

    _name = 'limp.contract.signature'
    _description = "Contract signature"

    contract_date = fields.Date('Signature date', required=True, defaults=fields.Date.today)

    def set_signature(self):
        contract = self.env['limp.contract'].browse(context['active_id'])
        contract.write({
            'signature_date': obj.contract_date,
            'state': 'open'
        })
        return {'type': 'ir.actions.act_window_close'}
