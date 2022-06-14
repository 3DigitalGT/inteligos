# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import (Char, Selection, Many2one, Date, Float, One2many)
from odoo.api import model


class Manifest(Model):
    """Objeto para los manifiestos de logística"""
    _name = 'mbe_logistics.manifest'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Manifiesto MBE'
    _order = "name desc, id desc"

    name = Char(
        string="# Referencia",
        copy=False,
        tracking=3
    )
    state = Selection(
        selection=[
            ('prepared', 'Preparado'), ('in_transit', 'En Tránsito'),
            ('customs', 'Aduana'), ('in_warehouse', 'En Bodega')
        ],
        default="prepared",
        string="Estado", tracking=3
    )
    supplier_id = Many2one(
        comodel_name="res.partner",
        string="Proveedor",
        tracking=3,
    )
    carrier_id = Many2one(
        comodel_name="res.partner",
        string="Transportista",
        tracking=3
    )
    reference = Char(
        string="Referencia",
        tracking=3
    )
    guide_bl = Char(
        string="Guía/BL",
        tracking=3
    )
    dispatch_date = Date(
        string="Fecha de despacho",
        tracking=3
    )
    prepared_date = Date(
        string="Fecha Preparado",
        help="Conforme cambia el estado, agregar fecha a los campos de fechas acorde al estado",
        tracking=3
    )
    in_transit_date = Date(
        string="Fecha En Tránsito",
        help="Conforme cambia el estado, agregar fecha a los campos de fechas acorde al estado",
        tracking=3
    )
    customs_date = Date(
        string="Fecha Aduana",
        help="Conforme cambia el estado, agregar fecha a los campos de fechas acorde al estado",
        tracking=3
    )
    in_warehouse_date = Date(
        string="Fecha Entregado",
        help="Conforme cambia el estado, agregar fecha a los campos de fechas acorde al estado",
        tracking=3
    )
    transport_type = Selection(
        selection=[
            ('maritime', 'Marítimo'),
            ('air', 'Aéreo'),
            ('courier', 'Courier'),
            ('land', 'Terrestre')
        ],
        default="maritime",
        string="Transporte", tracking=3
    )
    package_ids = One2many(
        comodel_name="mbe_logistics.package",
        inverse_name="manifest_id",
        string="Paquetes",
        tracking=3
    )
    shipping_cost_ids = One2many(
        comodel_name="shipping.cost",
        inverse_name="manifest_id",
        string="Gastos de Envío",
        tracking=3
    )
    currency_id = Many2one(
        comodel_name="res.currency",
        string="Moneda",
        tracking=3,
        default=lambda self: self.env.ref('base.USD').id
    )
    exchange_rate = Float(
        string="Tasa de Cambio",
        digits=(12, 5)
    )

    @model
    def create(self, vals):
        """Sobreescritura de método genérico para obtener y asignar secuencia como valor para el campo name."""
        vals['name'] = self.env['ir.sequence'].next_by_code('mbe_logistics.manifest.sequence') or 'Nuevo'
        result = super(Manifest, self).create(vals)
        return result
