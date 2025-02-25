from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QSystemTrayIcon, QMenu, QStyle, QTabWidget, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QRectF, QMargins
from PyQt6.QtGui import QIcon, QPalette, QColor, QPainter, QFont
from PyQt6.QtCharts import (
    QChart, QChartView, QPieSeries, QBarSeries, QBarSet, 
    QBarCategoryAxis, QValueAxis, QPieSlice
)
from PyQt6.QtWidgets import QGraphicsScene
from ..tracker.application_tracker import ApplicationTracker
from ..tracker.utils import get_active_window_info
from ..data_handlers.storage import DataStorage
from .styles import DARK_THEME
import time

class TimeTrackerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tracker = ApplicationTracker()
        self.timer = QTimer()
        self.tracking = False
        self.start_time = None
        self.current_app = None
        self.setup_ui()
        self.setStyleSheet(DARK_THEME)
        
    def setup_ui(self):
        """Setup the main window UI."""
        self.setWindowTitle("Time Tracker")
        self.setMinimumSize(1000, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add title and author
        title_layout = QHBoxLayout()
        title_label = QLabel("Time Tracker Pro")
        title_label.setObjectName("titleLabel")
        author_label = QLabel("by Patrick Tonderai Ganhiwa")
        author_label.setObjectName("authorLabel")
        title_layout.addWidget(title_label)
        title_layout.addWidget(author_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Add status label
        self.status_label = QLabel("Not tracking")
        layout.addWidget(self.status_label)
        
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
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Table tab
        table_tab = QWidget()
        table_layout = QVBoxLayout(table_tab)
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Application", "Window", "Time (min)"])
        self.table.horizontalHeader().setStretchLastSection(True)
        table_layout.addWidget(self.table)
        tab_widget.addTab(table_tab, "Details")
        
        # Charts tab
        charts_tab = QWidget()
        charts_layout = QHBoxLayout(charts_tab)
        
        # Pie chart setup
        pie_container = QWidget()
        pie_layout = QVBoxLayout(pie_container)
        
        self.pie_chart = QChart()
        self.pie_chart.setTitle("Application Usage Distribution")
        self.pie_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.pie_chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        self.pie_chart.setBackgroundVisible(False)
        self.pie_chart.legend().setVisible(True)
        self.pie_chart.legend().setAlignment(Qt.AlignmentFlag.AlignRight)
        
        pie_view = QChartView(self.pie_chart)
        pie_view.setRenderHints(QPainter.RenderHint.Antialiasing | 
                               QPainter.RenderHint.TextAntialiasing |
                               QPainter.RenderHint.SmoothPixmapTransform)
        pie_view.setMinimumSize(400, 300)
        pie_layout.addWidget(pie_view)
        
        # Create placeholder for pie chart
        self.pie_placeholder = QLabel("No data available\nStart tracking to see statistics")
        self.pie_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pie_placeholder.setStyleSheet("color: white; font-size: 12px;")
        pie_layout.addWidget(self.pie_placeholder)
        self.pie_placeholder.hide()
        
        charts_layout.addWidget(pie_container)
        
        # Bar chart setup
        bar_container = QWidget()
        bar_layout = QVBoxLayout(bar_container)
        
        self.bar_chart = QChart()
        self.bar_chart.setTitle("Top Applications by Time")
        self.bar_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.bar_chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        self.bar_chart.setBackgroundVisible(False)
        self.bar_chart.setMargins(QMargins(10, 10, 10, 10))
        self.bar_chart.legend().setVisible(True)
        self.bar_chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        bar_view = QChartView(self.bar_chart)
        bar_view.setRenderHints(QPainter.RenderHint.Antialiasing | 
                               QPainter.RenderHint.TextAntialiasing |
                               QPainter.RenderHint.SmoothPixmapTransform)
        bar_view.setMinimumSize(400, 300)
        bar_layout.addWidget(bar_view)
        
        # Create placeholder for bar chart
        self.bar_placeholder = QLabel("No data available\nStart tracking to see statistics")
        self.bar_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bar_placeholder.setStyleSheet("color: white; font-size: 12px;")
        bar_layout.addWidget(self.bar_placeholder)
        self.bar_placeholder.hide()
        
        charts_layout.addWidget(bar_container)
        
        # Add charts tab
        tab_widget.addTab(charts_tab, "Charts")
        
        # Statistics tab with better formatting
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        self.stats_label = QLabel()
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.stats_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                padding: 20px;
                background-color: #1e1e1e;
                border-radius: 10px;
            }
        """)
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        tab_widget.addTab(stats_tab, "Statistics")
        
        layout.addWidget(tab_widget)
        
        # Setup system tray
        self.setup_system_tray()
        
        # Setup update timer
        self.timer.timeout.connect(self.track_current_app)
        self.timer.setInterval(500)
        
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
        self.tracking = True
        self.start_time = time.time()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Tracking active...")
        self.timer.start()
        
    def stop_tracking(self):
        """Stop tracking and save results."""
        self.tracking = False
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Tracking stopped")
        
        # Handle final app
        if self.current_app:
            duration = time.time() - self.start_time
            if duration > 1:
                self.tracker._update_app_time(self.current_app, duration)
        
        # Save data
        self.tracker.storage.save_data(self.tracker.app_times)
        self.update_display()
        
    def track_current_app(self):
        """Track the current active application."""
        if not self.tracking:
            return
            
        current_time = time.time()
        active_app = get_active_window_info()
        
        if active_app != self.current_app:
            if self.current_app is not None:
                duration = current_time - self.start_time
                if duration > 1:
                    self.tracker._update_app_time(self.current_app, duration)
            
            self.current_app = active_app
            self.start_time = current_time
            
        self.update_display()
        
    def update_charts(self):
        """Update the charts with current data."""
        if not self.tracker.app_times:
            self.pie_chart.removeAllSeries()
            self.bar_chart.removeAllSeries()
            self.pie_placeholder.show()
            self.bar_placeholder.show()
            return
            
        self.pie_placeholder.hide()
        self.bar_placeholder.hide()
        
        # Update pie chart
        pie_series = QPieSeries()
        total_time = sum(self.tracker.app_times.values())
        
        for app, duration in self.tracker.app_times.items():
            app_name = app.split(" (")[0]
            percentage = (duration / total_time) * 100
            slice = pie_series.append(app_name, duration/60)  # Convert to minutes
            slice.setLabelVisible(True)
            slice.setLabel(f"{app_name}\n{percentage:.1f}%")
            slice.setLabelPosition(QPieSlice.LabelPosition.LabelOutside)
            slice.setExploded(True)
            slice.setExplodeDistanceFactor(0.1)
        
        self.pie_chart.removeAllSeries()
        self.pie_chart.addSeries(pie_series)
        
        # Update bar chart
        self.bar_chart.removeAllSeries()
        
        # Create and configure axes first
        axis_x = QBarCategoryAxis()
        axis_y = QValueAxis()
        axis_y.setTitleText("Minutes")
        
        # Add axes to chart first
        self.bar_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        self.bar_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        
        bar_series = QBarSeries()
        bar_set = QBarSet("Duration (minutes)")
        
        # Get top 5 apps
        sorted_apps = sorted(
            self.tracker.app_times.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        if not sorted_apps:  # Check if we have any data
            return
            
        categories = []
        for app, duration in sorted_apps:
            app_name = app.split(" (")[0]
            categories.append(app_name)
            bar_set.append(duration / 60)  # Convert to minutes
        
        # Update axis categories
        axis_x.append(categories)
        
        # Set y-axis range
        max_value = max(bar_set) if len(bar_set) > 0 else 0
        axis_y.setRange(0, max_value * 1.1 if max_value > 0 else 10)
        
        # Add series and attach axes
        bar_series.append(bar_set)
        self.bar_chart.addSeries(bar_series)
        bar_series.attachAxis(axis_x)
        bar_series.attachAxis(axis_y)
        
        self.bar_chart.legend().setVisible(True)
        self.bar_chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
    def update_statistics(self):
        """Update the statistics display."""
        if not self.tracker.app_times:
            self.stats_label.setText("No data available")
            return
            
        total_time = sum(self.tracker.app_times.values())
        app_count = len(self.tracker.app_times)
        avg_time = total_time / app_count if app_count > 0 else 0
        
        stats_text = f"""
        <h2>Session Statistics</h2>
        <p><b>Total Tracking Time:</b> {total_time/60:.1f} minutes</p>
        <p><b>Applications Tracked:</b> {app_count}</p>
        <p><b>Average Time per App:</b> {avg_time/60:.1f} minutes</p>
        <p><b>Most Used App:</b> {max(self.tracker.app_times.items(), key=lambda x: x[1])[0]}</p>
        """
        self.stats_label.setText(stats_text)
        
    def update_display(self):
        """Update all displays."""
        # Update table
        self.table.setRowCount(0)
        sorted_apps = sorted(
            self.tracker.app_times.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for app, duration in sorted_apps:
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
        
        self.table.resizeColumnsToContents()
        
        # Update charts and statistics
        self.update_charts()
        self.update_statistics()
        
    def quit_application(self):
        """Quit the application."""
        if self.tracking:
            self.stop_tracking()
        self.close()
        
    def closeEvent(self, event):
        """Handle application closing."""
        if self.tracking:
            self.stop_tracking()
        event.accept()