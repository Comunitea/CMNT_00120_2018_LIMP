# -*- coding: utf-8 -*-
from odoo import models, api, fields


class HrEmployee(models.Model):

    _inherit = "hr.employee"

    # ~ @api.model
    # ~ def create(self, vals):

        # ~ if vals.get('active', False):
            # ~ vals['name_related'] = '[Desactivado]'+self.

        # ~ return super(Timesheet, self).create(vals)


    # ~ @api.multi
    # ~ def write(self, vals):

        # ~ for tobj in self:

            # ~ if vals.get('active', False):
            # ~ vals['name_related'] = '[Desactivado]'+tobj.n
            # ~ super(HrEmployee, tobj).write(vals)

        # ~ return True
