# -*- coding: utf-8 -*-

from odoo.api import depends
from odoo.models import Model
from odoo.fields import (Boolean, Many2one, Char, Integer, Many2many)


class StockMoveInherited(Model):
    _inherit = 'stock.move'
    _name = 'stock.move'

    @depends('series_ids.name')
    def compute_countdown(self):
        for record in self:
            qty = record.series_ids.filtered(lambda s: s.name)
            record.countdown = record.product_uom_qty - len(qty)

    has_series = Boolean(
        related="product_id.has_series",
        string="Utiliza Serie"
    )
    its_done = Boolean(
        default=False,
        string="Está Hecho"
    )
    series_ids = Many2many(
        comodel_name="product.series",
        store=True,
        string="Series"
    )
    countdown = Integer(
        compute='compute_countdown',
        string="Contador Atrás"
    )

    def action_set_product_series(self):
        Series = self.env['product.series']
        product_series = Series.search([('stock_move_id', '=', self.id)])

        if not product_series:
            for idx in range(0, int(self.product_uom_qty)):
                series_value = {
                    'stock_move_id': self.id, 'product_id': self.product_id.id,
                    'name': '', 'stock_picking_id': self.picking_id.id, 'number': idx+1
                }
                series_id = Series.create(series_value)
                product_series += series_id
        self.write({'series_ids': [(6, 0, product_series.ids)]})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Series de ' + self.product_id.name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'view_id': self.env.ref('product_series.wizard_product_series_form').id,
            'views': [(self.env.ref('product_series.wizard_product_series_form').id, 'form')],
            'target': 'new',
            'res_id': self.id
        }

    def action_confirm_product_series(self):
        for series in self.series_ids:
            if series.name and not series.its_done:
                series.write({'its_done': True})
                self.quantity_done += 1

        if self.quantity_done == self.product_uom_qty:
            self.write({'its_done': True})
        return {
            'type': 'ir.actions.act_window_close'
        }

    def _action_cancel(self):
        """
        Sobrescritura al método genérico para eiminar las series enlazadas al movimiento.
        :return: valor genérico devuelto por Odoo.
        """
        result = super(StockMoveInherited, self)._action_cancel()
        product_series = self.env['product.series'].search([('stock_move_id', '=', self.id)])

        for series in product_series:
            series.unlink()
        return result
