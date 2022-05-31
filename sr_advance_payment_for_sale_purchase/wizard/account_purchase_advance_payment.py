# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class srAccountPurchaseAdvancePayment(models.TransientModel):
    _name = "account.purchase.advance.payment.register"

    name = fields.Char(string="Origen", readonly=True)
    purchase_order_id = fields.Many2one('purchase.order', string="Name")
    journal_id = fields.Many2one(
        'account.journal', domain=[('type', 'in', ['bank', 'cash'])], required=True, string="Diario"
    )
    payment_date = fields.Datetime(
        string="Fecha de pago", default=fields.Date.context_today
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id,
    )
    company_id = fields.Many2one(
        'res.company', related='journal_id.company_id', string='Compañia', readonly=True
    )
    company_currency_id = fields.Many2one(
        'res.currency', string="Company Currency", related='company_id.currency_id'
    )
    payment_method_id = fields.Many2one(
        'account.payment.method.line', string='Metodo de pago', required=True
    )
    total_amount = fields.Float(string="Cantidad total", readonly=True)
    payment_amount = fields.Monetary(required=True, string="Cantidad a pagar")
    paid_payment = fields.Monetary(
        compute='_compute_amount',
        readonly=True,
        string="Cantidad pagada",
        currency_field='company_currency_id',
    )
    remaining_balance = fields.Monetary(
        compute='_compute_amount',
        readonly=True,
        string="Cantidad restante",
        currency_field='company_currency_id',
    )
    communication = fields.Char('Comunicacion')
    payment_state = fields.Selection(
        [('draft', 'Borrador'), ('posted', 'Publicado')], string="Estado", default="draft"
    )

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            self.currency_id = (
                self.journal_id.currency_id or self.company_id.currency_id
            )
            payment_methods_id = self.journal_id.inbound_payment_method_line_ids
            self.payment_method_id = (
                payment_methods_id and payment_methods_id[0] or False
            )
            return {
                'domain': {
                    'payment_method_id': [
                        ('payment_type', '=', 'inbound'),
                        ('id', 'in', payment_methods_id.ids),
                    ]
                }
            }
        return {}

    @api.model
    def default_get(self, fields):
        res = super(srAccountPurchaseAdvancePayment, self).default_get(fields)
        if self._context.get('active_model') == 'purchase.order':
            active_id = self._context.get('active_id')
            journal = self.env['account.journal'].search(
                [
                    ('type', 'in', ('bank', 'cash')),
                    ('company_id', '=', self.env.user.company_id.id),
                    ('currency_id', '=', self.currency_id.id),
                ],
                limit=1,
            )
            res.update(
                {
                    'name': self.env[self._context.get('active_model')]
                    .browse(active_id)
                    .name,
                    'purchase_order_id': active_id,
                    'total_amount': self.env[self._context.get('active_model')]
                    .browse(active_id)
                    .amount_total,
                    'currency_id': self.env[self._context.get('active_model')]
                    .browse(active_id)
                    .currency_id.id,
                    'journal_id': journal.id,
                    'communication': 'Advance Payment Against '
                    + str(
                        self.env[self._context.get('active_model')]
                        .browse(active_id)
                        .name
                    ),
                }
            )
        else:
            raise UserError(
                _(
                    "The Advance payment wizard should only be called on Purchase order"
                    " records."
                )
            )
        return res

    def _compute_amount(self):
        total = 0
        active_id = self._context.get('active_id')
        payment_ids = self.env['account.payment'].search(
            [('purchase_order_id', '=', active_id)]
        )
        for record in payment_ids:
            total += record.amount_total_signed
        self.paid_payment = total
        self.remaining_balance = self.total_amount - self.paid_payment

    def action_pay_purchase_advance_payment(self):
        payment_id = self.env['account.payment'].create(
            {
                'payment_type': 'outbound',
                'partner_type': 'supplier',
                'ref': self.communication,
                'currency_id': self.currency_id.id,
                'partner_id': self.purchase_order_id.partner_id.id,
                'amount': self.payment_amount,
                'journal_id': self.journal_id.id,
                'date': self.payment_date,
                'purchase_order_id': self.purchase_order_id.id,
            }
        )
        if self.remaining_balance == 0:
            is_paid = True
        else:
            is_paid = False
        self.purchase_order_id.write(
            {
                "is_paid": is_paid,
                "advance_payment": self.paid_payment,
                "remaining_payment": self.remaining_balance,
            }
        )
        if self.payment_state == "posted":
            payment_id.action_post()
        return
