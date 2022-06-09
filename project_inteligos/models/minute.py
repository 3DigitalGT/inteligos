# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests, json
import base64
from bs4 import BeautifulSoup


# CREAR VISTA MINUTAS

class ProjectMinuteItem(models.Model):
    _name = 'project.minute.item'
    _inherit = ['pad.common']

    name = fields.Char("Nombre")
    minute_id = fields.Many2one('project.minute', 'Minuta')
    project_id = fields.Many2one('project.project', 'Proyecto')
    discussion = fields.Html(string='Description')
    discussion_pad = fields.Char('Pad URL', pad_content_field='discussion', copy=False)
    use_pad = fields.Boolean(related="project_id.use_pads", string="Use collaborative pad", readonly=True)

class MinuteCommitment(models.Model):
    _name = 'project.minute.commitment'

    name = fields.Char('Acuerdo')
    approved_by = fields.Many2one('res.partner', 'Aprobado por')
    minute_id = fields.Many2one('project.minute', 'Minuta')


class ProjectMinute(models.Model):
    _name = 'project.minute'
    _inherit = ['mail.thread']
    _check_company_auto = True

    @api.model
    def _default_company_id(self):
        if self._context.get('default_project_id'):
            return self.env['project.project'].browse(self._context['default_project_id']).company_id
        return self.env.company

    name = fields.Char('Titulo')
    code = fields.Char('Codigo', compute="_code_get")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=_default_company_id)
    sequence = fields.Char("Secuencia")
    event_id = fields.Many2one('calendar.event', 'Reunión', required=True)
    project_id = fields.Many2one('project.project', 'Proyecto')
    task_ids = fields.One2many('project.task', 'minute_id', 'Tareas')
    requirements_ids = fields.One2many('project.requirement', 'minute_id_r', 'Requerimientos')
    partner_ids = fields.Many2many(related='event_id.partner_ids')
    item_ids = fields.One2many('project.minute.item', 'minute_id', 'Puntos')
    test_id = fields.Many2one('survey.survey', 'Test')
    survey_id = fields.Many2one('survey.survey', 'Calificación el Cliente')
    task_id = fields.Many2one('project.task', 'Tarea')
    commitment_ids = fields.One2many('project.minute.commitment', 'minute_id', 'Acuerdos')
    user_id = fields.Many2one('res.users', string="Responsable:", required=True)
    # template_id = fields.Many2one('mail.template', string='Email Template',
    #                               required=True)

    # discussion = fields.Html(string='Description')
    # discussion_pad = fields.Char('Pad URL', pad_content_field='discussion', copy=False)
    # use_pad = fields.Boolean(related="project_id.use_pads", string="Use collaborative pad", readonly=True)


    @api.model
    def create(self, vals):
        result = super(ProjectMinute, self).create(vals)
        project_id = vals['project_id']
        project = self.env['project.project'].search([('id', '=', project_id)])[0]
        result.sequence = project.minute_sequence_id.next_by_id()
        return result

    def name_get(self):
        result = []
        for record in self:
            if record.project_id.prefix:
                display_name = f'[{record.project_id.prefix + "-" + str(record.sequence)}] {record.name}'
            else:
                display_name = f'[{str(record.sequence)}] {record.name}'
            result.append((record.id, display_name))
        return result

    def _code_get(self):
        for record in self:
            if self.project_id.prefix:
                record.code = f'[{self.project_id.prefix + "-" + str(self.sequence)}]'
            else:
                record.code = f'[{str(self.sequence)}]'

    def action_print(self):
        data = {
            'model': 'project.minute',
            'name': self.name,
            'event_id': self.event_id.id,
            'project_id': self.project_id.id
        }

        # Codigo Datos Puntos
        points_list = []
        points = self.item_ids
        pnt = 1
        for pt in points:
            r = requests.get(
                url=pt.discussion_pad
            )
            soup = BeautifulSoup(r.content, 'html5lib')
            table = soup.find('body', attrs={'id': 'innerdocbody'})

            vals_p = {
                'pnt': pnt,
                'name_pnt': pt.name,
                'pad': soup,
            }
            points_list.append(vals_p)
            pnt += 1

        data.update({'points': points_list})

        # Codigo Datos tareas
        task_list = []
        no_task = 1

        if not self.task_id.delivered_task_date:
            vals_t = {
                'No_task': no_task,
                'task': self.task_id.name,
                'in_charge_task': self.task_id.user_ids.mapped('partner_id').ids,
                'delivered_date_task': ' ',
            }
        else:
            vals_t = {
                'No_task': no_task,
                'task': self.task_id.name,
                'in_charge_task': self.task_id.user_ids.mapped('partner_id').ids,
                'delivered_date_task': self.task_id.delivered_task_date.strftime('%d/%m/%Y'),
            }
        task_list.append(vals_t)
        no_task += 1

        data.update({'task': task_list, 'len_task': len(task_list)})
        # Codigo Datos requerimientos
        requirement_list = []
        requirements = self.env["project.requirement"].browse(self.read()[0].get('requirements_ids'))
        no_req = 1

        for req in requirements:
            vals_r = {
                'no_req': no_req,
                'name': req.name,
                'request_date': req.request_date.strftime('%d/%m/%Y'),
                'delivered_date': req.delivered_date.strftime('%d/%m/%Y')
            }
            requirement_list.append(vals_r)
            no_req += 1

        data.update({'requirement': requirement_list, 'len_requirements': len(requirement_list)})

        # Codigo Datos Concluciones
        commitment_list = []
        commitment = self.env["project.minute.commitment"].browse(self.read()[0].get('commitment_ids'))
        no_com = 1

        for com in commitment:
            vals_c = {
                'no_req': no_com,
                'name': com.name,
                'approved_by': com.approved_by,

            }
            commitment_list.append(vals_c)
            no_com += 1
        data.update({'commitments': commitment_list})

        # Datos Evento
        ate = self.env["calendar.event"].browse(self.event_id.id)
        ast_list = {index + 1: t.name for index, t in enumerate(ate.partner_ids)}  # LIST COMP

        if not ate.start_datetime:
            date_start = " "
        else:
            date_start = ate.start_datetime
        if not ate.location:
            location = " "
        else:
            location = ate.location

        data.update({'assistants': ast_list, 'location': location, 'start_date': date_start})
        return self.env.ref('project_inteligos.report_minute_details').report_action(self, data=data)

    def action_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self.env['ir.model.data']._xmlid_to_res_id('project_inteligos.minute_template_inteligos')
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'project.minute',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            # 'model_description': self.with_context(lang=lang).type_name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }