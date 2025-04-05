import sys
import sqlite3
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QTableWidget, QTableWidgetItem, QDateEdit, 
                             QMessageBox, QHeaderView, QPushButton)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt, QDate

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
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

class BalanceGeneral(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.init_db()
        self.setWindowTitle("Balance General")
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        self.setMinimumSize(1200, 800)
        self.setup_ui()
    
    def init_db(self):
        """Solo conexión a la base de datos existente"""
        db_path = resource_path("contabilidad.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
    
    def calcular_balance(self):
        fecha_seleccionada = self.date_edit.date()
        mes = fecha_seleccionada.month()
        año = fecha_seleccionada.year()
        
        try:
            fecha_inicio = QDate(año, mes, 1)
            fecha_fin = fecha_inicio.addMonths(1).addDays(-1)
            fecha_inicio_plus_1 = fecha_inicio.addDays(1)
            
            # Consulta saldo inicial
            self.cursor.execute("""
                SELECT c.cuenta, 
                       SUM(CASE WHEN c.tipo = 'Debe' THEN c.monto ELSE -c.monto END)
                FROM cuentas c
                JOIN partidas p ON c.partida_id = p.id
                WHERE p.fecha = ?
                GROUP BY c.cuenta
            """, (fecha_inicio.toString(Qt.DateFormat.ISODate),))
            
            saldo_inicial = {row[0]: row[1] for row in self.cursor.fetchall()}
            
            # Consulta movimientos
            self.cursor.execute("""
                SELECT c.cuenta, 
                       SUM(CASE WHEN c.tipo = 'Debe' THEN c.monto ELSE 0 END),
                       SUM(CASE WHEN c.tipo = 'Haber' THEN c.monto ELSE 0 END)
                FROM cuentas c
                JOIN partidas p ON c.partida_id = p.id
                WHERE p.fecha BETWEEN ? AND ?
                GROUP BY c.cuenta
            """, (
                fecha_inicio_plus_1.toString(Qt.DateFormat.ISODate), 
                fecha_fin.toString(Qt.DateFormat.ISODate)
            ))
            
            movimientos = {row[0]: (row[1], row[2]) for row in self.cursor.fetchall()}
            
            self.tabla.setRowCount(0)
            
            # Combinar resultados
            todas_cuentas = set(saldo_inicial.keys()).union(set(movimientos.keys()))
            
            if not todas_cuentas:
                QMessageBox.information(self, "Información", "No hay movimientos en el periodo seleccionado")
                return
                
            for cuenta in todas_cuentas:
                row = self.tabla.rowCount()
                self.tabla.insertRow(row)
                
                inicial = saldo_inicial.get(cuenta, 0.0)
                debe, haber = movimientos.get(cuenta, (0.0, 0.0))
                saldo_actual = inicial + (debe - haber)
                
                self.tabla.setItem(row, 0, QTableWidgetItem(cuenta))
                self.tabla.setItem(row, 1, QTableWidgetItem(f"Q{inicial:.2f}"))
                self.tabla.setItem(row, 2, QTableWidgetItem(f"Q{debe:.2f}"))
                self.tabla.setItem(row, 3, QTableWidgetItem(f"Q{haber:.2f}"))
                self.tabla.setItem(row, 4, QTableWidgetItem(f"Q{saldo_actual:.2f}"))
            
            self.tabla.resizeColumnsToContents()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error en la base de datos: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error inesperado: {str(e)}")
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # Header
        header = QHBoxLayout()
        self.btn_volver = ModernButton("Volver al Menú")
        self.btn_volver.clicked.connect(self.volver_menu)
        title = QLabel("Balance General")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #004AAD;")
        header.addWidget(self.btn_volver)
        header.addWidget(title)
        header.addStretch()
        main_layout.addLayout(header)
        
        # Controles de fecha
        fecha_layout = QHBoxLayout()
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("MM/yyyy")
        self.btn_calcular = ModernButton("Generar Balance")
        self.btn_calcular.clicked.connect(self.calcular_balance)
        
        fecha_layout.addWidget(QLabel("Seleccione el mes:"))
        fecha_layout.addWidget(self.date_edit)
        fecha_layout.addWidget(self.btn_calcular)
        fecha_layout.addStretch()
        main_layout.addLayout(fecha_layout)
        
        # Tabla de resultados
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels([
            "Cuenta", 
            "Saldo Inicial (1er día)", 
            "Total Debe (resto mes)", 
            "Total Haber (resto mes)", 
            "Saldo Actual"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.tabla)
        
        self.setLayout(main_layout)
    
    def volver_menu(self):
        # Cierra la ventana actual e importa la ventana del menú principal
        from menu import MenuApp
        self.menu = MenuApp()
        self.menu.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BalanceGeneral()
    window.show()
    sys.exit(app.exec())