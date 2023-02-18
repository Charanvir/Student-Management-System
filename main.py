from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, QLineEdit, QPushButton, QMainWindow, \
    QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox
import sys
import sqlite3
from PyQt6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        # Self parameter will connect the QAction to the MainWindow class
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        # giving functionality to the action
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)

        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)
        # Needs to be added on Mac if the second menu item does not appear
        about_action.setMenuRole(QAction.MenuRole.NoRole)
        about_action.triggered.connect(self.about)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        # This will hide the first column of the table, which just shows the index
        self.table.verticalHeader().setVisible(False)
        # Need to add this to show the table
        self.setCentralWidget(self.table)

        # Create toolbar instance, can apply methods to them
        toolbar = QToolBar()
        # Make the toolbar movable, allow user to move it around
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Create status bar and add toolbar elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)
        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        # Clean any other buttons from the status bar
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

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

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
This app was created to keep track of students and their courses.
The app shows all of the students in the database, along with the course they are currently enrolled in and their mobile number.
Click the add icon to create a new record of a student, or search up a student using the search icon.
You can select an existing student and either update their record, or delete is entirely.
Enjoy! 
        """
        self.setText(content)


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


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        self.button = QPushButton("Search")
        self.button.clicked.connect(self.search_student)

        layout.addWidget(self.button)

        self.setLayout(layout)

    def search_student(self):
        name = self.student_name.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        rows = list(result)
        # QTableWidget has a findItems method
        # Takes the thing your searching for, and then a matching method from Qt
        items = management_system.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            # each item is an occurrence of the searching functionality
            # first argument gives the index of the current item, and then the index of the column
            # Essentially giving the coordinates of the searched name
            # Then flags the cells at that coordinate to selected (highlighted)
            management_system.table.item(item.row(), 1).setSelected(True)
        cursor.close()
        connection.close()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Will return an integer depending on which cell was selected
        index = management_system.table.currentRow()
        # Specify the index of the row and then index of the column
        # Extracting the text value from those coordinates
        student_name = management_system.table.item(index, 1).text()

        # Get id from selected row
        self.student_id = management_system.table.item(index, 0).text()

        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        course_name = management_system.table.item(index, 2).text()

        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics", "English"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        mobile = management_system.table.item(index, 3).text()

        self.student_module = QLineEdit(mobile)
        self.student_module.setPlaceholderText("0000000000")
        layout.addWidget(self.student_module)

        self.button = QPushButton("Update")
        self.button.clicked.connect(self.update_student)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def update_student(self):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
                       (self.student_name.text(), self.course_name.currentText(),
                        self.student_module.text(), self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        management_system.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        index = management_system.table.currentRow()
        self.student_id = management_system.table.item(index, 0).text()

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")
        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)

        self.setLayout(layout)
        yes.clicked.connect(self.delete_student)

    def delete_student(self):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = ?", (self.student_id,))
        connection.commit()
        cursor.close()
        connection.close()
        management_system.load_data()
        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully")
        confirmation_widget.exec()


app = QApplication(sys.argv)
management_system = MainWindow()
management_system.show()
management_system.load_data()
sys.exit(app.exec())
