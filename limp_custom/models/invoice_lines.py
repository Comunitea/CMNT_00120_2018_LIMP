from odoo import fields, models, tools


class InvoiceLines(models.Model):
    _name = "invoice.lines"
    _auto = False
    _rec_name = "ler_code_id"

    date = fields.Date("Date")
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

    def init(self):
        tools.drop_view_if_exists(self._cr, "invoice_lines")
        self._cr.execute(
            """
            create or replace view invoice_lines as (
            SELECT SM.id AS id,SP.date,SP.partner_id,SM.product_uos_qty AS quantity,P2.ler_code_id,SM.product_id,SM.product_uom_qty AS m3, AIL.price_unit*AIL.quantity AS subtotal, SP.company_id
            FROM stock_move AS SM
                INNER JOIN stock_picking AS SP  ON SM.picking_id = SP.id
                INNER JOIN product_product AS P ON SM.product_id = P.id
                INNER JOIN product_template AS P2 ON P.product_tmpl_id = P2.id
                LEFT JOIN account_invoice_line as AIL on AIL.move_id = SM.id
            WHERE P2.ler_code_id is not null and SP.state = 'done' and SP.memory_include = true
            AND SP.picking_type_id in (select id from stock_picking_type where code='outgoing')
            )"""
        )
