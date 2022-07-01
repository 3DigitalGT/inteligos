# -*- coding: utf-8 -*-
{
    'name': "Series de Inventario para Productos",
    'summary': """
        Series de Transferencias de Inventario para Productos.
    """,
    'description': """
        Asignación, seguimiento e historial de series de Productos según Transferencias de Inventario.
    """,
    'author': "Inteligos, S.A.",
    'website': "https://www.inteligos.gt",
    'category': 'Inventory',
    'version': '0.1',
    'depends': ['base', 'sale', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_series_view.xml',
        'views/product_template_view.xml',
        'views/stock_picking_view.xml',
        'wizards/product_series_wiz.xml',
        'reports/report_delivery_document_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3'
}
