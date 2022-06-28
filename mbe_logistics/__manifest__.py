# -*- coding: utf-8 -*-
{
    'name': "Logística MBE Guatemala",
    'summary': """
        Logística de importaciones MBE Guatemala    
    """,
    'description': """
       Logística de importaciones, pedidos de ventas y facturación MBE Guatemala.
    """,
    'author': "Intéligos, S. A.",
    'website': "https://www.inteligos.gt",
    'category': 'Operations',
    'version': '0.1',
    'depends': ['base', 'stock', 'sale_management', 'account', 'sale_purchase', 'sales_team', 'purchase_stock',
                'stock_landed_costs', 'purchase', 'stock_account', 'l10n_gt_td_generic_sale', 'l10n_gt_inteligos_fel'],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/main_menu.xml',
        'views/mbe_logistics_manifest_views.xml',
        'views/mbe_logistics_package_views.xml',
        'reports/mbe_invoice_report.xml',
        'reports/account_report_template_mbe.xml',
        'views/res_company.xml',
        'views/sale_order.xml',
        'views/account_move.xml',
        'wizards/fill_package_values_wiz_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3'
}
