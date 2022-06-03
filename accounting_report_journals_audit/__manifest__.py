# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Libro Diario',
    'version': '1.1',
    'summary': 'Modulo para impresion del libro diario',
    'sequence': 15,
    'description': """ Modulo de implementacion Libro Diario
    """,
    'category': 'Invoicing Management',
    'author': "Inteligos, S.A.",
    'website': 'https://www.inteligos.gt',
    'depends' : ['account', 'base'],
    'data': [
        'report/journal_report_template.xml',
        'wizard/journals_audit_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "LGPL-3",
}
