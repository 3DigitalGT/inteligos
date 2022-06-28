# -*- coding: utf-8 -*-

from odoo.fields import (Monetary, Many2one)
from odoo.models import TransientModel


class WizardFillPackageValues(TransientModel):
    """Objecto trasient para llenar valores de los paquetes sin necesidad de modificar los permisos principales
        de los valores ingresados por el usuario para filtrar los datos del informe.
    """
    _name = 'fill.package_values.wiz'
    _description = 'Wizard para el llenado de campos de los paquetes.'

    expenses = Monetary(
        string="Gastos",
        help="Gastos Adicionales para presentar Póliza",
        default=0
    )
    other_expenses = Monetary(
        string="Otros Gastos",
        help="Gastos como Pickup, Inland, In&Out y otros.",
        default=0
    )
    custom_expenses = Monetary(
        string="Gastos Aduana",
        help="Gastos Incurridos en Aduana",
        default=0
    )
    package_id = Many2one(
        comodel_name="mbe_logistics.package",
        string="Paquete",
        help="Campo utilizado para relacionar con el paquete"
    )
    currency_id = Many2one(
        string='Moneda de la Compañía',
        related='package_id.currency_id'
    )

    def action_fill_package_values(self):
        self.package_id.write({field_name: self[field_name]
                               for field_name in self._fields if field_name not in ['package_id', 'currency_id']})
        return {'type': 'ir.actions.act_window_close'}
