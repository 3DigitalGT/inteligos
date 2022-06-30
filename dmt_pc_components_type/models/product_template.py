# -*- coding: utf-8 -*-
from odoo.models import Model
from odoo.fields import Selection, Boolean


class ProductTemplateInherit(Model):
    _name = 'product.template'
    _description = 'Herencia del product template para agregar generacion de procesador'
    _inherit = 'product.template'

    is_computer = Boolean(string='Es Computadora', default=False)

    processor_type = Selection([('celeron', 'Celeron'),
                                ('core_2_duo', 'C2D'),
                                ('core_i3', 'CI3'),
                                ('core_i5', 'CI5'),
                                ('core_i7', 'CI7'),
                                ('core_i9', 'CI9'),
                                ('amd_ryzen_3', 'AMD/R3'),
                                ('amd_ryzen_5', 'AMD/R5'),
                                ('amd_ryzen_7', 'AMD/R7'),
                                ], string='Procesador')

    processor_gen = Selection([('first_gen', '1G'),
                               ('second_gen', '2G'),
                               ('third_gen', '3G'),
                               ('fourth_gen', '4G'),
                               ('fifth_gen', '5G'),
                               ('sixth_gen', '6G'),
                               ('seventh_gen', '7G'),
                               ('eighth_gen', '8G'),
                               ('ninth_gen', '9G'),
                               ('tenth_gen', '10G'),
                               ('eleventh_gen', '11G'),
                               ], string='Generacion de procesador')

    ram_type = Selection([('sdram', 'SDRAM'),
                          ('ddr_one', 'DDR1'),
                          ('ddr_two', 'DDR2'),
                          ('ddr_three', 'DDR3'),
                          ('ddr_four', 'DDR4'),
                          ('ddr_five', 'DDR5')
                          ], string='Tipo de RAM')

    ram_capacity = Selection([('2gb', '2GB'),
                              ('4gb', '4GB'),
                              ('8gb', '8GB'),
                              ('16gb', '16GB'),
                              ('32gb', '32GB'),
                              ('64gb', '64GB'),
                              ('128gb', '128GB'),
                              ], string='Capacidad de RAM')

