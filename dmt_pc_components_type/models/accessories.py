# -*- coding: utf-8 -*-
from odoo.models import Model
from odoo.fields import Selection, Boolean, Char
from odoo.api import model


class ProductTemplateInherit(Model):
    _name = 'pc.accessories'
    _description = 'Modelo para los accesorios de las pc'

    name = Char(string='Nombre del accesorio')


