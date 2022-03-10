from odoo import fields, models, tools


class InvoiceLines(models.Model):
    _name = "invoice.lines"
    _auto = False
    _rec_name = "ler_code_id"

    date = fields.Datetime("Date")
    partner_id = fields.Many2one(
        "res.partner", "Custumer/Supplier", readonly=True
    )
    quantity = fields.Float("Quantity", readonly=True)
    ler_code_id = fields.Many2one(
        "waste.ler.code", string="LER", readonly=True
    )
    product_id = fields.Many2one("product.product", "Product", readonly=True)
    m3 = fields.Float("m3", readonly=True)
    subtotal = fields.Float("subtotal", readonly=True)
    nif = fields.Char(
        related="partner_id.vat", string="N.I.F/C.I.F", readonly=True
    )
    company_id = fields.Many2one("res.company", "Company", readonly=True)
    city = fields.Char(related="partner_id.city", string="City", readonly=True)
    state_id = fields.Many2one(
        "res.country.state",
        related="partner_id.state_id",
        string="State",
        readonly=True,
    )
    manager_partner_id = fields.Many2one("res.partner", "Manager",
                                         readonly=True)
    picking_id = fields.Many2one("stock.picking", "Picking", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, "invoice_lines")
        self._cr.execute(
            """
            create or replace view invoice_lines as (
            SELECT SM.id AS id,SP.date,RP.commercial_partner_id as partner_id,
            case when SM.secondary_uom_qty != 0.0 then SM.secondary_uom_qty
            else SM.product_uom_qty end AS
            quantity,P2.ler_code_id,SM.product_id,SM.product_uom_qty AS m3,
            AIL.price_unit*AIL.quantity AS subtotal, SP.company_id,
            SW.partner_id as manager_partner_id, SP.id as picking_id
            FROM stock_move AS SM
                INNER JOIN stock_picking AS SP  ON SM.picking_id = SP.id
                INNER JOIN stock_picking_type as SPT on SP.picking_type_id =
                SPT.id
                INNER JOIN stock_warehouse SW on SW.id = SPT.warehouse_id
                INNER JOIN product_product AS P ON SM.product_id = P.id
                INNER JOIN product_template AS P2 ON P.product_tmpl_id = P2.id
                INNER JOIN res_partner RP on RP.id = SP.partner_id
                LEFT JOIN account_invoice_line as AIL on AIL.move_id = SM.id
            WHERE P2.ler_code_id is not null and SP.state = 'done'
                and SP.memory_include = true AND SPT.code = 'outgoing'
            )"""
        )
