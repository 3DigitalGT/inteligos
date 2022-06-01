# -*- coding: utf-8 -*-

from odoo import models, fields, api
#CREAR VISTA Y SOLO SI ES MINUTA QUE SALGA ESCOGER

class ProjectCommunication(models.Model):
    _name = 'project.communication'

    date = fields.Date('Fecha',default=fields.Date.today,required=True)
    project_id = fields.Many2one('project.project')
    user_id = fields.Many2one('res_partner')
    #recipient_ids = fields.One2many('res.partner')
    message = fields.Text('Mensaje')
    type = fields.Selection([
        ('m', 'Memorandum'),
        ('r', 'Recordatorio'),
        ('n', 'Minuta'),
        ('c', 'Cambio'),
    ])
    change_request_id = fields.Many2one('project.change_request', 'Cambio')
    task_id = fields.Many2one('project.task', 'Tarea')
    requirement_id = fields.Many2one('project.requirement', 'Requerimiento')
    minute_id = fields.Many2one('project.minute', 'Minuta')

