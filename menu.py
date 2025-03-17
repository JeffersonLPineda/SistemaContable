import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QPalette, QColor, QIcon

class MenuApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema Contable")
        self.setGeometry(100, 100, 500, 400)
        self.setStyleSheet("background-color: white;")
        self.setWindowIcon(QIcon("icon.ico"))

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#004AAD"))
        self.setPalette(palette)

        layout = QVBoxLayout()

        self.label = QLabel("Sistema Contable")
        self.label.setStyleSheet("font-size: 18px; font-weight: bold; color: #004AAD")
        layout.addWidget(self.label)

        self.balance_button = QPushButton("Balance General")
        self.balance_button.setStyleSheet("background-color: #004AAD; color: white; padding: 10px;")
        layout.addWidget(self.balance_button)

        self.estado_button = QPushButton("Estado de Resultados")
        self.estado_button.setStyleSheet("background-color: #004AAD; color: white; padding: 10px;")
        layout.addWidget(self.estado_button)

        self.partidas_button = QPushButton("Partidas Contables")
        self.partidas_button.setStyleSheet("background-color: #004AAD; color: white; padding: 10px;")
        layout.addWidget(self.partidas_button)

        self.diario_button = QPushButton("Diario Mayor General")
        self.diario_button.setStyleSheet("background-color: #004AAD; color: white; padding: 10px;")
        layout.addWidget(self.diario_button)

        self.saldos_button = QPushButton("Balance de Saldos")
        self.saldos_button.setStyleSheet("background-color: #004AAD; color: white; padding: 10px;")
        layout.addWidget(self.saldos_button)

        self.ingreso_button = QPushButton("Ingreso de Partidas")
        self.ingreso_button.setStyleSheet("background-color: #004AAD; color: white; padding: 10px;")
        layout.addWidget(self.ingreso_button)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    menu = MenuApp()
    menu.show()
    sys.exit(app.exec())
