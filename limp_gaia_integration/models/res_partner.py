# Copyright 2021 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields, exceptions


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
    association_type = fields.\
        Selection([('01', 'Sociedades anónimas'),
                   ('03', 'Sociedades colectivas'),
                   ('04', 'Sociedades comanditarias'),
                   ('05', 'Comunidades de bienes y herencias yacentes'),
                   ('06', 'Sociedades cooperativas'), ('07', 'Asociaciones'),
                   ('08', 'Comunidades de propietarios en régimen de '
                          'propiedad horizontal'),
                   ('10', 'Organismos públicos'),
                   ('11', 'Órganos de la Administración del Estado y de las '
                          'Comunidades Autónomas'),
                   ('18', 'Sociedades de responsabilidad limitada'),
                   ('19', 'Uniones Temporales de Empresas'),
                   ('25', 'Congregaciones e instituciones religiosas'),
                   ('26', 'Sociedades civiles, con o sin personalidad '
                          'jurídica'), ('27', 'Corporaciones Locales'),
                   ('28', 'Otros tipos no definidos en el resto de claves'),
                   ('29', 'Entidades extranjeras'),
                   ('30', 'Establecimientos permanentes de entidades no '
                          'residentes en España'), ('99', 'Otros')],
                  "Association type")



    @api.multi
    def get_authorization_id(self, lers, auth_types):
        self.ensure_one()
        temporaries = self.env['res.partner.ler.authorization']
        for authorization in self.ler_authorization_ids:
            if authorization.authorization_type[0] not in auth_types:
                continue
            if any(ler in lers for ler in authorization.ler_code_ids):
                return authorization
            elif authorization.other_state:
                temporaries |= authorization
        if temporaries:
            return temporaries[0]
        else:
            raise exceptions.UserError("La empresa {} no tiene una número "
                                       "de autorización válido del tipo {} y "
                                       "LER {}.".format(self.display_name,
                                                        auth_types,
                                                        lers.mapped('code')))

    @api.multi
    def check_gaia(self, part_type):
        for part in self:
            if not part.nima_no:
                raise exceptions.\
                    UserError("El {} no tiene establecido un NIMA".
                              format(part_type))
            elif part.nima_no[:2] != part.state_id.code:
                raise exceptions.\
                    UserError("En el {} los primeros dígitos del NIMA "
                              "no coinciden con el código de la provincia".
                              format(part_type))
            if not part.commercial_partner_id.association_type:
                raise exceptions.\
                    UserError("El {} no tiene establecido el tipo de "
                              "asociación".format(part_type))
            if not part.vialType:
                raise exceptions.\
                    UserError("El {} no tiene establecido el tipo de vía".
                              format(part_type))
            if not part.council_id:
                raise exceptions.\
                    UserError("El {} no tiene establecido el ayuntamiento".
                              format(part_type))
            if not part.zip:
                raise exceptions.\
                    UserError("El {} no tiene establecido el código postal".
                              format(part_type))
            if not part.street:
                raise exceptions.\
                    UserError("El {} no tiene establecida la dirección".
                              format(part_type))


class ResCompany(models.Model):

    _inherit = "res.company"

    gaia_test = fields.Boolean("Gaia Test", help="It is marked E3L's will be"
                               " generated in test mode.")
