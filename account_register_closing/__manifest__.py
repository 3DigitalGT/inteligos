# -*- coding: utf-8 -*-
{
    'name': "account_register_closing",

    'summary': """
        Modulo Cierre de Caja""",

    'description': """
        Permite realizar cierres de caja en el modulo de contabilidad
    """,

    'author': "Inteligos S.A.",
    'website': "https://www.inteligos.gt/",

    'category': 'Account Charts',
    'version': '15.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account', 'mail'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views_account_journal_closing.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'report/report_account_journal_closing.xml',
        'report/email_template_journal_closing.xml',
        'report/report_invoice.xml'

    ],

}
