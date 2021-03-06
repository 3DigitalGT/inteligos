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
        store=True
    )
    state = Selection(
        selection=[
            ('prepared', 'Preparado'), ('in_transit', 'En Tránsito'),
            ('customs', 'Aduana'), ('in_warehouse', 'En Bodega')
        ],
        default="prepared",
        string="Estado"
    )
    supplier_id = Many2one(
        comodel_name="res.partner",
        string="Proveedor",
        store=True
    )
    carrier_id = Many2one(
        comodel_name="res.partner",
        string="Transportista",
        store=True
    )
    reference = Char(
        string="Referencia",
        store=True
    )
    guide_bl = Char(
        string="Guía/BL",
        store=True
    )
    dispatch_date = Date(
        string="Fecha de despacho",
        store=True
    )
    prepared_date = Date(
        string="Fecha Preparado",
        help="Conforme cambia el estado, agregar fecha a los campos de fechas acorde al estado",
        store=True
    )
    in_transit_date = Date(
        string="Fecha En Tránsito",
        help="Conforme cambia el estado, agregar fecha a los campos de fechas acorde al estado",
        store=True
    )
    customs_date = Date(
        string="Fecha Aduana",
        help="Conforme cambia el estado, agregar fecha a los campos de fechas acorde al estado",
        store=True
    )
    in_warehouse_date = Date(
        string="Fecha Entregado",
        help="Conforme cambia el estado, agregar fecha a los campos de fechas acorde al estado",
        store=True
    )
    transport_type = Selection(
        selection=[
            ('maritime', 'Marítimo'),
            ('air', 'Aéreo'),
            ('courier', 'Courier'),
            ('land', 'Terrestre')
        ],
        default="maritime",
        string="Transporte"
    )
    package_ids = One2many(
        comodel_name="mbe_logistics.package",
        inverse_name="manifest_id",
        string="Paquetes"
    )
    shipping_cost_ids = One2many(
        comodel_name="shipping.cost",
        inverse_name="manifest_id",
        string="Gastos de Envío"
    )
    currency_id = Many2one(
        comodel_name="res.currency",
        string="Moneda",
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
