from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
import sys
import json
from datetime import datetime, timedelta, date
from collections import defaultdict
import os
import os.path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd

def nested_defaultdict():
    return defaultdict(nested_defaultdict)

# Get the script directory
if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)
else:
    script_dir = os.path.dirname(os.path.realpath(__file__))

class PomodoroWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load configuration from file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(script_dir, "config.json")
        self.load_config()

        self.pomodoro_minutes = self.pomodoro_minutes_initial
        self.pomodoro_seconds = self.pomodoro_seconds_initial
        self.break_minutes = self.break_minutes_initial
        self.break_seconds = self.break_seconds_initial

        # ...

        # Set up the window
        self.setWindowTitle("Pomodoro Timer")
        self.setFixedSize(300, 250)

        # Create the widgets
        # Remove this line: self.timer_label = QLabel("{:02d}:{:02d}".format(self.pomodoro_minutes, self.pomodoro_seconds))

        self.counter_label = QLabel("Pomodoros completed: 0")
        self.start_button = QPushButton("Start")
        self.reset_button = QPushButton("Reset")
        self.Menu_button = QPushButton("Menu")

        # ...

        self.timer_dial = QDial()
        self.timer_dial.setRange(
            0, (self.pomodoro_minutes_initial * 60) + self.pomodoro_seconds_initial)
        self.timer_dial.setValue(self.timer_dial.maximum())
        self.timer_dial.setFixedSize(150, 150)
        self.timer_dial.setNotchesVisible(True)

        # Keep this line
        self.timer_label = QLabel("{:02d}:{:02d}".format(
            self.pomodoro_minutes, self.pomodoro_seconds), self.timer_dial)
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setGeometry(QRect(0, 55, 150, 40))

        # Set up the stylesheet for the timer label
        self.timer_label.setStyleSheet(
            "QLabel { font-weight: bold; font-size: 24px; color: #3a3a3a; }")

        # ...

        # Set up the layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Replace self.timer_label with self.timer_dial
        layout.addWidget(self.timer_dial, alignment=Qt.AlignCenter)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.Menu_button)

        layout.addLayout(buttons_layout)
        layout.addWidget(self.counter_label)

        # Set up the timer
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_timer)

        # Connect the button signals
        self.start_button.clicked.connect(self.start_timer)
        self.reset_button.clicked.connect(self.reset_timer)
        self.Menu_button.clicked.connect(self.show_Menu_dialog)

        # Initialize the timer state
        self.timer_running = False
        self.pomodoro_counter = 0
        self.is_break_time = False
        self.pomo_start_time = None  # Add this line to initialize the variable

        # Set up the system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        icon_file_path = os.path.join(script_dir, "icon.jpg")
        self.tray_icon.setIcon(QIcon(icon_file_path))

        self.pomodoro_times = []


    def load_config(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(script_dir, "config.json")

        if not os.path.exists(config_file_path):
            default_config = {
                "pomodoro_minutes": 25,
                "pomodoro_seconds": 0,
                "break_minutes": 5,
                "break_seconds": 0,
                "auto_start": False
            }
            with open(config_file_path, "w") as f:
                json.dump(default_config, f)

        with open(config_file_path) as f:
            config = json.load(f)
            self.pomodoro_minutes_initial = config.get("pomodoro_minutes", 25)
            self.pomodoro_seconds_initial = config.get("pomodoro_seconds", 0)
            self.break_minutes_initial = config.get("break_minutes", 5)
            self.break_seconds_initial = config.get("break_seconds", 0)
            self.auto_start = config.get("auto_start", False)


    def save_config(self):
        # Save configuration to file
        config = {
            "pomodoro_minutes": self.pomodoro_minutes_initial,
            "pomodoro_seconds": self.pomodoro_seconds_initial,
            "break_minutes": self.break_minutes_initial,
            "break_seconds": self.break_seconds_initial,
            "auto_start": self.auto_start
        }
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(script_dir, "config.json")
        with open(config_file_path, "w") as f:
            json.dump(config, f)

    # ... (other methods are unchanged)

    def nested_defaultdict():
        return defaultdict(nested_defaultdict)
    
    stats_file_path = os.path.join(script_dir, "stats.txt")
    if os.path.exists(stats_file_path):
        with open("stats.txt", "r") as f:
            all_stats = json.load(f)
    else:
        all_stats = nested_defaultdict()

    def save_stats(self):
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day
        week = now.strftime("%U")

        # Load existing stats if the file exists
        stats_file_path = os.path.join(script_dir, "stats.txt")
        if os.path.exists(stats_file_path):
            with open("stats.txt", "r") as f:
                all_stats = json.load(f)
        else:
            all_stats = {}

        # Ensure the nested dictionaries are initialized
        if str(year) not in all_stats:
            all_stats[str(year)] = {}
        if str(month) not in all_stats[str(year)]:
            all_stats[str(year)][str(month)] = {}
        if str(day) not in all_stats[str(year)][str(month)]:
            all_stats[str(year)][str(month)][str(day)] = []

        # Save today's Pomodoro
        all_stats[str(year)][str(month)][str(day)].append(
            (self.pomo_start_time.strftime('%I:%M %p'), datetime.now().strftime('%I:%M %p')))

        # Increment the counter
        self.pomodoro_counter += 1
        self.counter_label.setText(
            f"Pomodoros completed: {self.pomodoro_counter}")

        # Save the updated stats
        with open("stats.txt", "w") as f:
            json.dump(all_stats, f, indent=4)

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.timer.start()
            self.start_button.setText("Stop")
            # Add this line to store the start time of the Pomodoro
            self.pomo_start_time = datetime.now()
        else:
            self.timer.stop()
            self.timer_running = False
            self.start_button.setText("Start")

    def start_auto_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.timer.start()

    def reset_timer(self):
        self.timer_running = False
        self.timer.stop()
        self.start_button.setText("Start")
        self.pomodoro_minutes = self.pomodoro_minutes_initial
        self.pomodoro_seconds = self.pomodoro_seconds_initial
        self.is_break_time = False
        self.update_timer()
        timer_type = "Break" if self.is_break_time else "Pomo"
        self.timer_label.setText(
            f"{timer_type} {self.pomodoro_minutes:02d}:{self.pomodoro_seconds:02d}")
        # Update the timer dial
        self.timer_dial.setValue(
            (self.pomodoro_minutes * 60) + self.pomodoro_seconds)
        self.save_config()

        self.pomodoro_times = []
        self.save_config()

    def update_timer(self):
        if self.timer_running:
            if not self.is_break_time:
                self.pomodoro_seconds -= 1
                if self.pomodoro_seconds < 0:
                    self.pomodoro_seconds = 59
                    self.pomodoro_minutes -= 1
                    if self.pomodoro_minutes < 0:
                        # Save statistics after the Pomodoro is finished
                        if self.pomo_start_time is not None:
                            self.pomodoro_times.append(
                                (self.pomo_start_time, datetime.now()))
                            self.save_stats()
                            self.pomo_start_time = None  # Reset the start time
                        if not self.is_break_time:
                            self.is_break_time = True
                            self.pomodoro_minutes = self.break_minutes_initial
                            self.pomodoro_seconds = self.break_seconds_initial
                            self.show_notification(
                                "Pomodoro session finished. Take a break!")

                            if self.auto_start:
                                self.start_auto_timer()
                            else:
                                self.timer.stop()
                                self.timer_running = False
                                self.start_button.setText("Start")
            else:
                self.pomodoro_seconds -= 1
                if self.pomodoro_seconds < 0:
                    self.pomodoro_seconds = 59
                    self.pomodoro_minutes -= 1
                    if self.pomodoro_minutes < 0:
                        self.is_break_time = False
                        self.pomodoro_minutes = self.pomodoro_minutes_initial
                        self.pomodoro_seconds = self.pomodoro_seconds_initial
                        self.show_notification(
                            "Break finished. Start a new Pomodoro session.")
                        # Update the start time for the new Pomodoro
                        self.pomo_start_time = datetime.now()
                        if self.auto_start:
                            self.start_auto_timer()

                        else:
                            self.timer.stop()
                            self.timer_running = False
                            self.start_button.setText("Start")
            timer_type = "Break" if self.is_break_time else "Pomo"
            self.timer_label.setText(
                f"{timer_type} {self.pomodoro_minutes:02d}:{self.pomodoro_seconds:02d}")
            # Update the timer dial
            self.timer_dial.setValue(
                (self.pomodoro_minutes * 60) + self.pomodoro_seconds)

    def show_notification(self, message):
        self.play_notification_sound()
        self.tray_icon.show()
        self.tray_icon.showMessage(
            "Pomodoro Timer", message, QSystemTrayIcon.Information, 5000)

        
    def play_notification_sound(self):
        self.media_player = QMediaPlayer()
        sound_file_path = os.path.join(script_dir, "notification.mp3")
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(sound_file_path)))
        self.media_player.play()


    def show_Menu_dialog(self):
        dialog = MenuDialog(
            self.pomodoro_minutes_initial, self.pomodoro_seconds_initial,
            self.break_minutes_initial, self.break_seconds_initial,
            self.auto_start
        )
        if dialog.exec_():
            (
                self.pomodoro_minutes_initial, self.pomodoro_seconds_initial,
                self.break_minutes_initial, self.break_seconds_initial,
                self.auto_start
            ) = dialog.get_values()
            self.pomodoro_times = []
            self.reset_timer()
            self.save_config()


