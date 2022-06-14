# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError


class ProjectProjectInherited(models.Model):
    _inherit = ['project.project', 'pad.common']
    _name = 'project.project'
    _description = 'Proyectos Inteligos'

    @api.depends('message_ids')
    def _compute_message_count(self):
        """
        Contador de reuniones que ha tenido la tarea.
        """
        for record in self:
            record.message_count = len(record.message_ids)

    def _compute_task_count(self):
        super(ProjectProjectInherited, self)._compute_task_count()
        for project in self:
            tasks = self.env['project.task'].search([('project_id', '=', project.id)])
            project.task_count_cus = len(tasks.filtered(lambda task: task.scope == 'c').ids)
            project.task_count_dev = len(tasks.filtered(lambda task: task.scope == 'd').ids)
            project.task_count_imp = len(tasks.filtered(lambda task: task.scope == 'i').ids)
            project.task_count_tic = len(tasks.filtered(lambda task: task.scope == 't').ids)

    prefix = fields.Char(
        required=True,
        copied=False,
        string="Prefijo de Proyecto"
    )
    message_count = fields.Integer(
        default=0,
        compute='_compute_message_count',
        string="Cantidad de Mensajes"
    )

    # minute_ids = fields.One2many('project.minute','project_id','Minutas')
    # description = fields.Html(string='Description')
    # description_pad = fields.Char('Pad URL', pad_content_field='description', copy=False)
    project_requirement_ids = fields.One2many('project.requirement', 'project_id', 'Requerimientos')
    project_sprints_ids = fields.One2many('project.sprint', 'project_id', 'Sprints')
    project_minute_ids = fields.One2many('project.minute.item', 'project_id', 'Minutas')
    sequence_id = fields.Many2one('ir.sequence', "Secuencia")
    requirement_sequence_id = fields.Many2one('ir.sequence', "Secuencia Requerimientos")
    sprint_sequence_id = fields.Many2one('ir.sequence', "Secuencia Sprints")
    minute_sequence_id = fields.Many2one('ir.sequence', "Secuencia Minutas")
    task_count_dev = fields.Integer(compute='_compute_task_count', string="Task Count Development", store=True)
    task_count_imp = fields.Integer(compute='_compute_task_count', string="Task Count Implementation", store=True)
    task_count_cus = fields.Integer(compute='_compute_task_count', string="Task Count Customer", store=True)
    task_count_tic = fields.Integer(compute='_compute_task_count', string="Task Count Customer", store=True)
    # Creados por mi
    # initial_date = fields.Date('Fecha de inicio')
    # delivery_date = fields.Date('Fecha de Entrega')

    # actual_phase = fields.Selection([
    #     ('Nuevo', 'Nuevo'),
    #     ('Exploracion', 'Exploracion'),
    #     ('En Marcha', 'En Marcha'),
    # ],
    #     track_visibility=True,
    # )
    # Campos para la vista Details
    requirement_count = fields.Integer("count_requirements")
    task_count = fields.Integer("count_task")
    changes_count = fields.Integer("count_changes")
    sprint_count = fields.Integer("count_sprint")
    minute_count = fields.Integer("count-minute")
    total_task = fields.Integer("task_t")
    total_backlog = fields.Integer("backlog_t")
    total_delivered = fields.Integer("delivered_t")
    total_delay = fields.Integer("delay_t")

    def name_get(self):
        result = []
        for record in self:
            display_name = f'{record.name} [{record.prefix or ""}]'
            result.append((record.id, display_name))
        return result

    @api.model
    def create(self, vals):
        result = super(ProjectProjectInherited, self).create(vals)
        if not self.sequence_id:
            result.sequence_id = self._create_sequence(vals)
            vals['sequence_id'] = result.sequence_id.id
        if not self.requirement_sequence_id:
            result.requirement_sequence_id = self._create_sequence(vals)
            vals['requirement_sequence_id'] = result.requirement_sequence_id.id
        if not self.sprint_sequence_id:
            result.sprint_sequence_id = self._create_sequence(vals)
            vals['sprint_sequence_id'] = result.sprint_sequence_id.id
        if not self.minute_sequence_id:
            result.minute_sequence_id = self._create_sequence(vals)
            vals['minute_sequence_id'] = result.minute_sequence_id.id
        result.type_ids = self.env['project.task.type'].search([('default', '=', True)]).ids
        return result

    def _create_sequence(self, vals):
        prefix = self.prefix
        seq_name = 'project_' + vals['name']
        seq = {
            'name': seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': False,
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
        seq = self.env['ir.sequence'].create(seq)
        return seq

    def print_report_complete(self):
        if self.partner_id:
            partner = self.partner_id.name
        else:
            partner = ' '

        if self.user_id:
            user = self.user_id.name
        else:
            user = ' '

        data = {
            'model': 'project.project',
            # 'form' : self.read()[0],
            'name': self.read()[0].get('name'),
            'cliente': partner,
            'implementador': user,
            'fecha': fields.Datetime.now().strftime('%d/%m/%Y'),
        }

        task_list_d = []
        task_list_i = []
        task_list_c = []
        task_list_t = []
        task_list_x = []

        len_d_n = 0
        len_d_p = 0
        len_d_r = 0
        len_d_c = 0
        len_d_d = 0

        len_i_n = 0
        len_i_p = 0
        len_i_r = 0
        len_i_c = 0
        len_i_d = 0

        len_c_n = 0
        len_c_p = 0
        len_c_r = 0
        len_c_c = 0
        len_c_d = 0

        len_t_n = 0
        len_t_p = 0
        len_t_r = 0
        len_t_c = 0
        len_t_d = 0

        len_x_n = 0
        len_x_p = 0
        len_x_r = 0
        len_x_c = 0
        len_x_d = 0

        no_tk_d = 1
        no_tk_i = 1
        no_tk_c = 1
        no_tk_t = 1
        no_tk_x = 1
        for tk in self.tasks:

            if tk.scope == 'd':
                scope = 'Desarrollo'
                # Calculo sprints

                today_date = datetime.date(datetime.now() - timedelta(days=1))


                # CALCULO PARA COLOCAR LA TAREA COMO ATRASADA O NO
                if tk.date_deadline:
                    if tk.date_deadline <= today_date:
                        tk.delay = True
                    else:
                        tk.delay = False
                if tk.stage_id:
                    if tk.stage_id.name == 'Nuevo':
                        if not tk.delay:
                            tk.new_task = True
                        else:
                            tk.new_task = False
                    elif tk.stage_id.name == 'Revision Cliente':
                        if not tk.delay:
                            tk.client = True
                        else:
                            tk.client = False

                vals_d = {
                    'No': no_tk_d,
                    'name': tk.name,
                    'user_id': "".join([x[0].upper() for x in str(tk.user_id.name).split(' ')]),
                    'task_stage': tk.stage_id.name,
                    'planned_hours': tk.planned_hours,
                    'effective_hours': tk.effective_hours,
                    # 'stage': tk.stage_id.name,
                    'delay': tk.delay,
                    'new': tk.new_task,
                    'client': tk.client,

                }

                if tk.stage_id.name == 'Nuevo':
                    len_d_n += 1
                elif tk.stage_id.name == 'En Proceso':
                    len_d_p += 1
                elif tk.stage_id.name == 'Revision Interna':
                    len_d_r += 1
                elif tk.stage_id.name == 'Revision Cliente':
                    len_d_c += 1
                elif tk.stage_id.name == 'Terminado':
                    len_d_d += 1

                task_list_d.append(vals_d)
                no_tk_d += 1

            elif tk.scope == 'i':
                scope = 'Implementacíon'

                # Calculo sprints

                today_date = datetime.date(datetime.now() - timedelta(days=1))
                # CALCULO PARA COLOCAR LA TAREA COMO ATRASADA O NO
                new_task_i = False
                client_i = False
                if tk.date_deadline:
                    if tk.date_deadline <= datetime.date(datetime.now() - timedelta(days=1)):
                        tk.delay = True
                    else:
                        tk.delay = False
                if tk.stage_id:
                    if tk.stage_id.name == 'Nuevo':
                        if not tk.delay:
                            new_task_i = True
                        else:
                            new_task_i = False
                    elif tk.stage_id.name == 'Revision Cliente':
                        if not tk.delay:
                            client_i = True
                        else:
                            client_i = False

                vals_i = {
                    'No': no_tk_i,
                    'name': tk.name,
                    'user_id': "".join([x[0].upper() for x in str(tk.user_id.name).split(' ')]),
                    'task_stage': tk.stage_id.name,
                    'planned_hours': tk.planned_hours,
                    'effective_hours': tk.effective_hours,
                    # 'stage': tk.stage_id.name,
                    'delay': tk.delay,
                    'new': new_task_i,
                    'client': client_i,

                }
                if tk.stage_id.name == 'Nuevo':
                    len_i_n += 1
                elif tk.stage_id.name == 'En Proceso':
                    len_i_p += 1
                elif tk.stage_id.name == 'Revision Interna':
                    len_i_r += 1
                elif tk.stage_id.name == 'Revision Cliente':
                    len_i_c += 1
                elif tk.stage_id.name == 'Terminado':
                    len_i_d += 1

                task_list_i.append(vals_i)
                no_tk_i += 1

            elif tk.scope == 'c':
                scope = 'Clientes'

                # Calculo sprints

                # CALCULO PARA COLOCAR LA TAREA COMO ATRASADA O NO
                if tk.date_deadline:
                    if tk.date_deadline <= datetime.date(datetime.now() - timedelta(days=1)):
                        tk.delay = True
                    else:
                        tk.delay = False
                if tk.stage_id:
                    if tk.stage_id.name == 'Nuevo':
                        if not tk.delay:
                            tk.new_task = True
                        else:
                            tk.new_task = False
                    elif tk.stage_id.name == 'Revision Cliente':
                        if not tk.delay:
                            tk.client = True
                        else:
                            tk.client = False

                vals_c = {
                    'No': no_tk_c,
                    'name': tk.name,
                    'user_id': "".join([x[0].upper() for x in str(tk.user_id.name).split(' ')]),
                    'task_stage': tk.stage_id.name,
                    'planned_hours': tk.planned_hours,
                    'effective_hours': tk.effective_hours,
                    # 'stage': tk.stage_id.name,
                    'delay': tk.delay,
                    'new': tk.new_task,
                    'client': tk.client,
                }
                if tk.stage_id.name == 'Nuevo':
                    len_c_n += 1
                elif tk.stage_id.name == 'En Proceso':
                    len_c_p += 1
                elif tk.stage_id.name == 'Revision Interna':
                    len_c_r += 1
                elif tk.stage_id.name == 'Revision Cliente':
                    len_c_c += 1
                elif tk.stage_id.name == 'Terminado':
                    len_c_d += 1

                task_list_c.append(vals_c)
                no_tk_c += 1
            elif tk.scope == 't':
                scope = 'Tickets'

                # CALCULO PARA COLOCAR LA TAREA COMO ATRASADA O NO
                if tk.date_deadline:
                    if tk.date_deadline <= datetime.date(datetime.now() - timedelta(days=1)):
                        tk.delay = True
                    else:
                        tk.delay = False
                if tk.stage_id:
                    if tk.stage_id.name == 'Nuevo':
                        if not tk.delay:
                            tk.new_task = True
                        else:
                            tk.new_task = False
                    elif tk.stage_id.name == 'Revision Cliente':
                        if not tk.delay:
                            tk.client = True
                        else:
                            tk.client = False

                vals_t = {
                    'No': no_tk_t,
                    'name': tk.name,
                    'user_id': "".join([x[0].upper() for x in str(tk.user_id.name).split(' ')]),
                    'task_stage': tk.stage_id.name,
                    'planned_hours': tk.planned_hours,
                    'effective_hours': tk.effective_hours,
                    # 'stage': tk.stage_id.name,
                    'delay': tk.delay,
                    'new': tk.new_task,
                    'client': tk.client,

                }
                if tk.stage_id.name == 'Nuevo':
                    len_t_n += 1
                elif tk.stage_id.name == 'En Proceso':
                    len_t_p += 1
                elif tk.stage_id.name == 'Revision Interna':
                    len_t_r += 1
                elif tk.stage_id.name == 'Revision Cliente':
                    len_t_c += 1
                elif tk.stage_id.name == 'Terminado':
                    len_t_d += 1

                task_list_t.append(vals_t)
                no_tk_t += 1
            else:
                scope = ''


                # CALCULO PARA COLOCAR LA TAREA COMO ATRASADA O NO
                if tk.date_deadline:
                    if tk.date_deadline <= datetime.date(datetime.now() - timedelta(days=1)):
                        tk.delay = True
                    else:
                        tk.delay = False
                if tk.stage_id:
                    if tk.stage_id.name == 'Nuevo':
                        if not tk.delay:
                            tk.new_task = True
                        else:
                            tk.new_task = False
                    elif tk.stage_id.name == 'Revision Cliente':
                        if not tk.delay:
                            tk.client = True
                        else:
                            tk.client = False

                vals_x = {
                    'No': no_tk_x,
                    'name': tk.name,
                    'user_id': "".join([x[0].upper() for x in str(tk.user_id.name).split(' ')]),
                    'task_stage': tk.stage_id.name,
                    'planned_hours': tk.planned_hours,
                    'effective_hours': tk.effective_hours,
                    # 'stage': tk.stage_id.name,
                    'delay': tk.delay,
                    'new': tk.new_task,
                    'client': tk.client,

                }
                if tk.stage_id.name == 'Nuevo':
                    len_x_n += 1
                elif tk.stage_id.name == 'En Proceso':
                    len_x_p += 1
                elif tk.stage_id.name == 'Revision Interna':
                    len_x_r += 1
                elif tk.stage_id.name == 'Revision Cliente':
                    len_x_c += 1
                elif tk.stage_id.name == 'Terminado':
                    len_x_d += 1

                task_list_x.append(vals_x)
                no_tk_x += 1

        data.update(
            {'task_d': task_list_d, 'total_task_d': len(task_list_d),
             'new_d': len_d_n,
             'on_process_d': len_d_p,
             'review_d': len_d_r,
             'client_d': len_d_c,
             'delivered_d': len_d_d,
             'task_i': task_list_i, 'total_task_i': len(task_list_i),
             'new_i': len_i_n,
             'on_process_i': len_i_p,
             'review_i': len_i_r,
             'client_i': len_i_c,
             'delivered_i': len_i_d,
             'task_c': task_list_c, 'total_task_c': len(task_list_c),
             'new_c': len_c_n,
             'on_process_c': len_c_p,
             'review_c': len_c_r,
             'client_c': len_c_c,
             'delivered_c': len_c_d,
             'task_t': task_list_t, 'total_task_t': len(task_list_t),
             'new_t': len_t_n,
             'on_process_t': len_t_p,
             'review_t': len_t_r,
             'client_t': len_t_c,
             'delivered_t': len_t_d,
             'task_x': task_list_x, 'total_task_x': len(task_list_x),
             'new_x': len_x_n,
             'on_process_x': len_x_p,
             'review_x': len_x_r,
             'client_x': len_x_c,
             'delivered_x': len_x_d,
             # 'task_x': task_list_x, 'total_task_x': len(task_list_x),
             })

        requirements_list = []
        requirements = self.env["project.requirement"].browse(self.read()[0].get('project_requirement_ids'))
        no = 1

        for req in requirements:
            if req.priority == 'mh':
                prioridad = 'Necesario'
            elif req.priority == 'nh':
                prioridad = 'Parcialmente Necesario'
            elif req.priority == 'wh':
                prioridad = 'Innecesario'
            else:
                prioridad = " "

            if req.solution_type == 'd':
                solucion = 'Desarrollo'
            elif req.solution_type == 'i':
                solucion = 'Implementación'
            else:
                solucion = " "

            if req.state == 'new':
                state = 'Nuevo'
            elif req.state == 'approved':
                state = 'Aprobado'
            elif req.state == 'backlog':
                state = 'Backlog'
            elif req.state == 'on_process':
                state = 'En proceso'
            elif req.state == 'done':
                state = 'Terminado'
            elif req.state == 'deploy':
                state = 'Deploy'
            elif req.state == 'delivered':
                state = 'Entregado'
            elif req.state == 'cancel':
                state = 'Cancelado'
            elif req.state == 'old':
                state = 'Version Antigua'
            else:
                state = ' '

            vals = {
                'No': no,
                'name': req.name,
                'state': state,
                'version': req.version,
                'solution_type': solucion,
                'request_Date': req.request_date,
                'requested_by': "".join([x[0].upper() for x in str(req.requested_by_id.name).split(' ')]),
                'approved_date': req.approved_date,
                'approved_by_id': "".join([x[0].upper() for x in str(req.approved_by_id.name).split(' ')]),
                'priority': "".join([x[0].upper() for x in str(prioridad).split(' ')]),
                'planned_hours': req.planned_hours,
                'effective_hours': req.effective_hours,
            }
            requirements_list.append(vals)
            no += 1

        data.update(
            {'total': len(requirements), 'entregados': len(requirements.filtered(lambda req: req.state == 'deliverd')),
             'proceso': len(requirements.filtered(lambda req: req.state == 'on_process')),
             'aprobado': len(requirements.filtered(lambda req: req.state == 'approved')),
             'terminados': len(requirements.filtered(lambda req: req.state == 'done')),
             'cancelados': len(requirements.filtered(lambda req: req.state == 'cancel')),
             'nuevos': len(requirements.filtered(lambda req: req.state == 'new')),
             'backlog': len(requirements.filtered(lambda req: req.state == 'backlog')),
             'antigua': len(requirements.filtered(lambda req: req.state == 'old')),
             'deploy': len(requirements.filtered(lambda req: req.state == 'deploy')),
             'requerimientos': requirements_list})

        return self.env.ref('project_inteligos.report_general').report_action(self, data=data)

    # Codigo Agregado para el boton
    def print_report_sprint(self):
        if self.partner_id:
            partner = self.partner_id.name
        else:
            partner = ' '

        if self.user_id:
            user = self.user_id.name
        else:
            user = ' '

        data = {
            'model': 'project.project',
            # 'form' : self.read()[0],
            'name': self.read()[0].get('name'),
            'cliente': partner,
            'implementador': user,
            'fecha': fields.Datetime.now().strftime('%d/%m/%Y'),
        }

        task_list_d = []
        task_list_i = []
        task_list_c = []
        task_list_t = []
        task_list_x = []

        len_d_n = 0
        len_d_p = 0
        len_d_r = 0
        len_d_c = 0
        len_d_d = 0

        len_i_n = 0
        len_i_p = 0
        len_i_r = 0
        len_i_c = 0
        len_i_d = 0

        len_c_n = 0
        len_c_p = 0
        len_c_r = 0
        len_c_c = 0
        len_c_d = 0

        len_t_n = 0
        len_t_p = 0
        len_t_r = 0
        len_t_c = 0
        len_t_d = 0

        len_x_n = 0
        len_x_p = 0
        len_x_r = 0
        len_x_c = 0
        len_x_d = 0

        no_tk_d = 1
        no_tk_i = 1
        no_tk_c = 1
        no_tk_t = 1
        no_tk_x = 1
        for tk in self.tasks:

            if tk.scope == 'd':
                scope = 'Desarrollo'
                # Calculo sprints

                today_date = datetime.date(datetime.now() - timedelta(days=1))
                if tk.sprint_id:
                    if tk.sprint_id.date_start <= today_date <= tk.sprint_id.date_end:
                        actual_sprint = True
                    else:
                        actual_sprint = False
                else:
                    actual_sprint = False

                # CALCULO PARA COLOCAR LA TAREA COMO ATRASADA O NO
                if tk.date_deadline:
                    if tk.date_deadline <= today_date:
                        tk.delay = True
                    else:
                        tk.delay = False
                if tk.stage_id:
                    if tk.stage_id.name == 'Nuevo':
                        if not tk.delay:
                            tk.new_task = True
                        else:
                            tk.new_task = False
                    elif tk.stage_id.name == 'Revision Cliente':
                        if not tk.delay:
                            tk.client = True
                        else:
                            tk.client = False
                if actual_sprint:
                    vals_d = {
                        'No': no_tk_d,
                        'name': tk.name,
                        'user_id': "".join([x[0].upper() for x in str(tk.user_id.name).split(' ')]),
                        'task_stage': tk.stage_id.name,
                        'planned_hours': tk.planned_hours,
                        'effective_hours': tk.effective_hours,
                        # 'stage': tk.stage_id.name,
                        'delay': tk.delay,
                        'new': tk.new_task,
                        'client': tk.client,
                        'actual_sprint': actual_sprint,
                    }

                    if tk.stage_id.name == 'Nuevo':
                        len_d_n += 1
                    elif tk.stage_id.name == 'En Proceso':
                        len_d_p += 1
                    elif tk.stage_id.name == 'Revision Interna':
                        len_d_r += 1
                    elif tk.stage_id.name == 'Revision Cliente':
                        len_d_c += 1
                    elif tk.stage_id.name == 'Terminado':
                        len_d_d += 1

                    task_list_d.append(vals_d)
                    no_tk_d += 1

            elif tk.scope == 'i':
                scope = 'Implementacíon'

                # Calculo sprints

                today_date = datetime.date(datetime.now() - timedelta(days=1))
                if tk.sprint_id:
                    if tk.sprint_id.date_start <= today_date <= tk.sprint_id.date_end:
                        actual_sprint = True
                    else:
                        actual_sprint = False
                else:
                    actual_sprint = False
                # CALCULO PARA COLOCAR LA TAREA COMO ATRASADA O NO
                new_task_i = False
                client_i = False
                if tk.date_deadline:
                    if tk.date_deadline <= datetime.date(datetime.now() - timedelta(days=1)):
                        tk.delay = True
                    else:
                        tk.delay = False
                if tk.stage_id:
                    if tk.stage_id.name == 'Nuevo':
                        if not tk.delay:
                            new_task_i = True
                        else:
                            new_task_i = False
                    elif tk.stage_id.name == 'Revision Cliente':
                        if not tk.delay:
                            client_i = True
                        else:
                            client_i = False
                if actual_sprint:
                    vals_i = {
                        'No': no_tk_i,
                        'name': tk.name,
                        'user_id': "".join([x[0].upper() for x in str(tk.user_id.name).split(' ')]),
                        'task_stage': tk.stage_id.name,
                        'planned_hours': tk.planned_hours,
                        'effective_hours': tk.effective_hours,
                        # 'stage': tk.stage_id.name,
                        'delay': tk.delay,
                        'new': new_task_i,
                        'client': client_i,
                        'actual_sprint': actual_sprint,
                    }
                    if tk.stage_id.name == 'Nuevo':
                        len_i_n += 1
                    elif tk.stage_id.name == 'En Proceso':
                        len_i_p += 1
                    elif tk.stage_id.name == 'Revision Interna':
                        len_i_r += 1
                    elif tk.stage_id.name == 'Revision Cliente':
                        len_i_c += 1
                    elif tk.stage_id.name == 'Terminado':
                        len_i_d += 1

                    task_list_i.append(vals_i)
                    no_tk_i += 1

            elif tk.scope == 'c':
                scope = 'Clientes'

                # Calculo sprints

                today_date = datetime.date(datetime.now() - timedelta(days=1))
                if tk.sprint_id:
                    if tk.sprint_id.date_start <= today_date <= tk.sprint_id.date_end:
                        actual_sprint = True
                    else:
                        actual_sprint = False
                else:
                    actual_sprint = False
                # CALCULO PARA COLOCAR LA TAREA COMO ATRASADA O NO
                if tk.date_deadline:
                    if tk.date_deadline <= datetime.date(datetime.now() - timedelta(days=1)):
                        tk.delay = True
                    else:
                        tk.delay = False
                if tk.stage_id:
                    if tk.stage_id.name == 'Nuevo':
                        if not tk.delay:
                            tk.new_task = True
                        else:
                            tk.new_task = False
                    elif tk.stage_id.name == 'Revision Cliente':
                        if not tk.delay:
                            tk.client = True
                        else:
                            tk.client = False
                if actual_sprint:
                    vals_c = {
                        'No': no_tk_c,
                        'name': tk.name,
                        'user_id': "".join([x[0].upper() for x in str(tk.user_id.name).split(' ')]),
                        'task_stage': tk.stage_id.name,
                        'planned_hours': tk.planned_hours,
                        'effective_hours': tk.effective_hours,
                        # 'stage': tk.stage_id.name,
                        'delay': tk.delay,
                        'new': tk.new_task,
                        'client': tk.client,
                        'actual_sprint': actual_sprint,
                    }
                    if tk.stage_id.name == 'Nuevo':
                        len_c_n += 1
                    elif tk.stage_id.name == 'En Proceso':
                        len_c_p += 1
                    elif tk.stage_id.name == 'Revision Interna':
                        len_c_r += 1
                    elif tk.stage_id.name == 'Revision Cliente':
                        len_c_c += 1
                    elif tk.stage_id.name == 'Terminado':
                        len_c_d += 1

                    task_list_c.append(vals_c)
                    no_tk_c += 1
            elif tk.scope == 't':
                scope = 'Tickets'

                # Calculo sprints

                today_date = datetime.date(datetime.now() - timedelta(days=1))
                if tk.sprint_id:
                    if tk.sprint_id.date_start <= today_date <= tk.sprint_id.date_end:
                        actual_sprint = True
                    else:
                        actual_sprint = False
                else:
                    actual_sprint = False
                # CALCULO PARA COLOCAR LA TAREA COMO ATRASADA O NO
                if tk.date_deadline:
                    if tk.date_deadline <= datetime.date(datetime.now() - timedelta(days=1)):
                        tk.delay = True
                    else:
                        tk.delay = False
                if tk.stage_id:
                    if tk.stage_id.name == 'Nuevo':
                        if not tk.delay:
                            tk.new_task = True
                        else:
                            tk.new_task = False
                    elif tk.stage_id.name == 'Revision Cliente':
                        if not tk.delay:
                            tk.client = True
                        else:
                            tk.client = False
                if actual_sprint:
                    vals_t = {
                        'No': no_tk_t,
                        'name': tk.name,
                        'user_id': "".join([x[0].upper() for x in str(tk.user_id.name).split(' ')]),
                        'task_stage': tk.stage_id.name,
                        'planned_hours': tk.planned_hours,
                        'effective_hours': tk.effective_hours,
                        # 'stage': tk.stage_id.name,
                        'delay': tk.delay,
                        'new': tk.new_task,
                        'client': tk.client,
                        'actual_sprint': actual_sprint,
                    }
                    if tk.stage_id.name == 'Nuevo':
                        len_t_n += 1
                    elif tk.stage_id.name == 'En Proceso':
                        len_t_p += 1
                    elif tk.stage_id.name == 'Revision Interna':
                        len_t_r += 1
                    elif tk.stage_id.name == 'Revision Cliente':
                        len_t_c += 1
                    elif tk.stage_id.name == 'Terminado':
                        len_t_d += 1

                    task_list_t.append(vals_t)
                    no_tk_t += 1
            else:
                scope = ''

                # Calculo sprints

                today_date = datetime.date(datetime.now() - timedelta(days=1))
                if tk.sprint_id:
                    if tk.sprint_id.date_start <= today_date <= tk.sprint_id.date_end:
                        actual_sprint = True
                    else:
                        actual_sprint = False
                else:
                    actual_sprint = False
                # CALCULO PARA COLOCAR LA TAREA COMO ATRASADA O NO
                if tk.date_deadline:
                    if tk.date_deadline <= datetime.date(datetime.now() - timedelta(days=1)):
                        tk.delay = True
                    else:
                        tk.delay = False
                if tk.stage_id:
                    if tk.stage_id.name == 'Nuevo':
                        if not tk.delay:
                            tk.new_task = True
                        else:
                            tk.new_task = False
                    elif tk.stage_id.name == 'Revision Cliente':
                        if not tk.delay:
                            tk.client = True
                        else:
                            tk.client = False
                if actual_sprint:
                    vals_x = {
                        'No': no_tk_x,
                        'name': tk.name,
                        'user_id': "".join([x[0].upper() for x in str(tk.user_id.name).split(' ')]),
                        'task_stage': tk.stage_id.name,
                        'planned_hours': tk.planned_hours,
                        'effective_hours': tk.effective_hours,
                        # 'stage': tk.stage_id.name,
                        'delay': tk.delay,
                        'new': tk.new_task,
                        'client': tk.client,
                        'actual_sprint': actual_sprint,
                    }
                    if tk.stage_id.name == 'Nuevo':
                        len_x_n += 1
                    elif tk.stage_id.name == 'En Proceso':
                        len_x_p += 1
                    elif tk.stage_id.name == 'Revision Interna':
                        len_x_r += 1
                    elif tk.stage_id.name == 'Revision Cliente':
                        len_x_c += 1
                    elif tk.stage_id.name == 'Terminado':
                        len_x_d += 1

                    task_list_x.append(vals_x)
                    no_tk_x += 1

        data.update(
            {'task_d': task_list_d, 'total_task_d': len(task_list_d),
             'new_d': len_d_n,
             'on_process_d': len_d_p,
             'review_d': len_d_r,
             'client_d': len_d_c,
             'delivered_d': len_d_d,
             'task_i': task_list_i, 'total_task_i': len(task_list_i),
             'new_i': len_i_n,
             'on_process_i': len_i_p,
             'review_i': len_i_r,
             'client_i': len_i_c,
             'delivered_i': len_i_d,
             'task_c': task_list_c, 'total_task_c': len(task_list_c),
             'new_c': len_c_n,
             'on_process_c': len_c_p,
             'review_c': len_c_r,
             'client_c': len_c_c,
             'delivered_c': len_c_d,
             'task_t': task_list_t, 'total_task_t': len(task_list_t),
             'new_t': len_t_n,
             'on_process_t': len_t_p,
             'review_t': len_t_r,
             'client_t': len_t_c,
             'delivered_t': len_t_d,
             'task_x': task_list_x, 'total_task_x': len(task_list_x),
             'new_x': len_x_n,
             'on_process_x': len_x_p,
             'review_x': len_x_r,
             'client_x': len_x_c,
             'delivered_x': len_x_d,
             # 'task_x': task_list_x, 'total_task_x': len(task_list_x),
             })

        requirements_list = []
        requirements = self.env["project.requirement"].browse(self.read()[0].get('project_requirement_ids'))
        no = 1

        for req in requirements:
            if req.priority == 'mh':
                prioridad = 'Necesario'
            elif req.priority == 'nh':
                prioridad = 'Parcialmente Necesario'
            elif req.priority == 'wh':
                prioridad = 'Innecesario'
            else:
                prioridad = " "

            if req.solution_type == 'd':
                solucion = 'Desarrollo'
            elif req.solution_type == 'i':
                solucion = 'Implementación'
            else:
                solucion = " "

            if req.state == 'new':
                state = 'Nuevo'
            elif req.state == 'approved':
                state = 'Aprobado'
            elif req.state == 'backlog':
                state = 'Backlog'
            elif req.state == 'on_process':
                state = 'En proceso'
            elif req.state == 'done':
                state = 'Terminado'
            elif req.state == 'deploy':
                state = 'Deploy'
            elif req.state == 'delivered':
                state = 'Entregado'
            elif req.state == 'cancel':
                state = 'Cancelado'
            elif req.state == 'old':
                state = 'Version Antigua'
            else:
                state = ' '

            vals = {
                'No': no,
                'name': req.name,
                'state': state,
                'version': req.version,
                'solution_type': solucion,
                'request_Date': req.request_date,
                'requested_by': "".join([x[0].upper() for x in str(req.requested_by_id.name).split(' ')]),
                'approved_date': req.approved_date,
                'approved_by_id': "".join([x[0].upper() for x in str(req.approved_by_id.name).split(' ')]),
                'priority': "".join([x[0].upper() for x in str(prioridad).split(' ')]),
                'planned_hours': req.planned_hours,
                'effective_hours': req.effective_hours,
            }
            requirements_list.append(vals)
            no += 1

        data.update(
            {'total': len(requirements), 'entregados': len(requirements.filtered(lambda req: req.state == 'deliverd')),
             'proceso': len(requirements.filtered(lambda req: req.state == 'on_process')),
             'aprobado': len(requirements.filtered(lambda req: req.state == 'approved')),
             'terminados': len(requirements.filtered(lambda req: req.state == 'done')),
             'cancelados': len(requirements.filtered(lambda req: req.state == 'cancel')),
             'nuevos': len(requirements.filtered(lambda req: req.state == 'new')),
             'backlog': len(requirements.filtered(lambda req: req.state == 'backlog')),
             'antigua': len(requirements.filtered(lambda req: req.state == 'old')),
             'deploy': len(requirements.filtered(lambda req: req.state == 'deploy')),
             'requerimientos': requirements_list})

        return self.env.ref('project_inteligos.report_requirements').report_action(self, data=data)

    def details_project(self):
        t_task = 0

        self.ensure_one()
        task_total = self.env["project.task"].browse(self.read()[0].get('tasks'))
        self.requirement_count = len(self.read()[0].get('project_requirement_ids'))
        self.task_count = len(self.read()[0].get('tasks'))
        self.changes_count = self._compute_changes()
        self.sprint_count = self._compute_sprints()

        self.minute_count = self._compute_minute()

        self.total_task = len(task_total)
        self.total_backlog = len(task_total.filtered(lambda tsk: tsk.task_state == 'backlog'))
        self.total_delivered = len(task_total.filtered(lambda tsk: tsk.task_state == 'delivered'))
        self.total_delay = len(task_total.filtered(lambda tsk: tsk.task_state == 'delay'))
        if (len(task_total.filtered(lambda tsk: tsk.task_state == 'delay')) / len(task_total)) == 0:
            self.health = 100
        else:
            self.health = (len(task_total.filtered(lambda tsk: tsk.task_state == 'delay')) / len(task_total)) * 100

        # if self.total_delay == 0:
        #     self.health == 100
        # else:
        #     self.health = /self.total_delay
        # PENDIENTE

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.project',
            'res_id': self.id,
            'view_id': self.env.ref('project_inteligos.form_view_inherit').id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def development_tasks(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'Development Task',
            'view_mode': 'tree',
            'res_model': 'project.task',
            'domain': [('project_id', '=', self.id), ('scope', '=', 'd')],

        }

    def implementation_tasks(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Implementation Task',
            'view_mode': 'tree',
            'res_model': 'project.task',
            'domain': [('project_id', '=', self.id), ('scope', '=', 'i')],

        }

    def customer_tasks(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer Task',
            'view_mode': 'tree',
            'res_model': 'project.task',
            'domain': [('project_id', '=', self.id), ('scope', '=', 'c')],

        }

    def open_project_requirements(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'Requirement',
            'view_mode': 'tree',
            'res_model': 'project.requirement',
            'domain': [('project_id', '=', self.id)],

        }

    def open_project_task(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'Task',
            'view_mode': 'tree',
            'res_model': 'project.task',
            'domain': [('project_id', '=', self.id)],

        }

    def open_project_sprints(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'Sprint',
            'view_mode': 'tree',
            'res_model': 'project.sprint',
            'domain': [('project_id', '=', self.id)],
        }

    def open_project_changes(self):
        print(self.env.ref('project_inteligos.tree_view_changes').id)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.change',
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': self.env.ref('project_inteligos.tree_view_changes').id,
            'target': 'current',
            'name': 'change',
            'domain': [('project_id', '=', self.id)],
        }

    def open_project_minute(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'Minute',
            'view_mode': 'tree',
            'res_model': 'project.minute',
            'domain': [('project_id', '=', self.id)],

        }

    def _compute_changes(self):
        for ch in self:
            ch.changes_count = self.env["project.change"].search_count([('project_id', '=', ch.id)])
        return ch.changes_count

    def _compute_minute(self):
        for mn in self:
            mn.minute_count = self.env["project.minute"].search_count([('project_id', '=', mn.id)])

        return mn.minute_count

    def _compute_sprints(self):
        for sp in self:
            sp.sprint_count = self.env["project.sprint"].search_count([('project_id', '=', sp.id)])

        return sp.changes_count

    def generate_sprints(self):
        sprints_amount = len(self.read()[0].get('project_sprints_ids'))

        if sprints_amount < 1:

            start_date = self.initial_date
            end_date = self.delivery_date
            n = 0
            days = end_date - start_date
            total_days = days.days
            sprints = total_days / 14

            while n < sprints:

                if n == 0:
                    start_day_sprint = start_date
                else:
                    start_day_sprint = start_date + timedelta(days=((14 * n) + n))

                end_date_sprint = start_day_sprint + timedelta(days=14)

                difference = sprints - n

                if difference < 1 and difference != 0:
                    start_day_sprint = start_date + timedelta(days=((14 * n) + n))
                    vals = {
                        'name': 'SPRINT' + ' ' + self.read()[0].get('prefix') + ' ' + str(n + 1),
                        'project_id': self.read()[0].get('id'),
                        'date_start': start_day_sprint,
                        'date_end': self.delivery_date,
                        # 'sequence': self.read()[0].get('id'),
                    }
                    self.env['project.sprint'].create(vals)
                    n += 1

                else:

                    start_day_sprint = start_date + timedelta(days=((14 * n) + n))
                    vals = {
                        'name': 'SPRINT' + ' ' + self.read()[0].get('prefix') + ' ' + str(n + 1),
                        'project_id': self.read()[0].get('id'),
                        'date_start': start_day_sprint,
                        'date_end': end_date_sprint,
                        # 'sequence': self.read()[0].get('id'),
                    }
                    self.env['project.sprint'].create(vals)
                    n += 1

        else:
            raise ValidationError("Ya existen sprints creados para este proyecto")


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    default = fields.Boolean("Agregar por Default", default=False)


