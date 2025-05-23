import sys
import os
import sqlite3
import pandas as pd
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QDateEdit, QScrollArea, QLineEdit, QPushButton, QFileDialog, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QIcon
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, relative_path)

class ModernButton(QPushButton):
    def __init__(self, text, color="#004AAD", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QPushButton {{ background-color: {color}; color: white; border: none; border-radius: 8px; padding: 8px 20px; font-size: 13px; font-weight: bold; }}
            QPushButton:hover {{ background-color: {color}; }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(140, 35)

class ModernInput(QLineEdit):
    def __init__(self, placeholder=""):
        super().__init__()
        self.setStyleSheet("""
            QLineEdit { border: 2px solid #E0E0E0; border-radius: 8px; padding: 6px; font-size: 13px; color: #000; background: #FFF; }
            QLineEdit:focus { border: 2px solid #004AAD; }
        """)
        self.setPlaceholderText(placeholder)
        self.setMinimumSize(150, 30)
        self.setReadOnly(True)

class EstadosResultadosUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Estado de Resultados')
        self.setWindowIcon(QIcon(resource_path('icon.ico')))
        self.setMinimumSize(1000, 800)
        self.init_db()
        self.setup_ui()
        self.result = {}

    def init_db(self):
        db_path = resource_path('contabilidad.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        main = QVBoxLayout(container)

        hdr = QHBoxLayout()
        lbl = QLabel('Estado de Resultados')
        lbl.setFont(QFont('Segoe UI', 18, QFont.Weight.Bold))
        lbl.setStyleSheet('color: #004AAD;')
        hdr.addWidget(lbl)
        hdr.addStretch()
        main.addLayout(hdr)

        dtl = QHBoxLayout()
        lbl_dt = QLabel('Fecha hasta:')
        lbl_dt.setFont(QFont('Segoe UI', 11))
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        btn_volver = ModernButton('Volver al Menú')
        btn_volver.clicked.connect(self.volver_menu)
        btn_calc = ModernButton('Calcular')
        btn_calc.clicked.connect(self.on_calcular)
        btn_export_excel = ModernButton('Exportar Excel')
        btn_export_excel.clicked.connect(self.export_excel)
        btn_export_pdf = ModernButton('Exportar PDF', color='#00796B')
        btn_export_pdf.clicked.connect(self.export_pdf)

        dtl.addWidget(lbl_dt)
        dtl.addWidget(self.date_edit)
        dtl.addWidget(btn_volver)
        dtl.addWidget(btn_calc)
        dtl.addWidget(btn_export_excel)
        dtl.addWidget(btn_export_pdf)
        dtl.addStretch()
        main.addLayout(dtl)

        sections = ['Ventas', 'Costo de Venta', 'Gastos de Operación', 'Otros Ingresos y Gastos - Neto']
        self.widgets = {}
        for title in sections:
            lbl = QLabel(title)
            lbl.setFont(QFont('Segoe UI', 13, QFont.Weight.Bold))
            main.addWidget(lbl)
            inp = ModernInput()
            main.addWidget(inp)
            self.widgets[title] = inp

        summary_titles = ['Utilidad Marginal', 'Pérdida en Operación', 'Pérdida antes del ISR', 'Impuesto Sobre la Renta', 'Utilidad (Pérdida) Neta']
        for title in summary_titles:
            h = QHBoxLayout()
            lbl = QLabel(f'{title}:')
            lbl.setFont(QFont('Segoe UI', 12, QFont.Weight.Bold))
            inp = ModernInput()
            h.addWidget(lbl)
            h.addWidget(inp)
            h.addStretch()
            main.addLayout(h)
            self.widgets[title] = inp

        scroll.setWidget(container)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)
        self.setLayout(layout)

    def sum_accounts(self, types, start, end):
        placeholders = ','.join('?' * len(types))
        q = f"""
            SELECT c.monto, c.tipo, c.tipo2, p.fecha
            FROM cuentas c
            JOIN partidas p ON c.partida_id = p.id
            WHERE c.tipo2 IN ({placeholders}) AND p.fecha BETWEEN ? AND ?
        """
        params = types + [start, end]
        self.cursor.execute(q, params)
        total = 0.0
        for amt, typ, t2, dt in self.cursor.fetchall():
            if amt is None:
                continue
            sign = -amt if typ.lower() == 'debe' else amt
            if 'ingreso' in t2.lower():
                sign = amt if typ.lower() == 'debe' else -amt
            total += sign
        return total

    def on_calcular(self):
        hasta = self.date_edit.date().toString('yyyy-MM-dd')
        year = int(hasta[:4])
        start, end = f'{year}-01-01', f'{year}-12-31'

        v = self.sum_accounts(['Ventas'], start, end)
        c = self.sum_accounts(['Costo de Venta'], start, end)
        g = self.sum_accounts(['Gasto'], start, end)
        o = self.sum_accounts(['Ingreso'], start, end)

        util_marg = v + c
        perd_oper = util_marg + g
        perd_antes_isr = perd_oper + o
        impuesto = perd_antes_isr * 0.25 if perd_antes_isr > 0 else 0.0
        neto = perd_antes_isr - impuesto

        self.result = {
            'Ventas': v,
            'Costo de Venta': c,
            'Gastos de Operación': g,
            'Otros Ingresos y Gastos - Neto': o,
            'Utilidad Marginal': util_marg,
            'Pérdida en Operación': perd_oper,
            'Pérdida antes del ISR': perd_antes_isr,
            'Impuesto Sobre la Renta': impuesto,
            'Utilidad (Pérdida) Neta': neto
        }

        fmt = lambda x: f"Q{x:,.2f}"
        for key, value in self.result.items():
            self.widgets[key].setText(fmt(value))

    def export_excel(self):
        if not self.result:
            QMessageBox.warning(self, 'Error', 'Primero calcule el estado de resultados.')
            return
        name, ok = QInputDialog.getText(self, 'Nombre de la Empresa', 'Ingrese el nombre de la empresa:')
        if not ok or not name.strip():
            return
        hasta = self.date_edit.date().toString('yyyy-MM-dd')
        year = int(hasta[:4])
        periodo = f'Del 1 de enero al 31 de diciembre del año {year}'
        df = pd.DataFrame([self.result])
        path, _ = QFileDialog.getSaveFileName(self, 'Guardar Excel', '', 'Excel Files (*.xlsx)')
        if path:
            if not path.lower().endswith('.xlsx'):
                path += '.xlsx'
            try:
                with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
                    workbook = writer.book
                    worksheet = workbook.add_worksheet('Estado de Resultados')
                    writer.sheets['Estado de Resultados'] = worksheet
                    title_fmt = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 14})
                    subtitle_fmt = workbook.add_format({'italic': True, 'align': 'center'})
                    worksheet.merge_range('A1:E1', name, title_fmt)
                    worksheet.merge_range('A2:E2', 'ESTADO DE RESULTADOS', title_fmt)
                    worksheet.merge_range('A3:E3', periodo, subtitle_fmt)
                    worksheet.merge_range('A4:E4', 'Cifras expresadas en Quetzales "Q"', subtitle_fmt)
                    df.to_excel(writer, sheet_name='Estado de Resultados', startrow=6, index=False)
                    header_fmt = workbook.add_format({'bold': True, 'bg_color': '#004AAD', 'font_color': 'white', 'align': 'center'})
                    for col_num, value in enumerate(df.columns.values):
                        worksheet.write(6, col_num, value, header_fmt)
                QMessageBox.information(self, 'Éxito', f'Exportado a Excel:\n{path}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'No se pudo exportar Excel:\n{e}')

    def export_pdf(self):
        if not self.result:
            QMessageBox.warning(self, 'Error', 'Primero calcule el estado de resultados.')
            return
        name, ok = QInputDialog.getText(self, 'Nombre de la Empresa', 'Ingrese el nombre de la empresa:')
        if not ok or not name.strip():
            return
        hasta = self.date_edit.date().toString('yyyy-MM-dd')
        year = int(hasta[:4])
        periodo = f"Del 1 de enero al 31 de diciembre del año {year}"

        path, _ = QFileDialog.getSaveFileName(self, 'Guardar PDF', '', 'PDF Files (*.pdf)')
        if path:
            if not path.lower().endswith('.pdf'):
                path += '.pdf'
            try:
                doc = SimpleDocTemplate(path, pagesize=letter)
                styles = getSampleStyleSheet()
                story = [
                    Paragraph(f"<b>{name}</b>", styles['Title']),
                    Paragraph("ESTADO DE RESULTADOS", styles['Title']),
                    Paragraph(periodo, styles['Italic']),
                    Paragraph('Cifras expresadas en Quetzales "Q"', styles['Italic']),
                    Spacer(1, 12)
                ]
                for label in [
                    'Ventas', 'Costo de Venta', 'Utilidad Marginal',
                    'Gastos de Operación', 'Pérdida en Operación',
                    'Otros Ingresos y Gastos - Neto',
                    'Pérdida antes del ISR', 'Impuesto Sobre la Renta', 'Utilidad (Pérdida) Neta']:
                    val = self.result[label]
                    sign = "(" if val < 0 else ""
                    end = ")" if val < 0 else ""
                    story.append(Paragraph(f"{label}: Q{sign}{abs(val):,.2f}{end}", styles['Normal']))
                story.append(Spacer(1, 12))
                story.append(Paragraph("<i>Las notas a los estados financieros deben leerse conjuntamente con este estado</i>", styles['Normal']))
                doc.build(story)
                QMessageBox.information(self, 'Éxito', f'Exportado a PDF:\n{path}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'No se pudo exportar PDF:\n{e}')

    def volver_menu(self):
        from menu import MenuApp
        self.menu = MenuApp()
        self.menu.show()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win1 = EstadosResultadosUI()
    win1.show()
    sys.exit(app.exec())