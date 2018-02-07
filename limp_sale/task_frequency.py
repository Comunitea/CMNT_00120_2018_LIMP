# -*- coding: utf-8 -*-
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
from osv import osv, fields

class task_frequency(osv.osv):
    _name = 'task.frequency'
    _description = 'o2m to limp.contract.task'
    # _rec_name = 'sale_id,task_id' MIGRACION: Error
    _order = "sequence asc"
    _columns = {
        'sale_id': fields.many2one('sale.order', 'Sale'),
        'task_id': fields.many2one('limp.contract.task', 'Task'),
        'description': fields.char('Description', size=255),
        'lu': fields.boolean('LU', help='Lunes'),
        'ma': fields.boolean('MA', help='Martes'),
        'mi': fields.boolean('MI', help='Miércoles'),
        'ju': fields.boolean('JU', help='Jueves'),
        'vi': fields.boolean('VI', help='Viernes'),
        'sa': fields.boolean('SA', help='Sábado'),
        'do': fields.boolean('DO', help='Domingo'),
        'sm': fields.boolean('SM', help='Semanal'),
        'qc': fields.boolean('QC', help='Quincenal'),
        'm': fields.boolean('M', help='Mensual'),
        'bt': fields.boolean('BT', help='Bimestral'),
        'tr': fields.boolean('TR', help='Trimestral'),
        'ct': fields.boolean('CT', help='Cuatrimestral'),
        'st': fields.boolean('ST', help='Semestral'),
        'an': fields.boolean('AN', help='Anual'),
        's_n': fields.boolean('S/N', help='Según Necesidad'),
        'sequence': fields.integer('Sequence')
    }

    _defaults = {
        'sequence': lambda *a: 1
    }

task_frequency()
