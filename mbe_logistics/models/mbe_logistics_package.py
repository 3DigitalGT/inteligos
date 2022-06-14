# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import (Char, Selection, Many2one, Date, Float, One2many, Boolean, Monetary, Integer)
from odoo.api import (depends, onchange)
from odoo.exceptions import ValidationError


class Package(Model):
    """Objeto para los paquetes de logística"""
    _name = 'mbe_logistics.package'
    _description = 'Paquete MBE'

    @depends('weight')
    def _compute_weight_grams(self):
        for record in self:
            record.weight_grams = record.weight / 0.0010000

    @depends('weight')
    def _compute_weight_pounds(self):
        for record in self:
            record.weight_pounds = record.weight / 0.45359237

    @depends('value')
    def _compute_value_gt(self):
        for record in self:
            record.value_gt = record.value * record.manifest_id.exchange_rate

    @depends('weight_pounds')
    def _compute_freight(self):
        for record in self:
            record.freight = record.weight_pounds * record.env.company.logistic_weight_factor

    @depends('iva', 'dai', 'custom_expenses')
    def _compute_logistic_employed(self):
        for record in self:
            record.logistic_employed = record.iva + record.dai + record.custom_expenses

    name = Char(
        string="Guía",
        help="Guía del paquete.",
        copy=True,
        required=True,
        tracking=3
    )
    qty = Float(
        string="Cantidad",
        help="Campo que se utiliza para agregar la cantidad de los paquetes",
        copy=True,
        tracking=3
    )
    manifest_id = Many2one(
        comodel_name="mbe_logistics.manifest",
        string="Manifiesto",
        help="Campo para relacionar los paquetes con los manifiestos",
        copy=False,
        tracking=3
    )
    factor = Float(
        string="Factor",
        help="El factor que se aplica por el DAI",
        copy=True,
        tracking=3,
        default=1.19
    )
    real_price = Float(
        string="Precio real",
        help="campo para ingresar el precio real que proviene del PO",
        copy=True,
        required=False,
        tracking=3
    )
    tariff_class = Char(
        string="Partida",
        help="Partida Arancelaria",
        copy=True,
        tracking=3
    )
    weight = Float(
        digits=(10, 7),
        string="Peso (kg.)",
        help="Peso en kilos",
        copy=True,
        tracking=3
    )
    weight_grams = Float(
        digits=(10, 7),
        string="Peso (gr.)",
        help="Peso en gramos",
        store=False,
        compute="_compute_weight_grams"
    )
    weight_pounds = Float(
        digits=(10, 7),
        string="Peso (lb.)",
        help="Peso en libras",
        store=False,
        compute="_compute_weight_pounds"
    )
    height = Float(
        string="Alto",
        help="Alto de paquete en pulgadas",
        copy=True,
        tracking=3
    )
    width = Float(
        string="Ancho",
        help="Ancho del paquete en pulgadas",
        copy=True,
        tracking=3
    )
    length = Float(
        string="Largo",
        help="Largo del paquete en pulgadas",
        copy=True,
        tracking=3
    )
    dimensions = Float(
        string="Dimensiones",
        help="Campo utilizado para ingresar el ancho del paquete en pulgadas",
        copy=True,
        tracking=3
    )
    value = Monetary(
        string="Valor",
        help="Valor del paquete",
        copy=True,
        tracking=3
    )
    value_gt = Monetary(
        string="Valor (Q.)",
        help="Valor del paquete en quetzales",
        store=True,
        compute="_compute_value_gt"
    )
    sky_way_no = Integer(
        string="Skywayno",
        help="Campo utilizado para ingresar el Sky way no",
        copy=True,
        tracking=3
    )
    documentation = Boolean(
        string="Documentación",
        help="Si tiene o no su factura",
        copy=False,
        tracking=3
    )
    supplier_name = Char(
        string='Proveedor',
        help="Proveedor del paquete",
        copy=True,
        tracking=3
    )
    carrier_name = Char(
        string="Transportista",
        help="Transportista que entregó el paquete en Miami",
        copy=True,
        tracking=3
    )
    mawb = Char(
        string="Mawb",
        help="campo para agregar el mawb para los paquetes",
        copy=True,
        tracking=3
    )
    sky_store = Char(
        string="Skystore",
        help="Campo para agregar el sky store en los paquetes",
        copy=True,
        tracking=3
    )
    skybox = Many2one(
        comodel_name="res.partner",
        string="Skybox",
        help="Campo para agregar el sky box en los paquetes",
        copy=True,
        tracking=3,
        required=True
    )
    tracking = Char(
        string="# seguimiento del transportista",
        help="",
        copy=True,
        tracking=3
    )
    currency_id = Many2one(
        comodel_name='res.currency',
        string='Moneda',
        help="Campo para la moneda del paquete",
        copy=True,
        tracking=3
    )
    freight = Monetary(
        digits=(10, 7),
        string="Flete",
        help="Peso para Aduanas",
        compute="_compute_freight",
        copy=True,
        tracking=3
    )
    expenses = Monetary(
        string="Gastos",
        help="Gastos Adicionales para presentar Póliza",
        copy=True,
        tracking=3,
        default=0
    )
    insurance = Monetary(
        string="Seguro",
        help="Monto del seguro del paquete",
        copy=True,
        tracking=3,
        default=0
    )
    other_expenses = Monetary(
        string="Otros Gastos",
        help="Gastos como Pickup, Inland, In&Out y otros.",
        copy=True,
        default=0
    )
    tariff = Char(
        string="Arancel",
        help="Porcentaje(%) de Arancel",
        copy=True,
        tracking=3
    )
    state = Selection(
        selection=[
            ('transit', 'En Transito'),
            ('stored', 'En Tienda'),
            ('invoiced', 'Facturado'),
            ('detained', 'Retenido'),
            ('policy', 'Poliza')
        ],
        string="Estado",
        help="campo para seleccionar el estado de los paquetes",
        copy=False,
        tracking=3,
        default="transit"
    )
    dai = Monetary(
        digits=(10, 4),
        string="DAI",
        help="Agregar el monto del DAI",
        copy=True,
        tracking=3
    )
    iva = Monetary(
        digits=(10, 4),
        string="IVA",
        help="Agregar el monto del IVA",
        copy=True,
        tracking=3
    )
    description = Char(
        string="Descripción",
        help="Descripción del paquete",
        copy=True,
        tracking=3
    )
    custom_expenses = Monetary(
        string="Gastos Aduana",
        help="Gastos Incurridos en Aduana",
        copy=True,
        tracking=3,
        default=0
    )
    sale_order_id = Many2one(
        comodel_name="sale.order",
        string="Pedido de Venta",
        help="Campo utilizado para relacionar con la orden de venta",
        copy=False,
        tracking=3
    )
    logistic_employed = Monetary(
        string="Cuenta Ajena",
        help="Campo donde se agrega el monto total de las cuentas ajenas.",
        copy=True,
        tracking=3,
        default=0,
    )

    def action_unlink_package(self):
        """Método para desenlazar un paquete del pedido de venta."""
        sale_order_id = self.sale_order_id
        if sale_order_id.state == 'draft':
            self.write({'sale_order_id': False})
            for line in sale_order_id.order_line:
                if line.product_id == self.env.company.logistic_weight_id:
                    if line.package_id.id == self.id:
                        line.unlink()
                elif line.product_id == self.env.company.logistic_clearance_id:
                    line.product_uom_qty -= self.qty

            sale_order_id.logistic_employed_iva -= self.iva
            sale_order_id.logistic_employed_dai -= self.dai
            sale_order_id.logistic_employed_others -= self.custom_expenses
            sale_order_id.logistic_employed -= (self.iva + self.dai + self.custom_expenses)
            sale_order_id.total_cif -= self.value_gt
            sale_order_id.oea = ", ".join([package.name + '(' + package.manifest_id.name + ')'
                                           for package in sale_order_id.package_ids if package.id != self.id])
        else:
            raise ValidationError('Sólo puede quitar paquetes de un pedido si este está en estado Borrador')
