# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AttachmentListWiz(models.Model):
    _name = 'project_inteligos.attachment_list_wiz'
    _description = 'Listado de Adjuntos Wizard'

    @api.model
    def _get_default_task_id(self):
        task_id = self._context['task_id']
        return task_id

    @api.depends('task_id')
    def _compute_attachments(self):
        for record in self:
            attachments_ids = record.env['ir.attachment'].search([('res_id', '=', record.task_id.id)])
            record.attachments = attachments_ids
            record.qty = len(attachments_ids)

    task_id = fields.Many2one(
        'project.task',
        default=_get_default_task_id,
        string='Tarea'
    )
    qty = fields.Integer(
        default=0,
        compute='_compute_attachments',
        string="Cantidad"
    )
    attachments = fields.One2many(
        'ir.attachment',
        'attachment_list_id',
        compute='_compute_attachments',
        string="Archivos Adjuntos"
    )
