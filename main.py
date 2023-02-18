from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, QLineEdit, QPushButton, QMainWindow, \
    QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QComboBox
import sys
import sqlite3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")

        # Self parameter will connect the QAction to the MainWindow class
        add_student_action = QAction("Add Student", self)
        # giving functionality to the action
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        # Needs to be added on Mac if the second menu item does not appear
        about_action.setMenuRole(QAction.MenuRole.NoRole)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        # This will hide the first column of the table, which just shows the index
        self.table.verticalHeader().setVisible(False)
        # Need to add this to show the table
        self.setCentralWidget(self.table)

    def load_data(self):
        connection = sqlite3.connect("database.db")
        result = connection.execute("SELECT * FROM students")
        # Whenever we load the program, it will not duplicate the data, will reset the table and load the data each time
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            # Used to insert an empty row
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                # populated the rows with data
                # QTableWidgetItem takes the data you want to insert into the table
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()


# QDialog is a specific class which serves the purpose of creating dialog windows
class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert New Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics", "English"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        self.student_module = QLineEdit()
        self.student_module.setPlaceholderText("0000000000")
        layout.addWidget(self.student_module)

        self.button = QPushButton("Register")
        self.button.clicked.connect(self.add_student)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        # This will give the choice the user made from the combo box
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.student_module.text()
        connection = sqlite3.connect("database.db")
        # Cursor needed because we are inserting new data and not just reading data from the database
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        # this will refresh the data for the main window when data in inserted from this window
        management_system.load_data()


app = QApplication(sys.argv)
management_system = MainWindow()
management_system.show()
management_system.load_data()
sys.exit(app.exec())
