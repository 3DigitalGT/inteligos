# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ChangeRequest(models.Model):
    _name = 'project.change'

    reference = fields.Char('Referencia')
    project_id = fields.Many2one('project.project', "Proyecto", required=True)
    requirement_id = fields.Many2one('project.requirement', 'Requerimiento')
    state = fields.Selection([
        ('new', 'Nuevo'),
        ('analysis', 'Análisis'),
        ('design', 'Diseño'),
        ('first_approve', 'Aprobación Funcional'),
        ('to_approve', 'Por Aprobar'),
        ('second_approve', 'Aprobado'),
        ('applied', 'Aplicado'),
        ('cancelled', 'Cancelado'),
    ])
    type = fields.Selection([
        ('add', 'Agregar Requerimiento'),
        ('change', 'Cambio a Requerimiento'),
        ('remove', 'Eliminar Requerimiento'),
    ])
    user_id = fields.Many2one('res.users', "Responsable")
    request_partner_id = fields.Many2one('res.partner', "Solicitado por")
    approve_partner_id = fields.Many2one('res.partner', "Autorizado por")
    request_date = fields.Date('Fecha Solicitud', required=True)
    approval_date = fields.Date('Fecha Aprobación', required=True)
    # removed_task_ids = fields.One2many('project.task', 'sprint_id', 'Tareas')
    task_ids = fields.One2many('project.task', 'change_request_id', 'Tareas')
    # sale_order_id = fields.Many2one('sale.order', 'Pedido de Venta')
    impact = fields.Integer('Impacto', help='Cantidad de días de atraso por el cambio')
    implementation_hours = fields.Integer('Horas de Implementación')
    development_hours = fields.Integer('Horas de Desarrollo')
    justification = fields.Text('Justificación')
    description = fields.Text('Descripción')
    communication_id = fields.Many2one('project.communication', 'Comunicación')
    version = fields.Integer('Versión', readonly=True, default=1)
    sprint_id = fields.Many2one('project.sprint', 'Sprint')
    delivered_date = fields.Date('Fecha de entrega')


