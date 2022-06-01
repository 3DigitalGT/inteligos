# -*- coding: utf-8 -*-

from odoo import models, fields, api

"""
Los sprints serán de dos semanas, comenzando cada lunes.
ToDo: Crear una tarea planificada para que cada lunes a las 00:00 para que si toca cambio, cambie los estados
de los sprints y ponga si las tareas fueron entregadas o no a tiempo.
"""


class ProjectSprint(models.Model):
    _name = "project.sprint"
    # _inherit = ['mail.thread']
    _order = 'project_id,sequence'
    _check_company_auto = True

    @api.model
    def _default_company_id(self):
        if self._context.get('default_project_id'):
            return self.env['project.project'].browse(self._context['default_project_id']).company_id
        return self.env.company

    name = fields.Char("Nombre")
    project_id = fields.Many2one('project.project', 'Proyecto', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=_default_company_id)
    sequence = fields.Char("Secuencia")
    date_start = fields.Date("Fecha Inicio")
    date_end = fields.Date("Fecha Fin")
    active = fields.Boolean("Activo", default = True)
    state = fields.Selection(
        [
            ('p', 'Planned'),
            ('c', 'Current'),
            ('o', 'Old'),
        ],
        default='p'
    )
    task_ids = fields.One2many('project.task', 'sprint_id', 'Tareas')
    requirement_ids = fields.One2many('project.requirement', 'sprint_id', 'Requerimientos')
    change_request_ids = fields.One2many('project.change', 'sprint_id', 'Cambios')

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s - %s - %s - %s' % (rec.name, rec.project_id.name, rec.date_start, rec.date_end)))

        return result

    def generate_sprints(self, date_start, date_end, range):
        """
        Debe crear los sprints entre las fechas indicadas.
        :param date_start:
        :param date_end:
        :param range: semana, mensual o bisemanal
        :return:
        """
        return True

    def set_new_sprint(self, current):
        """
        debe marcar el sprint actual como 'old' y el siguiente como 'current'
        :param current:
        :return:
        """
        return True

    @api.model
    def create(self, vals):
        """
        se debe validar que no exista ya un sprint con el que se puedan cruzar las fechas para el mismo proyecto
        :param vals_list:
        """
        result = super(ProjectSprint, self).create(vals)
        project_id = vals['project_id']
        project = self.env['project.project'].search([('id', '=', project_id)])
        result.sequence = project.sprint_sequence_id.next_by_id()
        return result

