import pytest
import time
from time_tracker.tracker.utils import get_active_window_info
from time_tracker.tracker.application_tracker import ApplicationTracker
from time_tracker.data_handlers.storage import DataStorage
from pathlib import Path
import json
import threading

@pytest.fixture
def temp_data_dir(tmp_path):
    """
    Fixture to create a temporary data directory.
    
    Returns:
        Path: Path to temporary directory
    """
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()
    return data_dir

class TestIntegration:
    """Integration test suite for Time Tracker application."""
    
    @pytest.mark.integration
    def test_actual_window_info(self):
        """Test getting actual window information from the system."""
        # Get actual window info
        result = get_active_window_info()
        
        # Basic validation
        assert isinstance(result, str), "Window info should be a string"
        assert len(result) > 0, "Window info should not be empty"
        assert result != "Unknown", "Should get actual window info"
        
        # Format validation
        if "(" in result:
            process_name, window_title = result.split(" (", 1)
            assert window_title.endswith(")"), "Window title should be in parentheses"
            assert len(process_name) > 0, "Process name should not be empty"
            assert ".exe" in process_name.lower(), "Process name should include .exe"

    @pytest.mark.integration
    def test_multiple_window_calls(self):
        """Test multiple consecutive calls to get window information."""
        results = []
        for _ in range(5):
            results.append(get_active_window_info())
            time.sleep(0.1)  # Small delay between calls
        
        # Verify all results are valid
        assert all(isinstance(r, str) for r in results), \
            "All results should be strings"
        assert all(len(r) > 0 for r in results), \
            "All results should be non-empty"
        
        # Check for consistency or changes
        assert len(set(results)) >= 1, \
            "Should get at least one unique window"

    @pytest.mark.integration
    def test_full_tracking_cycle(self, temp_data_dir):
        """Test a complete tracking cycle with actual window tracking."""
        # Setup tracker with temporary storage
        storage = DataStorage(data_dir=temp_data_dir)
        tracker = ApplicationTracker(storage_handler=storage)
        
        # Use an event to control the thread
        stop_event = threading.Event()
        
        def run_tracker():
            try:
                while not stop_event.is_set():
                    active_app = get_active_window_info()
                    current_time = time.time()
                    tracker._handle_app_switch(active_app, current_time)
                    time.sleep(0.5)
            except Exception as e:
                pytest.fail(f"Tracker thread failed: {e}")
            finally:
                # Save data when stopping
                tracker._handle_final_app()
                tracker.storage.save_data(tracker.app_times)
        
        thread = threading.Thread(target=run_tracker)
        thread.start()
        
        try:
            # Let it run for a few seconds
            time.sleep(3)
        finally:
            # Clean shutdown
            stop_event.set()
            thread.join(timeout=1)
            
            if thread.is_alive():
                pytest.fail("Tracker thread did not stop cleanly")
        
        # Verify data was saved
        data_files = list(temp_data_dir.glob("app_usage_*.json"))
        assert len(data_files) == 1, "Should create exactly one data file"
        
        # Verify file content
        with open(data_files[0]) as f:
            data = json.load(f)
            assert "date" in data, "Should include date"
            assert "applications" in data, "Should include applications data"
            assert "total_tracking_time" in data, "Should include total time"
            assert float(data["total_tracking_time"]) > 0, "Should have tracked some time"

    @pytest.mark.integration
    def test_storage_integration(self, temp_data_dir):
        """Test storage integration with actual file system."""
        storage = DataStorage(data_dir=temp_data_dir)
        test_data = {"test_app.exe (Test Window)": 60.0}
        
        # Save data
        storage.save_data(test_data)
        
        # Verify file was created
        data_files = list(temp_data_dir.glob("app_usage_*.json"))
        assert len(data_files) == 1, "Should create exactly one data file"
        
        # Verify file content
        with open(data_files[0]) as f:
            data = json.load(f)
            assert data["total_tracking_time"] == 60.0, "Should save correct total time"
            assert "test_app.exe" in str(data["applications"]), "Should save application data" 