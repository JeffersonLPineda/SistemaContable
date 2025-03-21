import sqlite3
import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,QMessageBox, QListWidget, QHBoxLayout, QGraphicsDropShadowEffect, QFrame)
from PyQt6.QtGui import QPalette, QColor, QIcon, QFont, QPixmap
from PyQt6.QtCore import Qt, QSize
from menu import MenuApp 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "usuarios.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

class ModernInput(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                color: #2C3E50;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #004AAD;
            }
        """)
        self.setMinimumSize(250, 40)

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
                background-color: {self.darken_color(color)};
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(160, 40)

    def darken_color(self, hex_color, factor=0.8):
        color = QColor(hex_color)
        return color.darker(int(100 * factor)).name()

class LoginApp(QWidget):
    def __init__(self):
        super().__init__()

        def resource_path(relative_path):
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)
        
        self.setWindowTitle("Login")
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        self.setMinimumSize(500, 400)
        
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0 y1:0, x2:1 y2:1,
                    stop:0 #ffffff, stop:1 #d6ffff
                );
            }
            QMessageBox QLabel {
                color: #2C3E50;
            }
            QMessageBox QPushButton {
                background-color: #004AAD;
                color: white;
                min-width: 80px;
            }             
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(25)
        
        # Header
        header = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(QPixmap("logo.png").scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))
        header.addWidget(logo)
        
        title = QLabel("Acceso al Sistema")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #004AAD;")
        header.addWidget(title)
        header.addStretch()
        main_layout.addLayout(header)
        
        # Form Container
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                padding: 30px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(3, 3)
        form_frame.setGraphicsEffect(shadow)
        
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        
        self.user_entry = ModernInput()
        self.user_entry.setPlaceholderText("Usuario")
        form_layout.addWidget(self.user_entry)
        
        self.pass_entry = ModernInput()
        self.pass_entry.setPlaceholderText("Contraseña")
        self.pass_entry.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.pass_entry)
        
        # Buttons
        btn_container = QHBoxLayout()
        self.login_button = ModernButton("Ingresar")
        self.login_button.clicked.connect(self.login)
        btn_container.addWidget(self.login_button)
        
        self.admin_button = ModernButton("Gestor", "#6C757D")
        self.admin_button.clicked.connect(self.admin_login)
        btn_container.addWidget(self.admin_button)
        
        form_layout.addLayout(btn_container)
        form_frame.setLayout(form_layout)
        main_layout.addWidget(form_frame)
        main_layout.addStretch()
        
        self.setLayout(main_layout)

    def login(self):
        user = self.user_entry.text()
        password = self.pass_entry.text()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (user, password))
        user_data = cursor.fetchone()
        conn.close()
        if user_data:
            QMessageBox.information(self, "Acceso", "Ingreso exitoso")
            self.close()
            self.menu_app = MenuApp()
            self.menu_app.show()
        else:
            QMessageBox.critical(self, "Error", "Credenciales incorrectas")

    def admin_login(self):
        user = self.user_entry.text()
        password = self.pass_entry.text()
        if user == "Admin" and password == "UMG2025":
            self.admin_app = AdminApp()
            self.admin_app.show()
        else:
            QMessageBox.critical(self, "Error", "Credenciales de Admin incorrectas")

class AdminApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Usuarios")
        self.setWindowIcon(QIcon("icon.ico"))
        self.setMinimumSize(600, 500)
        
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0 y1:0, x2:1 y2:1,
                    stop:0 #ffffff, stop:1 #d6ffff
                );
            }
            QMessageBox QLabel {
                color: #2C3E50;
            }
            QMessageBox QPushButton {
                background-color: #004AAD;
                color: white;
                min-width: 80px;
            }             
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Gestión de Usuarios")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #004AAD;")
        header.addWidget(title)
        header.addStretch()
        main_layout.addLayout(header)
        
        # Form Container
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                padding: 25px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(3, 3)
        container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Inputs
        self.new_user = ModernInput()
        self.new_user.setPlaceholderText("Nuevo usuario")
        layout.addWidget(self.new_user)
        
        self.new_pass = ModernInput()
        self.new_pass.setPlaceholderText("Contraseña")
        self.new_pass.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.new_pass)
        
        # Buttons
        btn_container = QHBoxLayout()
        self.add_user_btn = ModernButton("Agregar Usuario")
        self.add_user_btn.clicked.connect(self.add_user)
        btn_container.addWidget(self.add_user_btn)
        
        self.del_user_btn = ModernButton("Eliminar Usuario", "#DC3545")
        self.del_user_btn.clicked.connect(self.del_user_func)
        btn_container.addWidget(self.del_user_btn)
        layout.addLayout(btn_container)
        
        # User List
        self.user_list = QListWidget()
        self.user_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px;
                background-color: #FFFFFF;
                color: black;
            }
        """)
        self.load_users()
        layout.addWidget(self.user_list)
        
        container.setLayout(layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

    def load_users(self):
        self.user_list.clear()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM usuarios")
        users = cursor.fetchall()
        conn.close()
        for user in users:
            self.user_list.addItem(user[0])

    def add_user(self):
        user = self.new_user.text()
        password = self.new_pass.text()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", (user, password))
            conn.commit()
            QMessageBox.information(self, "Éxito", "Usuario agregado correctamente")
            self.load_users()
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Error", "El usuario ya existe")
        conn.close()

    def del_user_func(self):
        selected_user = self.user_list.currentItem()
        if selected_user:
            user = selected_user.text()
            reply = QMessageBox.question(
                self, 
                "Confirmación", 
                f"¿Eliminar usuario {user}?", 
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM usuarios WHERE username=?", (user,))
                conn.commit()
                conn.close()
                self.load_users()
                QMessageBox.information(self, "Éxito", "Usuario eliminado correctamente")

        app.setStyleSheet("""
            QMessageBox QLabel {
                color: #000000;
            }
            QMessageBox QPushButton {
                background-color: #e6ffff;
                color: white;
                min-width: 80px;
            }
        """)

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    
    login = LoginApp()
    login.show()
    sys.exit(app.exec())