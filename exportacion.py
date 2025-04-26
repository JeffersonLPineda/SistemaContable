import sys
import os
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QDateEdit, QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt, QDate


def resource_path(relative_path):
    """Obtiene la ruta absoluta del recurso, compatible con PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, relative_path)


class ModernButton(QPushButton):
    def __init__(self, text, color="#004AAD", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {color}; }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(40)


class Exportacion(QWidget):
    def __init__(self):
        super().__init__()
        self.init_db()
        self.setWindowTitle("Exportación de Datos")
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        self.setMinimumSize(600, 300)
        self.setup_ui()

    def init_db(self):
        db_path = resource_path("contabilidad.db")
        self.conn = sqlite3.connect(db_path)

    def setup_ui(self):
        layout = QVBoxLayout()
        self.btn_volver = ModernButton("Volver al Menú")
        self.btn_volver.clicked.connect(self.volver_menu)
        # Rango de fechas
        date_layout = QHBoxLayout()
        lbl_from = QLabel("Fecha Inicio:")
        lbl_from.setFont(QFont("Segoe UI", 12))
        self.date_from = QDateEdit(calendarPopup=True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setFont(QFont("Segoe UI", 11))
        lbl_to = QLabel("Fecha Fin:")
        lbl_to.setFont(QFont("Segoe UI", 12))
        self.date_to = QDateEdit(calendarPopup=True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setFont(QFont("Segoe UI", 11))

        date_layout.addWidget(lbl_from)
        date_layout.addWidget(self.date_from)
        date_layout.addSpacing(20)
        date_layout.addWidget(lbl_to)
        date_layout.addWidget(self.date_to)
        layout.addLayout(date_layout)

        # Botones de exportación
        btn_layout = QHBoxLayout()
        self.btn_export_excel = ModernButton("Exportar a Excel")
        self.btn_export_excel.clicked.connect(self.export_excel)
        self.btn_export_pdf = ModernButton("Exportar a PDF", color="#00796B")
        self.btn_export_pdf.clicked.connect(self.export_pdf)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_export_excel)
        btn_layout.addWidget(self.btn_export_pdf)
        btn_layout.addWidget(self.btn_volver )
        btn_layout.addStretch()
        layout.addSpacing(20)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def fetch_data(self):
        start = self.date_from.date().toString(Qt.DateFormat.ISODate)
        end = self.date_to.date().toString(Qt.DateFormat.ISODate)
        query = (
            "SELECT p.fecha, p.correlativo, p.descripcion, c.cuenta, c.tipo, c.monto "
            "FROM partidas p JOIN cuentas c ON p.id = c.partida_id "
            "WHERE p.fecha BETWEEN ? AND ? "
            "ORDER BY p.fecha, p.correlativo"
        )
        df = pd.read_sql_query(query, self.conn, params=(start, end))
        return df

    def export_excel(self):
        df = self.fetch_data()
        if df.empty:
            QMessageBox.information(self, "Sin Datos", "No hay registros en el rango seleccionado.")
            return
        fname, _ = QFileDialog.getSaveFileName(
            self, "Guardar Excel", "", "Excel Files (*.xlsx)"
        )
        if fname:
            if not fname.lower().endswith('.xlsx'):
                fname += '.xlsx'
            try:
                df.to_excel(fname, index=False)
                QMessageBox.information(self, "Éxito", f"Exportado a Excel:\n{fname}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo exportar Excel:\n{e}")

    def export_pdf(self):
        df = self.fetch_data()
        if df.empty:
            QMessageBox.information(self, "Sin Datos", "No hay registros en el rango seleccionado.")
            return
        fname, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF", "", "PDF Files (*.pdf)"
        )
        if fname:
            if not fname.lower().endswith('.pdf'):
                fname += '.pdf'
            try:
                doc = SimpleDocTemplate(fname, pagesize=letter)
                data = [df.columns.tolist()] + df.values.tolist()
                table = Table(data, repeatRows=1)
                style = TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#004AAD')),
                    ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                    ('ALIGN',(0,0),(-1,-1),'CENTER'),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ])
                table.setStyle(style)
                doc.build([table])
                QMessageBox.information(self, "Éxito", f"Exportado a PDF:\n{fname}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo exportar PDF:\n{e}")
    def volver_menu(self):
        # Cierra la ventana actual e importa la ventana del menú principal
        from menu import MenuApp
        self.menu = MenuApp()
        self.menu.show()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Exportacion()
    window.show()
    sys.exit(app.exec())
