import pytest
from unittest.mock import patch, Mock
from time_tracker.tracker.utils import get_active_window_info
import psutil

# Constants for testing
TEST_WINDOW_HANDLE = 12345
TEST_PROCESS_ID = 67890
TEST_WINDOW_TITLE = "Test Window"
TEST_PROCESS_NAME = "test_app.exe"
SYSTEM_PROCESSES = ['explorer.exe', 'MemCompression', 'System']

@pytest.fixture
def mock_window_setup():
    """
    Fixture to setup common window mocks.
    
    Returns:
        dict: Dictionary containing all mocked objects:
            - window: Mocked GetForegroundWindow
            - text: Mocked GetWindowText
            - pid: Mocked GetWindowThreadProcessId
            - process: Mocked Process class
            - process_instance: Mocked Process instance
    """
    with patch('time_tracker.tracker.utils.GetForegroundWindow') as mock_window, \
         patch('time_tracker.tracker.utils.GetWindowText') as mock_text, \
         patch('time_tracker.tracker.utils.GetWindowThreadProcessId') as mock_pid, \
         patch('time_tracker.tracker.utils.psutil.Process') as mock_process:
        
        # Setup default mock behavior
        mock_window.return_value = TEST_WINDOW_HANDLE
        mock_text.return_value = TEST_WINDOW_TITLE
        mock_pid.return_value = (None, TEST_PROCESS_ID)
        
        mock_process_instance = Mock()
        mock_process_instance.name.return_value = TEST_PROCESS_NAME
        mock_process.return_value = mock_process_instance
        
        yield {
            'window': mock_window,
            'text': mock_text,
            'pid': mock_pid,
            'process': mock_process,
            'process_instance': mock_process_instance
        }

class TestWindowInfo:
    """Test suite for window information retrieval functionality."""

    @pytest.mark.window
    def test_basic_window_info(self, mock_window_setup):
        """Verify basic window information retrieval works correctly."""
        result = get_active_window_info()
        assert result == f"{TEST_PROCESS_NAME} ({TEST_WINDOW_TITLE})", \
            "Basic window info should return process name and window title"

    @pytest.mark.window
    @pytest.mark.parametrize("title,expected", [
        ("", TEST_PROCESS_NAME),
        (None, TEST_PROCESS_NAME),
        ("Test © Window ! @ # $", f"{TEST_PROCESS_NAME} (Test © Window ! @ # $)"),
        ("A" * 1000, f"{TEST_PROCESS_NAME} ({'A' * 1000})")
    ])
    def test_window_titles(self, mock_window_setup, title, expected):
        """Test handling of various window title formats."""
        mock_window_setup['text'].return_value = title
        result = get_active_window_info()
        assert result == expected, f"Failed to handle window title: {title}"

    @pytest.mark.process
    @pytest.mark.parametrize("system_process", SYSTEM_PROCESSES)
    def test_system_processes(self, mock_window_setup, system_process):
        """Test handling of various system processes."""
        mock_window_setup['process_instance'].name.return_value = system_process
        result = get_active_window_info()
        assert result == system_process, \
            f"System process {system_process} should be returned as-is"

    @pytest.mark.process
    @pytest.mark.parametrize("error_type,expected", [
        (psutil.NoSuchProcess(TEST_PROCESS_ID), "Unknown"),
        (psutil.AccessDenied(TEST_PROCESS_ID), "Unknown"),
        (psutil.Error(), "Unknown"),
        (ValueError("Test error"), "Unknown"),
    ])
    def test_process_errors(self, mock_window_setup, error_type, expected):
        """Test handling of various process-related errors."""
        mock_window_setup['process'].side_effect = error_type
        result = get_active_window_info()
        assert result == expected, f"Failed to handle error: {type(error_type)}"

    @pytest.mark.window
    def test_window_handle_zero(self, mock_window_setup):
        """Test handling of zero window handle."""
        mock_window_setup['window'].return_value = 0
        result = get_active_window_info()
        assert result == "Unknown", "Zero window handle should return Unknown"

    @pytest.mark.process
    def test_pid_zero(self, mock_window_setup):
        """Test handling of zero process ID."""
        mock_window_setup['pid'].return_value = (None, 0)
        result = get_active_window_info()
        assert result == "Unknown", "Zero process ID should return Unknown"

    @pytest.mark.process
    def test_process_name_none(self, mock_window_setup):
        """Test handling of None process name."""
        mock_window_setup['process_instance'].name.return_value = None
        result = get_active_window_info()
        assert result == "Unknown", "None process name should return Unknown"

    @pytest.mark.window
    def test_concurrent_window_switch(self, mock_window_setup):
        """Test handling of window switching during process."""
        mock_window_setup['window'].side_effect = [12345, 67890]
        mock_window_setup['text'].side_effect = ["Window1", "Window2"]
        result = get_active_window_info()
        assert TEST_PROCESS_NAME in result, \
            "Should handle concurrent window switching gracefully"

    @pytest.mark.window
    def test_special_characters_process_name(self, mock_window_setup):
        """Test handling of special characters in process names."""
        mock_window_setup['process_instance'].name.return_value = "special-app_v1.2.exe"
        mock_window_setup['text'].return_value = "Test Window"
        result = get_active_window_info()
        assert result == "special-app_v1.2.exe (Test Window)"

    @pytest.mark.window
    def test_extended_ascii_process_name(self, mock_window_setup):
        """Test handling of extended ASCII characters in process names."""
        mock_window_setup['process_instance'].name.return_value = "app_with_accent_é.exe"
        mock_window_setup['text'].return_value = "Test Window"
        result = get_active_window_info()
        assert result == "app_with_accent_é.exe (Test Window)"

    @pytest.mark.window
    def test_get_active_window_info_multiple_parentheses(self, mock_window_setup):
        """Test handling of window titles with parentheses."""
        mock_window_setup['text'].return_value = "Test (Window) (More)"
        result = get_active_window_info()
        assert result == "test_app.exe (Test (Window) (More))"

    @pytest.mark.window
    @pytest.mark.parametrize("window_error", [
        OSError(123, "Test Windows Error"),  # Using OSError instead of WindowsError
        MemoryError(),
        Exception("Unexpected error")
    ])
    def test_window_api_errors(self, mock_window_setup, window_error):
        """Test handling of various Windows API errors."""
        mock_window_setup['window'].side_effect = window_error
        result = get_active_window_info()
        assert result == "Unknown"

    @pytest.mark.window
    def test_get_active_window_info_long_title(self, mock_window_setup):
        """Test handling of very long window titles."""
        long_title = "A" * 1000  # Very long title
        mock_window_setup['text'].return_value = long_title
        result = get_active_window_info()
        assert result == f"test_app.exe ({long_title})" 