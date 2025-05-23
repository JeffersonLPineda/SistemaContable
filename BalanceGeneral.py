import sys
import os
import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QDateEdit, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QLineEdit, QPushButton, QScrollArea, QFileDialog
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QIcon, QCursor
import pandas as pd
from fpdf import FPDF
from PyQt6.QtWidgets import QInputDialog


# Ruta de recursos para PyInstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, relative_path)

# Definición de categorías
CATEGORY_CURRENT = {
    'Disponibilidades': ['caja', 'cajas', 'banco', 'bancos'],
    'Inversiones CP': ['inversion', 'inversiones'],
    'Inventarios': ['inventario', 'inventarios'],
    'Clientes': ['clientes', 'cliente'],
    'Documentos por cobrar': ['documentos por cobrar'],
    'Impuestos por liquidar': ['isr por cobrar', 'igss por cobrar', 'iva por cobrar', 'iusi por cobrar'],
    'Otras cuentas': []
}
CATEGORY_NON_CURRENT = {
    'Vehiculos': ['vehiculos', 'edificios', 'maquinaria'],
    'Otras cuentas': []
}
CATEGORY_LIAB_CURRENT = {
    'Préstamos bancarios': ['prestamos bancarios', 'prestamo bancario'],
    'Proveedores': ['proveedores', 'proveedor'],
    'Impuestos por pagar': ['isr por pagar', 'igss por pagar', 'iva por pagar', 'iusi por pagar'],
    'Acreedores': ['acreedores', 'acreedor'],
    'Otras cuentas por pagar': []
}
CATEGORY_LIAB_NON_CURRENT = {
    'Documentos por pagar LP': ['documentos por pagar'],
    'Préstamos bancarios LP': ['prestamos bancarios', 'prestamo bancario'],
    'Otras cuentas por pagar': []
}
CATEGORY_EQUITY = {
    'Capital en acciones': ['capital en acciones', 'capital accionistas'],
    'Reserva Legal': ['reserva legal'],
    'Utilidades acumuladas': ['utilidades acumuladas', 'utilidades de años anteriores'],
    'Patrimonio': ['patrimonio'],
    'Otro patrimonio': []
}

