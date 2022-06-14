# -*- coding: utf-8 -*-
{
    'name': "project_inteligos",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Proyectos Ágiles S. A.",
    'website': "http://www.inteligos.gt",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','project','pad','pad_project','calendar','survey'],

    # always loaded
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/inherit_project_project_view.xml',
        'views/inherit_project_task_view.xml',
        'views/calendar_event_views.xml',
        'views/inherit_project_requirement_view.xml',
        'views/project_sprint_view.xml',
        'wizards/attachment_list.xml',
        'reports/report_tem.xml',
        'reports/report.xml',
        'reports/report_requirements.xml',
        'reports/report_requirements_tem.xml',
        'views/form_project_view.xml',
        'reports/email_template.xml',
        'views/project_changes_views.xml',
        'reports/comunication_template.xml',
        'views/minute_view.xml',
        'views/menu_item_view.xml',
        'reports/report_minute.xml',
        'reports/report_minute_tem.xml',
        'reports/email_minute_template.xml',
        'reports/report_complete.xml',
        'reports/report_complete_template.xml'

    ],

}