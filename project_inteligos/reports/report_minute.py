# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ReportMinuteReportMinute(models.AbstractModel):
    _name = 'report.minute.report_minute'
    _description = 'Reporte Minuta'

    # Creado por Androide
    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': docids,
            'doc_model': 'project.minute',
            'docs': self
        }
