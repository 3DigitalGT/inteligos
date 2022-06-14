# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import (Many2one, Float)


class InheritResCompanyLogistic(Model):
    """Herencia del objeto res.company para logística"""
    _inherit = 'res.company'
    _name = 'res.company'

    logistic_weight_id = Many2one(
        comodel_name="product.product",
        string="Producto Peso",
        help="Campo para agregar el producto que se utilizara como el peso de logística",
        copy=True,
        store=True
    )
    logistic_clearance_id = Many2one(
        comodel_name="product.product",
        string="Producto Desaduanaje",
        help="Campo para agregar el producto que se utilizara para los gastos de desaduanaje",
        copy=True,
        store=True
    )
    logistic_employed_id = Many2one(
        comodel_name="product.product",
        string="Producto cargo cuenta ajena",
        help="Campo para agregar el producto que se utilizara para cargo cuenta ajena",
        copy=True,
        store=True
    )
    logistic_weight_factor = Float(
        string="Factor de Peso",
        help="Factor para cálculo de peso de Aduana",
        copy=True,
        store=True
    )
    logistic_admin_expenses_id = Many2one(
        comodel_name="product.product",
        string="Producto gastos administrativos",
        help="Campo para agregar el producto que se utilizara para los gastos administrativos (pago con TC)",
        copy=True,
        store=True
    )
    journal_receipt_employed_id = Many2one(
        comodel_name="account.journal",
        string="Diario para recibo cuenta ajena",
        help="Campo para agregar el diario que se utilizara para los recibos de cuenta ajena",
        copy=True,
        store=True
    )
