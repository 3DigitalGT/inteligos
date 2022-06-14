# -*- coding: utf-8 -*-
# TODO: MANTENERLO MIENTRAS SE HACEN LAS EVALUACIONES DE USO
# import sys
# sys.path.append('C:/Users/UsuarioDocuments/Odoo15/Custom_addons_Odoo15/main_account/addons_gen')
#
# for line in sys.path:
#     print(line)

from datetime import datetime
from pytz import timezone, UTC
from logging import getLogger
from odoo.models import Model
from odoo.api import depends
from odoo.fields import (One2many, Monetary, Many2one, Date, Char)
from odoo.exceptions import ValidationError
from ...addons_gen.l10n_gt_inteligos_fel.providers.infile import InfileFel, emisor, receptor
from ...addons_gen.l10n_gt_inteligos_fel.providers.digifact import DigifactFel, DigifactEmisor, DigifactReceptor
from ...addons_gen.l10n_gt_inteligos_fel.providers.contap import ContapFel, ContapEmisor, ContapReceptor
from ...addons_gen.l10n_gt_inteligos_fel.providers.ecofacturas import EcofacturaFel, EcofacturaEmisor, EcofacturaReceptor
from ...addons_gen.l10n_gt_inteligos_fel.providers.megaPrint import MegaPrintFel, MegaPrintEmisor, MegaPrintReceptor

_logger = getLogger(__name__)