class MenuDialog(QDialog):
    def __init__(self, pomodoro_minutes, pomodoro_seconds, break_minutes, break_seconds, auto_start):
        super().__init__()

        # Set up the dialog
        self.setWindowTitle("Menu")
        self.setFixedSize(300, 350)

        # Create the widgets
        self.minutes_label = QLabel("Pomodoro Minutes:")
        self.minutes_spinbox = QSpinBox()
        self.minutes_spinbox.setRange(1, 60)
        self.minutes_spinbox.setValue(pomodoro_minutes)

        self.seconds_label = QLabel("Pomodoro Seconds:")
        self.seconds_spinbox = QSpinBox()
        self.seconds_spinbox.setRange(0, 59)
        self.seconds_spinbox.setValue(pomodoro_seconds)

        self.break_minutes_label = QLabel("Break Minutes:")
        self.break_minutes_spinbox = QSpinBox()
        self.break_minutes_spinbox.setRange(1, 60)
        self.break_minutes_spinbox.setValue(break_minutes)

        self.break_seconds_label = QLabel("Break Seconds:")
        self.break_seconds_spinbox = QSpinBox()
        self.break_seconds_spinbox.setRange(0, 59)
        self.break_seconds_spinbox.setValue(break_seconds)

        self.auto_start_checkbox = QCheckBox("Auto-start next timer")
        self.auto_start_checkbox.setChecked(auto_start)

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        self.stats_button = QPushButton("View Stats")
        self.about_button = QPushButton("About")

        # Set up the layout
        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(self.minutes_label, 0, 0)
        layout.addWidget(self.minutes_spinbox, 0, 1)

        layout.addWidget(self.seconds_label, 1, 0)
        layout.addWidget(self.seconds_spinbox, 1, 1)

        layout.addWidget(self.break_minutes_label, 2, 0)
        layout.addWidget(self.break_minutes_spinbox, 2, 1)

        layout.addWidget(self.break_seconds_label, 3, 0)
        layout.addWidget(self.break_seconds_spinbox, 3, 1)

        layout.addWidget(self.auto_start_checkbox, 4, 0, 1, 2)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout, 5, 1)

        layout.addWidget(self.stats_button, 6, 0, 1, 2)
        layout.addWidget(self.about_button, 9, 0, 1, 2)

        self.stats_range_combobox = QComboBox()
        self.stats_range_combobox.addItem("Last 7 days")
        self.stats_range_combobox.addItem("Weekly")
        self.stats_range_combobox.addItem("Monthly")

        layout.addWidget(self.stats_range_combobox, 8, 0, 1, 2)

        # Connect the button signals
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self.stats_button.clicked.connect(self.show_stats)
        self.about_button.clicked.connect(self.show_about)

    def get_values(self):
        return (
            self.minutes_spinbox.value(), self.seconds_spinbox.value(),
            self.break_minutes_spinbox.value(), self.break_seconds_spinbox.value(),
            self.auto_start_checkbox.isChecked()
        )

    def show_about(self):
        about_text = "MyPomoApp\n\n"
        about_text += "Developed by ELHoumaini Karim\n"
        about_text += "Email: elhoumaini.ka@gmail.com\n"
        about_text += "Linkden: linkedin.com/in/karim-elhoumaini/"

        QMessageBox.information(self, "About", about_text)

    def show_stats(self):
        # Load data from stats.txt
        stats_file_path = os.path.join(script_dir, "stats.txt")
        data = {}  # Initialize data as an empty dictionary
        if os.path.exists(stats_file_path):
            with open("stats.txt", "r") as file:
                data = json.load(file)
        # print("Data loaded from stats.txt:", data)  # Add this line

        # Process data
        daily_pomos = {}
        for year, months in data.items():
            for month, days in months.items():
                for day, pomos in days.items():
                    date_str = f"{year}-{month}-{day}"
                    daily_pomos[date_str] = len(pomos)

        # Filter last 7 days
        selected_option = self.stats_range_combobox.currentText()
        days_and_counts = {}
        if selected_option == "Last 7 days":
            today = date.today()
            days_and_counts = {
                date_str: count for date_str, count in daily_pomos.items()
                if today - timedelta(days=7) <= datetime.strptime(date_str, '%Y-%m-%d').date() <= today
            }
        elif selected_option == "Weekly":
            # Group the data by week
            df = pd.DataFrame(list(daily_pomos.items()),
                              columns=['Date', 'Count'])
            df['Date'] = pd.to_datetime(df['Date'])
            df['Week'] = df['Date'].dt.to_period(
                'W').apply(lambda r: r.start_time)
            weekly_pomos = df.groupby('Week').sum(numeric_only=True)

            days = weekly_pomos.index.strftime('%Y-%m-%d')
            pomo_counts = weekly_pomos['Count'].values
            days_and_counts = dict(zip(days, pomo_counts))

        elif selected_option == "Monthly":
            # Group the data by month
            df = pd.DataFrame(list(daily_pomos.items()),
                              columns=['Date', 'Count'])
            df['Date'] = pd.to_datetime(df['Date'])
            df['Month'] = df['Date'].dt.to_period(
                'M').apply(lambda r: r.start_time)
            monthly_pomos = df.groupby('Month').sum(numeric_only=True)

            days = monthly_pomos.index.strftime('%Y-%m')
            pomo_counts = monthly_pomos['Count'].values
            days_and_counts = dict(zip(days, pomo_counts))

        days = list(days_and_counts.keys())
        pomo_counts = list(days_and_counts.values())

        # Plot data
        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(1, 1, 1)

        ax.barh(days, pomo_counts, height=0.5)
        ax.set_xlabel("Number of Pomos")
        ax.set_ylabel("Date")

        # Set the title based on the selected option
        if selected_option == "Last 7 days":
            ax.set_title("Daily Pomo Count for Last 7 Days")
        elif selected_option == "Weekly":
            ax.set_title("Weekly Pomo Count")
        elif selected_option == "Monthly":
            ax.set_title("Monthly Pomo Count")

        # Calculate the maximum value for the x-axis limit
        max_pomo_count = max(pomo_counts) + 5
        ax.set_xticks(range(0, max_pomo_count, max(1, max_pomo_count // 10)))

        plt.tight_layout()

        # Show the figure in a QDialog
        stats_dialog = QDialog(self)
        stats_dialog.setWindowTitle("Pomo Stats")
        stats_dialog.setFixedSize(600, 420)

        layout = QVBoxLayout()
        stats_dialog.setLayout(layout)

        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)

        stats_dialog.exec_()


if __name__ == "__main__":
    app = QApplication([])
    window = PomodoroWindow()
    window.show()
    app.exec_()
