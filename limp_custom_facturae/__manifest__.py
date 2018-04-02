# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Limp facturae customizations',
    'summary': '',
    'version': '10.0.1.0.0',
    'category': 'Uncategorized',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'base',
        'l10n_es_facturae'
    ],
    'data': [
        'views/res_partner.xml',
        'views/account_invoice.xml',
        'views/report_facturae.xml'
    ],
}
