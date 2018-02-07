# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
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

"""Service pickings for Limpergal"""

from openerp.osv import osv, fields
import time
from openerp.addons.decimal_precision import decimal_precision as dp
# import netsvc MIGRACION: Comentado
from openerp.tools.translate import _

def base_calendar_id2real_id(base_calendar_id=None, with_date=False):
    """
    This function converts virtual event id into real id of actual event
    @param base_calendar_id: Id of calendar
    @param with_date: If value passed to this param it will return dates based on value of withdate + base_calendar_id
    """

    if base_calendar_id and isinstance(base_calendar_id, (str, unicode)):
        res = base_calendar_id.split('-')

        if len(res) >= 2:
            real_id = res[0]
            if with_date:
                real_date = time.strftime("%Y-%m-%d %H:%M:%S", \
                                 time.strptime(res[1], "%Y%m%d%H%M%S"))
                start = datetime.strptime(real_date, "%Y-%m-%d %H:%M:%S")
                end = start + timedelta(hours=with_date)
                return (int(real_id), real_date, end.strftime("%Y-%m-%d %H:%M:%S"))
            return int(real_id)

    return base_calendar_id and int(base_calendar_id) or base_calendar_id

class stock_service_picking(osv.osv):
    """Service pickings for Limpergal"""

    _name = "stock.service.picking"
    _description = "Service pickings"
    _inherits = {'account.analytic.account': "analytic_acc_id"}
    _order = "picking_date desc"

    def _get_picking(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('service.picking.invoice.concept').browse(cr, uid, ids):
            result[line.service_picking_id.id] = True
        return result.keys()

    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_ids, line.price,line.product_qty,line.product_id)['taxes']:
            val += c.get('amount', 0.0)
        return val

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}

        for picking in self.browse(cr, uid, ids):
            res[picking.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            am_tax = am_untax = 0.0
            #cur = picking.pricelist_id.currency_id
            for inv_cncpt in picking.service_invoice_concept_ids:
                am_untax += inv_cncpt.subtotal
                am_tax += self._amount_line_tax(cr, uid, inv_cncpt)
            if picking.product_sand_id and picking.sand_amount:
                for c in self.pool.get('account.tax').compute_all(cr, uid, picking.product_sand_id.taxes_id, picking.sand_amount,1,picking.product_sand_id)['taxes']:
                    am_tax += c.get('amount', 0.0)
                am_untax += picking.sand_amount
            #res[picking.id]['amount_tax'] = cur_obj.round(cr, uid, cur, am_tax)
            res[picking.id]['amount_tax'] = am_tax
            #res[picking.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur,am_untax)
            res[picking.id]['amount_untaxed'] = am_untax
            res[picking.id]['amount_total'] = res[picking.id]['amount_untaxed'] + res[picking.id]['amount_tax'] + (picking.taxes or 0.0)
        return res

    def _get_all_delegations(self, cr, uid, context=None):
        delegation_obj = self.pool.get('res.delegation')
        selection = []
        delegation_ids = delegation_obj.search(cr, 1, [], context=context)
        for delegation in delegation_obj.browse(cr, 1, delegation_ids,
                                                context=context):
            selection.append((str(delegation.id), delegation.name))
        return selection

    _columns = {
        'state': fields.selection([('draft', 'Draft'),('active', 'Active'),('closed', 'Closed'),('cancelled', 'Cancelled')], 'State', readonly=True),
        #'partner_id': fields.many2one('res.partner', 'Customer', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        #'address_id': fields.many2one('res.partner.address', 'Address', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'carrier_id': fields.many2one('res.partner', 'Carrier', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'manager_partner_id': fields.many2one('res.partner', 'Manager', help="Destination partner", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'manager_address_id': fields.many2one('res.partner', 'Address', help="Destination address", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'producer_mark': fields.selection([('small_producer', 'Small producer'),('producer', 'Producer')], 'Producer type', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'ccc_account_id': fields.many2one('res.partner.bank', 'Bank', states={'cancelled':[('readonly',True)]}),
        #'name': fields.char('Name', size=32, required=True, readonly=True),
        #'description': fields.char('Service', size=255, required=True, states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        #'employee_ids': fields.one2many('stock.service.picking.employees.rel', 'picking_id', string='Employees', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'service_ids': fields.one2many('stock.service.picking.line', 'picking_id', 'Transports', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'print_service_ids': fields.one2many('stock.service.picking.line', 'picking_id', 'Transports to print', readonly=True, domain=[('no_print', '=', False)]),
        'move_service_ids': fields.one2many('stock.service.picking.line', 'picking_id', 'Move transports', readonly=True, domain=[('type', '=', 'move')]),
        'remove_service_ids': fields.one2many('stock.service.picking.line', 'picking_id', 'Remove transports', readonly=True, domain=[('type', 'in', ['remove', 'inplant', 'move_to_plant','outstanding','aspirating','cleaning'])]),
        'carry_service_ids': fields.one2many('stock.service.picking.line', 'picking_id', 'Carry transports', readonly=True, domain=[('type', '=', 'carry')]),
        'picking_date': fields.date('Date', required=True, states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'retired_date': fields.date('Retired Date'),
        'note': fields.text('Note', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'warning': fields.text('Warning', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'product_id': fields.many2one('product.product', 'Product', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'ler_code_id': fields.many2one('waste.ler.code', 'LER', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'ler_name': fields.related('ler_code_id', 'name', string="Waste", readonly=True, type="char", size=256),
        'ler_dangerous': fields.related('ler_code_id', 'dangerous', readonly=True, type="boolean", string="Dangerous"),
        'gross_weight': fields.float('Gross (kg.)', digits=(12,2), help="Gross weight in Kg", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'tare': fields.float('Tare (kg.)', digits=(12,2), help="Tare in Kg.", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'net_weight': fields.float('Net (kg.)', digits=(12,2), help="Net weight in Kg.", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'volume': fields.float('Volume (m³)', digits=(12,2), help="Volume in m³", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'container_id': fields.many2one('container', 'Container', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'container_situation_id': fields.related('container_id', 'situation_id', relation='res.partner', readonly=True, type="many2one", string="Container situation"),
        'dcs_no': fields.char('DCS no.', size=24, states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'valorization': fields.boolean('Valorization', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'storage': fields.boolean('Storage', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'invoice_type': fields.selection([('toinvoice', 'To invoice'),('invoiced', 'Invoiced'),('noinvoice', 'No invoice')], 'Invoice state',states={'cancelled':[('readonly',True)]}),
        'holder_partner': fields.char('Holder / Builder',size=255, states={'cancelled':[('readonly',True)]}),
        'holder_address': fields.char('Address',size=148, states={'cancelled':[('readonly',True)]}),
        'producer_partner': fields.char('Producer', size=255, states={'cancelled':[('readonly',True)]}),
        'producer_address': fields.char('Producer Address',size=148, states={'cancelled':[('readonly',True)]}),
        'building_site_address_id': fields.many2one('res.partner', 'Building site address', states={'cancelled':[('readonly',True)]}),
        'building_site_city': fields.char('City', size=128, states={'cancelled':[('readonly',True)]}),
        'building_site_license': fields.char('License', size=64, states={'cancelled':[('readonly',True)]}),
        'building_site_id': fields.many2one('building.site.services', 'Building site/Service', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        #'address_invoice_id': fields.many2one('res.partner.address', 'Address invoice', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'building_site': fields.boolean('Building site', help="Demolition and building waste", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'rd_code': fields.char('R.D. 952/97', size=64, states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'overload_qty': fields.float('Overload', digits=(12,2), help="Overload in m³", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'invoice_date': fields.date('Invoice date', states={'cancelled':[('readonly',True)]}),
        'analytic_acc_id': fields.many2one("account.analytic.account", 'Analytic account', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        #'company_id': fields.many2one('res.company', 'Company', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        #'waste_type': fields.selection([('clean', 'Clean'),('dirty', 'Dirty')], 'Waste type', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        #'valorization_company_id': fields.many2one('res.company', 'Val. company', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        #'valorization_ler_code_id': fields.many2one('waste.ler.code', 'Val. LER', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        #'paint_cans_qty': fields.float('Paint cans', digits=(12,2), help="Quantity in m³", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        #'silicone_cans_qty': fields.float('Silicone cans', digits=(12,2), help="Quantity in m³", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        #'isolation_mat_qty': fields.float('Isolation m.', digits=(12,2), help="Quantity in m³", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'quality': fields.boolean('Quality', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        #'other_materials': fields.char('Other mat.', size=128, states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'service_type': fields.many2one('product.product',string='Service type', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'stock_picking_id': fields.one2many('stock.picking','stock_service_picking_id',string='Stock picking',states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal position',states={'cancelled':[('readonly',True)]}),
        'payment_term': fields.many2one('account.payment.term', 'Payment term',states={'cancelled':[('readonly',True)]}),
        'payment_mode': fields.many2one('payment.mode', 'Payment type',states={'cancelled':[('readonly',True)]}),
        'hours': fields.float('Hours',states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'service_invoice_concept_ids': fields.one2many('service.picking.invoice.concept', 'service_picking_id', 'Invoice concepts'),
        'other_concepts_ids': fields.one2many('service.picking.other.concepts.rel', 'service_picking_id', 'Other concepts'),
        'nima_no': fields.char('NIMA', size=255, states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'name_manager': fields.char('Name manager', size=255, states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'authorization_manager': fields.char('Authorization Manager', size=32, states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'picking_type': fields.selection([('wastes','Wastes'),('sporadic','Sporadic')], 'Type', change_default=True),
        'service_picking_valorization_ids': fields.one2many('service.picking.valorization.rel', 'service_picking_id', 'Valorization', states={'cancelled':[('readonly',True)]}),
        'service_move_ids': fields.one2many('service.picking.stock.move', 'service_picking_id', 'Consumptions', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        #'delegation_id': fields.many2one('res.delegation', 'Delegation', required=True, states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        #AÑADIDO PARA CALCULAR TOTALES
        'taxes': fields.float('Taxes', digits=(16,2)),
        'product_tax_id': fields.many2one('product.product', 'Product tax'),
        'sand_amount': fields.float('Amount', digits=(16,2)),
        'product_sand_id': fields.many2one('product.product', 'Sand Treatment'),
        'amount_untaxed': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Untaxed Amount',
            #~ store = {
                #~ 'stock.service.picking': (lambda self, cr, uid, ids, c={}: ids, ['service_invoice_concept_ids','sand_amount'], 10),
                #~ 'service.picking.invoice.concept': (_get_picking, ['price_unit', 'tax_id','product_qty'], 10),
            #~ },
            multi='sums', help="The amount without tax."),
        'amount_tax': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Taxes',
            #~ store = {
                #~ 'stock.service.picking': (lambda self, cr, uid, ids, c={}: ids, ['service_invoice_concept_ids','sand_amount'], 10),
                #~ 'service.picking.invoice.concept': (_get_picking,['price', 'tax_ids', 'product_qty'], 10),
            #~ },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Total with taxes',
            #~ store = {
                #~ 'stock.service.picking': (lambda self, cr, uid, ids, c={}: ids, ['service_invoice_concept_ids','taxes','sand_amount'], 10),
                #~ 'service.picking.invoice.concept': (_get_picking, ['price', 'tax_ids', 'product_qty'], 10),
            #~ },
            multi='sums', help="The total amount."),
        'picking_date': fields.date('Picking date', required=True),
        'service_id': fields.many2one('waste.service', 'Waste service', readonly=True),
        'intercompany': fields.boolean('Intercompay'),
        #'invoice_delegation_id': fields.many2one('res.delegation', 'Delegation', help="Delegation where inputs the cost"),
        'invoice_delegation_id': fields.selection(_get_all_delegations, string="Delegation", help="Delegation where inputs the cost"),
        'invoice_department_id': fields.many2one('hr.department', 'Department', help="Department where inputs the cost"),
        'invoice_responsible_id': fields.many2one('hr.employee', 'Responsible', help="Responsible who inputs the cost", domain=[('responsible', '=', True)]),
        'delivery_proof_no': fields.char('Delivery proof no.', size=128, readonly=True),
        'not_print_acceptation': fields.boolean('Not print acceptation', help="Not print acceptation in delivery waste check report"),
        'older': fields.boolean('Older'),
        'internal_notes': fields.text('Notes'),
        'planified': fields.boolean('Planified'),
        'container_placement': fields.selection([('on_street', 'On street'),('on_building', 'On building')], string="Container placement", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        'maintenance': fields.boolean('Maintenance'),
    }

    '''def browse(self, cr, uid, select, context=None, list_class=None, fields_process=None): MIGRACION: Parametros raros, logica imposible en nueva api?
        res = super(stock_service_picking,self).browse(cr, uid, select, context, list_class, fields_process)
        if isinstance(select, (int, long)):
            if res.invoice_delegation_id:
                res.invoice_delegation_id = self.pool.get('res.delegation').browse(cr, 1, int(res.invoice_delegation_id), context)
        else:
            for pick in res:
                if pick.invoice_delegation_id:
                    pick.invoice_delegation_id = self.pool.get('res.delegation').browse(cr, 1, int(pick.invoice_delegation_id), context)
        return res'''

    _defaults = {
        #'partner_id': lambda self, cr, uid, context: context.get('partner_id', False),
        #'address_id': lambda self, cr, uid, context: context.get('address_id', False),
        #'company_id': lambda self, cr, uid, context: context.get('company_id', False) or self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id and self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id or False,
        'fiscal_position': lambda self, cr, uid, context: context.get('fiscal_position', False),
        'payment_term': lambda self, cr, uid, context: context.get('payment_term', False),
        'payment_type': lambda self, cr, uid, context: context.get('payment_type', False),
        'container_placement': 'on_building',
        'ccc_account_id': lambda self, cr, uid, context: context.get('ccc_account_id', False),
        #'address_invoice_id': lambda self, cr, uid, context: context.get('address_invoice_id', False),
        #'manager_partner_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid).company_id.partner_id.id,
        'name_manager': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid).company_id.partner_id.name,
        'authorization_manager': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid).company_id.partner_id.manager_authorization_no or False,
        #'manager_address_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid).company_id.partner_id.address_get() and self.pool.get('res.users').browse(cr, uid, uid).company_id.partner_id.address_get()['default'] or False,
        'picking_type': lambda self, cr, uid, context: context.get('type', 'wastes'),
        'name': 'SEQ',
        'picking_date': lambda *a: time.strftime("%Y-%m-%d"),
        'gross_weight': 0.0,
        'tare': 0.0,
        'net_weight': 0.0,
        'volume': 0.0,
        'valorization': True,
        'storage': False,
        'building_site': False,
        'overload_qty': 0.0,
        'state': 'draft',
        'invoice_type': 'toinvoice',
        'picking_date': lambda *a: time.strftime('%Y-%m-%d')
        #'delegation_id': lambda s, cr, uid, c: s.pool.get('res.users').browse(cr, uid, uid).context_delegation_id.id
    }



    def onchange_partner_id(self, cr, uid, ids, part, service_id):
        """manage on_change event in partner_id field"""
        user = self.pool.get('res.users').browse(cr, uid, uid)
        if service_id:
            service = self.pool.get('waste.service').browse(cr, uid, service_id)
            val = {
                'address_invoice_id': service.address_invoice_id and service.address_invoice_id.id or service.contact_id.id,
                'address_id': service.partner_shipping_id and service.partner_shipping_id.id or service.contact_id.id,
                'ccc_account_id': (service.payment_type and service.payment_type.suitable_bank_types and service.partner_bank_id) and part.partner_bank_id.id or False,
                'fiscal_position':service.fiscal_position and service.fiscal_position.id or False,
                'payment_term': service.payment_term and service.payment_term.id or False,
                'payment_type': service.payment_type and service.payment_type.id or False,
                'intercompany': False
            }
            part = service.partner_id

        else:
            if not part:
                return {'value': {'address_id': False, 'address_invoice_id': False, 'orig_address_id': False}}

            addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['contact', 'invoice', 'default'])
            part = self.pool.get('res.partner').browse(cr, uid, part)
            payment = part.payment_type_customer and part.payment_type_customer or False
            val = {
                'address_invoice_id': addr['invoice'],
                'address_id': addr['contact'],
                'ccc_account_id': (payment and payment.suitable_bank_types and part.bank_ids) and part.bank_ids[0].id or False,
                'fiscal_position':part.property_account_position and part.property_account_position.id or False,
                'payment_term': part.property_payment_term and part.property_payment_term.id or False,
                'payment_type': payment and payment.id or False,
                'intercompany': False
            }

        if user.company_id.partner_id.id == part.id:
            val['intercompany'] = True

        warning = {}
        if part.picking_warn_type != 'no-message':
            if part.picking_warn_type == 'block':
                raise osv.except_osv(_('Alert for %s !') % (part.name), part.picking_warn_message)
            title = _("Warning for %s") % part.name
            message = part.picking_warn_message
            warning['title'] = title
            warning['message'] = message
            val['warning'] = part.picking_warn_message
        return {'value': val, 'warning':warning}

    def onchange_manager_partner_id(self, cr, uid, ids, part):
        """manage on_change event in partner_manager_id field"""
        if not part:
            return {'value': {'manager_address_id': False}}
        nima = False
        addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['management_plant'])
        part = self.pool.get('res.partner').browse(cr, uid, part)
        if part.nima_no:
            nima = part.nima_no
        val = {
            'manager_address_id': addr['management_plant'],
            'nima_no': nima,
            'name_manager': part.name,
            'authorization_manager': part.manager_authorization_no and part.manager_authorization_no or False
        }

        return {'value': val}

    def onchange_ler_code_id(self, cr, uid, ids, ler_code_id):
        """fill related fields meanwhile it doesn't save"""
        res = {}
        if ler_code_id:
            ler_code_obj = self.pool.get('waste.ler.code').browse(cr, uid, ler_code_id)
            res = {'value': {'ler_name': ler_code_obj.name,  'ler_dangerous': ler_code_obj.dangerous}}

        return res

    def onchange_product_id(self, cr, uid, ids, product_id):
        """fills product ler code"""
        res = {}
        if not product_id:
             return res

        product_obj = self.pool.get('product.product').browse(cr, uid, product_id)
        if product_obj.ler_code_id:
            res = {'ler_code_id': product_obj.ler_code_id.id,
                             'ler_name': product_obj.ler_code_id.name,
                             'ler_dangerous': product_obj.ler_code_id.dangerous
                             }
        else:
            res = {'ler_code_id': False,
                             'ler_name': False,
                             'ler_dangerous': False
                             }

        warning = {}
        if product_obj.picking_warn != 'no-message':
            if product_obj.picking_warn == 'block':
                raise osv.except_osv(_('Alert for %s !') % (product_obj.name), product_obj.picking_warn_msg)
            title = _("Warning for %s") % product_obj.name
            message = product_obj.picking_warn_msg
            warning['title'] = title
            warning['message'] = message
        return {'value': res, 'warning':warning}


    def onchange_building_site_id(self, cr, uid, ids, part):
        res = {}
        if part:
            bui_site_serv_obj = self.pool.get('building.site.services').browse(cr, uid, part)
            if bui_site_serv_obj:
                address_id = bui_site_serv_obj.address_building_site.id
                city = bui_site_serv_obj.city_building_site
                license = bui_site_serv_obj.building_site_license
                holder = bui_site_serv_obj.holder_builder
                holder_address = bui_site_serv_obj.address_holder
                producer = bui_site_serv_obj.producer_promoter
                producer_address = bui_site_serv_obj.address_producer
                pricelist = bui_site_serv_obj.pricelist_id.id

                res = {'value': {'building_site_address_id': address_id,
                                 'building_site_city': city,
                                 'building_site_license': license,
                                 'holder_partner': holder,
                                 'holder_address': holder_address,
                                 'producer_partner': producer,
                                 'producer_address': producer_address,
                                 'pricelist_id': pricelist}}
        else:
            res = {'value': {'building_site_address_id': False,
                                 'building_site_city': False,
                                 'building_site_license': False,
                                 'holder_partner': False,
                                 'holder_address': False,
                                 'producer_partner': False,
                                 'producer_address': False,
                                 'pricelist_id': False}}

        return res
    def onchange_service_type(self, cr, uid, ids,service_type):
        """manage on_change event in service_type field"""
        if not service_type:
            return {'value': {}}
        val = {}
        product = self.pool.get('product.product').browse(cr,uid,service_type)
        warning = {}
        if product.picking_warn != 'no-message':
            if product.picking_warn == 'block':
                raise osv.except_osv(_('Alert for %s !') % (product.name), product.picking_warn_msg)
            title = _("Warning for %s") % product.name
            message = product.picking_warn_msg
            warning['title'] = title
            warning['message'] = message
        return {'value': val, 'warning':warning}

    def create(self, cr, uid, vals, context=None):
        """Add a sequence name"""
        if context is None: context = {}
        if not vals.get('maintenance'):
            seq = self.pool.get('ir.sequence').get(cr, uid, 'stock.service.picking')
        else:
            seq = self.pool.get('ir.sequence').get(cr, uid, 'service.picking.maintenance')
        vals['name'] = seq
        res = super(stock_service_picking, self).create(cr, uid, vals)
        self.write(cr, uid, [res], {'state': 'draft'})
        return res

    def action_active(self, cr, uid, ids, context=None):
        """set active state"""
        if context is None: context = {}

        return self.write(cr, uid, ids, {'state': 'active'})

    def create_concept_lines(self,cr,uid,ids,context=None):
        if context is None: context = {}

        for order in self.browse(cr,uid,ids,context=context):
            if order.service_invoice_concept_ids:
                self.pool.get("service.picking.invoice.concept").unlink(cr,uid,[x.id for x in order.service_invoice_concept_ids])

            mod_obj= self.pool.get('ir.model.data')
            seq = 1
            for waste in order.service_picking_valorization_ids:
                if waste.billable:
                    if waste.product_qty and waste.product_id:
                        vals = {}
                        vals = {
                        'sequence': seq,
                        'product_id': waste.product_id.id,
                        'name': waste.name,
                        'product_qty': waste.product_qty,
                        'product_uom': waste.product_id.uom_id.id,
                        'price': waste.product_id.list_price,
                        'service_picking_id': order.id,
                        'tax_ids': [(6,0,[x.id for x in waste.product_id.taxes_id])]
                        }
                        vals['price'] = self.pool.get('product.product').get_price_product(cr, uid, [waste.product_id.id], order.address_id.id, waste.product_qty, order.pricelist_id and order.pricelist_id.id or False,
                        context={'date': order.retired_date or order.picking_date})

                        self.pool.get('service.picking.invoice.concept').create(cr, uid, vals)
                        seq += 1

                if waste.overload_qty and (waste.product_id and waste.product_id.overload_price):
                    vals = {}
                    vals = {
                    'product_id': waste.product_id.id,
                    'sequence': seq,
                    'name': _('Overload/') + self.pool.get('product.product').name_get(cr, uid, [waste.product_id.id], context=context)[0][1],
                    'product_qty': waste.overload_qty,
                    'product_uom': waste.product_id.uom_id.id,
                    'price': waste.product_id.overload_price,
                    'service_picking_id': order.id,
                    'tax_ids': [(6,0,[x.id for x in waste.product_id.taxes_id])]
                    }

                    self.pool.get('service.picking.invoice.concept').create(cr, uid, vals)
                    seq += 1

            for other_concept in order.other_concepts_ids:
                if other_concept.billable:
                    vals = {}
                    vals = {
                    'sequence': seq,
                    'product_id': other_concept.product_id.id,
                    'name': other_concept.name,
                    'product_qty': other_concept.product_qty,
                    'product_uom': other_concept.product_id.uom_id.id,
                    'price': other_concept.price_unit,
                    'service_picking_id': order.id,
                    'tax_ids': [(6,0,[x.id for x in other_concept.product_id.taxes_id])]
                    }

                    self.pool.get('service.picking.invoice.concept').create(cr, uid, vals)
                    seq += 1

        return True

    def action_close(self, cr, uid, ids, context=None):
        """set active state"""
        if context is None: context = {}
        mod_obj= self.pool.get('ir.model.data')
        for order in self.browse(cr,uid,ids):
            for line in order.service_ids:
                if line.state != "done":
                    raise osv.except_osv(_('Error !'), _('Cannot close because you have transports in draft state.'))

            picking_id = False
            location_id = False
            location_dest_id = False
            move_ids = []

            if order.intercompany and not order.no_quality:
                raise osv.except_osv(_('Error !'), _('Cannot close because you have checked intercompany and you have not checked scont.'))

            if order.picking_type == "wastes" and not order.retired_date:
                retired_date = False
                for line in order.remove_service_ids:
                    if not retired_date or retired_date < line.transport_date[:10]:
                        retired_date = line.transport_date

                if retired_date:
                    order.write({'retired_date':retired_date})
                else:
                    raise osv.except_osv(_('Error !'), _('You are trying to close a service picking without retired date.'))
            elif order.picking_type == "wastes" and order.retired_date:
                for line in order.remove_service_ids:
                    if order.retired_date < line.transport_date[:10]:
                        raise osv.except_osv(_('Error !'), _('You are trying to close a service picking with wrong retired date.'))
                if order.retired_date < order.picking_date:
                    raise osv.except_osv(_('Error !'), _('You are trying to close a service picking with wrong retired date.'))
            elif order.picking_type == "sporadic":
                order.write({'retired_date': order.picking_date})

            company_list = self.pool.get('res.company').search(cr,1,[('partner_id', '=', order.manager_partner_id.id)])
            if company_list:
                current_company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
                company = self.pool.get('res.company').browse(cr, 1, company_list[0])
                if current_company.id == company.id:
                    addr = order.address_id.id
                else:
                    addr = current_company.partner_id.address[0].id

                location_id = mod_obj.get_object_reference(cr,uid,'stock','stock_location_customers')[1]
                warehouse_ids = self.pool.get('stock.warehouse').search(cr, 1, [('company_id', '=', company_list[0])])
                if not warehouse_ids:
                    raise osv.except_osv(_('Error !'), _('There is no wharehouse to the order company'))
                location_dest_id = self.pool.get('stock.warehouse').browse(cr, 1, warehouse_ids[0]).lot_stock_id.id

                for valorization_line in order.service_picking_valorization_ids:
                    if valorization_line.overload_qty and (valorization_line.product_id and not valorization_line.product_id.overload_price):
                        raise osv.except_osv(_('Error !'), _('You are trying to close a service picking with overload quantity but the product has not the overload price. Please fill it!'))

                    if not picking_id:
                        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in')
                        picking_id = self.pool.get('stock.picking').create(cr, 1, {
                                    'name': u'S' + pick_name,
                                    'origin': order.name,
                                    'type': 'in',
                                    'state': 'auto',
                                    'address_id': addr,
                                    'no_quality': order.no_quality,
                                    'company_id': company.id,
                                    'stock_service_picking_id': order.id,
                                    'from_spicking' : True,
                                    'date': order.retired_date or order.picking_date,
                                    'invoice_state' : current_company.id == company.id and 'none' or'2binvoiced'
                                })

                    if (valorization_line.product_id.company_id.id == company.parent_id.id) or (valorization_line.product_id.company_id.id == False) or (valorization_line.product_id.company_id.id == company_list[0]):
                        move_id = self.pool.get('stock.move').create(cr, 1, {
                                'name': order.name,
                                'picking_id': picking_id,
                                'product_id': valorization_line.product_id.id,
                                'product_qty': valorization_line.product_qty + valorization_line.overload_qty,
                                'product_uom': valorization_line.product_id.uom_id.id,
                                'address_id': addr,
                                'location_id': location_id,
                                'location_dest_id':location_dest_id,
                                'tracking_id': False,
                                'date': order.retired_date or order.picking_date,
                                'date_expected': order.retired_date or order.picking_date,
                                'state': 'draft',
                                'company_id': company_list[0],
                            })
                        move_ids.append(move_id)

                        self.pool.get('stock.move').action_confirm(cr, 1, [move_id])
                        self.pool.get('stock.move').force_assign(cr, 1, [move_id])
                    else:
                        raise osv.except_osv(_('Error !'), _('Product %s must be shared inter companies for proceeding') % valorization_line.product_id.name)

                if picking_id:
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(1, 'stock.picking', picking_id, 'button_confirm', cr)
                    self.pool.get('stock.picking').action_move(cr, 1, [picking_id])
                    wf_service.trg_validate(1, 'stock.picking', picking_id, 'button_done', cr)
                    self.pool.get('stock.move').write(cr, 1, move_ids, {'date': order.retired_date or order.picking_date})
            order.analytic_acc_id.write({'state': 'close', 'date': order.retired_date or order.picking_date})

        self.create_concept_lines(cr, uid, ids, context=context)
        return self.write(cr, uid, ids, {'state': 'closed'})

    def action_cancel(self, cr, uid, ids, context=None):
        if context is None: context = {}

        return self.write(cr,uid,ids,{'state': 'cancelled'})

    def action_draft(self, cr, uid, ids, context=None):
        if context is None: context = {}

        return self.write(cr,uid,ids,{'state':'draft'})

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'container_situation_id' : False,
            'product_id' : False,
            'ler_code_id' : False,
            'ler_name' : False,
            'analytic_acc_id': False,
            'ler_dangerous' : False,
            'gross_weight' : 0.0,
            'tare' : 0.0,
            'net_weight' : 0.0,
            'volume' : 0.0,
            'storage' : False,
            'overload_qty' : 0.0,
            'hours' : 0.0,
            'dcs_no' : False,
            'rd_code' : False,
            'nima_no ' : False,
            'name_manager' : False,
            'authorization_manager' : False,
            'note' : False,
            'ccc_account_id' : False,
            'fiscal_position' : False,
            'payment_term' : False,
            'payment_type' : False,
            'invoice_date' : False,
            'stock_picking_id' : [],
            'amount_untaxed' : 0.0,
            'amount_tax' : 0.0,
            'invoice_type': 'toinvoice',
            'amount_total' : 0.0,
            'retired_date': False,
            'picking_date': time.strftime('%Y-%m-%d'),
            'delivery_proof_no': False,
            'product_sand_id': False,
            'sand_amount': 0.0,
            'taxes': 0.0,
            'product_tax_id': False,
            'invoice_line_ids': False,
            'warning': False,
            'service_ids': [],
            'line_ids': [],
            'print_service_ids': [],
            'move_service_ids': [],
            'remove_service_ids': [],
            'carry_service_ids': [],
            'service_move_ids': [],
            'service_picking_valorization_ids': [],
            'other_concepts_ids': [],
            'service_invoice_concept_ids': [],
            'employee_ids': [],
            'active_employee_ids': [],
            'inactive_employee_ids': []
        })

        return super(stock_service_picking, self).copy(cr, uid, id, default, context)

    def copy_data(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({'service_invoice_concept_ids' : [],'employee_ids' : [], 'service_picking_valorization_ids' : [], 'service_ids' : [], 'service_move_ids': [], 'move_service_ids': [],
            'service_invoice_concept_ids' : [], 'remove_service_ids': [], 'carry_service_ids': [], 'stock_picking_id': [], 'other_concepts_ids': [], 'invoice_line_ids': [], 'line_ids': []})
        return super(stock_service_picking, self).copy_data(cr, uid, id, default, context)

stock_service_picking()
