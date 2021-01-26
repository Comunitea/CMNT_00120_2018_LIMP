# Copyright 2021 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openupgradelib import openupgrade

COM_AUTO = {'00': '', '01': '16', '02': '08', '03': '10', '04': '01',
            '05': '07', '06': '11', '07': '04', '08': '09', '09': '07',
            '10': '11', '11': '01', '12': '10', '13': '08', '14': '01',
            '15': '12', '16': '08', '17': '09', '18': '01', '19': '08',
            '20': '16', '21': '01', '22': '02', '23': '01', '24': '07',
            '25': '09', '26': '17', '27': '12', '28': '13', '29': '01',
            '30': '14', '31': '15', '32': '12', '33': '03', '34': '07',
            '35': '05', '36': '12', '37': '07', '38': '05', '39': '06',
            '40': '07', '41': '01', '42': '07', '43': '09', '44': '02',
            '45': '08', '46': '10', '47': '07', '48': '16', '49': '07',
            '50': '02', '51': '18', '52': '19'}


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    spain_id = env.ref('base.es').id
    for state in env['res.country.state'].search([('country_id', '=',
                                                   spain_id)]):
        region = env['res.country.region'].\
            search([('code', '=', COM_AUTO[state.code]),
                    ('country_id', '=', spain_id)], limit=1)
        if region:
            state.region_id = region.id
