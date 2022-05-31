from odoo import models, fields, api, _
from datetime import datetime


class AccountJournalClosing(models.Model):
    _name = 'account.journal.closing'
    _description = 'account_register_closing.account.journal.closing'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = "id desc"

    """"
    Variables
    """
    select_state = [("confirmed", "Confirmado"), ("draft", "Borrador"), ("cancelled", "Cancelado")]

    name = fields.Char(
        string="Nombre",
        help="Campo util generado automaticamente por secuencia",
        copy=False,
        tracking=True,
        required=False,
    )

    state = fields.Selection(
        selection=select_state,
        string="Estado",
        help="Campo util para seleccionar el metodo de pago",
        copy=False,
        tracking=True,
        required=False,
        default='draft'
    )

    date_start = fields.Date(
        string="Fecha Inicial",
        help="Campo para ingresar la fecha inicial",
        copy=True,
        tracking=True,
        required=False,
        default=lambda self: self.compute_last_date()
    )

    date_end = fields.Date(
        string="Fecha Final",
        help="Campo para ingresar la fecha final",
        copy=True,
        tracking=True,
        required=False,
        default=datetime.today()
    )

    user_id = fields.Many2one(
        string="Usuario",
        help="campo para ingresar el usuario del modelo res.users",
        copy=True,
        tracking=True,
        required=False,
        comodel_name='res.users',
    )

    account_payments_ids = fields.Many2many(
        string="Pagos",
        help="campo para enlazar todos los pagos",
        copy=False,
        tracking=True,
        required=False,
        comodel_name="account.payment",
        inverse_name="journal_balance"
    )

    account_move_ids = fields.One2many(
        string="Facturas",
        help="Campo para enlazar todas las facturas",
        copy=False,
        tracking=True,
        required=False,
        comodel_name="account.move",
        inverse_name="journal_balance"
    )

    account_journal_balance_ids = fields.One2many(
        string="Saldos",
        help="Campo para enlazar todos los saldos",
        copy=False,
        required=False,
        comodel_name="account.journal.balance",
        inverse_name="journal_balance"
    )

    account_journals_id = fields.Many2one(
        string="Diario",
        help="Campo para seleccionar el diario",
        copy=True,
        required=True,
        comodel_name="account.journal",
        domain=[('type', 'in', ('bank', 'cash'))],
    )

    payments_ids = fields.Many2many(
        string='Pagos',
        comodel_name='account.payment',
        relation='account_register_closing_relation',
    )

    account_move_ids_button = fields.One2many(
        string='Facturas',
        comodel_name='account.move',
        inverse_name='journal_balance'

    )

    can_delete = fields.Boolean(
        string='Poder eliminar',
        help="Campo para poder eliminar o no un registro",
        copy=False,
    )

    invoice_count = fields.Integer(
        string="Contador Facturas",
        help="Campo para llevar el conteo de Facturas",
        compute='compute_count_invoices',
        copy=False
    )

    """
    Secuencia
    """

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'account.journal.closing.sequence') or 'Nuevo'
        result = super(AccountJournalClosing, self).create(vals)
        return result

    """
    Funciones de Compute
    """

    @api.model
    def compute_last_date(self):
        """
        Regresa la ultima fecha
        """
        last_date = self.env['account.journal.closing'].search([], limit=1).date_end
        return last_date

    """
    Funciones de botones
    """

    def calculate_movements2(self):
        """
        Verificamos los pagos que esten dentro de las fechas
        """

        for balances in self.account_journal_balance_ids:
            balances.unlink()
        banned_state = ["draft", "cancel"]
        data = self.env['account.payment'].search(["&", "&", "&", "&", ("date", ">=", self.date_start),
                                                   ("date", "<=", self.date_end),
                                                   ("journal_id", "=", self.account_journals_id.id),
                                                   ("state", "not in", banned_state), ("destination_journal_id", "=", False)]) + \
               self.env['account.payment'].search(["&", "&", "&", ("date", ">=", self.date_start),
                                                   ("date", "<=", self.date_end),
                                                   ("destination_journal_id", "=", self.account_journals_id.id),
                                                   ("state", "not in", banned_state)])

        self.account_payments_ids = data
        self.payments_ids = data
        account_balance = self.env['account.journal.balance']
        options = account_balance.compute_method()

        for method in options:
            initial_balance = 0
            payments_entry = 0
            outgoing_payments = 0
            temp = self.env['account.journal.closing'].search(
                [("account_journals_id", "=", self.account_journals_id.id)], limit=2)
            if len(temp) > 1:
                for last_balance in temp[1].account_journal_balance_ids:
                    if last_balance.payment_method == method[0]:
                        initial_balance = last_balance.final_balance
            # cliente en entradas proveedores en salidas
            if self.account_payments_ids:
                for payment in self.account_payments_ids:
                    if payment.method == method[0]:
                        if payment.partner_type == "customer" and payment.journal_id == self.account_journals_id:
                            if payment.amount >= 0:
                                payments_entry += payment.amount
                            if payment.amount < 0:
                                outgoing_payments += abs(payment.amount)
                        if payment.partner_type == "supplier" and payment.journal_id == self.account_journals_id:
                            if payment.amount >= 0:
                                outgoing_payments += payment.amount
                            if payment.amount < 0:
                                payments_entry += abs(payment.amount)
                        if payment.partner_type == 'supplier' and payment.destination_journal_id == self.account_journals_id:
                            if payment.journal_balance:
                                if payment.amount >= 0:
                                    payments_entry += payment.amount
                                if payment.amount < 0:
                                    outgoing_payments += abs(payment.amount)
            val = {
                "payment_method": method[0],
                "journal_balance": self.id,
                "initial_balance": initial_balance,
                "payments_entry": payments_entry,
                "outgoing_payments": outgoing_payments,
                "final_balance": (initial_balance + payments_entry - outgoing_payments)
            }
            account_balance.create(val)
            for record in self:
                record.account_move_ids_button = self.env['account.move'].search(
                    [('journal_balance', '=', self.id), ('move_type', 'in', ['in_invoice'])])

    def invoice_report(self):
        lines = {}
        n = 0
        total = 0
        net_total = 0
        tax_total = 0
        for line in self.account_move_ids_button:
            n += 1
            lines.update({
                'F_' + str(n): {
                    'document_date': line.date,
                    'desc': line.ref,
                    'serie': line.invoice_doc_serie,
                    'no_document': line.invoice_doc_number,
                    'vendor': line.partner_id.name,
                    'net_value': line.amount_untaxed,
                    'tax': line.amount_tax,
                    'total': line.amount_total
                }
            })
            total = total + line.amount_total
            net_total = net_total + line.amount_untaxed
            tax_total = tax_total + line.amount_tax
        user = str(self.env['res.users'].browse(self.env.uid).name)
        data = {
            'company': self.env.company.name,
            'name': self.name,
            'date': fields.Datetime.now().strftime('%Y-%m-%d'),
            'initial_cash_balance': 'Q ' + str(
                self.env['account.journal.balance'].search([('journal_balance', '=', self.id),
                                                            ('payment_method', '=', 'E'),
                                                            ]).initial_balance),
            'invoices': lines,
            'net_total': 'Q ' + "{:.2f}".format(net_total),
            'tax_total': 'Q ' + str(tax_total),
            'total': 'Q ' + str(total),
            'end_cash_balance': 'Q ' + str(
                self.env['account.journal.balance'].search([('journal_balance', '=', self.id),
                                                            ('payment_method', '=', 'E'),
                                                            ]).final_balance),
            'documents_number': len(self.account_move_ids_button),
            'log_user': str(user)
        }

        return self.env.ref('account_register_closing.report_invoice_journal_closing').report_action(self, data=data)

    def open_wizard_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'account.view_account_payment_form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'account.payment',
            'context': {'default_journal_balance': self.id}
        }

    def open_wizard_suppliers(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'account.view_move_form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'account.move',
            'context': {'default_move_type': 'in_invoice', 'default_journal_balance': self.id}
        }

    def action_view_payments(self):
        data = []
        for payments in self.payments_ids:
            data.append(payments.id)
        return {
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', data)],
            'name': 'Pagos',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'account.payment',
            'context': {'account_journal_closing': self.id}
        }

    def action_view_invoice(self):
        data = []
        for invoices in self.account_move_ids_button:
            data.append(invoices.id)
        return {
            'type': 'ir.actions.act_window',
            'domain': [('journal_balance', '=', self.id), ('move_type', '=', 'in_invoice')],
            'name': 'Facturas',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'account.move',
            'context': {'default_move_type': 'in_invoice', 'default_journal_balance': self.id, 'invoice_doc_type': '2'}
        }

    def compute_count_invoices(self):
        for record in self:
            record.invoice_count = self.env['account.move'].search_count(
                [('journal_balance', '=', self.id), ('move_type', 'in', ['out_invoice', 'in_invoice'])])

    def send_email(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']

        template_id = ir_model_data.get_object_reference('account_register_closing', 'email_template_journal_closing')[
            1]
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False

        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'account.journal.closing',
            'active_model': 'account.journal.closing',
            'active_id': self.id,
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'mark_rfq_as_sent': True,
        })

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def confirm_state(self):
        for payments in self.payments_ids:
            if payments.state == 'draft':
                payments.post()
        self.state = 'confirmed'

    def draft_state(self):
        self.state = 'draft'

    def cancel_state(self):
        self.state = 'cancelled'
