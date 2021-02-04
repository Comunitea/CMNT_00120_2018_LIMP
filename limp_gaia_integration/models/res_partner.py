# Copyright 2021 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    vialType = fields.\
        Selection([('001', 'Acceso'), ('002', 'Alameda'), ('003', 'Arrabal'),
                   ('004', 'Autopista'), ('005', 'Avenida'), ('006', 'Bajada'),
                   ('007', 'Barriada'), ('008', 'Barrio'), ('009', 'Calle'),
                   ('010', 'Calleja'), ('011', 'Callejón'),
                   ('012', 'Callejuela'), ('013', 'Calzada'),
                   ('014', 'Camino'), ('015', 'Canal'), ('016', 'Cañada'),
                   ('017', 'Carrera'), ('018', 'Carretera'), ('019', 'Carril'),
                   ('020', 'Colonia'), ('021', 'Complejo'),
                   ('022', 'Conjunto'), ('023', 'Corredor'),
                   ('024', 'Corredera'), ('025', 'Costanilla'),
                   ('026', 'Cuesta'), ('027', 'Escalinata'),
                   ('028', 'Extramuros'), ('029', 'Extrarradio'),
                   ('030', 'Galería'), ('031', 'Glorieta'), ('032', 'Parque'),
                   ('033', 'Pasadizo'), ('034', 'Pasaje'), ('035', 'Paseo'),
                   ('036', 'Plaza'), ('037', 'Plazoleta'), ('038', 'Plazuela'),
                   ('039', 'Polígono'), ('040', 'Prolongación'),
                   ('041', 'Pseudovía'), ('042', 'Puente'), ('043', 'Ramal'),
                   ('044', 'Rinconada'), ('045', 'Rincón'), ('046', 'Ronda'),
                   ('047', 'Rotonda'), ('048', 'Sector'), ('049', 'Senda'),
                   ('050', 'Sendero'), ('051', 'Subida'), ('052', 'Travesía'),
                   ('053', 'Vereda'), ('054', 'Vía'), ('055', 'Vial'),
                   ('999', 'Vía pública')], "Vial type")
    ler_authorization_ids = fields.One2many("res.partner.ler.authorization",
                                            "partner_id", "LER authorizations")