class ProjectTaskInherited(models.Model):
    _inherit = 'project.task'
    _description = 'Tareas Inteligos'

    meeting_ids = fields.One2many('calendar.event', 'task_id', 'Reuniones')
    # meeting_count = fields.Integer('Reuniones',compute='_get_meeting_count',store=True)
    approve_task_partner_id = fields.Many2one('res.partner', "Autorizado por")
    delivered_task_date = fields.Date('Fecha de entrega')
    minute_id = fields.Many2one('project.minute', 'Minuta')
    delay = fields.Boolean(string="RETRASADO O NO", default=False)
    new_task = fields.Boolean(string="Nueva y no retrasada", default=False)
    client = fields.Boolean(string="Revision Cliente y no retrasada", default=False)

    @api.model
    def create(self, vals):
        result = super(ProjectTaskInherited, self).create(vals)
        project = result.project_id
        if project:
            next_val = project.sequence_id.next_by_id()
            result.reference = (project.prefix or '') + '-' + str(next_val)
            return result
        else:
            return result

    task_state = fields.Selection([
        ('backlog', 'Backlog'),
        ('delivered', 'Delivered'),
        ('delay', 'Delay'),
        ('onprocess', 'On Process')
    ],
        string="Task State"
    )

    reference = fields.Char(
        readonly=True,
        required=True,
        copied=False,
        default="New",
        string="Secuencia de Tarea"
    )

    summary = fields.Text(
        required=True,
        copied=True,
        string='Resumen'
    )

    agenda_id = fields.Many2one(
        'calendar.agenda',
        index=True,
        store=True,
        help='Ingrese las agenda de la reunión.',
        string="Agenda"
    )
    event_id = fields.Many2one(
        'calendar.event',
        index=True,
        store=True,
        help='Reunión principal a la que pertenece la agenda padre de la tarea.',
        string="Evento"
    )

    scope = fields.Selection(
        [
            ('d', 'Desarrollo'),
            ('i', 'Implementación'),
            ('c', 'Clientes'),
            ('t', 'Tickets'),
        ],
        string="Ambito",
        required="True"
    )

    meeting_counter = fields.Integer(
        "# Reuniones",
        compute='_get_meeting_count',

    )

    requirement_ids = fields.Many2many(
        'project.requirement',
        string="Requerimiento"
    )

    sprint_id = fields.Many2one(
        'project.sprint',
        track_visibilty=True,
        string='Sprint',
        # domain="[('project_id','=',self.project_id)]",
    )

    change_request_id = fields.Many2one(
        'project.change_request_id',
        track_visibilty=True,
        string='Cambio'
    )

    def action_change_state(self):

        for req in self.requirement_ids:
            req.state = 'on_process'

    def name_get(self):
        result = []
        for record in self:
            display_name = f'[{(record.reference or "")}] {record.name}'
            result.append((record.id, display_name))
        return result

    def action_schedule_meeting(self):
        """ Open meeting's calendar view to schedule meeting on current opportunity.
            :return dict: dictionary value for created Meeting view
        """
        self.ensure_one()
        action = self.env.ref('calendar.action_calendar_event').read()[0]
        partner_ids = self.env.user.partner_id.ids
        if self.partner_id:
            partner_ids.append(self.partner_id.id)
        action['context'] = {
            'default_task_id': self.id,
            'default_project_id': self.project_id.id,
            'default_user_id': self.env.user,
        }
        return action

    def action_attachment_list(self):
        view = self.env.ref('project_inteligos.wizard_attachment_form')
        ctx = {
            'task_id': self.id
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project_inteligos.attachment_list_wiz',
            'view_id': view.id,
            'views': [(view.id, 'form')],
            'target': 'new',
            'context': ctx
        }

    def _get_meeting_count(self):
        meeting_data = self.env['calendar.event'].read_group([('task_id', 'in', self.ids)], ['task_id'])
        mapped_data = {m['task_id'][0]: m['task_id_count'] for m in meeting_data}
        for lead in self:
            lead.meeting_count = mapped_data.get(lead.id, 0)

    def on_change_requeriment(self):
        """
        Si cambia el requerimiento colocar de forma predeterminada:
            - cliente = requirement.partner_id
            - correo_cc = requirement.approver_id
        :return:
        """
        return True


class IrAttachmentInherited(models.Model):
    _inherit = 'ir.attachment'
    _description = 'Archivos Adjuntos'

    attachment_list_id = fields.Many2one(
        'project_inteligos.attachment_list_wiz',
        readonly=True,
        string="Lista de Archivos Adjuntos"
    )
