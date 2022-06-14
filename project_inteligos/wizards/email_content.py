from odoo import models, fields, api


class EmailContent(models.TransientModel):
    _name = 'project.email'
    _inherits = {'mail.compose.message': 'composer_id'}
    _description = 'Project Sent'

    email_address = fields.Text(string='Email address')
    invoice_ids = fields.Many2many('account.move', 'account_move_account_invoice_send_rel', string='Invoices')
    composer_id = fields.Many2one('mail.compose.message', string='Composer', required=True, ondelete='cascade')
    template_id = fields.Many2one(
        'mail.template', 'Use template', index=True,
        domain="[('model', '=', 'project.minute')]"
    )

    @api.onchange('template_id')
    def onchange_template_id(self):
        for wizard in self:
            if wizard.composer_id:
                wizard.composer_id.template_id = wizard.template_id.id
                wizard._compute_composition_mode()
                wizard.composer_id.onchange_template_id_wrapper()

    @api.onchange('is_email')
    def onchange_is_email(self):
        if self.is_email:
            if not self.composer_id:
                res_ids = self._context.get('active_ids')
                self.composer_id = self.env['mail.compose.message'].create({
                    'composition_mode': 'comment' if len(res_ids) == 1 else 'mass_mail',
                    'template_id': self.template_id.id
                })
            else:
                self.composer_id.template_id = self.template_id.id
            self.composer_id.onchange_template_id_wrapper()

    def _send_email(self):
        self.composer_id.send_mail()
        if not self.attachment:
            # Enviar correo sin adjunto
            pass
        elif self.attachment:
            self.env['mail.thread']._message_set_main_attachment_id([(False, self.attachment.id)])
