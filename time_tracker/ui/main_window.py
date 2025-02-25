from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QSystemTrayIcon, QMenu, QStyle
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from ..tracker.application_tracker import ApplicationTracker
from ..data_handlers.storage import DataStorage

class TimeTrackerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tracker = ApplicationTracker()
        self.timer = QTimer()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main window UI."""
        self.setWindowTitle("Time Tracker")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add controls
        controls_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Tracking")
        self.start_button.clicked.connect(self.start_tracking)
        controls_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Tracking")
        self.stop_button.clicked.connect(self.stop_tracking)
        self.stop_button.setEnabled(False)
        controls_layout.addWidget(self.stop_button)
        
        layout.addLayout(controls_layout)
        
        # Add table for displaying results
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Application", "Window", "Time (min)"])
        layout.addWidget(self.table)
        
        # Setup system tray
        self.setup_system_tray()
        
        # Setup update timer
        self.timer.timeout.connect(self.update_display)
        self.timer.setInterval(1000)  # Update every second
        
    def setup_system_tray(self):
        """Setup system tray icon and menu."""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        
        # Create tray menu
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_application)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def start_tracking(self):
        """Start tracking application usage."""
        self.tracker = ApplicationTracker()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.timer.start()
        
    def stop_tracking(self):
        """Stop tracking and save results."""
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.tracker.storage.save_data(self.tracker.app_times)
        self.update_display()
        
    def update_display(self):
        """Update the display with current tracking data."""
        self.table.setRowCount(0)
        for app, duration in self.tracker.app_times.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            if " (" in app:
                app_name, window = app.split(" (", 1)
                window = window.rstrip(")")
            else:
                app_name, window = app, ""
            
            self.table.setItem(row, 0, QTableWidgetItem(app_name))
            self.table.setItem(row, 1, QTableWidgetItem(window))
            self.table.setItem(row, 2, QTableWidgetItem(f"{duration/60:.1f}"))
            
    def quit_application(self):
        """Quit the application."""
        if self.tracker.app_times:
            self.stop_tracking()
        self.close() 