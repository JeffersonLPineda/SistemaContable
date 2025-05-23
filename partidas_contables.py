import sys
import os
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QDateEdit, QMessageBox, QHeaderView, QComboBox
)
from PyQt6.QtGui import QIcon, QFont, QCursor
from PyQt6.QtCore import Qt, QDate

# Ruta de recursos para PyInstaller
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
            QPushButton {{ background-color: {color}; color: white; border: none; border-radius: 8px; padding: 12px 25px; font-size: 14px; font-weight: bold; }}
            QPushButton:hover {{ background-color: {color}; }}
        """)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedSize(180, 45)

class ModernInput(QLineEdit):
    def __init__(self, placeholder=""):
        super().__init__()
        self.setStyleSheet("""
            QLineEdit { border: 2px solid #E0E0E0; border-radius: 8px; padding: 10px; font-size: 14px; color: #000; background: #FFF; }
            QLineEdit:focus { border: 2px solid #004AAD; }
        """)
        self.setPlaceholderText(placeholder)
        self.setMinimumSize(200, 40)

class PartidasContables(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.init_db()
        self.setup_ui()
        self.setWindowTitle("Gestión de Partidas Contables")
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        self.setMinimumSize(1200, 800)

    def init_db(self):
        db = resource_path("contabilidad.db")
        self.conn = sqlite3.connect(db)
        self.cursor = self.conn.cursor()
        # Crear tabla partidas
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS partidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                correlativo INTEGER UNIQUE NOT NULL,
                descripcion TEXT NOT NULL
            );""")
        # Crear tabla cuentas con campo tipo2
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cuentas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partida_id INTEGER NOT NULL,
                cuenta TEXT NOT NULL,
                monto REAL NOT NULL,
                tipo TEXT NOT NULL,
                tipo2 TEXT NOT NULL,
                FOREIGN KEY(partida_id) REFERENCES partidas(id) ON DELETE CASCADE
            );""")
        self.conn.commit()

    def agregar_cuenta(self):
        c = self.cuenta.text().strip()
        m_text = self.monto.text().strip()
        th = self.tipo_cuenta.currentText()
        t2 = self.tipo_cuentas.currentText()
        if not c or not m_text:
            QMessageBox.warning(self, "Error", "Cuenta y monto requeridos.")
            return
        try:
            m = float(m_text)
        except ValueError:
            QMessageBox.warning(self, "Error", "Monto inválido.")
            return
        if m <= 0:
            QMessageBox.warning(self, "Error", "Monto debe >0.")
            return
        r = self.tabla.rowCount()
        self.tabla.insertRow(r)
        # Inserción: Cuenta, Monto, Tipo, Tipo2, Acciones
        self.tabla.setItem(r, 0, QTableWidgetItem(c))
        self.tabla.setItem(r, 1, QTableWidgetItem(f"Q{m:.2f}"))
        self.tabla.setItem(r, 2, QTableWidgetItem(th))
        self.tabla.setItem(r, 3, QTableWidgetItem(t2))
        btn = QPushButton("X")
        btn.setStyleSheet("""
            QPushButton { background-color: #D32F2F; color: white; border: none; border-radius: 4px; padding: 2px 4px; font-size: 10px; }
            QPushButton:hover { background-color: #B71C1C; }
        """)
        btn.clicked.connect(self.eliminar_fila)
        self.tabla.setCellWidget(r, 4, btn)
        self.cuenta.clear()
        self.monto.clear()

    def eliminar_fila(self):
        btn = self.sender()
        for i in range(self.tabla.rowCount()):
            if self.tabla.cellWidget(i, 4) == btn:
                self.tabla.removeRow(i)
                return

    def buscar_partida(self):
        txt = self.buscar_correlativo.text().strip()
        if not txt:
            QMessageBox.warning(self, "Error", "Correlativo requerido.")
            return
        try:
            num = int(txt)
        except ValueError:
            QMessageBox.warning(self, "Error", "Correlativo entero.")
            return
        self.cursor.execute("SELECT id, fecha, descripcion FROM partidas WHERE correlativo=?", (num,))
        partida = self.cursor.fetchone()
        if not partida:
            QMessageBox.warning(self, "No encontrado", "Partida no existe.")
            return
        partida_id, fecha, desc = partida
        self.cursor.execute("SELECT cuenta, monto, tipo, tipo2 FROM cuentas WHERE partida_id=?", (partida_id,))
        cuentas = self.cursor.fetchall()
        self.limpiar_formulario()
        self.correlativo.setText(str(num))
        self.correlativo.setReadOnly(True)
        self.date_edit.setDate(QDate.fromString(fecha, Qt.DateFormat.ISODate))
        self.descripcion.setText(desc)
        for c, m, t, t2 in cuentas:
            r = self.tabla.rowCount()
            self.tabla.insertRow(r)
            self.tabla.setItem(r, 0, QTableWidgetItem(c))
            self.tabla.setItem(r, 1, QTableWidgetItem(f"Q{m:.2f}"))
            self.tabla.setItem(r, 2, QTableWidgetItem(t))
            self.tabla.setItem(r, 3, QTableWidgetItem(t2))
            btn = QPushButton("X")
            btn.setStyleSheet("""
                QPushButton { background-color: #D32F2F; color: white; border: none; border-radius: 4px; padding: 2px 4px; font-size: 10px; }
                QPushButton:hover { background-color: #B71C1C; }
            """)
            btn.clicked.connect(self.eliminar_fila)
            self.tabla.setCellWidget(r, 4, btn)

    def guardar_partida(self):
        if not self.date_edit.date().isValid():
            QMessageBox.warning(self, "Error", "Fecha inválida.")
            return
        fecha = self.date_edit.date().toString(Qt.DateFormat.ISODate)
        desc = self.descripcion.text().strip()
        if not desc:
            QMessageBox.warning(self, "Error", "Descripción vacía.")
            return
        self.cursor.execute("SELECT MAX(correlativo) FROM partidas")
        max_corr = self.cursor.fetchone()[0]
        corr = 1 if max_corr is None else max_corr + 1
        entradas = []
        for i in range(self.tabla.rowCount()):
            ci = self.tabla.item(i, 0);
            mi = self.tabla.item(i, 1);
            ti = self.tabla.item(i, 2);
            t2i = self.tabla.item(i, 3);
            if not ci or not mi or not ti or not t2i:
                QMessageBox.warning(self, "Error", f"Fila {i+1} incompleta.")
                return
            cv = ci.text().strip(); mv = float(mi.text().lstrip('Q').strip()); tp = ti.text().strip(); t2v = t2i.text().strip()
            entradas.append((cv, mv, tp, t2v))
        if len(entradas) < 2:
            QMessageBox.warning(self, "Error", "Mínimo 2 cuentas.")
            return
        debe = sum(e[1] for e in entradas if e[2] == 'Debe'); haber = sum(e[1] for e in entradas if e[2] == 'Haber')
        if abs(debe - haber) > 0.01:
            QMessageBox.warning(self, "Error", "Debe/Haber no balancean.")
            return
        try:
            self.conn.execute("BEGIN")
            self.cursor.execute("INSERT INTO partidas(fecha, correlativo, descripcion) VALUES(?,?,?)", (fecha, corr, desc))
            partida_id = self.cursor.lastrowid
            for cv, mv, tp, t2v in entradas:
                self.cursor.execute("INSERT INTO cuentas(partida_id, cuenta, monto, tipo, tipo2) VALUES(?,?,?,?,?)",
                                    (partida_id, cv, mv, tp, t2v))
            self.conn.commit(); QMessageBox.information(self, "Éxito", f"Partida {corr} guardada."); self.limpiar_formulario()
        except Exception as e:
            self.conn.rollback(); QMessageBox.critical(self, "Error", str(e))


    def eliminar_partida(self):
        txt = self.correlativo.text().strip()
        if not txt:
            QMessageBox.warning(self, "Error", "No hay partida seleccionada.")
            return
        try:
            corr = int(txt)
        except ValueError:
            QMessageBox.warning(self, "Error", "Correlativo inválido.")
            return
        self.cursor.execute("SELECT id FROM partidas WHERE correlativo=?", (corr,))
        partida = self.cursor.fetchone()
        if not partida:
            QMessageBox.warning(self, "Error", "Partida no encontrada en DB.")
            return
        partida_id = partida[0]
        ret = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Está seguro de eliminar la partida y sus cuentas asociadas?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ret != QMessageBox.StandardButton.Yes:
            return
        try:
            self.cursor.execute("DELETE FROM cuentas WHERE partida_id=?", (partida_id,))
            self.cursor.execute("DELETE FROM partidas WHERE id=?", (partida_id,))
            self.conn.commit()
            QMessageBox.information(self, "Eliminado", "Partida y cuentas asociadas eliminadas.")
            self.limpiar_formulario()
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Error", str(e))

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
        layout = QVBoxLayout()
        header = QHBoxLayout()
        btn_volver = ModernButton("Volver al Menú")
        btn_volver.clicked.connect(self.volver_menu)
        lbl = QLabel("Partidas Contables")
        lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #004AAD;")
        btn_nuevo = ModernButton("Nueva Partida")
        btn_nuevo.clicked.connect(self.nueva_partida)
        header.addWidget(btn_volver)
        header.addWidget(lbl)
        header.addWidget(btn_nuevo)
        header.addStretch()
        layout.addLayout(header)
        # Búsqueda
        search = QHBoxLayout()
        self.buscar_correlativo = ModernInput("Buscar por correlativo")
        btn_search = ModernButton("Buscar")
        btn_search.clicked.connect(self.buscar_partida)
        search.addWidget(self.buscar_correlativo)
        search.addWidget(btn_search)
        layout.addLayout(search)
        # Formulario
        grid = QGridLayout()
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QDate.currentDate())
        self.correlativo = ModernInput("Correlativo (auto)")
        self.correlativo.setReadOnly(True)
        self.descripcion = ModernInput("Descripción de la partida")
        self.cuenta = ModernInput("Cuenta")
        self.monto = ModernInput("Monto")
        self.tipo_cuenta = QComboBox()
        self.tipo_cuenta.addItems(["Debe", "Haber"])
        self.tipo_cuentas = QComboBox()
        # Carga de tipos fijos en combo
        for t in ["Activo", "Pasivo", "Patrimonio", "Ingreso", "Gasto", "Costo de Venta", "Ventas"]:
            self.tipo_cuentas.addItem(t)
        btn_add = ModernButton("Agregar Cuenta")
        btn_add.clicked.connect(self.agregar_cuenta)
        grid.addWidget(QLabel("Fecha:"), 0, 0)
        grid.addWidget(self.date_edit, 0, 1)
        grid.addWidget(QLabel("Correlativo:"), 0, 2)
        grid.addWidget(self.correlativo, 0, 3)
        grid.addWidget(QLabel("Descripción:"), 1, 0)
        grid.addWidget(self.descripcion, 1, 1, 1, 3)
        grid.addWidget(QLabel("Cuenta"), 2, 0)
        grid.addWidget(QLabel("Monto"), 2, 1)
        grid.addWidget(QLabel("Tipo"), 2, 2)
        grid.addWidget(QLabel("Tipo2"), 2, 3)
        grid.addWidget(self.cuenta, 3, 0)
        grid.addWidget(self.monto, 3, 1)
        grid.addWidget(self.tipo_cuenta, 3, 2)
        grid.addWidget(self.tipo_cuentas, 3, 3)
        grid.addWidget(btn_add, 3, 4)
        layout.addLayout(grid)
        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Cuenta", "Monto", "Tipo", "Clasificacion BG/ER", "Acciones"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla)
        # Botones guardar/eliminar
        foot = QHBoxLayout()
        btn_save = ModernButton("Guardar Partida")
        btn_save.clicked.connect(self.guardar_partida)
        btn_delete = ModernButton("Eliminar Partida", color="#D32F2F")
        btn_delete.clicked.connect(self.eliminar_partida)
        foot.addWidget(btn_save)
        foot.addWidget(btn_delete)
        foot.addStretch()
        layout.addLayout(foot)
        self.setLayout(layout)

    def volver_menu(self):
        from menu import MenuApp
        self.menu = MenuApp()
        self.menu.show()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = PartidasContables()
    win.show()
    sys.exit(app.exec())
