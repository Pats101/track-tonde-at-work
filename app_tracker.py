import time
from datetime import datetime
import psutil
import json
import logging

class ApplicationTracker:
    def __init__(self):
        self.current_app = None
        self.start_time = None
        self.app_times = {}
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def get_active_window_process(self):
        """Get the process name of the currently active window."""
        try:
            # Get all processes with CPU and memory info
            processes = []
            for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.as_dict(['name', 'cpu_percent', 'memory_percent'])
                    if proc_info['cpu_percent'] > 0 or proc_info['memory_percent'] > 0:
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    self.logger.debug(f"Error accessing process: {e}")
                    continue
            
            if processes:
                # Sort by CPU usage first, then by memory usage
                active_process = sorted(processes, 
                                     key=lambda x: (x['cpu_percent'], x['memory_percent']),
                                     reverse=True)[0]
                self.logger.info(f"Active process: {active_process['name']} "
                               f"(CPU: {active_process['cpu_percent']}%, "
                               f"Memory: {active_process['memory_percent']}%)")
                return active_process['name']
            
            self.logger.warning("No active processes found")
            return "Unknown"
        except Exception as e:
            self.logger.error(f"Error in get_active_window_process: {e}")
            return "Unknown"
    
    def track(self):
        """Start tracking application usage."""
        print("Starting application tracking... Press Ctrl+C to stop.")
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
                        
                        # Update the time for the previous app
                        if self.current_app in self.app_times:
                            self.app_times[self.current_app] += duration
                        else:
                            self.app_times[self.current_app] = duration
                        
                        self.logger.info(f"Switched from {self.current_app} to {active_app} "
                                       f"(duration: {duration:.2f}s)")
                    
                    # Reset for new app
                    self.current_app = active_app
                    self.start_time = current_time
                
                time.sleep(1)  # Check every second
                
        except KeyboardInterrupt:
            # Make sure to account for the last active app
            if self.current_app is not None:
                duration = time.time() - self.start_time
                if self.current_app in self.app_times:
                    self.app_times[self.current_app] += duration
                else:
                    self.app_times[self.current_app] = duration
            
            self.save_data()
            self.display_summary()
    
    def save_data(self):
        """Save tracking data to a JSON file."""
        data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'app_times': {app: round(time_spent, 2) 
                         for app, time_spent in self.app_times.items()}
        }
        
        with open('app_usage.json', 'w') as f:
            json.dump(data, f, indent=4)
    
    def display_summary(self):
        """Display a summary of time spent on each application."""
        print("\nApplication Usage Summary:")
        print("-" * 40)
        
        for app, duration in sorted(self.app_times.items(), 
                                  key=lambda x: x[1], reverse=True):
            minutes = duration / 60
            print(f"{app}: {minutes:.2f} minutes")

if __name__ == "__main__":
    tracker = ApplicationTracker()
    tracker.track() 