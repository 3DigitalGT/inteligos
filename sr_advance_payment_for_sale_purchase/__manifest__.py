# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

{
    'name': 'Anticipos proveedores y clientes',
    'version': '15.0.0.3',
    'category': 'Extra Addons',
    "license": "LGPL-3",
    'summary': 'Pagos Avanzados para ordenes de compra y ventas',
    'description': """Modulo utilizado para registrar pagos en clientes y proveedores """,
    'author': 'Sitaram',
    'website':"https://sitaramsolutions.in",
    'depends': ['base', 'sale_management', 'purchase'],
    'data': [
            'security/ir.model.access.csv',
             'views/sr_inherit_sale_order.xml',
             'views/sr_inherit_purchase_order.xml',
             'wizard/account_sale_advance_payment.xml',
             'wizard/account_purchase_advance_payment.xml'
    ],
    'installable': True,
    'auto_install': False,
    'live_test_url': 'https://youtu.be/w_cYaf52jeI',
    "images": ['static/description/banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
