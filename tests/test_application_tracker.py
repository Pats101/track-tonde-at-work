import pytest
from unittest.mock import Mock, patch
from time_tracker.tracker.application_tracker import ApplicationTracker

@pytest.fixture
def tracker():
    """Create a tracker instance with mocked storage."""
    mock_storage = Mock()
    return ApplicationTracker(storage_handler=mock_storage)

def test_tracker_initialization(tracker):
    """Test tracker initialization."""
    assert tracker.current_app is None
    assert tracker.start_time is None
    assert tracker.app_times == {}

@patch('time_tracker.tracker.utils.get_active_window_info')
@patch('time.time')
def test_handle_app_switch(mock_time, mock_get_window, tracker):
    """Test handling application switches."""
    # Setup mock returns
    mock_time.side_effect = [100, 105]  # Start time, switch time
    mock_get_window.return_value = "test_app"
    
    # First app
    tracker._handle_app_switch("test_app", 100)
    assert tracker.current_app == "test_app"
    assert tracker.start_time == 100
    
    # Switch to second app
    tracker._handle_app_switch("another_app", 105)
    assert tracker.current_app == "another_app"
    assert tracker.start_time == 105
    assert tracker.app_times["test_app"] == 5

def test_update_app_time(tracker):
    """Test updating application time."""
    # New app
    tracker._update_app_time("test_app", 5)
    assert tracker.app_times["test_app"] == 5
    
    # Update existing app
    tracker._update_app_time("test_app", 3)
    assert tracker.app_times["test_app"] == 8

@patch('time.time')
def test_handle_final_app(mock_time, tracker):
    """Test handling the final application."""
    mock_time.return_value = 110
    tracker.current_app = "final_app"
    tracker.start_time = 100
    
    tracker._handle_final_app()
    assert tracker.app_times["final_app"] == 10 