class InheritSaleOrderLogistic(Model):
    """Herencia del objeto account.order para logística"""
    _inherit = 'account.move'
    _name = 'account.move'

    @depends('amount_total', 'logistic_employed')
    def _compute_total_logistic(self):
        for record in self:
            record.total_logistic = record.logistic_employed + record.amount_total

    @depends('total_logistic')
    def _compute_logistic_amount_in_words(self):
        for record in self:
            amount = record.convert_amount_in_words(record.total_logistic, 'es',
                                                    record.currency_id, record.partner_id.lang)
            record.logistic_amount_in_words = amount.capitalize()

    logistic_employed_iva = Monetary(
        string="Cuenta Ajena IVA",
        help="Campo donde se agrega el monto de las cuentas ajenas.",
        copy=True,
        tracking=3,
        default=0,
    )
    logistic_employed_dai = Monetary(
        string="Cuenta Ajena DAI",
        help="Campo donde se agrega el monto de las cuentas ajenas.",
        copy=True,
        tracking=3,
        default=0,
    )

    logistic_employed_others = Monetary(
        string="Cuenta Ajena Otros",
        help="Campo donde se agrega el monto de las cuentas ajenas.",
        copy=True,
        tracking=3,
        default=0,
    )
    logistic_employed = Monetary(
        string="Cuenta Ajena",
        help="Campo donde se agrega el monto total de las cuentas ajenas.",
        copy=True,
        tracking=3,
        default=0,
    )
    receipt_id = Many2one(
        comodel_name="account.move",
        string="Recibo",
        tracking=3
    )
    total_logistic = Monetary(
        string="Total de logística",
        help="Campo donde se agrega el monto total de las cuentas ajenas + monto total del documento.",
        compute="_compute_total_logistic",
        copy=True,
        store=True,
        default=0,
    )
    logistic_amount_in_words = Char(
        compute='_compute_logistic_amount_in_words',
        string='Monto en letras logística'
    )

    def set_data_from_packages(self):
        """
        Método para colocar en el pedido los valores necesarios de logística que son obtenidos de los paquetes enlazados
        :return: None
        """

        for line in self.order_line:
            if line.product_id == self.env.company.logistic_weight:
                line.product_uom_qty = float(sum([package.weight for package in self.package_ids if package.weight]))
            elif line.product_id == self.env.company.logistic_clearance:
                line.product_uom_qty = sum([package.qty for package in self.package_ids if package.qty])
        self.logistic_employed_iva = sum([package.iva for package in self.package_ids if package.iva])
        self.logistic_employed_dai = sum([package.dai for package in self.package_ids if package.dai])
        self.logistic_employed_others = sum(
            [package.other_costs for package in self.package_ids if package.other_costs])
        self.write({'logistic_employed': sum([package.iva for package in self.package_ids if package.iva]) +
                                         sum([package.dai for package in self.package_ids if package.dai]) +
                                         sum([package.custom_expenses for package in self.package_ids
                                              if package.custom_expenses])
                    })

    def dte_fel(self):
        for move in self:
            _logger.info("ESTAS DENTRO DE FEL!")
            instance_company = move.company_id
            instance_partner = move.partner_id

            if instance_company.fel_provider == 'IN':
                provider = InfileFel
                emisor_fel = emisor
                receptor_fel = receptor
            elif instance_company.fel_provider == 'DI':
                provider = DigifactFel
                emisor_fel = DigifactEmisor
                receptor_fel = DigifactReceptor
            elif instance_company.fel_provider == 'CO':
                provider = ContapFel
                emisor_fel = ContapEmisor
                receptor_fel = ContapReceptor
            elif instance_company.fel_provider == "MP":
                provider = MegaPrintFel
                emisor_fel = MegaPrintEmisor
                receptor_fel = MegaPrintReceptor
            elif instance_company.fel_provider == "ECO":
                provider = EcofacturaFel
                emisor_fel = EcofacturaEmisor
                receptor_fel = EcofacturaReceptor
            else:
                raise ValidationError('No ha seleccionado a ningún proveedor para la emisión FEL. '
                                      'Debe ser configurado en la compañía emisora. '
                                      'Por favor hágalo o comuníquese con administración.')

            # Metodos principales de librerias FEL según cada proveedor
            certify_fel_dte = provider.fel_dte()
            emisor_fel = emisor_fel.emisor()
            receptor_fel = receptor_fel.receptor()

            # Variables para emisor y receptor
            factor = 'compañía'
            establishment_code = instance_company.establishment_number
            street = False
            zip_code = False
            city = False
            state = False
            country = False
            name = False
            receptor_name = False
            receptor_street = False
            receptor_city = False
            receptor_state = False
            receptor_country = False
            receptor_zip = False
            receptor_email = False
            if move.pos_inv:
                po_order = self.env['pos.order'].search([('account_move', '=', move.id)], limit=1)
                if po_order:
                    instance_config_po = po_order.session_id.config_id
                    street = instance_config_po.street
                    zip_code = instance_config_po.zip_code
                    city = instance_config_po.county_name
                    state = instance_config_po.state_id.name
                    country = instance_config_po.country_id.code
                    name = instance_config_po.name
                    establishment_code = str(instance_config_po.establishment_number)
                    factor = 'punto de venta'
                    receptor_name = self.validate_nit(instance_partner.vat) \
                        if instance_partner.vat != 'CF' else instance_partner.legal_name or instance_partner.name
                    instance_partner.legal_name = receptor_name
                    receptor_street = instance_partner.street or 'Guatemala'
                    # receptor_city = instance_partner.county_id.name if instance_partner.county_id else ' ' TODO: Mejora para el POS
                    receptor_city = instance_partner.city if instance_partner.city else ' '
                    receptor_state = instance_partner.state_id.name or ' '
                    receptor_country = instance_partner.country_id.code or 'GT'
                    receptor_zip = instance_partner.zip or '00000'
                    receptor_email = instance_partner.email or ' '
            else:
                street = instance_company.street
                zip_code = instance_company.zip
                city = instance_company.county_id.name
                state = instance_company.state_id.name
                country = instance_company.country_id.code
                name = instance_company.name
                receptor_name = instance_partner.legal_name.strip()
                receptor_email = instance_partner.email
                if not instance_company.fel_provider == "MP":
                    receptor_email = instance_partner.email or ' '

                """ Mejora para agregar lógica de configuración para el ingreso de direcciones FEL.
-                    Obligatoria o no, en dependencia de la configuración de Contabilidad."""
                if not instance_company.mandatory_address_fel:
                    receptor_street = instance_partner.street or 'Guatemala'
                    receptor_city = instance_partner.county_id.name if instance_partner.county_id else 'Guatemala'
                    receptor_state = instance_partner.state_id.name or 'Guatemala'
                    receptor_country = instance_partner.country_id.code or 'GT'
                    receptor_zip = instance_partner.zip or '00000'
                else:
                    receptor_street = instance_partner.street
                    receptor_city = instance_partner.county_id.name if instance_partner.county_id else False
                    receptor_state = instance_partner.state_id.name
                    receptor_country = instance_partner.country_id.code
                    receptor_zip = instance_partner.zip

            # Datos emisor
            direction_values_emisor = {
                'Calle': street, 'Código Postal': zip_code,
                'Ciudad': city, 'Departamento': state,
                'País': country
            }
            vde = self.examine_values(direction_values_emisor, factor)
            if instance_company.fel_provider != "ECO":
                emisor_fel.set_direccion(vde['Calle'], vde['Código Postal'], vde['Ciudad'], vde['Departamento'],
                                         vde['País'])
            data_values_emisor = {
                'Fel Iva': instance_company.fel_iva, 'Correo': instance_company.email,
                'Nit': instance_company.vat, 'Nombre Comercial': name,
                'Razón Social': instance_company.legal_name
            }
            dve = self.examine_values(data_values_emisor, factor)
            emisor_fel.set_datos_emisor(dve['Fel Iva'], establishment_code, dve['Correo'],
                                        dve['Nit'], dve['Nombre Comercial'], dve['Razón Social'])
            certify_fel_dte.set_datos_emisor(emisor_fel)

            #  Datos Receptor
            direction_values_receptor = {
                'Calle': receptor_street, 'Código Postal': receptor_zip,
                'Ciudad': receptor_city, 'Departamento': receptor_state,
                'País': receptor_country
            }
            vdr = self.examine_values(direction_values_receptor, 'cliente')
            receptor_fel.set_direccion(vdr['Calle'], vdr['Código Postal'], vdr['Ciudad'], vdr['Departamento'],
                                       vdr['País'])

            """ Mejora para envío de datos si el cliente es un consumidor final."""
            if instance_partner.its_final_consumer:
                receptor_name = 'Consumidor Final'

            data_values_receptor = {
                'Correo': receptor_email, 'Nit': instance_partner.vat,
                'Razón Social': receptor_name
            }
            dvr = self.examine_values(data_values_receptor, 'cliente')
            receptor_fel.set_datos_receptor(dvr['Correo'], dvr['Nit'], dvr['Razón Social'])

            certify_fel_dte.set_datos_receptor(receptor_fel)

            gt = timezone('America/Guatemala')
            utc_dt = datetime.now(tz=UTC).astimezone(gt)
            custom_dt = datetime.combine(move.invoice_date, datetime.min.time()) \
                if move.invoice_date and move.invoice_date < Date.today() else False
            dt = utc_dt if not custom_dt else custom_dt

            dtime_emission = False
            if instance_company.fel_provider in ['IN', 'MP']:
                dtime_emission = dt.strftime("%Y-%m-%dT%H:%M:%S") + '-06:00'
            elif instance_company.fel_provider in ['DI', 'CO']:
                dtime_emission = dt.strftime("%Y-%m-%dT%H:%M:%S")
            elif instance_company.fel_provider == 'ECO':
                dtime_emission = dt.strftime("%Y-%m-%d")

            if move.journal_id:
                if move.invoice_doc_type == move._get_sequence().l10n_latam_document_type_id:
                    dte_type = move._get_sequence().l10n_latam_document_type_id.doc_code_prefix
                else:
                    raise ValidationError(
                        'La secuencia del diario seleccionado no concuerda con el tipo de documento a emitir.'
                    )
            else:
                raise ValidationError('No tienes un diario seleccionado.')
            certify_fel_dte.set_datos_generales(move.currency_id.name, dtime_emission, dte_type.strip())

            # # identificador unico del dte del cliente
            identifier = move.name
            if not move.key_identifier:
                identifier = self.set_key_identifier()
                move.key_identifier = identifier
            elif move.key_identifier:
                identifier = move.key_identifier
            certify_fel_dte.set_clave_unica(identifier)

            if move.state == 'contingency' and instance_company.fel_provider != 'ECO':  # USO PARA CONTINGENCIAS
                if dte_type.strip() == 'NCRE':
                    access_number = move.fel_num_acceso_ncre
                elif dte_type.strip() == 'NDEB':
                    access_number = move.fel_num_acceso_ndeb
                else:
                    access_number = move.fel_num_acceso
                certify_fel_dte.set_acceso(access_number)

            export = ''
            exempt = False

            def set_phrases(phrase, type_phrase):
                # Exentos
                if str(phrase) == '1' and str(type_phrase) == '4':
                    # agregar las frases exportacion
                    certify_fel_dte.frase_fel.set_frase(str(phrase), str(type_phrase))
                    export = "SI"
                    certify_fel_dte.set_exportacion(export)
                    return False, export
                elif str(x.phrase) in ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12') and str(
                        x.type) == '4':
                    certify_fel_dte.frase_fel.set_frase(str(phrase), str(type_phrase))
                    return True, ''
                elif str(x.phrase) and str(x.type):
                    certify_fel_dte.frase_fel.set_frase(str(phrase), str(type_phrase))
                    return False, ''

            # agregar las frases
            phrases = dict()
            if dte_type.strip() in ['FACT', 'FCAM']:
                # indicador de las frases exportacion
                if instance_partner.property_account_position_id:
                    for x in instance_partner.property_account_position_id.fel_phrases_ids:
                        if x.phrase not in phrases.keys() or phrases.get(x.phrase, False) != x.type:
                            phrases.update({x.phrase: x.type})
                            exempt, export = set_phrases(x.phrase, x.type)
                elif instance_partner.fel_phrases_ids:
                    for t in instance_partner.fel_phrases_ids:
                        if t.phrase not in phrases.keys() or phrases.get(t.phrase, False) != t.type:
                            phrases.update({t.phrase: t.type})
                            exempt, export = set_phrases(t.phrase, t.type)
                if instance_company.fel_phrases_ids:
                    for p in instance_company.fel_phrases_ids:
                        if p.phrase not in phrases.keys() or phrases.get(p.phrase, False) != p.type:
                            phrases.update({p.phrase: p.type})
                            certify_fel_dte.frase_fel.set_frase(str(p.phrase), str(p.type))

            tax_total = 0
            t = {}
            taxes = []
            for idx, line in enumerate(move.invoice_line_ids):
                item = provider.item()
                item.set_numero_linea(idx + 1)

                if line.product_id.type == 'service':
                    goods_service = 'S'
                    item.set_bien_o_servicio(goods_service)
                elif line.product_id.type == 'consu' or line.product_id.type == 'product':
                    goods_service = 'B'
                    item.set_bien_o_servicio(goods_service)
                item.set_cantidad(line.quantity)
                item.set_unidad_medida(line.product_id.uom_id.name)
                description_sanitized = self.examine_values(
                    {'description': line.display_name or line.name}, 'líneas de factura')
                description = description_sanitized.get('description')
                item.set_descripcion(description)
                item.set_precio_unitario(self.truncate(line.price_unit, 10))
                # Descuentos
                desc = (line.price_unit * line.quantity * line.discount) / 100
                price = line.line_total + desc
                item.set_precio(self.truncate(price, 10))  # a este no aplicar el descuento
                item.set_descuento(self.truncate(desc, 10))
                """Mejora para envio de tipo de impuesto TIMBRE DE PRENSA"""
                """RECORDATORIO, CAMBIOS EN TD GENERICO METODO set_total_amount ARCHIVO account_move.py"""
                amount_tax = line.tax_ids.filtered(lambda tax: tax.tax_group_id.name == 'TIMBRE DE PRENSA').amount
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxable_amount = price * line.quantity / 1.12
                sum_tax = (amount_tax * taxable_amount) / 100
                item.set_total(self.truncate(line.line_total + sum_tax or 0.0, 10))

                # no aplica para Notas de Abono ni para Recibos, ni recibo por donación
                if dte_type.strip() not in ['NABN', 'RECI', 'RDON']:
                    for tax in line.tax_ids:
                        tax_item = provider.impuesto()

                        if tax.tax_group_id:
                            tax_short_name = tax.tax_group_id.name
                            if tax_short_name == 'IVA':
                                if instance_company.fel_iva == 'GEN':
                                    if export == 'SI':
                                        t = move.tax(2, self.truncate(line.line_total, 10), 0)
                                    else:
                                        """Exentos"""
                                        if exempt:  # Exentos
                                            t = move.tax(2, self.truncate(line.line_total, 10), 0)
                                        else:
                                            taxable_amount = self.truncate(
                                                abs(line.price_unit * line.quantity - desc) / (
                                                            1 + (tax.amount / 100)),
                                                10)
                                            t = move.tax(1, taxable_amount,
                                                         self.truncate((tax.amount * taxable_amount) / 100, 10))
                                elif instance_company.fel_iva == 'PEQ' or instance_company.fel_iva == 'EXE':
                                    t = move.tax(2, self.truncate(line.line_total, 10), 0)
                            elif tax_short_name == 'RETENCIONES':
                                continue
                            elif tax_short_name == 'IDP':
                                continue
                            elif tax_short_name == 'TIMBRE DE PRENSA':
                                if instance_company.fel_iva == 'GEN':
                                    taxable_amount = abs(line.price_unit * line.quantity - desc) / 1.12
                                    t = move.tax(1, self.truncate(taxable_amount, 10),
                                                 self.truncate((tax.amount * taxable_amount) / 100, 10))
                                elif instance_company.fel_iva == 'PEQ' or instance_company.fel_iva == 'EXE':
                                    t = move.tax(2, self.truncate(line.line_total, 10), 0)
                            else:
                                raise ValidationError('El impuesto en la(s) línea(s) tiene grupo'
                                                      ' de impuestos no permitido.')
                            tax_total += t['tax_amount']
                            tax_item.set_monto_gravable(t['taxable_amount'])
                            tax_item.set_monto_impuesto(t['tax_amount'])
                            tax_item.set_codigo_unidad_gravable(t['taxable_unit_code'])
                            tax_item.set_nombre_corto(tax_short_name)
                            item.set_impuesto(tax_item)

                            """Mejora para envio de más de un tipo de impuesto"""
                            if tax_short_name not in [tax['tax'] for tax in taxes]:
                                taxes.append({'tax': tax_short_name, 'total_tax': t['tax_amount']})
                            else:
                                for tax in taxes:
                                    if tax_short_name == tax['tax']:
                                        tax['total_tax'] += t['tax_amount']
                        else:
                            raise ValidationError('El impuesto en la(s) línea(s) no tiene grupo de impuestos.')
                # no aplica para Notas de Abono ni para Recibos, ni recibo por donación
                certify_fel_dte.agregar_item(item)

            if instance_company.fel_provider != "ECO":
                # Totales
                total_fel = provider.totales()
                total_fel.set_gran_total(self.truncate(move.amount, 10))
                # no aplica para Notas de Abono ni para Recibos, ni recibo por donación
                if dte_type.strip() not in ['NABN', 'RECI', 'RDON']:
                    for tax in taxes:
                        taxes_total = provider.total_impuesto()
                        taxes_total.set_nombre_corto(tax['tax'])
                        taxes_total.set_total_monto_impuesto(self.truncate(tax['total_tax'], 10))
                        total_fel.set_total_impuestos(taxes_total)
                    # no aplica para Notas de Abono ni para Recibos, ni recibo por donación
                certify_fel_dte.agregar_totales(total_fel)

            if instance_company.fel_provider == 'IN':
                if instance_company.adendas_ids:
                    for adenda in instance_company.adendas_ids:
                        """Mejora para permitir que las adendas sean enviadas segun tipo de documento o sin tipo definido.
                            Si no se ha definido tipo, las adendas serán para cualquier tipo de doc,
                            si se ha definido tipo de documento, se evaluara que sea el mismo tipo de la emision.
                            caso contrario, no se enviaran las adendas."""
                        if not adenda.doc_type_id:
                            access = True
                        elif adenda.doc_type_id.doc_code_prefix.strip() == dte_type.strip():
                            access = True
                        else:
                            access = False
                        if access:
                            # # agregar adendas al gusto
                            fel_adenda = InfileFel.adenda()

                            fel_adenda.nombre = adenda.name
                            if adenda.model_id != 'account.move':
                                if adenda.model_id == 'res.partner':
                                    fel_adenda.valor = str(move.partner_id[adenda.field_id.name])
                                elif adenda.model_id == 'res.users':
                                    fel_adenda.valor = str(move.user_id[adenda.field_id.name])
                                elif adenda.model_id == 'res.company':
                                    fel_adenda.valor = str(move.company_id[adenda.field_id.name])
                                elif adenda.model_id == 'account.payment.term':
                                    fel_adenda.valor = str(move.invoice_payment_term_id[adenda.field_id.name])
                                elif adenda.model_id == 'sale.order':
                                    for line in move.invoice_line_ids:
                                        order = line.sale_line_ids.mapped('order_id')
                                        if order:
                                            if adenda.field_id.name == 'partner_id':
                                                value = str(order.partner_id.name) \
                                                    if order.partner_id.company_type == 'person' else ''
                                                fel_adenda.valor = value
                                            else:
                                                fel_adenda.valor = str(order[adenda.field_id.name])
                                        else:
                                            """Quitar el warning fue necesario debido a que 
                                                no alertaba de nada, nunca aparecia esto, 
                                                y no permitia la emision del documento con FEL, solo en odoo.
                                                A cambio coloqué fel_adenda.valor = ''"""
                                            fel_adenda.valor = ''
                                elif adenda.model_id == 'product.template':
                                    product_adendas = ''
                                    for idx, line in enumerate(move.invoice_line_ids):
                                        product_adendas += str(idx + 1) + " @ " \
                                                           + str(line.product_id[adenda.field_id.name]) + " | "
                                    fel_adenda.valor = product_adendas
                            else:
                                if adenda.field_id.ttype == 'many2one':
                                    fel_adenda.valor = str(move[adenda.field_id.name].name)
                                elif adenda.field_id.name == 'display_name':
                                    sequence = move._get_sequence()
                                    number = '%%0%sd' % sequence.padding % \
                                             sequence._get_current_sequence().number_next_actual
                                    name = '%s%s' % (sequence.prefix or '', number)
                                    fel_adenda.valor = name
                                else:
                                    fel_adenda.valor = str(move[adenda.field_id.name])
                            certify_fel_dte.agregar_adenda(fel_adenda)
            elif instance_company.fel_provider == 'DI':
                # # agregar adendas al gusto
                fel_adenda = DigifactFel.adenda()
                fel_adenda.internal_reference = identifier
                fel_adenda.reference_date = dtime_emission
                fel_adenda.validate_internal_reference = move.validate_internal_reference
                certify_fel_dte.agregar_adenda(fel_adenda)
            elif instance_company.fel_provider == 'ECO':
                # # agregar adendas al gusto
                for idx, adenda in enumerate(instance_company.adendas_ids):
                    if not adenda.doc_type_id:
                        access = True
                    elif adenda.doc_type_id.doc_code_prefix.strip() == dte_type.strip():
                        access = True
                    else:
                        access = False
                    if access:
                        fel_adenda = EcofacturaFel.adenda()
                        concatenate_name_value = '0' if 0 < idx + 1 < 10 else ''
                        fel_adenda.name = 'TrnCampAd' + concatenate_name_value + str(idx + 1)
                        if adenda.model_id != 'account.move':
                            if adenda.model_id == 'res.partner':
                                fel_adenda.value = str(move.partner_id[adenda.field_id.name])
                            elif adenda.model_id == 'res.users':
                                fel_adenda.value = str(move.user_id[adenda.field_id.name])
                            elif adenda.model_id == 'res.company':
                                fel_adenda.value = str(move.company_id[adenda.field_id.name])
                            elif adenda.model_id == 'account.payment.term':
                                fel_adenda.value = str(move.invoice_payment_term_id[adenda.field_id.name])
                            elif adenda.model_id == 'sale.order':
                                for line in move.invoice_line_ids:
                                    order = line.sale_line_ids.mapped('order_id')
                                    if order:
                                        if adenda.field_id.name == 'partner_id':
                                            value = str(order.partner_id.name) \
                                                if order.partner_id.company_type == 'person' else ''
                                            fel_adenda.value = value
                                        else:
                                            fel_adenda.value = str(order[adenda.field_id.name])
                                    else:
                                        fel_adenda.value = ''
                            elif adenda.model_id == 'product.template':
                                product_adendas = ''
                                for idx, line in enumerate(move.invoice_line_ids):
                                    product_adendas += str(idx + 1) + " @ " \
                                                       + str(line.product_id[adenda.field_id.name]) + " | "
                                fel_adenda.value = product_adendas
                        else:
                            if adenda.field_id.ttype == 'many2one':
                                fel_adenda.value = str(move[adenda.field_id.name].name)
                            elif adenda.field_id.name == 'display_name':
                                sequence = move._get_sequence()
                                number = '%%0%sd' % sequence.padding % \
                                         sequence._get_current_sequence().number_next_actual
                                name = '%s%s' % (sequence.prefix or '', number)
                                fel_adenda.value = name
                            else:
                                fel_adenda.valor = str(move[adenda.field_id.name])
                        certify_fel_dte.agregar_adenda(fel_adenda)

            if dte_type == 'NCRE':
                """Mejora para cambiar el envío de posibles caracteres especiales en el campo motivo de ajuste
                       Mejora: ascii(move.reason_note) if isinstance(move.reason_note, str) else ascii('Anulación')
                """
                credit_notes_complement = provider.complemento_notas()
                data_notes = move.data_notes(dte_type.strip())
                reason_sanitized = self.examine_values({'reason': move.reason_note
                if isinstance(move.reason_note, str) else 'Anulación'}, 'Nota de crédito')
                reason = reason_sanitized.get('reason')
                credit_notes_complement.agregar("ANTIGUO" if move.ancient_regime else "",
                                                reason, data_notes['fel_date'],
                                                data_notes['series'], data_notes['uuid'], data_notes['doc_dte'])
                certify_fel_dte.agregar_complemento(credit_notes_complement)
            elif dte_type.strip() == 'FCAM':
                exchange_complement = provider.complemento_cambiaria()
                expiration_date = move.invoice_date_due
                exchange_complement.agregar(1, expiration_date, self.truncate(move.amount, 10))
                certify_fel_dte.agregar_complemento(exchange_complement)
            elif dte_type == 'FESP':
                especial_type = "2" if instance_company.fel_provider == 'ECO' else "CUI"
                certify_fel_dte.set_tipo_especial(
                    especial_type)  # instance_partner.l10n_latam_identification_type_id.name
                if instance_company.fel_provider != 'ECO':
                    fesp_complement = provider.complemento_especial()
                    """Mejora para cambiar porcentaje para calculo de ISR retenido, 
                        del 7 al 5%. Segun nueva instruccion SAT
                        Nueva reforma hecha por SAT."""
                    isr_retencion = self.truncate(t['taxable_amount'] * (5 / 100), 10)
                    """----------FIN-----------"""
                    free_total = self.truncate(abs(t['taxable_amount'] - isr_retencion), 10)
                    fesp_complement.agregar(isr_retencion, tax_total, free_total)
                    certify_fel_dte.agregar_complemento(fesp_complement)
            elif dte_type.strip() == 'NDEB':
                debit_notes_complement = provider.complemento_notas()
                data_notes = move.data_notes(dte_type.strip())
                reason_sanitized = self.examine_values(
                    {'reason': move.reason_note
                    if isinstance(move.reason_note, str) else 'Anulación'}, 'Nota de débito')
                reason = reason_sanitized.get('reason')
                debit_notes_complement.agregar("ANTIGUO" if move.ancient_regime else "",
                                               reason, data_notes['fel_date'],
                                               data_notes['series'], data_notes['uuid'], data_notes['doc_dte'])
                certify_fel_dte.agregar_complemento(debit_notes_complement)

            if dte_type.strip() == 'FCAM' and move.logistic_employed:
                employed_complement = provider.complemento_cuenta_ajena()

                if move.receipt_id.state != 'posted':
                    raise ValidationError('No ha publicado el recibo enlazado a esta factura.')
                third_party_accounts = [{'IVA': move.logistic_employed_iva,
                                         'DAI': move.logistic_employed_dai,
                                         'OTROS': move.logistic_employed_others
                                         }]

                for employed in third_party_accounts:
                    for k, v in employed.items():
                        iva = 0
                        dai = 0
                        others = 0

                        if k == 'IVA':
                            iva = v
                        elif k == 'DAI':
                            dai = v
                        else:
                            others = v

                        total = iva + dai + others
                        employed_complement.agregar(instance_partner.vat, move.receipt_id.name,
                                                    move.receipt_id.date,
                                                    k, self.truncate(iva / 0.12, 10), dai, iva, others, total)
                certify_fel_dte.agregar_complemento(employed_complement)

            if export == 'SI':
                if instance_company.fel_provider == 'ECO':
                    receptor_fel.set_purchaser_code(instance_partner.ref if instance_partner.ref else False)
                export_complement = provider.complemento_exportacion()
                if not move.invoice_incoterm_id:
                    raise ValidationError('No puedes realizar una factura de exportación '
                                          'sin INCONTERM, llénalo en la factura.')
                if instance_company.fel_provider == 'IN':
                    if not instance_company.exporter_code:
                        raise ValidationError('No puedes realizar una factura de exportación con INFILE'
                                              'sin Código de exportación del emisor.')
                elif instance_company.fel_provider in ['DI', 'MP']:
                    if not move.partner_shipping_id:
                        raise ValidationError('No puedes realizar una factura de exportación con DIGIFACT'
                                              'sin los datos del consignatario de destino.')
                    if move.partner_shipping_id:
                        if not move.partner_shipping_id.name:
                            raise ValidationError('No puedes realizar una factura de exportación con DIGIFACT'
                                                  'sin el nombre del consignatario de destino.')
                        if not move.partner_shipping_id.street:
                            raise ValidationError('No puedes realizar una factura de exportación con DIGIFACT'
                                                  'sin enviar la dirección del consignatario de destino.')

                export_complement.agregar(move.partner_shipping_id.name
                                          if move.partner_shipping_id and move.partner_shipping_id.name else '',
                                          move.partner_shipping_id.street
                                          if move.partner_shipping_id and move.partner_shipping_id.street else '',
                                          move.partner_shipping_id.ref
                                          if move.partner_shipping_id and move.partner_shipping_id.ref else ' ',
                                          instance_partner.name, instance_partner.street, instance_partner.ref
                                          if instance_partner.ref else ' ',
                                          move.invoice_origin, move.invoice_incoterm_id.code,
                                          instance_company.legal_name, instance_company.exporter_code)
                certify_fel_dte.agregar_complemento(export_complement)

            certify_fel = False
            if instance_company.fel_provider in ['IN', 'ECO']:
                credentials = [instance_company.fel_pass, instance_company.fel_pass_sign,
                               instance_company.fel_user, instance_company.vat, instance_company.email]
                for credential in credentials:
                    if not credential:
                        raise ValidationError('La compañía no está bien configurada para el proveedor INFILE. '
                                              'Hay campos sin datos.')

                certify_fel = certify_fel_dte.certificar(instance_company.fel_pass, instance_company.fel_pass_sign,
                                                         instance_company.fel_user,
                                                         instance_company.vat.replace("-", ""),
                                                         instance_company.email, instance_company)
            elif instance_company.fel_provider == 'DI':
                credentials = [instance_company.token, instance_company.vat_digifact]
                for credential in credentials:
                    if not credential:
                        raise ValidationError('La compañía no está bien configurada para el proveedor DIGIFACT. '
                                              'Hay campos sin datos. Por favor revise.')
                certify_fel = certify_fel_dte.certificar(instance_company.token,
                                                         instance_company.vat_digifact, instance_company)

            elif instance_company.fel_provider in ['CO', 'MP']:
                if not instance_company.token:
                    raise ValidationError(
                        'La compañía no está bien configurada para el proveedor CONTAP o MEGAPRINT'
                        'Falta el Token de autenticación. Por favor revise.')
                certify_fel = certify_fel_dte.certificar(instance_company.token, instance_company)

            _logger.info("HAZ PROBADO CERTIFICAR FEL!")
            certificate = move.response_dte_fel(certify_fel, 'doc_xml_generated', 'certify_xml',
                                                'signed_xml', 'fel_uuid', 'fel_date',
                                                'fel_serie', 'fel_number', move.id)
            return certificate
