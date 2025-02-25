import json
from datetime import datetime
from pathlib import Path
from .formatters import group_application_data

class DataStorage:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
    
    def save_data(self, app_times):
        """Save tracking data to a JSON file."""
        current_date = datetime.now().strftime('%Y-%m-%d')
        filename = self.data_dir / f'app_usage_{current_date}.json'
        
        app_groups = group_application_data(app_times)
        
        data = {
            'date': current_date,
            'total_tracking_time': sum(app_times.values()),
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
    
    def display_summary(self, app_times):
        """Display a summary of time spent on each application."""
        print("\nApplication Usage Summary:")
        print("-" * 60)
        
        app_groups = group_application_data(app_times)
        
        for app_name, data in sorted(app_groups.items(), 
                                   key=lambda x: x[1]["total"], 
                                   reverse=True):
            total_minutes = data["total"] / 60
            print(f"\n{app_name}:")
            print(f"  Total time: {total_minutes:.2f} minutes")
            
            if data["windows"]:
                print("  Window breakdown:")
                for window, duration in sorted(data["windows"].items(), 
                                            key=lambda x: x[1], 
                                            reverse=True):
                    minutes = duration / 60
                    print(f"    - {window}: {minutes:.2f} minutes") 