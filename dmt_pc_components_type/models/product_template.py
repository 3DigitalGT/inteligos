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

    processor_frequency = Selection([('2.4', '2.4GHz'),
                                     ('3.0', '3.0GHz'),
                                     ('3.2', '3.2GHz'),
                                     ('3.5', '3.5GHz'),
                                     ('4.2', '4.2GHz'),
                                     ], string='Velocidad del procesador')

    ram_type = Selection([('sdram', 'SDRAM'),
                          ('ddr_one', 'DDR1'),
                          ('ddr_two', 'DDR2'),
                          ('ddr_three', 'DDR3'),
                          ('ddr_four', 'DDR4'),
                          ('ddr_five', 'DDR5')
                          ], string='Tipo de RAM')

    ram_frequency = Selection([('400', '400 MHz'),
                               ('1.066', '1.066 MHz'),
                               ('2.4', '2.4 MHz'),
                               ('3', '3 MHz'),
                               ('4', '4 MHz'),
                               ], string='Tipo de RAM')

    monitor_size = Selection([('17pulg', '17'),
                              ('19pulg', '19'),
                              ('20pulg', '20'),
                              ('21pulg', '21'),
                              ('22pulg', '22'),
                              ('23pulg', '23'),
                              ('24pulg', '24'),
                              ('25pulg', '25'),
                              ('26pulg', '26'),
                              ('27pulg', '27'),
                              ], string='Tamaño de monitor')

    monitor_type = Selection([('square', 'C'),
                              ('wide', 'W'),
                              ], string='Tipo de Monitor')

    mouse = Selection([('new', 'N'),
                       ('reusable', 'R'),
                       ], string='Mouse')

    keyboard = Selection([('new', 'N'),
                          ('reusable', 'R'),
                          ], string='Teclado')

    video_cable = Selection([('new', 'N'),
                             ('reusable', 'R'),
                             ], string='Cable de Video')

    power_cable = Selection([('new', 'N'),
                             ('reusable', 'R'),
                             ], string='Cable de Poder')

    speakers = Selection([('new', 'N'),
                          ], string='Bocina')

    printer = Selection([('new', 'N'),
                         ], string='Impresora')

    ups = Selection([('new', 'N'),
                     ], string='UPS')
