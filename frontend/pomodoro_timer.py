# frontend/pomodoro_timer.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer, Qt
import requests

class PomodoroTimer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.time_left = 25 * 60  # 25 minutes in seconds
        self.is_running = False
        self.session_id = None

    def init_ui(self):
        layout = QVBoxLayout()

        # Timer display
        self.timer_label = QLabel("25:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 48px; font-weight: bold;")
        layout.addWidget(self.timer_label)

        # Buttons
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_timer)
        layout.addWidget(self.start_button)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_timer)
        layout.addWidget(self.pause_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_timer)
        layout.addWidget(self.reset_button)

        self.setLayout(layout)

    def start_timer(self):
        if not self.is_running:
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/api/pomodoro/start",
                    json={"start_time": "2023-01-01T00:00:00"},  # Placeholder start time
                )
                if response.status_code == 200:
                    self.session_id = response.json().get("session_id")
                    self.timer.start(1000)  # Update every second
                    self.is_running = True
                    self.start_button.setEnabled(False)
                    self.pause_button.setEnabled(True)
            except Exception as e:
                print(f"Error starting Pomodoro session: {e}")

    def pause_timer(self):
        if self.is_running:
            self.timer.stop()
            self.is_running = False
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)

    def reset_timer(self):
        self.timer.stop()
        self.time_left = 25 * 60
        self.update_display()
        self.is_running = False
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.update_display()
        else:
            self.timer.stop()
            self.is_running = False
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.end_pomodoro_session()

    def update_display(self):
        minutes, seconds = divmod(self.time_left, 60)
        self.timer_label.setText(f"{minutes:02}:{seconds:02}")

    def end_pomodoro_session(self):
        if self.session_id:
            try:
                response = requests.post(
                    f"http://127.0.0.1:8000/api/pomodoro/end/{self.session_id}",
                    json={"end_time": "2023-01-01T00:25:00"},  # Placeholder end time
                )
                if response.status_code == 200:
                    print("Pomodoro session ended successfully.")
            except Exception as e:
                print(f"Error ending Pomodoro session: {e}")