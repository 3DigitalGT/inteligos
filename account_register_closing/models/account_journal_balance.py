from odoo import models, fields, api


class AccountJournalBalance(models.Model):
    _name = 'account.journal.balance'
    _description = 'account_register_closing.account.journal.balance'
    _order = "id desc"

    """
    Variables
    """

    select_method_data = [("E", "Efectivo"), ("C", "Cheque"), ("T", "Transferencia"), ("TC", "Tarjeta de Credito"),
                          ("DE", "Deposito")]
    payment_method = fields.Selection(
        selection=select_method_data,
        string="Metodo de Pago",
        help="Campo util para seleccionar el metodo de pago",
        copy=True,
        tracking=True,
        required=False,
    )

    initial_balance = fields.Monetary(
        string="Saldo Inicial",
        help="Campo util para ver el saldo inicial",
        copy=False,
        tracking=True,
        required=False,
        currency_field='currency_id'
    )

    final_balance = fields.Monetary(
        string="Saldo final",
        help="Campo util para ver el saldo final",
        copy=False,
        tracking=True,
        required=False,
        currency_field='currency_id'
    )

    payments_entry = fields.Monetary(
        string="Entradas",
        help="Campo util para ver las Entradas",
        copy=False,
        tracking=True,
        required=False,
        currency_field='currency_id',
    )

    outgoing_payments = fields.Monetary(
        string="Salidas",
        help="Campo util para ver las Salidas",
        copy=False,
        tracking=True,
        required=False,
        currency_field='currency_id',
    )

    journal_balance = fields.Many2one(
        string="Cierre",
        help="Campo relacionado con modulo account journal closing",
        copy=False,
        tracking=True,
        required=False,
        comodel_name="account.journal.closing",
    )

    currency_id = fields.Many2one(
        string="Currency",
        help="Campo relacionado para la moneda",
        copy=False,
        tracking=True,
        required=False,
        comodel_name='res.currency',
        default=lambda self: self.env.ref('base.main_company').currency_id
    )

    @api.model
    def compute_method(self):
        """
        regresar las opciones
        """
        return self.select_method_data
