# -*- coding: utf-8 -*-

from odoo.models import Model


class InheritResPartnerLogistic(Model):
    """Herencia del objeto res.partner para logística"""
    _inherit = 'res.partner'
    _name = 'res.partner'

    def name_get(self):
        """Sobreescritura del método para agregar valor de referencia al nombre desplegado."""
        res = [(contact.id, "%s %s" % (contact.name, '- ' + contact.ref if contact.ref else '')) for contact in self]
        return res
