# -*- coding: utf-8 -*-
{
    'name': "Reportes MBE",

    'summary': """
        Modulo para los formatos de facturas y presupuestos MBE""",

    'description': """
        Formatos personalizados para MBE
    """,

    'author': "Intéligos, S. A.",
    'website': "https://www.inteligos.gt",
    'category': 'Operations',
    'version': '0.1',
    'depends': ['base', 'account_accountant'],

    'data': [
        'reports/sale_order_report.xml',

    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3'
}
