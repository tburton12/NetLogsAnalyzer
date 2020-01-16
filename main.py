import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
from os import listdir, path
import datetime
import black_list

logs_path = "UrlLog"


class LogsAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analizer logów")
        self.setGeometry(350, 150, 1000, 600)

        self.black_listed_ports = QListWidget()
        self.black_listed_mac = QListWidget()

        self.widgets()
        self.layouts()

        self.live_interval = 2000
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(self.live_interval)

        self.black_listed_ports.addItem("23")
        self.ports_cb.addItem("23")
        self.black_listed_ports.addItem("443")
        self.ports_cb.addItem("443")

        self.setWindowIcon(QIcon('icon.ico'))
        self.default_logs_path = self.find_newest_logs_file()
        self.user_logs_path = None

        self.load_logs()

    def widgets(self):
        # All events section
        self.all_events_tab = QWidget()
        self.all_events_table = QTableWidget()
        self.all_events_table.setColumnCount(6)
        table_header = ["Data", "ID", "Nazwa", "MAC", "URL", "Port"]
        self.all_events_table.setHorizontalHeaderLabels(table_header)
        self.all_events_count_label = QLabel("0 zdarzeń")

        self.tabs_widget = QTabWidget()
        self.all_events_tab = QWidget()
        self.tabs_widget.addTab(self.all_events_tab, "Wszystkie zdarzenia")

        # --- Tabs section -- #
        # Followed Ports section
        self.black_listed_ports_tab = QWidget()
        self.tabs_widget.addTab(self.black_listed_ports_tab, "Czarna lista portów")
        self.ports_cb = QComboBox()
        for port in range(self.black_listed_ports.count()):
            self.ports_cb.addItem(self.black_listed_ports.item(port))

        self.refresh_ports_table_button = QToolButton()
        self.refresh_ports_table_button.setText("Wyświetl")
        self.refresh_ports_table_button.clicked.connect(self.refresh_ports_table)

        self.black_listed_ports_table = QTableWidget()
        self.black_listed_ports_table.setColumnCount(6)
        self.black_listed_ports_table.setHorizontalHeaderLabels(table_header)
        self.black_listed_ports_count_label = QLabel("0 zdarzeń")

        # Black listed MAC section
        self.black_listed_mac_tab = QWidget()
        self.tabs_widget.addTab(self.black_listed_mac_tab, "Czarna lista MAC")
        self.mac_cb = QComboBox()
        for mac in range(self.black_listed_mac.count()):
            self.mac_cb.addItem(self.black_listed_mac.item(mac))

        self.refresh_mac_table_button = QToolButton()
        self.refresh_mac_table_button.setText("Wyświetl")
        self.refresh_mac_table_button.clicked.connect(self.refresh_mac_table)

        self.black_listed_mac_table = QTableWidget()
        self.black_listed_mac_table.setColumnCount(6)
        self.black_listed_mac_table.setHorizontalHeaderLabels(table_header)
        self.black_listed_mac_count_label = QLabel("0 zdarzeń")

        # --- Menu section --- #
        # Refresh button

        self.refresh_button = QPushButton("Odśwież", self)
        self.refresh_button.clicked.connect(lambda: self.load_logs())

        # Browse button
        self.browse_button = QPushButton("Wybierz plik", self)
        self.browse_button.clicked.connect(self.browse_button_clicked)

        # Add to black list button
        self.blacklist_button = QPushButton("Dodaj do czarnej listy", self)
        self.blacklist_button.clicked.connect(self.blacklist_button_clicked)

        # Live mode
        self.live_checkbox = QCheckBox()
        self.live_checkbox.setText("Podgląd na żywo")
        self.live_checkbox.setChecked(True)
        self.live_checkbox.stateChanged.connect(self.live_checkbox_clicked)

        self.credits_label = QLabel("Twórcy:\nMarek Kopeć\nAdrian Śmiglarski\nPatryk Tracz\nPaweł Wrzesień\nKarol Zuba")

    def layouts(self):
        self.main_layout = QHBoxLayout()

        # --- Left side --- #
        self.main_layout.addWidget(self.tabs_widget)

        # - All events tab - #
        self.all_events_layout = QVBoxLayout()
        self.all_events_layout.addWidget(self.all_events_table)
        self.all_events_layout.addWidget(self.all_events_count_label)
        self.all_events_tab.setLayout(self.all_events_layout)

        # --- Followed tab - #
        self.black_listed_ports_layout = QVBoxLayout()
        self.black_listed_ports_layout.addWidget(self.ports_cb)
        self.black_listed_ports_layout.addWidget(self.refresh_ports_table_button)
        self.black_listed_ports_layout.addWidget(self.black_listed_ports_table)
        self.black_listed_ports_layout.addWidget(self.black_listed_ports_count_label)
        self.black_listed_ports_tab.setLayout(self.black_listed_ports_layout)

        # --- Black listed MAC tab - #
        self.black_listed_mac_layout = QVBoxLayout()
        self.black_listed_mac_layout.addWidget(self.mac_cb)
        self.black_listed_mac_layout.addWidget(self.refresh_mac_table_button)
        self.black_listed_mac_layout.addWidget(self.black_listed_mac_table)
        self.black_listed_mac_layout.addWidget(self.black_listed_mac_count_label)
        self.black_listed_mac_tab.setLayout(self.black_listed_mac_layout)

        # --- Right side --- #
        self.right_layout = QVBoxLayout()
        self.right_layout.addStretch()
        self.right_layout.addWidget(self.refresh_button)
        self.right_layout.addWidget(self.browse_button)
        self.right_layout.addWidget(self.blacklist_button)
        self.right_layout.addWidget(self.live_checkbox)
        self.right_layout.addStretch()
        self.right_layout.addWidget(self.credits_label)

        self.main_layout.addLayout(self.right_layout)
        self.setLayout(self.main_layout)

        self.show()

    def blacklist_button_clicked(self):
        try:
            self.bl = black_list.BlackListManager(self)
        except Exception as e:
            print(e)
        self.bl.show()

    def refresh_ports_table(self):
        self.load_logs(table=self.black_listed_ports_table, counter=self.black_listed_ports_count_label,
                       port_filter=self.ports_cb.currentText())

    def refresh_mac_table(self):
        self.load_logs(table=self.black_listed_mac_table, counter=self.black_listed_mac_count_label,
                       mac_filter=self.mac_cb.currentText())

    def load_logs(self, table=None, counter=None, port_filter=None, mac_filter=None):
        """
        Loads logs and adds it to table specified table.
        It uses user path or default one or return
        """

        if table is None:
            table = self.all_events_table

        if counter is None:
            counter = self.all_events_count_label

        if self.user_logs_path is not None:
            file_path = self.user_logs_path
        elif self.default_logs_path is not None:
            file_path = self.default_logs_path
        else:
            return

        # Clear table before loading new data
        table.setRowCount(0)

        with open(file_path, "r") as f:
            print("Reading logs from: ", file_path)
            logs = f.read()

        table_row_position = table.rowCount()

        for line in logs.splitlines():
            try:
                date, id, name, mac, url, port = line.split("\t")
                if mac == mac_filter or port == port_filter or (mac_filter is None and port_filter is None):
                    table.insertRow(table_row_position)
                    table.setItem(table_row_position, 0, QTableWidgetItem(date))
                    table.setItem(table_row_position, 1, QTableWidgetItem(id))
                    table.setItem(table_row_position, 2, QTableWidgetItem(name))
                    table.setItem(table_row_position, 3, QTableWidgetItem(mac))
                    table.setItem(table_row_position, 4, QTableWidgetItem(url))
                    table.setItem(table_row_position, 5, QTableWidgetItem(port))

                    table_row_position += 1

            except ValueError:
                print("Unexpected logs format")

        counter.setText(str(table_row_position) + " zdarzeń")


    @staticmethod
    def find_newest_logs_file():
        """
        It tries to find newest logs file
        :return: path to file with newest date in name or None
        """
        # Logs has a date in file name. We try to find the newest one
        global logs_path

        if path.isdir(logs_path) is False:
            logs_path = "\\"

        files = []

        for file in listdir(logs_path):
            if ".txt" in file:
                filename = file.replace(".txt", "")

                # Check whether filename has datetime format
                # Append only such files
                try:
                    datetime.datetime.strptime(filename, '%Y-%m-%d')
                    files.append(filename)
                except ValueError:
                    pass

        files.sort()

        # Return None if no path found
        try:
            prepared_path = logs_path + "\\" + files[0] + ".txt"
        except IndexError:
            msg = QMessageBox()
            msg.setWindowTitle("Brak pliku")
            msg.setInformativeText("Nie udało się odnaleźć pliku. Proszę wybrać go ręcznie")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return None

        # Return file with newest date in name
        return prepared_path

    def browse_button_clicked(self):
        """
        Allows user to select desired txt logs file
        Sets self.desired_logs_path
        """
        selected_files = QFileDialog.getOpenFileName(self, "Add Media", "", "Text files (*.txt)")
        self.user_logs_path = selected_files[0]

        self.load_logs()

    def live_checkbox_clicked(self):
        if self.live_checkbox.isChecked():
            self.timer.start(self.live_interval)
        else:
            self.timer.stop()

    def tick(self):
        self.load_logs()


def main():
    App=QApplication(sys.argv)
    window = LogsAnalyzer()
    sys.exit(App.exec_())


if __name__ == '__main__':
    main()
