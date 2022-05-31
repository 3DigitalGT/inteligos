from odoo import models, fields, api


class InheritAccountPayment(models.Model):
    _inherit = 'account.payment'
    _description = 'account_register_closing.account.payment'

    select_payment_type = [("outbound", "Enviar Dinero"), ("inbound", "Recibir Dinero")]

    payment_type = fields.Selection(
        selection=select_payment_type,
        string="Tipo de Pago",
        help="Campo para seleccionar el tipo de pago",
        required=True,
    )

    journal_balance = fields.Many2one(
        string="Cierre",
        help="Campo relacionado con modulo account journal closing",
        copy=False,
        tracking=True,
        required=False,
        comodel_name="account.journal.closing",
    )
    name_to = fields.Char(
        string="A Nombre De",
        help="Campo util para mostrar en la imprecion del cheque el nombre",
        required=True
    )
    communication = fields.Char(
        string="Circular",
        help="Campo util para el circular",
        required=False,
    )
    text_free = fields.Char(
        string="Nota",
        help="Campo util para las notas del pago",
        required=False
    )
    sat_reference = fields.Char(
        string="Numero de Formulario",
        help="Campo util para el numero de formulario",
        required=False,
    )

    @api.onchange('payment_type')
    def _on_change_payment_type(self):
        if self.journal_balance and self.journal_balance:
            if self.payment_type == 'outbound':
                self.partner_type = 'supplier'
            elif self.payment_type == 'inbound':
                self.partner_type = 'customer'

