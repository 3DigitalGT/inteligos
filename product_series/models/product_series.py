# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import (Boolean, Many2one, Char, Integer, Datetime)


class ProductSeries(Model):
    _name = "product.series"
    _description = "Series de Inventario para Productos"

    name = Char(
        required=True,
        store=True,
        copy=False,
        string="Serie Producto"
    )
    stock_move_id = Many2one(
        comodel_name='stock.move',
        readonly=True,
        store=True,
        string="Movimiento inventario"
    )
    stock_picking_id = Many2one(
        comodel_name='stock.picking',
        readonly=True,
        store=True,
        string="Despacho"
    )
    partner_id = Many2one(
        comodel_name='res.partner',
        related='stock_picking_id.partner_id',
        store=True,
        string="Cliente"
    )
    date_done = Datetime(
        related='stock_picking_id.date_done',
        store=True,
        string="Fecha de despacho"
    )
    origin = Char(
        string='Documento Origen', index=True,
        related='stock_picking_id.origin',
        help="Referencia al documento", store=True)
    product_id = Many2one(
        comodel_name='product.product',
        readonly=True,
        store=True,
        string='Producto'
    )
    number = Integer(
        readonly=True,
        store=True,
        string="# Producto"
    )
    its_done = Boolean(
        default=False,
        store=True,
        string="Hecho"
    )
