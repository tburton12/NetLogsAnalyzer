from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon


class BlackListManager(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(BlackListManager, self).__init__()
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setGeometry(600, 300, 350, 300)
        self.setWindowIcon(QIcon('icon.ico'))
        self.setWindowTitle("Czarna lista")
        self.widgets()
        self.layout()

    def widgets(self):
        self.port_radio = QRadioButton("Port")
        self.port_radio.setChecked(True)
        self.port_text = QLineEdit()

        self.mac_radio = QRadioButton("MAC")
        self.mac_radio.setChecked(False)
        self.mac_text = QLineEdit()

        self.add_button = QToolButton()
        self.add_button.setText("Dodaj")
        self.add_button.clicked.connect(self.add_to_blacklist)

        self.remove_button = QToolButton()
        self.remove_button.setText("Usuń")
        self.remove_button.clicked.connect(self.remove_from_blacklist)

    def layout(self):
        self.title = QLabel("Dodaj Port lub MAC do czarnej listy")

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.title)
        self.mainLayout.addWidget(self.port_radio)
        self.mainLayout.addWidget(self.parent.black_listed_ports)
        self.mainLayout.addWidget(self.port_text)
        self.mainLayout.addWidget(self.mac_radio)
        self.mainLayout.addWidget(self.parent.black_listed_mac)
        self.mainLayout.addWidget(self.mac_text)
        self.mainLayout.addWidget(self.add_button)
        self.mainLayout.addWidget(self.remove_button)

        self.setLayout(self.mainLayout)

    def add_to_blacklist(self):
        if self.port_radio.isChecked():
            port = self.port_text.text()
            if port != "":
                self.parent.black_listed_ports.addItem(port)
                self.parent.ports_cb.addItem(port)
                print(port, " added to black list")
        elif self.mac_radio.isChecked():
            mac = self.mac_text.text()
            if mac != "":
                self.parent.black_listed_mac.addItem(mac)
                self.parent.mac_cb.addItem(mac)
                print(mac, " added to black list")

    def remove_from_blacklist(self):
        if self.port_radio.isChecked():
            cr = self.parent.black_listed_ports.currentRow()
            self.parent.port_cb.removeItem(cr)
            self.parent.black_listed_ports.takeItem(cr)
        elif self.mac_radio.isChecked():
            cr = self.parent.black_listed_mac.currentRow()
            self.parent.mac_cb.removeItem(cr)
            self.parent.black_listed_mac.takeItem(cr)
