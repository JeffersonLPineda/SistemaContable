import sys
import os
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QComboBox, QLineEdit
)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt

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
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color};
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(180, 45)


class ModernInput(QLineEdit):
    def __init__(self, placeholder=""):
        super().__init__()
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                color: #000000;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #004AAD;
            }
        """)
        self.setPlaceholderText(placeholder)
        self.setMinimumSize(200, 40)


class LibroMayor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_db()
        self.setWindowTitle("Libro Mayor")
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        self.setMinimumSize(1000, 700)
        self.setup_ui()

    def init_db(self):
        db_path = resource_path("contabilidad.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # Header con botón de cerrar
        header = QHBoxLayout()
        self.btn_close = ModernButton("Volver al Menú")
        self.btn_close.clicked.connect(self.volver_menu)
        title = QLabel("Libro Mayor")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #004AAD;")
        header.addWidget(self.btn_close)
        header.addWidget(title)
        header.addStretch()
        main_layout.addLayout(header)

        # Filtro de cuentas
        filter_layout = QHBoxLayout()
        self.search_input = ModernInput("Buscar cuenta")
        self.search_input.textChanged.connect(self.filter_accounts)
        self.combo_accounts = QComboBox()
        self.combo_accounts.setMinimumWidth(200)
        self.combo_accounts.setEditable(False)
        self.load_button = ModernButton("Cargar Libro")
        self.load_button.clicked.connect(self.load_ledger)

        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(self.combo_accounts)
        filter_layout.addWidget(self.load_button)
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)

        # Tabla del libro mayor
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Cuenta", "Fecha", "Correlativo", "Descripción", "Debe", "Haber"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)
        self.load_accounts()

    def volver_menu(self):
        from menu import MenuApp
        self.menu = MenuApp()
        self.menu.show()
        self.close()

    def load_accounts(self):
        self.cursor.execute("SELECT DISTINCT cuenta FROM cuentas ORDER BY cuenta")
        accounts = [r[0] for r in self.cursor.fetchall()]
        self.combo_accounts.clear()
        self.combo_accounts.addItem("Todas")
        self.combo_accounts.addItems(accounts)

    def filter_accounts(self, text):
        text = text.strip()
        if text:
            self.cursor.execute(
                "SELECT DISTINCT cuenta FROM cuentas WHERE cuenta LIKE ? ORDER BY cuenta",
                (f"%{text}%",)
            )
            accounts = [r[0] for r in self.cursor.fetchall()]
            self.combo_accounts.clear()
            self.combo_accounts.addItem("Todas")
            self.combo_accounts.addItems(accounts)
        else:
            self.load_accounts()

    def load_ledger(self):
        selected = self.combo_accounts.currentText()
        self.table.setRowCount(0)
        if selected == "Todas":
            query = (
                "SELECT c.cuenta, p.fecha, p.correlativo, p.descripcion, c.tipo, c.monto "
                "FROM partidas p JOIN cuentas c ON p.id = c.partida_id "
                "ORDER BY p.fecha, p.correlativo"
            )
            self.cursor.execute(query)
        else:
            query = (
                "SELECT c.cuenta, p.fecha, p.correlativo, p.descripcion, c.tipo, c.monto "
                "FROM partidas p JOIN cuentas c ON p.id = c.partida_id "
                "WHERE c.cuenta = ? ORDER BY p.fecha, p.correlativo"
            )
            self.cursor.execute(query, (selected,))
        rows = self.cursor.fetchall()
        if not rows:
            QMessageBox.information(self, "Información", "No hay registros para la cuenta seleccionada.")
            return
        for acct, date, corr, desc, typ, amt in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(acct))
            self.table.setItem(row, 1, QTableWidgetItem(date))
            self.table.setItem(row, 2, QTableWidgetItem(str(corr)))
            self.table.setItem(row, 3, QTableWidgetItem(desc))
            if typ == 'Debe':
                self.table.setItem(row, 4, QTableWidgetItem(f"Q{amt:.2f}"))
                self.table.setItem(row, 5, QTableWidgetItem(""))
            else:
                self.table.setItem(row, 4, QTableWidgetItem(""))
                self.table.setItem(row, 5, QTableWidgetItem(f"Q{amt:.2f}"))



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LibroMayor()
    window.show()
    sys.exit(app.exec())
