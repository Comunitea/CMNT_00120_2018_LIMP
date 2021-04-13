# Copyright 2021 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class ResPartnerLerAuthorization(models.Model):

    _name = "res.partner.ler.authorization"
    _description = "Partner LER Authorization"

    name = fields.Char("Authorizatio no.", required=True)
    partner_id = fields.Many2one("res.partner", "Manager", required=True)
    ler_code_ids = fields.Many2many("waste.ler.code", string="Related LERs",
                                    required=True)
    other_state = fields.Selection([('01', 'En trámite'),
                                    ('02', 'No disponible')], "Other Status")
    authorization_type = fields.\
        Selection([('A01', 'A01 - Agente de residuos peligrosos'),
                   ('A02', 'A02 - Agente de residuos no peligrosos'),
                   ('E01', 'E01 - Gestor de tratamiento de residuos '
                    'peligrosos'),
                   ('E02', 'E02 - Gestor de tratamiento de residuos no '
                    'peligrosos'),
                   ('G01', 'G01 - Centro Gestor de residuos peligrosos'),
                   ('G02', 'G02- Centro Gestor intermedio de residuos '
                    'peligrosos (almacenamiento)'),
                   ('G04', 'G04 - Centro Gestor de residuos no peligrosos'),
                   ('G05', 'G05 - Centro Gestor intermedio de residuos no '
                    'peligrosos (almacenamiento)'),
                   ('G06', 'G06 - Plataforma logística de RAEE'),
                   ('N01', 'N01 - Negociante de residuos peligrosos'),
                   ('N02', 'N02 - Negociante de residuos no peligrosos'),
                   ('P01', 'P01 - Productor de residuos peligrosos'),
                   ('P02', 'P02 - Pequeño productor de residuos peligrosos'),
                   ('P03', 'P03 - Productor de residuos no peligrosos'),
                   ('P04', 'P04 - Actividad productora de Residuos No '
                    'Peligrosos en cantidad inferior a 1000 tn anuales y por '
                    'tanto no sometida al régimen de comunicación previa'),
                   ('P05', 'P05 - Poseedor de residuos y, por tanto, no '
                    'sometido a régimen de autorización o comunicación '
                    '(accidentes, obras puntuales, comunidades de vecinos, '
                    'ciudadanía...)'),
                   ('SCR', 'SCR - Sistema colectivo de Responsabilidad '
                    'ampliada'),
                   ('SIR', 'SIR - Sistema individual de Responsabilidad '
                    'ampliada'),
                   ('T01', 'T01 - Transportista de residuos peligrosos'),
                   ('T02', 'T02 - Transportista de residuos no peligrosos')],
                  "Authorization Type", required=True)
