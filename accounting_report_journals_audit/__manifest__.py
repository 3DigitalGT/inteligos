# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Accounting Report Audit Journal',
    'version': '1.1',
    'summary': 'Libro Diario',
    'sequence': 15,
    'description': """ Modulo de implementacion Libro Diario
    """,
    'category': 'Invoicing Management',
    'website': '',
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
