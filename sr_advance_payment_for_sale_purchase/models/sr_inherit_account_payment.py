# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import models, fields, _


class SrAccountPayment(models.Model):
    """Herencia del modulo account.payment"""

    _inherit = "account.payment"

    sale_order_id = fields.Many2one('sale.order', string="Ordenes de Venta")
    purchase_order_id = fields.Many2one('purchase.order', string="Ordenes de Compra")
