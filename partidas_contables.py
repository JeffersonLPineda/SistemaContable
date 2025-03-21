import sys
import os
import sqlite3
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QDateEdit, QMessageBox, QHeaderView, QComboBox)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt, QDate

def resource_path(relative_path):
    """Obtiene la ruta absoluta del recurso, compatible con PyInstaller."""
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

class PartidasContables(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.init_db()
        self.setWindowTitle("Gestión de Partidas Contables")
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        self.setMinimumSize(1200, 800)
        self.setup_ui()
    
    def init_db(self):
        # Conexión a la base de datos y creación del esquema si no existe.
        self.conn = sqlite3.connect("contabilidad.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS partidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE NOT NULL,
                correlativo INTEGER NOT NULL UNIQUE,
                descripcion TEXT NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cuentas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partida_id INTEGER NOT NULL,
                cuenta TEXT NOT NULL,
                monto REAL NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('Debe', 'Haber')),
                FOREIGN KEY (partida_id) REFERENCES partidas(id) ON DELETE CASCADE
            )
        """)
        self.conn.commit()
    
    def agregar_cuenta(self):
        cuenta = self.cuenta.text().strip()
        monto_text = self.monto.text().strip()
        tipo = self.tipo_cuenta.currentText()
        
        if not cuenta or not monto_text:
            QMessageBox.warning(self, "Error", "Debe ingresar una cuenta y un monto válido.")
            return
        
        try:
            monto = float(monto_text)
        except ValueError:
            QMessageBox.warning(self, "Error", "Ingrese un monto válido.")
            return
        
        if monto <= 0:
            QMessageBox.warning(self, "Error", "El monto debe ser mayor que cero.")
            return
        
        row = self.tabla.rowCount()
        self.tabla.insertRow(row)
        self.tabla.setItem(row, 0, QTableWidgetItem(cuenta))
        self.tabla.setItem(row, 1, QTableWidgetItem(f"Q{monto:.2f}"))
        self.tabla.setItem(row, 2, QTableWidgetItem(tipo))
        
        # Botón de eliminación para cuentas nuevas (antes de guardar)
        btn_eliminar = QPushButton("X")
        btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 2px 4px;
                font-size: 10px;
                min-width: 20px;
            }
            QPushButton:hover {
                background-color: #B71C1C;
            }
        """)
        btn_eliminar.clicked.connect(self.eliminar_fila)
        self.tabla.setCellWidget(row, 3, btn_eliminar)
        
        self.cuenta.clear()
        self.monto.clear()
    
    def eliminar_fila(self):
        # Elimina la fila correspondiente al botón presionado
        boton = self.sender()
        if boton:
            for row in range(self.tabla.rowCount()):
                if self.tabla.cellWidget(row, 3) == boton:
                    self.tabla.removeRow(row)
                    break
    
    def buscar_partida(self):
        correlativo_buscar = self.buscar_correlativo.text().strip()
        if not correlativo_buscar:
            QMessageBox.warning(self, "Error", "Ingrese un correlativo para buscar.")
            return
        
        try:
            correlativo = int(correlativo_buscar)
        except ValueError:
            QMessageBox.warning(self, "Error", "El correlativo debe ser un número entero.")
            return
        
        self.cursor.execute("""
            SELECT id, fecha, descripcion 
            FROM partidas 
            WHERE correlativo=?
        """, (correlativo,))
        partida = self.cursor.fetchone()
        
        if not partida:
            QMessageBox.warning(self, "No encontrado", "No existe una partida con ese correlativo.")
            return
        
        partida_id, fecha_str, descripcion = partida
        self.cursor.execute("""
            SELECT cuenta, monto, tipo 
            FROM cuentas 
            WHERE partida_id=?
        """, (partida_id,))
        cuentas = self.cursor.fetchall()
        
        self.limpiar_formulario()
        self.correlativo.setText(str(correlativo))
        self.correlativo.setReadOnly(True)
        fecha_obj = QDate.fromString(fecha_str, Qt.DateFormat.ISODate)
        if not fecha_obj.isValid():
            QMessageBox.warning(self, "Error", "La fecha almacenada es inválida.")
            return
        self.date_edit.setDate(fecha_obj)
        self.descripcion.setText(descripcion)
        
        # Se cargan las cuentas sin botón de eliminación (ya guardadas)
        for cuenta, monto, tipo in cuentas:
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            self.tabla.setItem(row, 0, QTableWidgetItem(cuenta))
            self.tabla.setItem(row, 1, QTableWidgetItem(f"Q{monto:.2f}"))
            self.tabla.setItem(row, 2, QTableWidgetItem(tipo))
            self.tabla.setItem(row, 3, QTableWidgetItem(""))
    
    def guardar_partida(self):
        if not self.date_edit.date().isValid():
            QMessageBox.warning(self, "Error", "La fecha no es válida.")
            return
        
        fecha = self.date_edit.date().toString(Qt.DateFormat.ISODate)
        descripcion = self.descripcion.text().strip()
        
        if not descripcion:
            QMessageBox.warning(self, "Error", "La descripción es obligatoria.")
            return
        
        self.cursor.execute("SELECT MAX(correlativo) FROM partidas")
        max_correlativo = self.cursor.fetchone()[0]
        correlativo = 1 if max_correlativo is None else max_correlativo + 1
        
        cuentas = []
        for row in range(self.tabla.rowCount()):
            cuenta_item = self.tabla.item(row, 0)
            monto_item = self.tabla.item(row, 1)
            tipo_item = self.tabla.item(row, 2)
            
            if not cuenta_item or not monto_item or not tipo_item:
                QMessageBox.warning(self, "Error", f"Fila {row+1}: Datos incompletos.")
                return
            
            cuenta_val = cuenta_item.text().strip()
            monto_text = monto_item.text().strip()
            if monto_text.startswith("Q"):
                monto_text = monto_text[1:].strip()
            tipo = tipo_item.text().strip()
            
            if not cuenta_val:
                QMessageBox.warning(self, "Error", f"Fila {row+1}: La cuenta no puede estar vacía.")
                return
            
            if not monto_text:
                QMessageBox.warning(self, "Error", f"Fila {row+1}: El monto no puede estar vacío.")
                return
            
            try:
                monto = float(monto_text)
            except ValueError:
                QMessageBox.warning(self, "Error", f"Fila {row+1}: Monto inválido.")
                return
            
            if monto <= 0:
                QMessageBox.warning(self, "Error", f"Fila {row+1}: El monto debe ser mayor que cero.")
                return
            
            if tipo not in ('Debe', 'Haber'):
                QMessageBox.warning(self, "Error", f"Fila {row+1}: Tipo de cuenta inválido.")
                return
            
            cuentas.append((cuenta_val, monto, tipo))
        
        if len(cuentas) < 2:
            QMessageBox.warning(self, "Error", "Debe ingresar al menos dos cuentas.")
            return
        
        total_debe = sum(c[1] for c in cuentas if c[2] == 'Debe')
        total_haber = sum(c[1] for c in cuentas if c[2] == 'Haber')
        
        if abs(total_debe - total_haber) > 0.01:
            QMessageBox.warning(self, "Error", f"El Debe (Q{total_debe:.2f}) y el Haber (Q{total_haber:.2f}) no están balanceados.")
            return
        
        try:
            self.conn.execute("BEGIN TRANSACTION")
            self.cursor.execute("""
                INSERT INTO partidas (fecha, correlativo, descripcion)
                VALUES (?, ?, ?)
            """, (fecha, correlativo, descripcion))
            partida_id = self.cursor.lastrowid
            
            for cuenta_val, monto, tipo in cuentas:
                self.cursor.execute("""
                    INSERT INTO cuentas (partida_id, cuenta, monto, tipo)
                    VALUES (?, ?, ?, ?)
                """, (partida_id, cuenta_val, monto, tipo))
            
            self.conn.commit()
            QMessageBox.information(self, "Éxito", f"Partida guardada correctamente con correlativo {correlativo}.")
            self.limpiar_formulario()
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Error", f"Error al guardar: {str(e)}")
    
    def eliminar_partida(self):
        correlativo_text = self.correlativo.text().strip()
        if not correlativo_text:
            QMessageBox.warning(self, "Error", "No hay partida seleccionada para eliminar.")
            return
        
        ret = QMessageBox.question(
            self, 
            "Confirmar eliminación", 
            "¿Está seguro de que desea eliminar la partida?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ret == QMessageBox.StandardButton.Yes:
            try:
                correlativo = int(correlativo_text)
            except ValueError:
                QMessageBox.warning(self, "Error", "El correlativo es inválido.")
                return
            try:
                self.cursor.execute("DELETE FROM partidas WHERE correlativo=?", (correlativo,))
                self.conn.commit()
                QMessageBox.information(self, "Eliminado", "Partida eliminada correctamente.")
                self.limpiar_formulario()
            except Exception as e:
                self.conn.rollback()
                QMessageBox.critical(self, "Error", f"Error al eliminar: {str(e)}")
    
    def limpiar_formulario(self):
        self.date_edit.setDate(QDate.currentDate())
        self.descripcion.clear()
        self.cuenta.clear()
        self.monto.clear()
        self.tipo_cuenta.setCurrentIndex(0)
        self.tabla.setRowCount(0)
        self.correlativo.clear()
        self.correlativo.setReadOnly(True)
    
    def nueva_partida(self):
        self.limpiar_formulario()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # Header
        header = QHBoxLayout()
        self.btn_volver = ModernButton("Volver al Menú")
        self.btn_volver.clicked.connect(self.volver_menu)
        title = QLabel("Partidas Contables")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #004AAD;")
        self.btn_nuevo = ModernButton("Nueva Partida")
        self.btn_nuevo.clicked.connect(self.nueva_partida)
        header.addWidget(self.btn_volver)
        header.addWidget(title)
        header.addWidget(self.btn_nuevo)
        header.addStretch()
        main_layout.addLayout(header)
        
        # Búsqueda
        search_layout = QHBoxLayout()
        self.buscar_correlativo = ModernInput("Buscar por correlativo")
        self.btn_buscar = ModernButton("Buscar")
        self.btn_buscar.clicked.connect(self.buscar_partida)
        search_layout.addWidget(self.buscar_correlativo)
        search_layout.addWidget(self.btn_buscar)
        main_layout.addLayout(search_layout)
        
        # Formulario
        form_layout = QGridLayout()
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QDate.currentDate())
        self.correlativo = ModernInput("Correlativo (auto)")
        self.correlativo.setReadOnly(True)
        self.descripcion = ModernInput("Descripción de la partida")
        self.cuenta = ModernInput("Cuenta")
        self.monto = ModernInput("Monto")
        self.tipo_cuenta = QComboBox()
        self.tipo_cuenta.addItems(["Debe", "Haber"])
        
        self.btn_agregar_cuenta = ModernButton("Agregar Cuenta")
        self.btn_agregar_cuenta.clicked.connect(self.agregar_cuenta)
        
        # Botones de Guardar y Eliminar Partida
        self.btn_guardar = ModernButton("Guardar Partida")
        self.btn_guardar.clicked.connect(self.guardar_partida)
        self.btn_eliminar = ModernButton("Eliminar Partida", color="#D32F2F")
        self.btn_eliminar.clicked.connect(self.eliminar_partida)
        botones_layout = QHBoxLayout()
        botones_layout.addWidget(self.btn_guardar)
        botones_layout.addWidget(self.btn_eliminar)
        botones_layout.addStretch()
        
        form_layout.addWidget(QLabel("Fecha:"), 0, 0)
        form_layout.addWidget(self.date_edit, 0, 1)
        form_layout.addWidget(QLabel("Correlativo:"), 0, 2)
        form_layout.addWidget(self.correlativo, 0, 3)
        form_layout.addWidget(QLabel("Descripción:"), 1, 0)
        form_layout.addWidget(self.descripcion, 1, 1, 1, 3)
        form_layout.addWidget(QLabel("Cuenta"), 2, 0)
        form_layout.addWidget(QLabel("Monto"), 2, 1)
        form_layout.addWidget(QLabel("Tipo"), 2, 2)
        form_layout.addWidget(self.cuenta, 3, 0)
        form_layout.addWidget(self.monto, 3, 1)
        form_layout.addWidget(self.tipo_cuenta, 3, 2)
        form_layout.addWidget(self.btn_agregar_cuenta, 3, 3)
        
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Cuenta", "Monto", "Tipo", "Acciones"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.tabla)
        main_layout.addLayout(botones_layout)
        self.setLayout(main_layout)
    
    def volver_menu(self):
        # Cierra la ventana actual e importa la ventana del menú principal
        from menu import MenuApp
        self.menu = MenuApp()
        self.menu.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PartidasContables()
    window.show()
    sys.exit(app.exec())
