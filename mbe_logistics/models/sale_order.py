# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import (One2many, Monetary, Text, Char)
from odoo.api import (onchange, depends)
from odoo.exceptions import ValidationError


class InheritSaleOrderLogistic(Model):
    """Herencia del objeto sale.order para logística"""
    _inherit = 'sale.order'
    _name = 'sale.order'

    @depends('amount_total', 'logistic_employed')
    def _compute_total_logistic(self):
        for record in self:
            record.total_logistic = record.logistic_employed + record.amount_total

    package_ids = One2many(
        comodel_name="mbe_logistics.package",
        inverse_name="sale_order_id",
        string="Paquetes",
        help="Paquetes incluidos en la orden",
        store=True
    )
    logistic_employed_iva = Monetary(
        string="Cuenta Ajena IVA",
        help="Campo donde se agrega el monto de las cuentas ajenas.",
        copy=True,
        default=0
    )
    logistic_employed_dai = Monetary(
        string="Cuenta Ajena DAI",
        help="Campo donde se agrega el monto de las cuentas ajenas.",
        copy=True,
        default=0
    )
    logistic_employed_others = Monetary(
        string="Cuenta Ajena Otros",
        help="Campo donde se agrega el monto de las cuentas ajenas.",
        copy=True,
        default=0
    )
    logistic_employed = Monetary(
        string="Cuenta Ajena",
        help="Campo donde se agrega el monto total de las cuentas ajenas.",
        copy=True,
        default=0
    )
    total_cif = Monetary(
        string="CIF",
        help="Campo donde se calcula la suma de los valores quetzalisados de los paquetes.",
        copy=True,
        default=0
    )
    oea = Text(
        string="OEA",
        help="Campo que almacena el unificado de las guías y secuencias de manifiesto de cada uno de los paquetes.",
        copy=True,
        default=0
    )
    total_logistic = Monetary(
        string="Total de logística",
        help="Campo donde se agrega el monto total de las cuentas ajenas + monto total del documento.",
        compute="_compute_total_logistic",
        copy=True,
        store=True,
        default=0
    )

    def set_data_from_packages(self):
        """
        Método para colocar en el pedido los valores necesarios de logística que son obtenidos de los paquetes enlazados
        :return: record sale.order
        """
        for line in self.order_line:
            if line.product_id == self.env.company.logistic_weight_id:
                for package in self.package_ids:
                    if line.package_id.id == package.id:
                        line.write({'product_uom_qty': package.weight_pounds})
            elif line.product_id == self.env.company.logistic_clearance_id:
                line.product_uom_qty = sum([package.qty for package in self.package_ids if package.qty])
        self.logistic_employed_iva = sum([package.iva for package in self.package_ids if package.iva])
        self.logistic_employed_dai = sum([package.dai for package in self.package_ids if package.dai])
        self.logistic_employed_others = sum(
            [package.custom_expenses for package in self.package_ids if package.custom_expenses])
        self.write({'logistic_employed': sum([package.iva for package in self.package_ids if package.iva]) +
                                         sum([package.dai for package in self.package_ids if package.dai]) +
                                         sum([package.custom_expenses for package in self.package_ids
                                              if package.custom_expenses]),
                    'total_cif': sum([package.value_gt for package in self.package_ids if package.value_gt]),
                    'oea': ", ".join([package.name + '(' + package.manifest_id.name + ')'
                                      for package in self.package_ids if package.name and package.manifest_id.name])
                    })
        return self

    # @onchange('payment_method') # # TODO: Código en desuso debido a que no es necesario para el uso actual.
    # def onchange_payment_method(self):
    #     """Sobreescritura del método para eliminar la línea del pedido
    #         (si el método de pago no es tarjeta de crédito) que tiene
    #         el producto configurado en la compañía para gastos administrativos.
    #     """
    #     super(InheritSaleOrderLogistic, self).onchange_payment_method()
    #     logistic_admin_expenses_id = self.env.company.logistic_admin_expenses_id.id
    #
    #     if self.state == 'draft' and self.payment_method == 'tc' \
    #             and logistic_admin_expenses_id in self.order_line.mapped('product_id').ids:
    #         line = self.order_line.filtered(lambda l: l.product_id.id == logistic_admin_expenses_id)
    #         line.unlink()

    @onchange("package_ids")
    def update_packages(self):
        """Método para actualizar los productos en las líneas de pedidos según los paquetes enlazados al mismo.
        :return: None
        """
        if (not self.env.company.logistic_weight_id or not self.env.company.logistic_clearance_id) \
                and self.package_ids:  # TODO: analizar cómo hacer uso de este módulo en multicompañía sin afectar en nada a las compañías que no lo usarán (módulo)
            raise ValidationError("Error 101: uno o varios productos de logística "
                                  "no están configurados dentro de la compañia")

        for package in self.package_ids.filtered(lambda p: not p.sale_order_id):
            package.write({'sale_order_id': self.id})

        sale = self.set_data_from_packages()

    def action_get_packages(self):
        """
        - Método utilizado para colocar los paquetes en el SO.
        search:     paquete.skybox.ref = partner_id.ref
        search:     paquete.state == stored
        search:     paquete.sale_order_id == False

        - Método utilizado para agregar los productos que están en la configuración de res.company
        field:      logistic_weight_id
        field:      logistic_clearance_id

        - Manejo se Errores
        Error(101):     Faltan productos en la configuracion de la compañia
        Error(102):     No se encontraron paquetes que estén en tienda para el cliente: Nombre de registro res.partner

        1. Agrega los paquetes del cliente con el mismo gua y la referencia del cliente a la seccion de paquetes.
        2. agrega los productos que estan en la configuracion de la compañia al SO
        :return: None
        """
        if not self.partner_id:
            raise ValidationError("Error 100: No ha ingresado un cliente, hágalo e intente de nuevo.")

        if not self.env.company.logistic_weight_id or not self.env.company.logistic_clearance_id:
            raise ValidationError("Error 101: uno o varios productos no estan configurados dentro de la compañia")

        if self.order_line:
            products = self.order_line.mapped('product_id').ids

            if self.env.company.logistic_weight_id.id in products and self.env.company.logistic_clearance_id.id in products:
                raise ValidationError("Error 103: Ya han sido colocados los productos en las líneas de pedido.")

        packages = self.env["mbe_logistics.package"].search(
            [("skybox", "=", self.partner_id.id), ("state", "=", "stored"), ("sale_order_id", "=", False)]
        )

        if not packages:
            raise ValidationError("Error 102: No se encontraron paquetes que estén "
                                  "en tienda para el cliente: " + self.partner_id.name)

        for package in packages:
            package.write({'sale_order_id': self.id})

        products_values = [{'package_id': package.id, 'qty': package.weight_pounds,
                            'product_id': self.env.company.logistic_weight_id}
                           for package in self.package_ids if package.weight_pounds
                           ]
        products_values.append({'package_id': False,
                                'qty': float(sum([package.qty for package in self.package_ids if package.qty])),
                                'product_id': self.env.company.logistic_clearance_id})

        # if self.payment_method == 'tc':  # # TODO: Código en desuso debido a que no es necesario para el uso actual.
        #     products_values.append({'package_id': False, 'qty': 1.00,
        #                             'product_id': self.env.company.logistic_admin_expenses_id})

        values_list = []
        SaleOrderLine = self.env["sale.order.line"]

        for value in products_values:
            product = value['product_id'].with_context(
                lang=self.partner_id.lang,
                partner=self.partner_id.id,
                quantity=value['qty'],
                date=self.date_order,
                pricelist=self.pricelist_id.id,
                uom=value['product_id'].uom_id.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            values = {
                'product_id': product.id,
                'name': product.name,
                'order_id': self.id,
                'product_uom_qty': value['qty'],
                'product_uom': product.uom_id.id,
                'tax_id': [(6, 0, product.taxes_id.ids)],
                'price_unit': product.lst_price,
                'package_id': value['package_id']
            }

            line = SaleOrderLine.new(values)
            company = self.company_id or self.company_id
            price_unit = self.env['account.tax']._fix_tax_included_price_company(line._get_display_price(product),
                                                                                 product.taxes_id,
                                                                                 product.taxes_id, company)
            values.update({'price_unit': price_unit})
            values_list.append(values)

        SaleOrderLine.create(values_list)
        sale = self.set_data_from_packages()

    def action_cancel(self):
        """
        Sobreescritura del método para quitar el enlace entre los paquetes y el pedido de venta
        :return: dict values
        """
        result = super(InheritSaleOrderLogistic, self).action_cancel()
        if self.package_ids:
            for package in self.package_ids:
                package.write({'sale_order_id': False})
        return result

    def _prepare_invoice(self):
        """
        Sobreescritura del método para trasladar los valores de
        cuentas ajenas a los campos homónimos del objeto account.move.
        :return: dict values
        """
        invoice_vals = super(InheritSaleOrderLogistic, self)._prepare_invoice()
        if self.package_ids:
            invoice_vals['logistic_employed_iva'] = self.logistic_employed_iva
            invoice_vals['logistic_employed_dai'] = self.logistic_employed_dai
            invoice_vals['logistic_employed_others'] = self.logistic_employed_others
            invoice_vals['logistic_employed'] = self.logistic_employed
        return invoice_vals

    def _create_invoices(self, grouped=False, final=False, date=None):
        """
        Sobreescritura del método para agregar lógica que permita crear un recibo de cliente
        con el producto de cuenta ajena configurado en la compañía cuando hayan paquetes en el pedido de venta.
        Y cambia el estado de los paquetes enlazados a un estado FACTURADO.
        :return: record account.move
        """
        moves = super(InheritSaleOrderLogistic, self)._create_invoices(grouped=grouped, final=final, date=date)

        if self.package_ids:
            invoice_vals = self._prepare_invoice()
            invoice_vals['move_type'] = 'out_receipt'
            invoice_vals['invoice_line_ids'] = [
                (0, 0, {
                    'display_type': False,
                    'sequence': 1,
                    'name': self.env.company.logistic_employed_id.name,
                    'product_id': self.env.company.logistic_employed_id.id,
                    'product_uom_id': self.env.company.logistic_employed_id.uom_id.id,
                    'quantity': 1,
                    'discount': 0.00,
                    'price_unit': self.logistic_employed,
                    'tax_ids': [(6, 0, self.env.company.logistic_employed_id.taxes_id.ids)],
                    'analytic_account_id': self.analytic_account_id.id,
                    'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids) for line in self.order_line]
                })]  # # TODO: FIX me when add sale_line_ids field with relation records Odoo fix him. Odoo error inside sale module, on action_post method. Bad use for records.
            # # TODO: Error: singleton. Code error: line.sale_line_ids.is_downpayment, line.sale_line_ids.tax_id, line.sale_line_ids.price_unit, line.sale_line_ids.untaxed_amount_to_invoice

            receipt = self.env['account.move'].sudo().create(invoice_vals)

            for package in self.package_ids:
                package.write({'state': "invoiced"})

            moves.write({'receipt_id': receipt.id})
            receipt.write({'journal_id': self.env.company.journal_receipt_employed_id.id})
        return moves

    def action_unlink_packages(self):
        """Método para desenlazar un paquetes del pedido de venta."""
        for package in self.package_ids:
            package.write({'sale_order_id': False})

        self.order_line.unlink()
        self.logistic_employed_iva = 0
        self.logistic_employed_dai = 0
        self.logistic_employed_others = 0
        self.logistic_employed = 0
        self.total_cif = 0
        self.oea = ''
