# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectRequirement(models.Model):
    _name = "project.requirement"
    _inherit = ['mail.thread', 'pad.common']
    _check_company_auto = True

    # def action_print(self):
    #     return self.env.ref('project_inteligos.report_requirements').report_action(self)

    @api.model
    def _default_company_id(self):
        if self._context.get('default_project_id'):
            return self.env['project.project'].browse(self._context['default_project_id']).company_id
        return self.env.company

    project_id = fields.Many2one(
        'project.project',
        string="Proyecto",
        required=True)
    active = fields.Boolean('Activo', default=True)
    # minute_id = fields.Many2one
    # minute_ids = fields.Many2many("project.minute","Minuta")
    sequence = fields.Char("Codigo")
    name = fields.Char("Name")
    minute_id_r = fields.Many2one('project.minute', 'Minutas')
    state = fields.Selection([
        ('new', 'New'),
        ('approved', 'Approved'),
        ('backlog', 'Backlog'),
        ('on_process', 'On Process'),
        ('done', 'Done'),
        ('deploy', 'On Deployment'),
        ('delivered', 'Delivered'),
        ('cancel', 'Cancel'),
        ('old', 'Old Version')
    ],
        track_visibility=True,
        default = 'new'
    )
    description = fields.Html(string='Description')
    description_pad = fields.Char('Pad URL', pad_content_field='description', copy=False)
    use_pad = fields.Boolean(related="project_id.use_pads", string="Use collaborative pad", readonly=True)
    volume = fields.Integer('Volumen', Help='Cantidad de operaciones diaras o mensuales ')
    volume_range = fields.Selection(
        [
            ('d', 'Diario'),
            ('s', 'Semanal'),
            ('m', 'Mensual'),
            ('s', 'Anual'),
        ],
        string="Rango del volumen"
    )
    task_ids = fields.Many2many('project.task',string='Tareas')
    customer_story = fields.Html("Customer Story")
    scenario = fields.Html("Escenario")

    request_date = fields.Date('Fecha Requerimiento', default=fields.Date.today)
    requested_by_id = fields.Many2one('res.partner', string="Solicitado Por:", required=True)
    approved_by_id = fields.Many2one('res.partner', string="Aprobrado Por:")
    approved_date = fields.Date('Fecha Aprobación')
    delivered_date = fields.Date('Fecha De Entrega')
    employee_id = fields.Many2one('res.users', string="Consultor:", requiered=True)
    category_id = fields.Many2many('project.tags')
    solution_type = fields.Selection(
        [
            ('d', 'Desarrollo'),
            ('i', 'Implementación'),
        ],
        string="Tipo Solución"
    )
    gap = fields.Text("Solución Propuesta")
    version = fields.Integer("Versión", default=1)
    parent_id = fields.Many2one('project.requirement', string="Nuevo Requerimiento", index=True, ondelete='cascade')
    prev_project_requirement_id = fields.Many2one('project.requirement', string="Version Anterior")
    current_operation = fields.Selection(
        [
            ('n', 'No existe'),
            ('m', 'Manual'),
            ('e', 'Excel'),
            ('s', 'Software')
        ]
    )
    complexity = fields.Selection(
        [
            ('l', 'Baja'),
            ('m', 'Media'),
            ('h', 'Alta'),
        ]
    )
    planned_hours = fields.Integer('Horas Planificadas')
    effective_hours = fields.Integer('Horas Reales')
    change_request_ids = fields.One2many('project.change', 'requirement_id', string='Cambios')
    sprint_id = fields.Many2one('project.sprint', 'Sprint')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=_default_company_id)
    compliance = fields.Char('Reglamentación Aplicable', default='N/A', requried=True)  # ToDo: add to view
    priority = fields.Selection(
        [
            ('mh', 'Must Have'),
            ('nh', 'Nice to Have'),
            ('wh', 'Wont Have'),
        ]
    )

    def name_get(self):
        result = []
        for record in self:
            if record.project_id.prefix:
                display_name = f'[{record.project_id.prefix + "-" + str(record.sequence)}] {record.name}'
            else:
                display_name = f'[{str(record.sequence)}] {record.name}'
            result.append((record.id, display_name))
        return result

    @api.model
    def create(self, vals):
        result = super(ProjectRequirement, self).create(vals)
        project_id = vals['project_id']
        project = self.env['project.project'].search([('id', '=', project_id)])[0]
        result.sequence = project.requirement_sequence_id.next_by_id()
        return result

    def action_print(self):
        if self.read()[0].get('complexity') == 'l':
            complejidad = 'Baja'
        elif self.read()[0].get('complexity') == 'm':
            complejidad = 'Media'
        elif self.read()[0].get('complexity') == 'h':
            complejidad = 'Alta'
        else:
            complejidad = ' '

        if self.read()[0].get('priority') == 'mh':
            prioridad = 'Must Have'
        elif self.read()[0].get('priority') == 'nh':
            prioridad = 'Nice to Have'
        elif self.read()[0].get('priority') == 'wh':
            prioridad = 'Wont Have'
        else:
            prioridad = ' '

        if self.approved_by_id:
            approved_by = self.approved_by_id.name
        else:
            approved_by = ' '

        if self.requested_by_id:
            requested_by = self.requested_by_id.name
        else:
            requested_by = ' '

        if self.request_date:
            request_date = self.request_date.strftime('%d/%m/%Y')
        else:
            request_date = ' '

        if self.approved_date:
            approved_date = self.approved_date.strftime('%d/%m/%Y')
        else:
            approved_date = ' '

        if self.delivered_date:
            delivered_date = self.delivered_date.strftime('%d/%m/%Y')
        else:
            delivered_date = ' '

        data = {
            'model': 'project.requirement',
            # 'form' : self.read(),
            'name_proyect': self.project_id.name,
            'cliente': self.company_id.name,
            'name_requested': requested_by,
            'name_approved': approved_by,
            'date_requested': request_date,
            'date_approved': approved_date,
            'parent': self.parent_id.name,
            'delivered_date': delivered_date,
            'priority': prioridad,
            'name_requirement': self.read()[0].get('display_name'),
            'Details': self.customer_story,
            'scenario': self.scenario,
            'solution': self.gap,
            'version': self.version,
            'complexity': complejidad,
            'planned_hours': self.planned_hours,
            'effective_hours': self.effective_hours,
        }

        # Codigo Datos Cambios
        changes_list = []
        changes = self.env["project.change"].browse(self.read()[0].get('change_request_ids'))
        no = 1
        for ch in changes:
            if ch.type == 'add':
                cambio = 'Agregar Requerimiento'
            elif ch.type == 'change':
                cambio = 'Cambio a Requerimiento'
            elif ch.type == 'remove':
                cambio = 'Eliminar Requerimiento'
            # Filtrado de tareas entregadas vs atrasadas
            vals = {
                'No': no,
                'change': cambio,
                'in_charge': ch.read()[0].get('user_id')[1],
                # 'department': ,
                'approved_by': ch.read()[0].get('approve_partner_id')[1],
                'delivered_date': ch.read()[0].get('delivered_date').strftime('%d/%m/%Y'),
            }
            changes_list.append(vals)
            no += 1
            print(ch)

        # Codigo Tareas
        task_list = []
        tasks = self.env["project.task"].browse(self.read()[0].get('task_ids'))
        no_task = 1
        for tk in tasks:
            vals_t = {
                'No_task': no_task,
                'task': tk.name,
                'in_charge_task': tk.user_id.read()[0].get('partner_id')[1],
                # 'department': ,
                'approved_by_task': tk.approve_task_partner_id.read()[0].get('name'),
                'delivered_date_task': tk.delivered_task_date.strftime('%d/%m/%Y'),
            }
            task_list.append(vals_t)
            no_task += 1
        data.update({'changes': changes_list, 'task': task_list, 'total_changes': len(changes_list),
                     'total_tasks': len(task_list)})

        return self.env.ref('project_inteligos.report_project_details').report_action(self, data=data)

    def _get_previous_versions(self):
        """
        Función para devolver un listado de todas las versiones anteriores del requerimiento
        :return:
        """
        return True

    def _create_new_version(self):
        """
        Función para crear una nueva tarea, con su respectiva versión y marcar la actual con estado 'old'
        :return:
        """
        return True

    def action_send_email_requirement(self):

        '''
         This function opens a window to compose an email, with the emai template message loaded by default
         '''

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = \
                ir_model_data.get_object_reference('project_inteligos','email_template')[1]
            # print(template_id)
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'project.requirement',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def action_send_communication(self):
        '''
         This function opens a window to compose an email, with the emai template message loaded by default
         '''

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = \
                ir_model_data.get_object_reference('project_inteligos', 'comunication_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'project.requirement',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def action_cancel(self):
        '''
        ToDo: crear codigo para cancelar eventos
        '''
        return True