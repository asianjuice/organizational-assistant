# frontend/task_dashboard.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QPushButton, QLineEdit, QHBoxLayout, QComboBox, QMessageBox, QInputDialog, QCheckBox, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
import requests
from datetime import datetime

class TaskDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_tasks()

    def init_ui(self):
        layout = QVBoxLayout()

        # Task list
        self.task_list = QListWidget()
        self.task_list.itemDoubleClicked.connect(self.edit_task)  # Double-click to edit
        layout.addWidget(self.task_list)

        # Add task input and button
        add_task_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter a new task...")
        add_task_layout.addWidget(self.task_input)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["low", "medium", "high"])
        add_task_layout.addWidget(self.priority_combo)

        self.due_date_edit = QDateEdit()
        self.due_date_edit.setDate(QDate.currentDate())  # Set default to today
        self.due_date_edit.setCalendarPopup(True)  # Enable calendar popup
        add_task_layout.addWidget(self.due_date_edit)

        self.reminder_checkbox = QCheckBox("Enable Reminder")
        add_task_layout.addWidget(self.reminder_checkbox)

        self.add_task_button = QPushButton("Add Task")
        self.add_task_button.clicked.connect(self.add_task)
        add_task_layout.addWidget(self.add_task_button)

        layout.addLayout(add_task_layout)

        # Filter and sort options
        filter_sort_layout = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "low", "medium", "high"])
        self.filter_combo.currentTextChanged.connect(self.load_tasks)
        filter_sort_layout.addWidget(self.filter_combo)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Due Date", "Priority"])
        self.sort_combo.currentTextChanged.connect(self.load_tasks)
        filter_sort_layout.addWidget(self.sort_combo)

        layout.addLayout(filter_sort_layout)

        # Edit and delete buttons
        button_layout = QHBoxLayout()
        self.edit_task_button = QPushButton("Edit Task")
        self.edit_task_button.clicked.connect(self.edit_task)
        button_layout.addWidget(self.edit_task_button)

        self.delete_task_button = QPushButton("Delete Task")
        self.delete_task_button.clicked.connect(self.delete_task)
        button_layout.addWidget(self.delete_task_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_tasks(self):
        """Fetch tasks from the backend and display them."""
        try:
            filter_priority = self.filter_combo.currentText()
            sort_by = self.sort_combo.currentText().lower().replace(" ", "_")

            response = requests.get(
                "http://127.0.0.1:8000/api/tasks/",
                params={"priority": filter_priority, "sort_by": sort_by},
            )
            if response.status_code == 200:
                tasks = response.json()
                self.task_list.clear()
                for task in tasks:
                    self.task_list.addItem(
                        f"{task['id']}: {task['title']} - Priority: {task['priority']} - Due: {task['due_date']}"
                    )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load tasks: {e}")

    def add_task(self):
        """Send a new task to the backend."""
        task_text = self.task_input.text()
        if task_text:
            try:
                due_date = self.due_date_edit.date().toString(Qt.ISODate)  # Get selected due date
                response = requests.post(
                    "http://127.0.0.1:8000/api/tasks/",
                    json={
                        "title": task_text,
                        "description": "",
                        "priority": self.priority_combo.currentText(),
                        "due_date": due_date + "T00:00:00Z",  # Add time to make it a valid datetime
                        "reminder_enabled": self.reminder_checkbox.isChecked(),
                    },
                )
                if response.status_code == 200:
                    self.load_tasks()  # Refresh the task list
                    self.task_input.clear()
                else:
                    QMessageBox.critical(self, "Error", f"Failed to add task: {response.text}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add task: {e}")

    def edit_task(self):
        """Edit the selected task."""
        selected_item = self.task_list.currentItem()
        if selected_item:
            task_id = selected_item.text().split(":")[0]
            task_title = selected_item.text().split(" - ")[0].split(": ")[1]

            new_title, ok = QInputDialog.getText(self, "Edit Task", "Enter new task title:", text=task_title)
            if ok and new_title:
                try:
                    due_date = self.due_date_edit.date().toString(Qt.ISODate)  # Get selected due date
                    response = requests.put(
                        f"http://127.0.0.1:8000/api/tasks/{task_id}",
                        json={
                            "title": new_title,
                            "description": "",
                            "priority": self.priority_combo.currentText(),
                            "due_date": due_date + "T00:00:00Z",  # Add time to make it a valid datetime
                            "reminder_enabled": self.reminder_checkbox.isChecked(),
                        },
                    )
                    if response.status_code == 200:
                        self.load_tasks()  # Refresh the task list
                    else:
                        QMessageBox.critical(self, "Error", f"Failed to edit task: {response.text}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to edit task: {e}")

    def delete_task(self):
        """Delete the selected task."""
        selected_item = self.task_list.currentItem()
        if selected_item:
            task_id = selected_item.text().split(":")[0]
            try:
                response = requests.delete(f"http://127.0.0.1:8000/api/tasks/{task_id}")
                if response.status_code == 200:
                    self.load_tasks()  # Refresh the task list
                else:
                    QMessageBox.critical(self, "Error", f"Failed to delete task: {response.text}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete task: {e}")