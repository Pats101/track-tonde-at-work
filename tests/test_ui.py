import pytest
from PyQt6.QtWidgets import QApplication
from time_tracker.ui.main_window import TimeTrackerUI

@pytest.fixture
def app():
    """Create a Qt Application."""
    return QApplication([])

@pytest.fixture
def window(app):
    """Create the main window."""
    return TimeTrackerUI()

class TestTimeTrackerUI:
    def test_window_title(self, window):
        """Test window title is set correctly."""
        assert window.windowTitle() == "Time Tracker"
    
    def test_start_stop_buttons(self, window):
        """Test start/stop button states."""
        assert window.start_button.isEnabled()
        assert not window.stop_button.isEnabled()
        
        window.start_tracking()
        assert not window.start_button.isEnabled()
        assert window.stop_button.isEnabled()
        
        window.stop_tracking()
        assert window.start_button.isEnabled()
        assert not window.stop_button.isEnabled() 