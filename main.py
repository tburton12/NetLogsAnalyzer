import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from os import listdir, path
import datetime

logs_path = "UrlLog"


class LogsAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analizer logów")
        self.setGeometry(350, 150, 1000, 600)

        self.widgets()
        self.layouts()

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

        # --- Tabs section -- #
        self.tabs_widget = QTabWidget()
        self.all_events_tab = QWidget()
        self.tabs_widget.addTab(self.all_events_tab, "Wszystkie zdarzenia")

        # --- Menu section --- #
        # Refresh button
        self.refresh_button = QPushButton("Odśwież", self)
        self.refresh_button.clicked.connect(self.load_logs)

        # Browse button
        self.browse_button = QPushButton("Wybierz plik", self)
        self.browse_button.clicked.connect(self.browse_button_clicked)

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

        # --- Right side --- #
        self.right_layout = QVBoxLayout()
        self.right_layout.addStretch()
        self.right_layout.addWidget(self.refresh_button)
        self.right_layout.addWidget(self.browse_button)
        self.right_layout.addStretch()
        self.right_layout.addWidget(self.credits_label)

        self.main_layout.addLayout(self.right_layout)
        self.setLayout(self.main_layout)

        self.show()

    def load_logs(self):
        """
        Loads logs and adds it to 'all events' table.
        It uses user path or default one or return
        """

        if self.user_logs_path is not None:
            file_path = self.user_logs_path
        elif self.default_logs_path is not None:
            file_path = self.default_logs_path
        else:
            return

        # Clear table before loading new data
        self.all_events_table.setRowCount(0)

        with open(file_path, "r") as f:
            print("Reading logs from: ", file_path)
            logs = f.read()

        table_row_position = self.all_events_table.rowCount()

        for line in logs.splitlines():
            try:
                date, id, name, mac, url, port = line.split("\t")
                self.all_events_table.insertRow(table_row_position)
                self.all_events_table.setItem(table_row_position, 0, QTableWidgetItem(date))
                self.all_events_table.setItem(table_row_position, 1, QTableWidgetItem(id))
                self.all_events_table.setItem(table_row_position, 2, QTableWidgetItem(name))
                self.all_events_table.setItem(table_row_position, 3, QTableWidgetItem(mac))
                self.all_events_table.setItem(table_row_position, 4, QTableWidgetItem(url))
                self.all_events_table.setItem(table_row_position, 5, QTableWidgetItem(port))

                table_row_position += 1

            except ValueError:
                print("Unexpected logs format")

        self.all_events_count_label.setText(str(table_row_position) + " zdarzeń")

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


def main():
    App=QApplication(sys.argv)
    window = LogsAnalyzer()
    sys.exit(App.exec_())


if __name__ == '__main__':
    main()
