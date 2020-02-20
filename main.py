import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import QTimer
from os import listdir, path
import datetime
import black_list
from pathlib import Path


def get_log_path():
    # Prepared for not compiled app run
    path = "UrlLog"

    # Uncomment below for compiled exe run
    # exe_path = sys.executable
    # path = Path(exe_path)
    # path = str(path) + "\\UrlLog"

    return path


logs_path = get_log_path()

RED_COLOR = QColor(255, 204, 203)


class LogsAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logs analyzer")
        self.setGeometry(350, 150, 1000, 600)

        self.black_listed_ports = QListWidget()
        self.black_listed_mac = QListWidget()
        self.events_list = ["Router address website visited"]

        self.user_logs_path = None

        self.widgets()
        self.layouts()

        self.default_logs_path = self.find_newest_logs_file()

        self.live_interval = 500
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(self.live_interval)

        self.black_listed_ports.addItem("23")
        self.ports_cb.addItem("23")
        self.black_listed_ports.addItem("443")
        self.ports_cb.addItem("443")

        self.setWindowIcon(QIcon('icon.ico'))

        self.load_logs()

    def widgets(self):
        # All events section
        self.all_events_tab = QWidget()
        self.all_events_table = QTableWidget()
        self.all_events_table.setColumnCount(6)
        table_header = ["Date", "ID", "Name", "MAC", "URL", "Port"]
        self.all_events_table.setHorizontalHeaderLabels(table_header)
        self.all_events_count_label = QLabel("0 events")

        self.tabs_widget = QTabWidget()
        self.all_events_tab = QWidget()
        self.tabs_widget.addTab(self.all_events_tab, "All events")

        # --- Tabs section -- #
        # Followed Ports section
        self.black_listed_ports_tab = QWidget()
        self.tabs_widget.addTab(self.black_listed_ports_tab, "Black listed ports")
        self.ports_cb = QComboBox()
        for port in range(self.black_listed_ports.count()):
            self.ports_cb.addItem(self.black_listed_ports.item(port))

        self.refresh_ports_table_button = QToolButton()
        self.refresh_ports_table_button.setText("Show")
        self.refresh_ports_table_button.clicked.connect(self.refresh_ports_table)

        self.black_listed_ports_table = QTableWidget()
        self.black_listed_ports_table.setColumnCount(6)
        self.black_listed_ports_table.setHorizontalHeaderLabels(table_header)
        self.black_listed_ports_count_label = QLabel("0 events")

        # Black listed MAC section
        self.black_listed_mac_tab = QWidget()
        self.tabs_widget.addTab(self.black_listed_mac_tab, "Black listed MACs")
        self.mac_cb = QComboBox()
        for mac in range(self.black_listed_mac.count()):
            self.mac_cb.addItem(self.black_listed_mac.item(mac))

        self.refresh_mac_table_button = QToolButton()
        self.refresh_mac_table_button.setText("Show")
        self.refresh_mac_table_button.clicked.connect(self.refresh_mac_table)

        self.black_listed_mac_table = QTableWidget()
        self.black_listed_mac_table.setColumnCount(6)
        self.black_listed_mac_table.setHorizontalHeaderLabels(table_header)
        self.black_listed_mac_count_label = QLabel("0 events")

        # Events section
        self.events_tab = QWidget()
        self.tabs_widget.addTab(self.events_tab, "Events")
        self.events_cb = QComboBox()
        for event in self.events_list:
            self.events_cb.addItem(event)

        self.refresh_events_table_button = QToolButton()
        self.refresh_events_table_button.setText("Show")
        self.refresh_events_table_button.clicked.connect(self.refresh_events_table)

        self.events_table = QTableWidget()
        self.events_table.setColumnCount(6)
        self.events_table.setHorizontalHeaderLabels(table_header)
        self.events_count_label = QLabel("0 events")

        # --- Menu section --- #
        # Refresh button

        self.refresh_button = QPushButton("Refresh", self)
        self.refresh_button.clicked.connect(lambda: self.load_logs())

        # Browse button
        self.browse_button = QPushButton("Choose file", self)
        self.browse_button.clicked.connect(self.browse_button_clicked)

        # Add to black list button
        self.blacklist_button = QPushButton("Manage black list", self)
        self.blacklist_button.clicked.connect(self.blacklist_button_clicked)

        # Live mode
        self.live_checkbox = QCheckBox()
        self.live_checkbox.setText("Live mode")
        self.live_checkbox.setChecked(True)
        self.live_checkbox.stateChanged.connect(self.live_checkbox_clicked)

        # Follow table checkbox
        self.follow_table_checkbox = QCheckBox()
        self.follow_table_checkbox.setText("Follow new events")
        self.follow_table_checkbox.setChecked(True)

        self.credits_label = QLabel("Credits:\nPaweł Wrzesień")

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

        # --- Events tab - #
        self.events_layout = QVBoxLayout()
        self.events_layout.addWidget(self.events_cb)
        self.events_layout.addWidget(self.refresh_events_table_button)
        self.events_layout.addWidget(self.events_table)
        self.events_layout.addWidget(self.events_count_label)
        self.events_tab.setLayout(self.events_layout)

        # --- Right side --- #
        self.right_layout = QVBoxLayout()
        self.right_layout.addStretch()
        self.right_layout.addWidget(self.refresh_button)
        self.right_layout.addWidget(self.browse_button)
        self.right_layout.addWidget(self.blacklist_button)
        self.right_layout.addWidget(self.live_checkbox)
        self.right_layout.addWidget(self.follow_table_checkbox)
        self.right_layout.addStretch()
        self.right_layout.addWidget(self.credits_label)

        self.main_layout.addLayout(self.right_layout)
        self.setLayout(self.main_layout)

        self.show()

    def refresh_events_table(self):
        number_of_rows = self.all_events_table.rowCount()
        table = self.events_table

        # Clear table before loading new data
        # It's obviously not the most efficient way, but it's enough for simple presentation.
        table.setRowCount(0)

        row_pos = 0

        for row in range(number_of_rows):
            try:
                date = self.all_events_table.item(row, 0).text()
                id = self.all_events_table.item(row, 1).text()
                name = self.all_events_table.item(row, 2).text()
                mac = self.all_events_table.item(row, 3).text()
                url = self.all_events_table.item(row, 4).text()
                port = self.all_events_table.item(row, 5).text()
            except AttributeError as err:
                print(err)

            if self.events_cb.currentText() == "Router address website visited":
                if "http://192.168.2.1/" in url:
                    row_pos = self.events_table.rowCount()
                    table.insertRow(row_pos)
                    table.setItem(row_pos, 0, QTableWidgetItem(date))
                    table.setItem(row_pos, 1, QTableWidgetItem(id))
                    table.setItem(row_pos, 2, QTableWidgetItem(name))
                    table.setItem(row_pos, 3, QTableWidgetItem(mac))
                    table.setItem(row_pos, 4, QTableWidgetItem(url))
                    table.setItem(row_pos, 5, QTableWidgetItem(port))
                    self.set_row_color(table, row_pos, RED_COLOR)

        try:
            self.events_count_label.setText(str(table.rowCount()) + " events")

        except Exception as e:
            print(e)

    @staticmethod
    def set_row_color(table, row_pos, color):
        for j in range(table.columnCount()):
            table.item(row_pos, j).setBackground(color)

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

        try:
            if self.user_logs_path is not None:
                file_path = self.user_logs_path
            elif self.default_logs_path is not None:
                file_path = self.default_logs_path
            else:
                return
        except Exception as e:
            print(e)

        # Clear table before loading new data
        # It's obviously not the most efficient way, but it's enough for simple presentation.
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

                    if "http://192.168.2.1/" in url:
                        self.set_row_color(table, table_row_position, RED_COLOR)

                    table_row_position += 1

            except ValueError:
                print("Unexpected logs format")

        counter.setText(str(table_row_position) + " events")

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

        files.sort(reverse=True)

        # Return None if no path found
        try:
            prepared_path = logs_path + "\\" + files[0] + ".txt"
        except IndexError:
            msg = QMessageBox()
            msg.setWindowTitle("File not found")
            msg.setInformativeText("File not found. Please choose it manually")
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
        try:
            self.user_logs_path = selected_files[0]
            self.load_logs()
        except IndexError:
            return
        except Exception as err:
            print(err)

    def live_checkbox_clicked(self):
        if self.live_checkbox.isChecked():
            self.timer.start(self.live_interval)
        else:
            self.timer.stop()

    def tick(self):
        self.load_logs()
        self.refresh_events_table()
        self.refresh_mac_table()
        self.refresh_ports_table()
        self.load_logs()

        if self.follow_table_checkbox.isChecked():
            self.black_listed_mac_table.scrollToBottom()
            self.black_listed_ports_table.scrollToBottom()
            self.all_events_table.scrollToBottom()
            self.events_table.scrollToBottom()


def main():
    App=QApplication(sys.argv)
    window = LogsAnalyzer()
    sys.exit(App.exec_())


if __name__ == '__main__':
    main()
