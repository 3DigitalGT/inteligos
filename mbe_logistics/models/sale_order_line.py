# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import Many2one


class InheritSaleOrderLineLogistic(Model):
    """Herencia del objeto sale.order.line para logística"""
    _inherit = 'sale.order.line'
    _name = 'sale.order.line'

    package_id = Many2one(
        comodel_name="mbe_logistics.package",
        string="Paquete",
        help="Paquete incluido en la línea de la orden",
        tracking=3
    )
