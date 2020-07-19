from odoo import models, fields


class EquipmentToBeUsed(models.Model):

    _name = "equipment.to.be.used"

    name = fields.Char("Equipment", required=True)
    purpose_equipment = fields.Text("Purpose Equipment")
