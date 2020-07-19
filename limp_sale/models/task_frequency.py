##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Marta Vázquez Rodríguez$
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


class TaskFrequency(models.Model):
    _name = "task.frequency"
    _description = "o2m to limp.contract.task"
    _order = "sequence asc"

    sale_id = fields.Many2one("sale.order", "Sale")
    task_id = fields.Many2one("limp.contract.task", "Task")
    description = fields.Char("Description", size=255)
    lu = fields.Boolean("LU", help="Lunes")
    ma = fields.Boolean("MA", help="Martes")
    mi = fields.Boolean("MI", help="Miércoles")
    ju = fields.Boolean("JU", help="Jueves")
    vi = fields.Boolean("VI", help="Viernes")
    sa = fields.Boolean("SA", help="Sábado")
    do = fields.Boolean("DO", help="Domingo")
    sm = fields.Boolean("SM", help="Semanal")
    qc = fields.Boolean("QC", help="Quincenal")
    m = fields.Boolean("M", help="Mensual")
    bt = fields.Boolean("BT", help="Bimestral")
    tr = fields.Boolean("TR", help="Trimestral")
    ct = fields.Boolean("CT", help="Cuatrimestral")
    st = fields.Boolean("ST", help="Semestral")
    an = fields.Boolean("AN", help="Anual")
    s_n = fields.Boolean("S/N", help="Según Necesidad")
    sequence = fields.Integer("Sequence", default=1)
