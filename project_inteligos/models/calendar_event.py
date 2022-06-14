# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CalendarEventInherited(models.Model):
    _inherit = 'calendar.event'

    def compute_data_into_agendas(self):
        for record in self:
            done_agendas = record.agenda_ids \
                .filtered(lambda agenda: agenda.status == 'done')
            list_conclusion_ids = [agenda.conclusion_ids.ids for agenda in done_agendas]
            conclusion_ids = [element for lis in list_conclusion_ids for element in lis]
            list_task_ids = [agenda.task_ids.ids for agenda in done_agendas]
            task_ids = [element for lis in list_task_ids for element in lis]
            record['conclusion_ids'] = conclusion_ids or False
            record['task_ids'] = task_ids or False

    def compute_real_duration(self):
        for record in self:
            if record.start_time and record.end_time:
                duration = record.end_time - record.start_time
                record['real_duration'] = duration
            else:
                record['real_duration'] = ''

    agenda_ids = fields.One2many(
        'calendar.agenda',
        'event_id',
        index=True,
        store=True,
        help='Ingrese las agendas de la reunión.',
        string="Agendas"
    )
    notes = fields.Text(
        index=True,
        store=True,
        help='Ingrese las notas de la reunión.',
        string="Notas"
    )
    real_participant_ids = fields.One2many(
        'res.users',
        'event_id',
        index=True,
        store=True,
        required=True,
        help='Ingrese los participantes de la reunión',
        string="Participantes"
    )
    start_time = fields.Datetime(
        index=True,
        store=True,
        readonly=True,
        help='Tiempo inicial de la reunión, obtenida al hacer Check-In.',
        string="Fecha y hora de Inicio"
    )
    start_lat = fields.Char(
        index=True,
        store=True,
        readonly=True,
        help='Latitud inicial de la reunión, obtenida al hacer Check-In.',
        string="Lat. Inicial"
    )
    start_long = fields.Char(
        index=True,
        store=True,
        readonly=True,
        help='Longitud inicial de la reunión, obtenida al hacer Check-In.',
        string="Long. Inicial"
    )
    end_time = fields.Datetime(
        index=True,
        store=True,
        readonly=True,
        help='Tiempo final de la reunión, obtenida al hacer Check-In.',
        string="Fecha y hora Final"
    )
    end_lat = fields.Char(
        index=True,
        store=True,
        readonly=True,
        help='Latitud final de la reunión, obtenida al hacer Check-Out.',
        string="Lat. Final"
    )
    end_long = fields.Char(
        index=True,
        store=True,
        readonly=True,
        help='Longitud final de la reunión, obtenida al hacer Check-Out.',
        string="Long. Final"
    )
    real_duration = fields.Char(
        compute="compute_real_duration",
        help='Duración real de la minuta.',
        string="Duración"
    )
    minute_id = fields.Many2one(
        'project.minute',
        'Reunión'
    )
    project_id = fields.Many2one(
        'project.project',
        index=True,
        store=True,
        help='Ingrese el proyecto para la reunión.',
        string="Proyecto"
    )
    task_id = fields.Many2one(
        'project.task',
        string="Tarea"
    )

    def print_report(self):
        return self.env.ref('minute.action_report_minute').with_context(
            landscape=True).report_action(self)

    def send_minute(self):
        '''
        This function opens a window to compose an email, with the email template message loaded by default
        '''

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('minute', 'minute_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'calendar.event',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        }
        return {
            'name': 'Compose Email',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def get_partner_ids(self):
        emails = ''
        for p in self.partner_ids:
            emails = emails + str(p.id) + ","
        return emails[:-1]


class ResUsersInherited(models.Model):
    _inherit = 'res.users'

    event_id = fields.Many2one(
        'calendar.event',
        index=True,
        store=True,
        help='Reunión principal a la que pertenece la agenda.',
        string="Evento"
    )


class CalendarAgenda(models.Model):
    _name = 'calendar.agenda'

    event_id = fields.Many2one(
        'calendar.event',
        index=True,
        store=True,
        readonly=True,
        help='Reunión principal a la que pertenece la agenda.',
        string="Evento"
    )
    time = fields.Float(
        index=True,
        store=True,
        help='Duración de tiempo del punto de la agenda.',
        string="Duración"
    )
    # (debe ser cantidad de minutos)
    name = fields.Char(
        index=True,
        store=True,
        required=True,
        help='Punto de agenda',
        string="Punto"
    )