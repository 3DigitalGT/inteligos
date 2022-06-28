# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import (Char, Float, Many2one)


class ShippingCost(Model):
    """Objeto para los gastos de envío logística"""
    _name = "shipping.cost"
    _description = "Gastos de envío en logística"

    name = Char(string="Descripción")
    price_usd = Float(string="Precio USD")
    price_unit = Float(string="Coste")
    product_id = Many2one(comodel_name="product.product", string="Producto")
    manifest_id = Many2one(comodel_name="mbe_logistics.manifest", string="Manifiesto", )
