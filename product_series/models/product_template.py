# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import Boolean


class ProductTemplateInherited(Model):
    _inherit = 'product.template'
    _name = 'product.template'

    has_series = Boolean(
        default=False,
        string="Utiliza Series"
    )
