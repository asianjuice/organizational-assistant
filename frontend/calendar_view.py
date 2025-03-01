# frontend/calendar_view.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCalendarWidget, QLabel
from PyQt5.QtCore import Qt
import requests

class CalendarView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Calendar widget
        self.calendar = QCalendarWidget()
        layout.addWidget(self.calendar)

        # Event display
        self.event_label = QLabel("No events for selected date.")
        self.event_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.event_label)

        # Connect calendar selection change to update events
        self.calendar.selectionChanged.connect(self.update_events)

        self.setLayout(layout)

    def update_events(self):
        selected_date = self.calendar.selectedDate().toString(Qt.ISODate)
        try:
            response = requests.post(
                "http://127.0.0.1:8000/api/calendar/events",
                json={
                    "start_time": f"{selected_date}T00:00:00",
                    "end_time": f"{selected_date}T23:59:59",
                },
            )
            if response.status_code == 200:
                events = response.json().get("events", [])
                if events:
                    self.event_label.setText(f"Events for {selected_date}: {len(events)}")
                else:
                    self.event_label.setText(f"No events for {selected_date}.")
        except Exception as e:
            print(f"Error fetching events: {e}")