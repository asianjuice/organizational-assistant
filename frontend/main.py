# frontend/main.py

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from task_dashboard import TaskDashboard
from pomodoro_timer import PomodoroTimer
from calendar_view import CalendarView

class OrganizationalAssistantApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Organizational Assistant")
        self.setGeometry(100, 100, 800, 600)

        # Create a tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Add tabs
        self.tabs.addTab(TaskDashboard(), "Tasks")
        self.tabs.addTab(PomodoroTimer(), "Pomodoro Timer")
        self.tabs.addTab(CalendarView(), "Calendar")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OrganizationalAssistantApp()
    window.show()
    sys.exit(app.exec_())