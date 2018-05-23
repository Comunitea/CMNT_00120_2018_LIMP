# -*- coding: utf-8 -*-
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
from odoo import models, fields, api


class Timesheet(models.Model):

    _inherit = 'timesheet'

    building_site_id = fields.Many2one('building.site.services', 'Building site/Service')

    @api.model
    def create(self, vals):
        if vals.get('analytic_id', False):
            picking_ids = self.env['stock.service.picking'].search([('analytic_acc_id', '=', vals['analytic_id'])])
            if picking_ids:
                if picking_ids[0].building_site_id:
                    vals['building_site_id'] = picking_ids[0].building_site_id.id
        return super(Timesheet, self).create(vals)

    @api.multi
    def write(self, vals):
        for tobj in self:
            picking_ids = self.env['stock.service.picking'].search([('analytic_acc_id', '=', vals.get('analytic_id', tobj.analytic_id.id))])
            if picking_ids:
                vals2 = dict(vals)
                if picking_ids[0].building_site_id:
                    vals2['building_site_id'] = picking_ids[0].building_site_id.id
                else:
                    vals2['building_site_id'] = False
                super(Timesheet, tobj).write(vals2)
            else:
                super(Timesheet, tobj).write(vals)

        return True
