from osv import fields,osv
import tools
class invoice_lines(osv.osv):
    _name = "invoice.lines"
    _auto = False
    _rec_name = 'ler_code_id'
    _columns = {
        'date': fields.date('Date'),
        'partner_id':fields.many2one('res.partner','Custumer/Supplier',readonly=True),
        #'address_id':fields.many2one('res.partner.address', 'Address', readonly=True),
        'quantity':fields.float("Quantity",readonly=True),
        'ler_code_id':fields.many2one('waste.ler.code',string="LER", readonly=True),
        'product_id':fields.many2one('product.product','Product',readonly=True),
        'm3':fields.float("m3",readonly=True),
        'subtotal':fields.float("subtotal",readonly=True),
        'nif':fields.related('partner_id','vat',string="N.I.F/C.I.F", readonly=True, type="char", size=256),
        'company_id':fields.many2one('res.company', "Company", readonly=True),
        'city':fields.related('partner_id','city',string="City", readonly=True, type="char", size=128),
        'state_id':fields.related('partner_id','state_id',string="State", readonly=True, type="many2one",relation="res.country.state"),

    }

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr,  "invoice_lines")
        #MIGRACION: se elimina address_id de la query
        cr.execute("""
            create or replace view invoice_lines as (
            SELECT SM.id AS id,SP.date,SP.partner_id,SM.product_uos_qty AS quantity,P2.ler_code_id,SM.product_id,SM.product_qty AS m3, AIL.price_unit*AIL.quantity AS subtotal, SP.company_id
            FROM stock_move AS SM
                INNER JOIN stock_picking AS SP  ON SM.picking_id = SP.id
                INNER JOIN product_product AS P ON SM.product_id = P.id
                INNER JOIN product_template AS P2 ON P.product_tmpl_id = P2.id
                LEFT JOIN account_invoice_line as AIL on AIL.move_id = SM.id
            WHERE SP.type = 'out' AND P2.ler_code_id is not null and SP.state = 'done' and SP.memory_include = true
            )""")
invoice_lines()
