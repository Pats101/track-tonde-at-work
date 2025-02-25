import pytest
from unittest.mock import Mock, patch
from time_tracker.tracker.application_tracker import ApplicationTracker
import time

# Constants for testing
TEST_APP_NAME = "test_app.exe"
TEST_WINDOW_TITLE = "Test Window"
TEST_DURATION = 5.0

@pytest.fixture
def mock_storage():
    """
    Fixture to create a mock storage handler.
    
    Returns:
        Mock: Mocked storage handler with save_data and display_summary methods
    """
    storage = Mock()
    storage.save_data = Mock()
    storage.display_summary = Mock()
    return storage

@pytest.fixture
def tracker(mock_storage):
    """
    Fixture to create an ApplicationTracker instance with mocked storage.
    
    Args:
        mock_storage: The mocked storage handler from mock_storage fixture
    
    Returns:
        ApplicationTracker: Configured tracker instance for testing
    """
    return ApplicationTracker(storage_handler=mock_storage)

class TestApplicationTracker:
    """Test suite for ApplicationTracker functionality."""
    
    def test_initialization(self, tracker):
        """Verify tracker initializes with correct default values."""
        assert tracker.current_app is None, "Current app should be None initially"
        assert tracker.start_time is None, "Start time should be None initially"
        assert tracker.app_times == {}, "App times should be empty initially"
    
    @pytest.mark.parametrize("duration,should_log", [
        (0.5, False),  # Too short, shouldn't log
        (1.5, True),   # Long enough, should log
        (10.0, True),  # Definitely long enough
    ])
    def test_update_app_time(self, tracker, duration, should_log):
        """Test updating application time with various durations."""
        app_name = TEST_APP_NAME
        
        # Update time for the first time
        tracker._update_app_time(app_name, duration)
        
        if should_log:
            assert app_name in tracker.app_times, \
                f"App should be logged for duration {duration}"
            assert tracker.app_times[app_name] == duration, \
                f"Duration should be exactly {duration}"
        else:
            assert app_name not in tracker.app_times, \
                f"App should not be logged for duration {duration}"
    
    @patch('time.time')
    def test_handle_app_switch(self, mock_time, tracker):
        """Test handling of application switching."""
        # Setup initial state
        mock_time.return_value = 100.0
        tracker.current_app = TEST_APP_NAME
        tracker.start_time = 95.0  # 5 seconds ago
        
        # Switch to new app
        new_app = "new_app.exe"
        tracker._handle_app_switch(new_app, 100.0)
        
        assert tracker.current_app == new_app, \
            "Current app should be updated to new app"
        assert tracker.start_time == 100.0, \
            "Start time should be updated to current time"
        assert tracker.app_times[TEST_APP_NAME] == TEST_DURATION, \
            "Previous app time should be recorded correctly"
    
    @patch('time.time')
    def test_handle_final_app(self, mock_time, tracker):
        """Test handling of the final application when stopping tracking."""
        # Setup final state
        mock_time.return_value = 110.0
        tracker.current_app = TEST_APP_NAME
        tracker.start_time = 100.0
        
        # Handle final app
        tracker._handle_final_app()
        
        assert TEST_APP_NAME in tracker.app_times, \
            "Final app should be recorded"
        assert tracker.app_times[TEST_APP_NAME] == 10.0, \
            "Final app duration should be calculated correctly"
    
    @patch('time_tracker.tracker.application_tracker.get_active_window_info')
    @patch('time.time')
    def test_track_keyboard_interrupt(self, mock_time, mock_get_window, tracker):
        """Test handling of KeyboardInterrupt during tracking."""
        # Setup mocks
        mock_time.side_effect = [100.0, 105.0]
        mock_get_window.return_value = TEST_APP_NAME
        
        # Simulate KeyboardInterrupt after one iteration
        mock_get_window.side_effect = KeyboardInterrupt()
        
        # Run tracking
        tracker.track()
        
        # Verify cleanup was performed
        tracker.storage.save_data.assert_called_once_with(tracker.app_times)
        tracker.storage.display_summary.assert_called_once_with(tracker.app_times) 