class ModernButton(QPushButton):
    def __init__(self, text, color="#004AAD", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QPushButton {{ background-color: {color}; color: white; border: none; border-radius: 8px;
                        padding: 8px 20px; font-size: 13px; font-weight: bold; }}
            QPushButton:hover {{ background-color: {color}; }}
        """)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedSize(140, 35)

class ModernInput(QLineEdit):
    def __init__(self, placeholder=""):
        super().__init__()
        self.setStyleSheet("""
            QLineEdit { border: 2px solid #E0E0E0; border-radius: 8px; padding: 6px;
                       font-size: 13px; color: #000; background: #FFF; }
            QLineEdit:focus { border: 2px solid #004AAD; }
        """
        )
        self.setPlaceholderText(placeholder)
        self.setMinimumSize(150, 30)
        self.setReadOnly(True)

class CalculoActivoUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Balance General')
        self.setWindowIcon(QIcon(resource_path('icon.ico')))
        self.setMinimumSize(1000, 800)
        self.conn = sqlite3.connect(resource_path('contabilidad.db'))
        self.cursor = self.conn.cursor()
        self.setup_ui()

    def setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        main = QVBoxLayout(container)

        hdr = QHBoxLayout()
        lbl = QLabel('Balance General')
        lbl.setFont(QFont('Segoe UI', 18, QFont.Weight.Bold))
        lbl.setStyleSheet('color:#004AAD;')
        hdr.addWidget(lbl)
        hdr.addStretch()
        main.addLayout(hdr)

        dtl = QHBoxLayout()
        lbl_dt = QLabel('Fecha focal:')
        lbl_dt.setFont(QFont('Segoe UI', 11))
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        btn_volver = ModernButton("Volver al Menú")
        btn_volver.clicked.connect(self.volver_menu)
        btn = ModernButton('Calcular')
        btn.clicked.connect(self.on_calcular)
        dtl.addWidget(lbl_dt)
        dtl.addWidget(self.date_edit)
        dtl.addWidget(btn_volver)
        dtl.addWidget(btn)
        dtl.addStretch()
        main.addLayout(dtl)

        self.tbl_ac, self.inp_ac = self._make_table('Activo Corriente', CATEGORY_CURRENT, main)
        self.tbl_anc, self.inp_anc = self._make_table('Activo No Corriente', CATEGORY_NON_CURRENT, main)
        self.tbl_pc, self.inp_pc = self._make_table('Pasivo Corriente', CATEGORY_LIAB_CURRENT, main)
        self.tbl_pnc, self.inp_pnc = self._make_table('Pasivo No Corriente', CATEGORY_LIAB_NON_CURRENT, main)

        main.addWidget(QLabel('Patrimonio'))
        cats_eq = list(CATEGORY_EQUITY.keys()) + ['Utilidad (Pérdida) neta del año']
        self.tbl_eq = QTableWidget(len(cats_eq), 2)
        self.tbl_eq.setHorizontalHeaderLabels(['Patrimonio', 'Total Q'])
        self.tbl_eq.verticalHeader().setVisible(False)
        for i, cat in enumerate(cats_eq):
            it = QTableWidgetItem(cat)
            it.setFlags(it.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.tbl_eq.setItem(i, 0, it)
            self.tbl_eq.setItem(i, 1, QTableWidgetItem('Q0.00'))
        self.tbl_eq.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main.addWidget(self.tbl_eq)
        h_eq = QHBoxLayout()
        h_eq.addWidget(QLabel('Total Patrimonio:'))
        self.inp_eq = ModernInput()
        h_eq.addWidget(self.inp_eq)
        h_eq.addStretch()
        main.addLayout(h_eq)

        exp_layout = QHBoxLayout()
        self.btn_export_excel = ModernButton("Exportar a Excel")
        self.btn_export_excel.clicked.connect(self.export_to_excel)
        self.btn_export_pdf = ModernButton("Exportar a PDF")
        self.btn_export_pdf.clicked.connect(self.export_to_pdf)
        exp_layout.addWidget(self.btn_export_excel)
        exp_layout.addWidget(self.btn_export_pdf)
        exp_layout.addStretch()
        main.addLayout(exp_layout)

        scroll.setWidget(container)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll)

    def _make_table(self, title, cats, layout):
        layout.addWidget(QLabel(title))
        keys = list(cats.keys())
        tbl = QTableWidget(len(keys), 2)
        tbl.setHorizontalHeaderLabels([title, 'Total Q'])
        tbl.verticalHeader().setVisible(False)
        for i, k in enumerate(keys):
            it = QTableWidgetItem(k)
            it.setFlags(it.flags() ^ Qt.ItemFlag.ItemIsEditable)
            tbl.setItem(i, 0, it)
            tbl.setItem(i, 1, QTableWidgetItem('Q0.00'))
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(tbl)
        h = QHBoxLayout()
        h.addWidget(QLabel(f'Total {title}:'))
        inp = ModernInput()
        h.addWidget(inp)
        h.addStretch()
        layout.addLayout(h)
        return tbl, inp

    def export_to_excel(self):
        from PyQt6.QtWidgets import QInputDialog

        path, _ = QFileDialog.getSaveFileName(self, "Guardar como", "balance_general.xlsx", "Excel Files (*.xlsx)")
        if not path:
            return

        empresa, ok = QInputDialog.getText(self, "Nombre de la empresa", "Ingrese el nombre de la empresa:")
        if not ok or not empresa:
            return

        writer = pd.ExcelWriter(path, engine='xlsxwriter')
        workbook = writer.book
        worksheet = workbook.add_worksheet('Balance')
        writer.sheets['Balance'] = worksheet

        # Encabezado personalizado
        fecha_focal = self.date_edit.date().toString('dd MMMM yyyy')
        header_format = workbook.add_format({
            'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter'
        })
        worksheet.merge_range('A1:E1', f'EJERCICIO No. 7', header_format)
        worksheet.merge_range('A3:E3', f'{empresa.upper()}', header_format)
        worksheet.merge_range('A4:E4', 'BALANCE GENERAL', header_format)
        worksheet.merge_range('A5:E5', f'Al {fecha_focal}', header_format)
        worksheet.merge_range('A6:E6', 'Cifras expresadas en Quetzales "Q"', header_format)

        def write_table(start_row, title, tbl):
            worksheet.write(start_row, 0, title, workbook.add_format({'bold': True, 'bg_color': '#D9D9D9'}))
            worksheet.write(start_row + 1, 0, tbl.horizontalHeaderItem(0).text())
            worksheet.write(start_row + 1, 1, tbl.horizontalHeaderItem(1).text())
            for i in range(tbl.rowCount()):
                worksheet.write(start_row + 2 + i, 0, tbl.item(i, 0).text())
                worksheet.write(start_row + 2 + i, 1, tbl.item(i, 1).text())
            return start_row + 2 + tbl.rowCount() + 1

        row = 7
        row = write_table(row, 'Activo Corriente', self.tbl_ac)
        row = write_table(row, 'Activo No Corriente', self.tbl_anc)
        row = write_table(row, 'Pasivo Corriente', self.tbl_pc)
        row = write_table(row, 'Pasivo No Corriente', self.tbl_pnc)
        row = write_table(row, 'Patrimonio', self.tbl_eq)

        writer.close()
        QMessageBox.information(self, "Exportado", f"Balance exportado exitosamente a {path}")

    def export_to_pdf(self):
        empresa, ok = QInputDialog.getText(self, "Nombre de la empresa", "Ingrese el nombre de la empresa:")
        if not ok or not empresa:
            return

        self.on_calcular()  # Asegura que los datos estén actualizados

        path, _ = QFileDialog.getSaveFileName(self, "Guardar como", f"{empresa}_balance_general.pdf", "PDF Files (*.pdf)")
        if not path:
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Balance General", ln=True, align='C')

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Empresa: {empresa}", ln=True)
        pdf.cell(0, 10, f"Fecha: {self.date_edit.date().toString('yyyy-MM-dd')}", ln=True)
        pdf.ln(5)

        def write_table(title, table):
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, title, ln=True)
            pdf.set_font("Arial", size=10)
            for r in range(table.rowCount()):
                pdf.cell(95, 8, table.item(r, 0).text(), 1)
                pdf.cell(95, 8, table.item(r, 1).text(), 1, ln=True)
            pdf.ln(5)

        write_table("Activo Corriente", self.tbl_ac)
        write_table("Activo No Corriente", self.tbl_anc)
        write_table("Pasivo Corriente", self.tbl_pc)
        write_table("Pasivo No Corriente", self.tbl_pnc)
        write_table("Patrimonio", self.tbl_eq)

        pdf.output(path)
        QMessageBox.information(self, "Exportado", f"Balance exportado exitosamente a {path}")

    def on_calcular(self):
        fecha_str = self.date_edit.date().toString('yyyy-MM-dd')
        focal = datetime.fromisoformat(fecha_str)
        year = focal.year

        # Cálculo de ventas, costo, gastos e ingresos en el año
        start = f'{year}-01-01'
        end   = f'{year}-12-31'
        q = '''
            SELECT c.monto, c.tipo, c.tipo2, p.fecha
            FROM cuentas c
            JOIN partidas p ON c.partida_id = p.id
            WHERE p.fecha BETWEEN ? AND ?
        '''
        ventas = costo = gastos = ingresos = 0.0
        self.cursor.execute(q, (start, end))
        for amt, typ, t2, dt in self.cursor.fetchall():
            sign = -amt if typ.lower() == 'debe' else amt if 'venta' in t2.lower() or 'gasto' in t2.lower() else amt
            tl = t2.lower()
            if 'ventas' in tl:
                ventas += sign
            elif 'costo de venta' in tl:
                costo += sign
            elif 'gasto' in tl:
                gastos += (amt if typ.lower() == 'debe' else -amt)
            elif 'ingreso' in tl:
                ingresos += sign

        raw_uti = ventas + costo - gastos + ingresos
        utilidad_neta = raw_uti - raw_uti * 0.25 if raw_uti > 0 else raw_uti

        # Totales por sección
        totals = {
            'AC': {c: 0.0 for c in CATEGORY_CURRENT},
            'ANC': {c: 0.0 for c in CATEGORY_NON_CURRENT},
            'PC': {c: 0.0 for c in CATEGORY_LIAB_CURRENT},
            'PNC': {c: 0.0 for c in CATEGORY_LIAB_NON_CURRENT},
            'EQ': {c: 0.0 for c in CATEGORY_EQUITY}
        }

        q2 = '''
            SELECT c.cuenta, c.monto, c.tipo, p.fecha, c.tipo2
            FROM cuentas c
            JOIN partidas p ON c.partida_id = p.id
            WHERE p.fecha <= ?
        '''
        self.cursor.execute(q2, (fecha_str,))
        for name, amt, typ, dt, t2 in self.cursor.fetchall():
            try:
                mov_date = datetime.fromisoformat(dt)
            except ValueError:
                continue
            if mov_date > focal:
                continue
            sign = amt if typ.lower() == 'debe' else -amt
            tl = t2.lower()
            dias = (focal - mov_date).days
            nm = name.lower()

            if tl == 'activo':
                nm = name.lower()
                if any(palabra in nm for palabra in ['vehiculos', 'vehículo', 'edificios', 'edificio', 'maquinaria']):
                    sec, cat = 'ANC', 'Otras cuentas'
                else:
                    sec, cat = ('AC', self.classify(name, CATEGORY_CURRENT, 'AC')[1]) if dias <= 365 else ('ANC', 'Otras cuentas')
            elif tl == 'pasivo':
                sec, cat = self.classify(name, CATEGORY_LIAB_CURRENT, 'PC') if dias <= 365 else self.classify(name, CATEGORY_LIAB_NON_CURRENT, 'PNC')
            elif tl == 'patrimonio':
                if 'capital en acciones' in nm:
                    cat = 'Capital en acciones'
                elif 'reserva legal' in nm:
                    cat = 'Reserva Legal'
                elif 'utilidades acumuladas' in nm:
                    cat = 'Utilidades acumuladas'
                elif nm == 'patrimonio':
                    cat = 'Patrimonio'
                else:
                    cat = 'Otro patrimonio'
                sec = 'EQ'
            else:
                continue

            totals[sec][cat] += sign

        # Poblar tablas y mostrar totales
        sections = [
            (self.tbl_ac, self.inp_ac, CATEGORY_CURRENT, 'AC'),
            (self.tbl_anc, self.inp_anc, CATEGORY_NON_CURRENT, 'ANC'),
            (self.tbl_pc, self.inp_pc, CATEGORY_LIAB_CURRENT, 'PC'),
            (self.tbl_pnc, self.inp_pnc, CATEGORY_LIAB_NON_CURRENT, 'PNC')
        ]
        for tbl, inp, cats, key in sections:
            total = sum(totals[key].values())
            for i, cat in enumerate(cats):
                tbl.setItem(i, 1, QTableWidgetItem(f"Q{totals[key][cat]:,.2f}"))
            inp.setText(f"Q{total:,.2f}")

        for i, cat in enumerate(CATEGORY_EQUITY):
            self.tbl_eq.setItem(i, 1, QTableWidgetItem(f"Q{totals['EQ'][cat]:,.2f}"))
        last = self.tbl_eq.rowCount() - 1
        self.tbl_eq.setItem(last, 1, QTableWidgetItem(f"Q{utilidad_neta:,.2f}"))
        self.inp_eq.setText(f"Q{utilidad_neta:,.2f}")

    def classify(self, name, cat_dict, prefix):
        nm = name.lower()
        for cat, keys in cat_dict.items():
            if any(k in nm for k in keys):
                return prefix, cat
        return prefix, list(cat_dict.keys())[0]
    
    def volver_menu(self):
        from menu import MenuApp
        self.menu = MenuApp()
        self.menu.show()
        self.close()
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = CalculoActivoUI()
    win.show()
    sys.exit(app.exec())