# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
#    $Javier Colmenero Fernández$
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

from openerp.osv import osv, fields
import os
import datetime,time
from mako.template import Template
from mako.lookup import TemplateLookup
from openerp.tools.translate import _
# import pooler MIGRACION: Comentado
import base64
from openerp.tools import config

class export_account_to_glasof(osv.osv_memory):

    _name = "export.account.to.glasof"

    _columns = {
        'file_xdiario': fields.binary("File xDiario", readonly=True),
        'xdiario_name': fields.char('Xdiario name', size=40, readonly=True),
        'file_xsubcta': fields.binary("File xSubCta", readonly=True),
        'xsubcta_name': fields.char('xSubCta name', size=40, readonly=True),
        'state' : fields.selection([('no_export', 'No Export'),('export', 'Exported')],'State',readonly=True),
        'account_length': fields.integer('Account length', required=True),
        'no_department': fields.boolean('No department')
    }
    _defaults = {
        'state' : 'no_export',
        'account_length': 11,
    }

    def format_acc_number(self, cr, uid, ids, num, ref):
        wiz = self.browse(cr, uid, ids[0])
        total_len = wiz.account_length
        var_len = total_len - len(ref)
        res = False
        if var_len > len(num):
            res = num.ljust(var_len,"0")
        else:
            res = num[:len(num)-(len(num)-var_len)]
        res += ref
        return res

    def format_normal_account(self, cr, uid, ids, account_id, delegation=False, department=False):
        wiz = self.browse(cr, uid, ids[0])
        nd = wiz.no_department
        total_len = wiz.account_length
        account_obj = self.pool.get('account.account').browse(cr, uid, account_id)
        parent_len = len(account_obj.parent_id.code)
        rjust_len = total_len - parent_len - ((delegation and not nd) and len(delegation.code) or 0) - ((department and not nd) and len(department.code) or 0)
        if len(account_obj.code) <= total_len:
            if account_obj.code.startswith('6') or account_obj.code.startswith('7'):
                new_account_code = account_obj.code[:parent_len] + ((delegation and not nd) and delegation.code or "") + account_obj.code[parent_len:].rjust(rjust_len, "0") + ((department and not nd) and department.code or "")
            else:
                new_account_code = account_obj.code[:parent_len] + "".rjust(total_len - len(account_obj.code), "0") + account_obj.code[parent_len:]
            if len(new_account_code) > total_len:
                raise osv.except_osv(_('Error'), _('New account code compound of departement and delegation code is bigger than selected account size.'))
            return new_account_code
        else:
            raise osv.except_osv(_('Error'), _('Selected account size smaller than the size of real accounts'))

    def export_account_moves(self, cr, uid, ids, context=None):

        if context is None: context = {}
        errors_list = set()
        wiz = self.browse(cr, uid, ids[0])
        tmp_path = config.get('root_path', os.getcwd())+"/addons/limp_account_export_glasof/wizard/templates/"
        objects = self.pool.get('account.move').browse(cr, uid, context.get('active_ids',[]))
        move_lines=[]
        acc_numbers = {}
        for move in objects:
            for line in move.line_id:
                if line.partner_id and (line.account_id.code.startswith('40') or line.account_id.code.startswith('41') or line.account_id.code.startswith('43')):
                    if not line.partner_id.ref:
                        errors_list.add(_('The partner %s has not field ref. Please fill this field and try again.') % line.partner_id.name)
                    else:
                        acc_numbers[line.id] = wiz.format_acc_number(line.account_id.code,line.partner_id.ref)
                else:
                    acc_numbers[line.id] = wiz.format_normal_account(line.account_id.id, line.delegation_id, line.department_id)
                move_lines.append(line)

        if errors_list:
            raise osv.except_osv(_("Error"), "\n\n".join(list(errors_list)))
        move_lines = sorted(move_lines, key=lambda x: (x.move_id.id,x.partner_id.id,x.account_id.code))
        pool = pooler.get_pool(cr.dbname)
        mylookup = TemplateLookup( input_encoding='utf-8', output_encoding='utf-8', encoding_errors='replace')
        tmp = Template(filename=tmp_path+"xdiario_template.txt", lookup=mylookup, default_filters=['decode.utf8'])
        doc = tmp.render_unicode(objects=move_lines, acc_numbers = acc_numbers, pool=pool, cr=cr, uid=uid, formatAccount=wiz.format_acc_number).encode('utf-8','replace')

        partners = set()
        acc_numbers = {}
        for move in objects:
            for line in move.line_id:
                receiv_acc = line.partner_id.property_account_receivable.code
                pay_acc = line.partner_id.property_account_payable.code
                move_acc = line.account_id.code
                if move_acc in [pay_acc,receiv_acc]:
                    if not line.partner_id.ref:
                        raise osv.except_osv(_('Error'), _('The partner %s has not field ref. Please fill this field and try again.') % line.partner_id.name)

                    acc_numbers[line.partner_id.id] = wiz.format_acc_number(move_acc,line.partner_id.ref)
                    partners.add(line.partner_id.id)

        objects = self.pool.get('res.partner').browse(cr, uid, list(partners))
        tmp = Template(filename=tmp_path+"xsubcta_template.txt", lookup=mylookup, default_filters=['decode.utf8'])
        doc2 = tmp.render_unicode(objects=objects,acc_numbers = acc_numbers,pool=pool,cr=cr,uid=uid).encode('utf-8','replace')

        xdiario_base64 = base64.b64encode(doc)
        xsubcta_base64 = base64.b64encode(doc2)
        wiz.write({ 'file_xdiario' : xdiario_base64 ,'file_xsubcta' : xsubcta_base64, 'state' : 'export', 'xdiario_name': "xDiario.txt", 'xsubcta_name': "xSubCta.txt" })

        return
export_account_to_glasof()
