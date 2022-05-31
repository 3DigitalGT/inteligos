# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import models, fields, _


class SrSaleOrder(models.Model):
    """Herencia del modulo sale.order"""

    _inherit = 'sale.order'

    payment_count = fields.Integer(
        string='Conteo de pagos', compute='_get_advance_payment', readonly=True
    )
    payment_ids = fields.One2many(
        'account.payment', 'sale_order_id', string="Pagos", readonly=True
    )
    is_paid = fields.Boolean(string="Esta pagado")
    advance_payment = fields.Float(string="Pagos Registrados")
    remaining_payment = fields.Float(string="Pago Restante")

    def action_register_sale_advance_payment(self):
        return {
            'name': _('Register Advance Payment'),
            'res_model': 'account.sale.advance.payment.register',
            'view_mode': 'form',
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def _get_advance_payment(self):
        for order in self:
            payment_ids = self.env['account.payment'].search(
                [('sale_order_id', '=', order.id)]
            )
            order.payment_count = len(payment_ids)

    def action_view_payment(self):
        payments = self.env['account.payment'].search([('sale_order_id', '=', self.id)])
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_account_payments"
        )
        if len(payments) > 1:
            action['domain'] = [('id', 'in', payments.ids)]
        elif len(payments) == 1:
            form_view = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [
                    (state, view) for state, view in action['views'] if view != 'form'
                ]
            else:
                action['views'] = form_view
            action['res_id'] = payments.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        return action
