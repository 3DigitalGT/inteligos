from odoo import models, fields, api


class InheritAccountPayment(models.Model):
    _inherit = 'account.move'
    _description = 'account_register_closing.account.payment'

    journal_balance = fields.Many2one(
        string="Cierre",
        help="Campo relacionado con modulo account journal closing",
        copy=False,
        tracking=True,
        required=False,
        comodel_name="account.journal.closing",
    )
