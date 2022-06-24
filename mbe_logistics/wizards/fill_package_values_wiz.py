# -*- coding: utf-8 -*-

from logging import getLogger
from base64 import encodebytes
from datetime import datetime, date
from odoo.api import model
from odoo.fields import (Many2one, Date, Binary, Selection)
from odoo.models import TransientModel
from odoo.tools import ustr
from odoo.modules.module import get_module_resource

_logger = getLogger(__name__)


class WizardFillPackageValues(TransientModel):
    """Objecto trasient para llenar valores de los paquetes sin necesidad de modificar los permisos principales
        de los valores ingresados por el usuario para filtrar los datos del informe.
    """
    _name = 'fill.package_values.wiz'
    _description = 'Wizard para el llenado de campos de los paquetes.'

    journal_id = Many2one(
        comodel_name='account.journal',
        domain="[('type', '=', 'bank')]",
        required=True, string='Diario'
    )
    date_from = Date(
        string='Fecha Inicial',
        required=True,
        default=lambda self: datetime.now().strftime('%Y-%m-01')
    )
    date_to = Date(
        string='Fecha Final',
        required=True,
        default=lambda self: datetime.now().strftime('%Y-%m-%d')
    )
    type = Selection(
        selection=[('basic', 'Básica'), ('sat', 'SAT')],
        default='basic',
        string="Tipo Reporte"
    )
    excel_file = Binary(string='Archivo Excel')

    def action_print_pdf_report(self):
        """Función ejecutada por la acción del usuario al seleccionar el botón impirmir PDF.
            Manda a llamar al método report_action para recopilar
            los datos para la generación del reporte en el formato .pdf
        :return: la acción de tipo reporte para generar el informe
                l10n_gt_bank_reconciliation.bank_reconciliation_action_report
        """
        return self.env.ref('l10n_gt_bank_reconciliation.bank_reconciliation_action_report').report_action(self,
                                                                                                           data={})

    def get_data(self, filter_data):
        """Función necesaria para llamar el método genérico de Odoo **_get_report_values
            para obtener los valores para crear el reporte.
        :param filter_data: dict con los datos requeridos
            para ejecutar la acción tipo reporte que genera los valores del informe.
        :return: dict con los valores para crear el informe.
        """

        data = self.env['report.l10n_gt_bank_reconciliation.bank_reconciliation_report']. \
            with_context(active_model=self._name, active_ids=[self.id], active_id=self.id). \
            _get_report_values([], filter_data)
        return data

    @model
    def get_style(self):
        main_header_style = easyxf('font:height 300;'
                                   'align: horiz center;font: color black; font:bold True;'
                                   "borders: top thin,left thin,right thin,bottom thin")

        header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                              'align: horiz right;font: color black; font:bold True;'
                              "borders: top thin,left thin,right thin,bottom thin")

        left_header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                                   'align: horiz left;font: color black; font:bold True;'
                                   "borders: top thin,left thin,right thin,bottom thin")

        text_left = easyxf('font:height 200; align: horiz left;')

        text_right = easyxf('font:height 200; align: horiz right;', num_format_str='0.00')

        text_left_bold = easyxf('font:height 200; align: horiz right;font:bold True;')

        text_right_bold = easyxf('font:height 200; align: horiz right;font:bold True;', num_format_str='0.00')
        text_center = easyxf('font:height 200; align: horiz center;')
        return (main_header_style, left_header_style, header_style,
                text_left, text_right, text_left_bold, text_right_bold, text_center)

    @model
    def create_excel_header(self, worksheet):
        """

        :param worksheet:
        :return:
        """
        # ====================================
        # Style of Excel Sheet
        main_header_style, left_header_style, header_style, text_left, \
        text_right, text_left_bold, text_right_bold, text_center = self.get_style()
        # ====================================

        data = self.get_data({})
        unredeemed_checks = data.get('unredeemed_checks')
        unredeemed_transfers = data.get('unredeemed_transfers')
        deposits_in_transit = data.get('deposits_in_transit')
        multi_transactions = data.get('multi_transactions')
        ino_transactions = data.get('ino_transactions')
        rno_transactions = data.get('rno_transactions')
        amount_transactions = data.get('amount_transactions', 0.00)
        account_balance = data.get('account_balance', 0.00)

        """Cálculo de monto para BALANCE DE BANCOS, TOTAL EN CHEQUES NO CONCILIADOS, 
            TOTAL DEPÓSITOS EN TRANSITO, TOTAL TRANSACCIONES RNO, TOTAL TRANSACCIONES INO, 
            TOTAL OTRAS TRANSACCIONES, TOTAL TRANSACCIONES RECTIFICATIVAS, BALANCE CONTABLE DEL REPORTE
        """
        last_bank_balance = data.get('last_balance')
        total_unredeemed_checks = 0.00
        total_unredeemed_transfers = 0.00
        total_deposits_in_transit = 0.00
        total_rno_transactions = 0.00
        total_ino_transactions = 0.00
        total_other_transactions = 0.00
        total_note_transactions = 0.00
        account_balance_report = account_balance - amount_transactions

        p_group_style = easyxf('font:height 200;pattern: pattern solid, fore_color ivory;'
                               'align: horiz center;font: color black; font:bold True;')
        group_style = easyxf('font:height 200;pattern: pattern solid, fore_color ice_blue;'
                             'align: horiz left;font: color black; font:bold True;')
        sign_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                            'align: horiz center;font: color black; font:bold True;'
                            "borders: top thin")

        """Encabezado"""
        report_title = 'REPORTE DE CONCILIACION BANCARIA'
        row = 2
        worksheet.write(row, 0, '', left_header_style)
        worksheet.write_merge(row, row, 0, 4, report_title, main_header_style)
        row += 1
        worksheet.write(row, 0, 'Diario', left_header_style)
        worksheet.write_merge(row, row, 1, 2, self.journal_id.name, main_header_style)
        worksheet.write(row, 3, 'Moneda', left_header_style)
        worksheet.write_merge(row, row, 4, 4, self.env.company.currency_id.name, main_header_style)
        row += 1
        worksheet.write(row, 0, 'Desde', left_header_style)
        worksheet.write_merge(row, row, 1, 2, data.get('date_from', ''), main_header_style)
        worksheet.write(row, 3, 'Hasta', left_header_style)
        worksheet.write_merge(row, row, 4, 4, data.get('date_to', ''), main_header_style)
        row += 3
        """Encabezado"""

        worksheet.write(row, 0, '', left_header_style)
        worksheet.write(row, 1, 'Saldos', left_header_style)
        worksheet.write(row, 2, '', left_header_style)
        worksheet.write(row, 3, 'Contabilidad', header_style)
        worksheet.write(row, 4, 'Bancos', header_style)

        row += 1
        worksheet.write(row, 0, '', text_left)
        worksheet.write(row, 1, '', text_left)
        worksheet.write(row, 2, '', text_left)
        worksheet.write(row, 3, account_balance_report, text_right)
        worksheet.write(row, 4, last_bank_balance, text_right)

        """Cheques en circulación"""
        row += 2
        worksheet.write(row, 0, '(-)', p_group_style)
        worksheet.write(row, 1, 'Cheques en circulación', p_group_style)
        worksheet.write(row, 2, '', p_group_style)
        worksheet.write(row, 3, '', p_group_style)
        worksheet.write(row, 4, '', p_group_style)

        for check in unredeemed_checks:
            row += 1
            worksheet.write(row, 0, datetime.strftime(check.date, '%d/%m/%Y'), text_center)
            worksheet.write(row, 1, 'Cheque ' + check.document_reference if isinstance(check.document_reference, str) else 'Cheque', text_left)
            worksheet.write(row, 2, check.amount, text_right)
            worksheet.write(row, 3, '', text_right)
            worksheet.write(row, 4, (total_unredeemed_checks + check.amount), text_right)
            total_unredeemed_checks += check.amount
            """Actualización de last_bank_balance"""
            last_bank_balance -= check.amount
        """Cheques en circulación"""

        """Transferencias en circulación"""
        row += 2
        worksheet.write(row, 0, '(-)', p_group_style)
        worksheet.write(row, 1, 'Transferencias en circulación', p_group_style)
        worksheet.write(row, 2, '', p_group_style)
        worksheet.write(row, 3, '', p_group_style)
        worksheet.write(row, 4, '', p_group_style)

        for transfer in unredeemed_transfers:
            row += 1
            worksheet.write(row, 0, datetime.strftime(transfer.date, '%d/%m/%Y'), text_center)
            worksheet.write(row, 1, 'Transferencia ' + transfer.document_reference if isinstance(transfer.document_reference, str) else 'Transferencia', text_left)
            worksheet.write(row, 2, transfer.amount, text_right)
            worksheet.write(row, 3, '', text_right)
            worksheet.write(row, 4, (total_unredeemed_checks + transfer.amount), text_right)
            total_unredeemed_transfers += transfer.amount
            """Actualización de last_bank_balance"""
            last_bank_balance -= transfer.amount
        """Transferencias en circulación"""

        """Retiros no Operados"""
        row += 2
        worksheet.write(row, 0, '(-)', p_group_style)
        worksheet.write(row, 1, 'Retiros no Operados', p_group_style)
        worksheet.write(row, 2, '', p_group_style)
        worksheet.write(row, 3, '', p_group_style)
        worksheet.write(row, 4, '', p_group_style)

        for withdrawal in rno_transactions:
            row += 1
            worksheet.write(row, 0, datetime.strftime(withdrawal.date, '%d/%m/%Y'), text_center)
            worksheet.write(row, 1, withdrawal.name, text_left)
            worksheet.write(row, 2, withdrawal.amount, text_right)
            worksheet.write(row, 3, (total_rno_transactions + withdrawal.amount), text_right)
            worksheet.write(row, 4, '', text_right)
            total_rno_transactions += withdrawal.amount
            """Actualización de account_balance_report"""
            account_balance_report -= withdrawal.amount
        """Retiros no Operados"""

        """Intereses no Operados"""
        row += 2
        worksheet.write(row, 0, '(+)', p_group_style)
        worksheet.write(row, 1, 'Intereses no Operados', p_group_style)
        worksheet.write(row, 2, '', p_group_style)
        worksheet.write(row, 3, '', p_group_style)
        worksheet.write(row, 4, '', p_group_style)

        for interest in ino_transactions:
            row += 1
            worksheet.write(row, 0, datetime.strftime(interest.date, '%d/%m/%Y'), text_center)
            worksheet.write(row, 1, interest.name, text_left)
            worksheet.write(row, 2, interest.amount, text_right)
            worksheet.write(row, 3, (total_ino_transactions + interest.amount), text_right)
            worksheet.write(row, 4, '', text_right)
            total_ino_transactions += interest.amount
            """Actualización de account_balance_report"""
            account_balance_report += interest.amount
        """Intereses no Operados"""

        """Depósito en tránsito"""
        row += 2
        worksheet.write(row, 0, '(+)', p_group_style)
        worksheet.write(row, 1, 'Depósito en tránsito', p_group_style)
        worksheet.write(row, 2, '', p_group_style)
        worksheet.write(row, 3, '', p_group_style)
        worksheet.write(row, 4, '', p_group_style)

        for deposit in deposits_in_transit:
            row += 1
            worksheet.write(row, 0, datetime.strftime(deposit.date, '%d/%m/%Y'), text_center)
            worksheet.write(row, 1, deposit.communication, text_left)
            worksheet.write(row, 2, deposit.amount, text_right)
            worksheet.write(row, 3, '', text_right)
            worksheet.write(row, 4, (total_deposits_in_transit + deposit.amount), text_right)
            total_deposits_in_transit += deposit.amount
            """Actualización de last_bank_balance"""
            last_bank_balance += deposit.amount
        """Depósito en tránsito"""

        """Otros"""
        row += 2
        worksheet.write(row, 0, '(+)(-)', p_group_style)
        worksheet.write(row, 1, 'Otros', p_group_style)
        worksheet.write(row, 2, '', p_group_style)
        worksheet.write(row, 3, '', p_group_style)
        worksheet.write(row, 4, '', p_group_style)

        for transaction in multi_transactions:
            row += 1
            worksheet.write(row, 0, datetime.strftime(transaction.date, '%d/%m/%Y'), text_center)
            worksheet.write(row, 1, transaction.name, text_left)
            worksheet.write(row, 2, transaction.amount, text_right)
            worksheet.write(row, 3, transaction.amount, text_right)
            worksheet.write(row, 4, transaction.amount, text_right)

            """Actualización de account_balance_report ó total_note_transactions 
                ó total_other_transactions ó last_bank_balance
            """
            if transaction.operations_type in ['NCRE', 'NDEB']:
                account_balance_report += transaction.amount
                total_note_transactions += transaction.amount
            elif transaction.operations_type == 'Others':
                total_other_transactions += transaction.amount
                if transaction.amount < 0:
                    account_balance_report += transaction.amount
                elif transaction.amount > 0:
                    last_bank_balance += transaction.amount
        """Otros"""

        """Saldo Conciliado"""
        row += 2
        worksheet.write(row, 0, '', group_style)
        worksheet.write(row, 1, '', group_style)
        worksheet.write(row, 2, '', group_style)
        worksheet.write(row, 3, '', group_style)
        worksheet.write(row, 4, '', group_style)

        row += 1
        worksheet.write(row, 0, '', text_right)
        worksheet.write(row, 1, 'Saldo Conciliado', text_center)
        worksheet.write(row, 2, '', text_right)
        worksheet.write(row, 3, account_balance_report, text_right)
        worksheet.write(row, 4, last_bank_balance, text_right)

        row += 1
        worksheet.write(row, 0, '', group_style)
        worksheet.write(row, 1, '', group_style)
        worksheet.write(row, 2, '', group_style)
        worksheet.write(row, 3, '', group_style)
        worksheet.write(row, 4, '', group_style)
        """Saldo Conciliado"""

        """Firmas"""
        row += 6
        worksheet.write_merge(row, row, 1, 2, 'Hecho por', sign_style)
        worksheet.write_merge(row, row, 3, 4, 'Aprobado por', sign_style)
        """Firmas"""
        return worksheet, row

    @model
    def write_values(self, sheet, list_values):
        """Método útil y necesario para escribir los datos en la hoja de cálculo generada de forma dinámica y eficiente.
        :param sheet: object Worksheet
        :param list_values: lista de diccionarios con los datos a escribir en el informe
        :return: None
        """
        for values in list_values:
            row, col, length = values.get('filters')
            horizontal, vertical = values.get('alignment')
            sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=(col + length - 1))
            cell = sheet.cell(row=row, column=col, value=values.get('value'))
            cell.alignment = Alignment(horizontal=horizontal, vertical=vertical)
        return sheet

    @model
    def detail_total_accounts(self, details, data, cols_by_month):
        """
        :param data:
        :param details:
        :param cols_by_month:
        :return:
        """
        row_values = {'1': 21, '2': 22, '5': 41, '6': 42, '7': 43, '10': 61, '11': 62, '12': 63}

        try:
            for value, row in row_values.items():
                for month, transaction in data['reconciled_transactions_on_time'].items():
                    total_amount = sum([value.get('amount') for value in transaction.get(value, [])])
                    details += [
                        {'value': total_amount or 0.00,
                         'filters': (row, cols_by_month[month], 1), 'alignment': ('right', 'center')}
                    ]
        except Exception as err:
            _logger.warning('Hubo un error al realizar el detalle de montos totales de conciliaciones: ' + ustr(err))
        return details

    @model
    def detail_amounts(self, details, data, cols_by_month):
        """Método para controlar los datos necesarios para ser escritos en el encabezado del reporte xls
        :param details:
        :param data:
        :param cols_by_month:
        :return: object Worksheet, int que indica la fila en la que se va escribiendo en el informe.
        """
        row_values = {'deposits_in_transit': 118, 'unredeemed_checks': 119,
                      'other_transactions': 120, 'ino_transactions': 126, 'note_transactions': 127}

        try:
            for value, row in row_values.items():
                for month, list_values in data[value].items():
                    details += [
                        {'value': sum([value.amount for value in list_values]) or 0.00,
                         'filters': (row, cols_by_month[month], 1), 'alignment': ('right', 'center')}
                    ]
        except Exception as error:
            _logger.warning('Hubo un error al realizar el detalle de montos de conciliaciones: ' + ustr(error))
        return details

    @model
    def detail_accounts(self, details, data, cols_by_month):
        """Método para controlar los datos necesarios para ser escritos en el encabezado del reporte xls
        :param details:
        :param data:
        :param cols_by_month:
        :return: object Worksheet, int que indica la fila en la que se va escribiendo en el informe.
        """
        row_values = [('3', 25, False), ('4', 34, False), ('8', 46, True), ('9', 55, False),
                      ('13', 66, False), ('14', 74, False), ('15', 82, False), ('16', 90, False),
                      ('17', 98, False), ('18', 106, True), ('19', 113, False)]

        try:
            for value, row, no_bank in row_values:
                for month, dict_value in data['reconciled_transactions_on_time'].items():
                    for detail in dict_value.get(value, {}):
                        details += [
                            {'value': detail.get('partner_id', [False, ''])[1], 'filters': (row, 3, 1),
                             'alignment': ('center', 'center')},
                            {'value': detail.get('account_bank_name', ''), 'filters': (row, 4, 2),
                             'alignment': ('center', 'center')},
                            {'value': detail.get('amount', 0.00), 'filters': (row, 6, 1),
                             'alignment': ('right', 'center')}] \
                            if no_bank else [
                            {'value': detail.get('partner_id', [False, ''])[1], 'filters': (row, 3, 1),
                             'alignment': ('center', 'center')},
                            {'value': detail.get('bank_name', ''), 'filters': (row, 4, 1),
                             'alignment': ('center', 'center')},
                            {'value': detail.get('account_bank_name', ''), 'filters': (row, 5, 1),
                             'alignment': ('center', 'center')},
                            {'value': detail.get('amount', 0.00), 'filters': (row, 6, 1),
                             'alignment': ('right', 'center')}
                        ]
        except Exception as e:
            _logger.warning('Hubo un error al realizar el detalle de cuentas por tipo de conciliación: ' + ustr(e))
        return details

    def fill_report(self, sheet):
        """Método para controlar los datos necesarios para ser escritos en el encabezado del reporte xls
        :param sheet: object Worksheet
        :return: object Worksheet, int que indica la fila en la que se va escribiendo en el informe.
        """
        data = self.get_data({})
        cols_by_month = {1: 7, 2: 9, 3: 11, 4: 13, 5: 15, 6: 17, 7: 19, 8: 21, 9: 23, 10: 25, 11: 27, 12: 29}
        current_cols_by_month = {key: value for k in data['by_months'].keys()
                                 for key, value in cols_by_month.items() if k == key}
        details = self.detail_accounts(details=[], data=data, cols_by_month=current_cols_by_month)
        detail_amounts = self.detail_amounts(details=[], data=data, cols_by_month=current_cols_by_month)
        detail_total_accounts = self.detail_total_accounts(details=[], data=data, cols_by_month=current_cols_by_month)

        values = [
                     {'value': self.env.company.name or self.env.company.legal_name,
                      'filters': (4, 4, 2), 'alignment': ('center', 'center')},
                     {'value': self.env.company.vat or '-', 'filters': (4, 7, 1), 'alignment': ('center', 'center')},
                     {'value': self.journal_id.bank_id.name or '-', 'filters': (6, 4, 4),
                      'alignment': ('center', 'center')},
                     {'value': self.env.company.country_id.name or '-', 'filters': (7, 4, 4),
                      'alignment': ('center', 'center')},
                     {'value': self.journal_id.bank_acc_number or '-', 'filters': (8, 4, 1),
                      'alignment': ('center', 'center')},
                     {'value': self.env.company.currency_id.name or '-', 'filters': (8, 6, 2),
                      'alignment': ('center', 'center')},
                     {'value': self.journal_id.name or '-', 'filters': (9, 4, 4), 'alignment': ('center', 'center')},
                     {'value': self.journal_id.default_account_id.name or '-',
                      'filters': (11, 4, 4), 'alignment': ('center', 'center')},
                     {'value': self.journal_id.default_account_type.name or '-',
                      'filters': (12, 4, 4), 'alignment': ('center', 'center')},
                     {'value': data['account_balance'] or 0.00, 'filters': (19, 7, 1),
                      'alignment': ('right', 'center')}
                 ] + details + detail_amounts + detail_total_accounts

        try:
            sheet = self.write_values(sheet, values)
        except Exception as e:
            _logger.warning('Hubo un error al realizar la retención de impuestos: ' + ustr(e))
        else:
            return sheet

    def action_generate_excel(self):
        """Método necesario y útil para administrar la generación del reporte xls.
            Desde obtener los estilos que darán una visualización agradable al informe,
            hasta obtener los datos que conformarán el reporte.
        """
        if self.type == 'sat':
            work_book = load_workbook(filename=get_module_resource('l10n_gt_bank_reconciliation',
                                                                   'static/xlsx/', 'Conciliacion Bancaria SAT.xlsx'))
            work_sheet = work_book.active
            work_sheet.title = 'Conciliación Bancaria'
            work_sheet = self.fill_report(work_sheet)
        else:
            filename = 'Conciliacion_Bancaria.xls'
            work_book = Workbook()
            worksheet = work_book.add_sheet(filename, cell_overwrite_ok=True)
            for i in range(0, 10):
                worksheet.col(i).width = 300 * 30

            worksheet, row = self.create_excel_header(worksheet)

        to_write = BytesIO()
        work_book.save(to_write)
        to_write.seek(0)
        excel_file = encodebytes(to_write.read())
        to_write.close()
        self.write({'excel_file': excel_file})
        filename = 'Conciliación Bancaria SAT.xlsx' if self.type == 'sat' else 'Conciliación Bancaria.xls'

        if self.excel_file:
            active_id = self.ids[0]
            return {
                'type': 'ir.actions.act_url',
                'url': 'web/content/?model=%s&download=true&field=excel_file&id=%s&filename=%s' % (
                    self._name, active_id, filename),
                'target': 'new',
            }
