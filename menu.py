import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QGridLayout, QPushButton, 
                             QLabel, QVBoxLayout, QHBoxLayout, QFrame, 
                             QGraphicsDropShadowEffect, QMessageBox)
from PyQt6.QtGui import QIcon, QFont, QPixmap, QColor
from PyQt6.QtCore import Qt
from partidas_contables import PartidasContables
from balance import BalanceGeneral
from libromayor import LibroMayor
from exportacion import Exportacion

def resource_path(relative_path):
    """Obtiene la ruta absoluta del recurso, compatible con PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class IconButton(QPushButton):
    def __init__(self, text, icon_path, parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 180)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QPixmap(icon_path).scaled(90, 90, 
                           Qt.AspectRatioMode.KeepAspectRatio, 
                           Qt.TransformationMode.SmoothTransformation))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)
        
        self.text_label = QLabel(text)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("""
            QLabel {
                color: #2C3E50;
                font-size: 14px;
                font-weight: 600;
                margin-top: 8px;
            }
        """)
        layout.addWidget(self.text_label)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 2px solid #E0E0E0;
                border-radius: 18px;
                padding: 12px;
            }
            QPushButton:hover {
                border: 2px solid #004AAD;
                background-color: #F8F9FA;
            }
        """)

class MenuApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menú Principal")
        self.setMinimumSize(1000, 800)
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0 y1:0, x2:1 y2:1,
                    stop:0 #F8F9FA, stop:1 #E9ECEF
                );
            }
            QMessageBox {
                background-color: #FFFFFF;
            }
            QMessageBox QLabel {
                color: #2C3E50;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #004AAD;
                color: white;
                min-width: 100px;
                padding: 8px;
                border-radius: 6px;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        
        # Cabecera
        header = QHBoxLayout()
        header.setSpacing(20)
        
        logo = QLabel()
        logo.setPixmap(QPixmap(resource_path("logo.png")).scaled(80, 80,
                        Qt.AspectRatioMode.KeepAspectRatio))
        header.addWidget(logo)
        
        title_container = QVBoxLayout()
        title = QLabel("Sistema Contable")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet("color: #004AAD;")
        
        subtitle = QLabel("Menú Principal")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet("color: #6C757D;")
        
        title_container.addWidget(title)
        title_container.addWidget(subtitle)
        header.addLayout(title_container)
        header.addStretch()
        main_layout.addLayout(header)
        
        # Botones
        button_frame = QFrame()
        button_frame.setStyleSheet("background-color: transparent;")
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(25)
        grid_layout.setContentsMargins(25, 25, 25, 25)
        
        buttons_info = [
            ("Partidas Contables", "ParCoIco.png", self.abrir_partidas),
            ("Balance General", "BalIco.png", self.mostrar_advertencia),
            ("Estado de Resultados", "EstaIco.png", self.mostrar_advertencia),
            ("Libro Mayor General", "LibMaIco.png", self.abrir_libro_mayor),
            ("Balance de Saldos", "BalsaIco.png", self.abrir_balance_general),
            ("Exportación", "Config.png",self.abrir_exportacion)
        ]
        
        positions = [(i // 3, i % 3) for i in range(6)]
        for (row, col), (name, icon, funcion) in zip(positions, buttons_info):
            btn = IconButton(name, resource_path(icon))
            btn.clicked.connect(funcion)
            
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(25)
            shadow.setColor(QColor(0, 0, 0, 25))
            shadow.setOffset(4, 4)
            btn.setGraphicsEffect(shadow)
            
            grid_layout.addWidget(btn, row, col, Qt.AlignmentFlag.AlignCenter)
        
        button_frame.setLayout(grid_layout)
        main_layout.addWidget(button_frame)
        
        # Pie de página
        footer = QLabel("© 2025 Sistema Contable - Versión 0.1")
        footer.setFont(QFont("Segoe UI", 10))
        footer.setStyleSheet("color: #6C757D;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(footer)
        
        self.setLayout(main_layout)
    
    def abrir_partidas(self):
        self.partidas_window = PartidasContables()
        self.partidas_window.show()
        self.close()  # Cierra el menú actual

    def abrir_balance_general(self):
        self.balance_window = BalanceGeneral()
        self.balance_window.show()
        self.close()  # Cierra el menú actual

    def abrir_libro_mayor(self):
        self.balance_window = LibroMayor()
        self.balance_window.show()
        self.close()  # Cierra el menú actual   

    def abrir_exportacion(self):
        self.balance_window = Exportacion()
        self.balance_window.show()
        self.close()  # Cierra el menú actual 

    def mostrar_advertencia(self):
        msg = QMessageBox()
        msg.setWindowTitle("Función en Desarrollo")
        msg.setText("Esta funcionalidad estará disponible en la próxima actualización")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MenuApp()
    window.show()
    sys.exit(app.exec())
