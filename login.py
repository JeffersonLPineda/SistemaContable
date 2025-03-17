import sqlite3
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QListWidget
from PyQt6.QtGui import QPalette, QColor, QIcon
from menu import MenuApp  # Importa la ventana del sistema contable desde otro archivo
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Ubicación del archivo actual
DB_PATH = os.path.join(BASE_DIR, "usuarios.db")

def init_db():
    conn = sqlite3.connect("usuarios.db")
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

class LoginApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Sistema Contable")
        self.setWindowIcon(QIcon("icon.ico"))
        self.setGeometry(100, 100, 400, 250)
        self.setStyleSheet("background-color: white;")

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#004AAD"))
        self.setPalette(palette)
        
        layout = QVBoxLayout()
        
        self.label_user = QLabel("Usuario:")
        self.user_entry = QLineEdit()
        self.user_entry.setStyleSheet("border: 2px solid #004AAD; padding: 5px;")
        layout.addWidget(self.label_user)
        layout.addWidget(self.user_entry)
        
        self.label_pass = QLabel("Contraseña:")
        self.pass_entry = QLineEdit()
        self.pass_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_entry.setStyleSheet("border: 2px solid #004AAD; padding: 5px;")
        layout.addWidget(self.label_pass)
        layout.addWidget(self.pass_entry)
        
        self.login_button = QPushButton("Ingresar")
        self.login_button.setStyleSheet("background-color: #004AAD; color: white; padding: 5px;")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)
        
        self.admin_button = QPushButton("Admin")
        self.admin_button.setStyleSheet("background-color: #004AAD; color: white; padding: 5px;")
        self.admin_button.clicked.connect(self.admin_login)
        layout.addWidget(self.admin_button)
        
        self.setLayout(layout)
    
    def login(self):
        user = self.user_entry.text()
        password = self.pass_entry.text()
        conn = sqlite3.connect("usuarios.db")
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
        self.setWindowTitle("Admin - Gestión de Usuarios")
        self.setWindowIcon(QIcon("icon.ico"))
        self.setGeometry(100, 100, 350, 300)
        self.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout()
        
        self.label_new_user = QLabel("Nuevo Usuario:")
        self.new_user = QLineEdit()
        self.new_user.setStyleSheet("border: 2px solid #004AAD; padding: 5px;")
        layout.addWidget(self.label_new_user)
        layout.addWidget(self.new_user)
        
        self.label_new_pass = QLabel("Contraseña:")
        self.new_pass = QLineEdit()
        self.new_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pass.setStyleSheet("border: 2px solid #004AAD; padding: 5px;")
        layout.addWidget(self.label_new_pass)
        layout.addWidget(self.new_pass)
        
        self.add_user_btn = QPushButton("Agregar Usuario")
        self.add_user_btn.setStyleSheet("background-color: #004AAD; color: white; padding: 5px;")
        self.add_user_btn.clicked.connect(self.add_user)
        layout.addWidget(self.add_user_btn)
        
        self.label_users = QLabel("Usuarios Registrados:")
        layout.addWidget(self.label_users)
        
        self.user_list = QListWidget()
        self.load_users()
        layout.addWidget(self.user_list)
        
        self.del_user_btn = QPushButton("Eliminar Usuario")
        self.del_user_btn.setStyleSheet("background-color: #FF0000; color: white; padding: 5px;")
        self.del_user_btn.clicked.connect(self.del_user_func)
        layout.addWidget(self.del_user_btn)
        
        self.setLayout(layout)
    
    def load_users(self):
        self.user_list.clear()
        conn = sqlite3.connect("usuarios.db")
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM usuarios")
        users = cursor.fetchall()
        conn.close()
        for user in users:
            self.user_list.addItem(user[0])
    
    def add_user(self):
        user = self.new_user.text()
        password = self.new_pass.text()
        conn = sqlite3.connect("usuarios.db")
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
            reply = QMessageBox.question(self, "Confirmación", f"Una vez eliminado el usuario {user}, no se puede revertir. ¿Desea continuar?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                conn = sqlite3.connect("usuarios.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM usuarios WHERE username=?", (user,))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Éxito", "Usuario eliminado correctamente")
                self.load_users()

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    login = LoginApp()
    login.show()
    sys.exit(app.exec())