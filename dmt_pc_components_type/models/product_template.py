# -*- coding: utf-8 -*-
from odoo.models import Model
from odoo.fields import Selection, Boolean, Char
from odoo.api import model


class ProductTemplateInherit(Model):
    _name = 'product.template'
    _description = 'Herencia del product template para agregar generacion de procesador'
    _inherit = 'product.template'

    is_computer = Boolean(string='Es Computadora', default=False)

    processor_type = Selection([('celeron', 'Celeron'),
                                ('C2D', 'C2D'),
                                ('CI3', 'CI3'),
                                ('CI5', 'CI5'),
                                ('CI7', 'CI7'),
                                ('CI9', 'CI9'),
                                ('AMD/R3', 'AMD/R3'),
                                ('AMD/R5', 'AMD/R5'),
                                ('AMD/R7', 'AMD/R7'),
                                ], string='Procesador')

    processor_gen = Selection([('1G', '1G'),
                               ('2G', '2G'),
                               ('3G', '3G'),
                               ('4G', '4G'),
                               ('5G', '5G'),
                               ('6G', '6G'),
                               ('7G', '7G'),
                               ('8G', '8G'),
                               ('9G', '9G'),
                               ('10G', '10G'),
                               ('11G', '11G'),
                               ], string='Generacion de procesador')

    processor_frequency = Selection([('LR', 'LR'),
                                     ('MR', 'MR'),
                                     ('HR', 'HR'),

                                     ], string='Velocidad del procesador')

    ram_type = Selection([('SDRAM', 'SDRAM'),
                          ('DDR1', 'DDR1'),
                          ('DDR2', 'DDR2'),
                          ('DDR3', 'DDR3'),
                          ('DDR4', 'DDR4'),
                          ('DDR5', 'DDR5')
                          ], string='Tipo de RAM')

    # ram_frequency = Selection([('400', '400 MHz'),
    #                            ('1.066', '1.066 MHz'),
    #                            ('2.4', '2.4 MHz'),
    #                            ('3', '3 MHz'),
    #                            ('4', '4 MHz'),
    #                            ], string='Frecuencia de RAM')

    monitor_size = Selection([('17', '17'),
                              ('19', '19'),
                              ('20', '20'),
                              ('21', '21'),
                              ('22', '22'),
                              ('23', '23'),
                              ('24', '24'),
                              ('25', '25'),
                              ('26', '26'),
                              ('27', '27'),
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

    computer_brand = Selection([('DE', 'DE'),
                                ('HP', 'HP'),
                                ('MM', 'MM'),
                                ], string='Marca Computador')

    computer_size = Selection([('SFF', 'SFF'),
                               ('MD', 'MD'),
                               ('D', 'D'),
                               ('T', 'T'),
                               ], string='Tamaño computador')
    internal_reference = Char(string='Referencia interna')

    @model
    def create(self, vals):
        """Sobrescritura del método genérico de Odoo para la creación de registros product.tempalte.
            para asignar una secuencia[Correlativo] a los productos creados.
        """
        #ToDo: Marca/Procesador/Velocidad/Tamaño/Tipoderam/secuencianumerica
        code = len(self.env['product.template'].search([]))
        vals['internal_reference'] = str(vals['computer_brand']) + str(vals['processor_type']) + str(vals['processor_frequency']) + str(vals['computer_size']) + str(vals['ram_type']) + str(code)
        result = super(ProductTemplateInherit, self).create(vals)
        return result