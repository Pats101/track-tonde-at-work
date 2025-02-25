import time
from datetime import datetime
import psutil
import json
import logging
import win32gui
import win32process
from win32gui import GetWindowText, GetForegroundWindow

class ApplicationTracker:
    def __init__(self):
        self.current_app = None
        self.start_time = None
        self.app_times = {}
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def get_active_window_process(self):
        """Get the process name and window title of the currently active window."""
        try:
            # Get the foreground window handle
            window = GetForegroundWindow()
            window_title = GetWindowText(window)
            
            # Get the process ID from the window handle
            _, pid = win32process.GetWindowThreadProcessId(window)
            
            try:
                # Get process name using psutil
                process = psutil.Process(pid)
                process_name = process.name()
                
                # Log the detected window and process
                self.logger.info(f"Active Window: '{window_title}' - Process: {process_name}")
                
                # Only return non-system processes with window titles
                if window_title and process_name not in ['explorer.exe', 'MemCompression', 'System']:
                    return f"{process_name} ({window_title})"
                return process_name
                
            except psutil.NoSuchProcess:
                self.logger.warning(f"Could not find process with PID {pid}")
                return "Unknown"
                
        except Exception as e:
            self.logger.error(f"Error getting active window: {e}")
            return "Unknown"
    
    def track(self):
        """Start tracking application usage."""
        print("Starting application tracking... Press Ctrl+C to stop.")
        print("Tracking active windows... (Press Ctrl+C to stop)")
        self.start_time = time.time()
        
        try:
            while True:
                active_app = self.get_active_window_process()
                current_time = time.time()
                
                # If this is a new app or we're just starting
                if active_app != self.current_app:
                    if self.current_app is not None:
                        # Calculate time spent on previous app
                        duration = current_time - self.start_time
                        
                        # Only log if duration is more than 1 second
                        if duration > 1:
                            if self.current_app in self.app_times:
                                self.app_times[self.current_app] += duration
                            else:
                                self.app_times[self.current_app] = duration
                            
                            self.logger.info(f"Switched from '{self.current_app}' to '{active_app}' "
                                           f"(duration: {duration:.2f}s)")
                    
                    # Reset for new app
                    self.current_app = active_app
                    self.start_time = current_time
                
                time.sleep(0.5)  # Check every half second
                
        except KeyboardInterrupt:
            # Make sure to account for the last active app
            if self.current_app is not None:
                duration = time.time() - self.start_time
                if duration > 1:  # Only log if duration is more than 1 second
                    if self.current_app in self.app_times:
                        self.app_times[self.current_app] += duration
                    else:
                        self.app_times[self.current_app] = duration
            
            self.save_data()
            self.display_summary()
    
    def save_data(self):
        """Save tracking data to a JSON file."""
        current_date = datetime.now().strftime('%Y-%m-%d')
        filename = f'app_usage_{current_date}.json'
        
        # Group by application
        app_groups = {}
        for app_window, duration in self.app_times.items():
            app_name = app_window.split(" (")[0]
            window_title = app_window.split(" (")[1][:-1] if " (" in app_window else ""
            
            if app_name not in app_groups:
                app_groups[app_name] = {"total": 0, "windows": {}}
            
            app_groups[app_name]["total"] += duration
            if window_title:
                app_groups[app_name]["windows"][window_title] = duration
        
        data = {
            'date': current_date,
            'total_tracking_time': sum(self.app_times.values()),
            'applications': {
                app_name: {
                    'total_time': round(data["total"], 2),
                    'windows': {
                        window: round(duration, 2)
                        for window, duration in data["windows"].items()
                    }
                }
                for app_name, data in app_groups.items()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"\nData saved to {filename}")
    
    def display_summary(self):
        """Display a summary of time spent on each application."""
        print("\nApplication Usage Summary:")
        print("-" * 60)
        
        # Group by application
        app_groups = {}
        for app_window, duration in self.app_times.items():
            app_name = app_window.split(" (")[0]
            window_title = app_window.split(" (")[1][:-1] if " (" in app_window else ""
            
            if app_name not in app_groups:
                app_groups[app_name] = {"total": 0, "windows": {}}
            
            app_groups[app_name]["total"] += duration
            if window_title:
                app_groups[app_name]["windows"][window_title] = duration
        
        # Display grouped summary
        for app_name, data in sorted(app_groups.items(), key=lambda x: x[1]["total"], reverse=True):
            total_minutes = data["total"] / 60
            print(f"\n{app_name}:")
            print(f"  Total time: {total_minutes:.2f} minutes")
            
            if data["windows"]:
                print("  Window breakdown:")
                for window, duration in sorted(data["windows"].items(), key=lambda x: x[1], reverse=True):
                    minutes = duration / 60
                    print(f"    - {window}: {minutes:.2f} minutes")

if __name__ == "__main__":
    tracker = ApplicationTracker()
    tracker.track() 