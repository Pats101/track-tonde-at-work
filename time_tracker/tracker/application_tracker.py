import time
from datetime import datetime
import logging
from ..data_handlers.storage import DataStorage
from .utils import get_active_window_info

class ApplicationTracker:
    def __init__(self, storage_handler=None):
        self.current_app = None
        self.start_time = None
        self.app_times = {}
        self.storage = storage_handler or DataStorage()
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def track(self):
        """Start tracking application usage."""
        print("Starting application tracking... Press Ctrl+C to stop.")
        print("Tracking active windows... (Press Ctrl+C to stop)")
        self.start_time = time.time()
        
        try:
            while True:
                active_app = get_active_window_info()
                current_time = time.time()
                
                self._handle_app_switch(active_app, current_time)
                time.sleep(0.5)  # Check every half second
                
        except KeyboardInterrupt:
            self._handle_final_app()
            self.storage.save_data(self.app_times)
            self.storage.display_summary(self.app_times)
    
    def _handle_app_switch(self, active_app, current_time):
        """Handle switching between applications."""
        if active_app != self.current_app:
            if self.current_app is not None:
                duration = current_time - self.start_time
                
                if duration > 1:  # Only log if duration is more than 1 second
                    self._update_app_time(self.current_app, duration)
                    self.logger.info(
                        f"Switched from '{self.current_app}' to '{active_app}' "
                        f"(duration: {duration:.2f}s)"
                    )
            
            self.current_app = active_app
            self.start_time = current_time
    
    def _handle_final_app(self):
        """Handle the final application when stopping tracking."""
        if self.current_app is not None:
            duration = time.time() - self.start_time
            if duration > 1:
                self._update_app_time(self.current_app, duration)
    
    def _update_app_time(self, app, duration):
        """Update the time spent on an application."""
        # Only log if duration is more than 1 second
        if duration >= 1.0:
            if app in self.app_times:
                self.app_times[app] += duration
            else:
                self.app_times[app] = duration 