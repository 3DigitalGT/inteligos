# -*- coding: utf-8 -*-
{
    'name': "DMT PC COMPONENTES",
    'summary': """
        Tipo de componentes para pc""",
    'description': """
        Este modulo sirve para agregar toda la informacion pertinente 
        a los componentes de una PC de DMT
    """,
    'author': "Inteligos, S.A.",
    'website': "https://www.inteligos.gt/",
    'category': 'Sales',
    'version': '15.0',
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,

    'depends': ['base', 'sale_management'],

    'data': [
        'views/product_template.xml',
    ],
}
