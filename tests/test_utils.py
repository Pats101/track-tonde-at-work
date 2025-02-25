import pytest
from unittest.mock import patch, Mock
from time_tracker.tracker.utils import get_active_window_info
import psutil

@pytest.fixture
def mock_window_setup():
    """Fixture to setup common window mocks."""
    with patch('time_tracker.tracker.utils.GetForegroundWindow') as mock_window, \
         patch('time_tracker.tracker.utils.GetWindowText') as mock_text, \
         patch('time_tracker.tracker.utils.GetWindowThreadProcessId') as mock_pid, \
         patch('time_tracker.tracker.utils.psutil.Process') as mock_process:
        
        # Default mock setup
        mock_window.return_value = 12345
        mock_text.return_value = "Test Window"
        mock_pid.return_value = (None, 67890)
        
        mock_process_instance = Mock()
        mock_process_instance.name.return_value = "test_app.exe"
        mock_process.return_value = mock_process_instance
        
        yield {
            'window': mock_window,
            'text': mock_text,
            'pid': mock_pid,
            'process': mock_process,
            'process_instance': mock_process_instance
        }

def test_get_active_window_info_basic(mock_window_setup):
    """Test basic window information retrieval."""
    result = get_active_window_info()
    assert result == "test_app.exe (Test Window)"

def test_get_active_window_info_empty_title(mock_window_setup):
    """Test handling of empty window titles."""
    mock_window_setup['text'].return_value = ""
    result = get_active_window_info()
    assert result == "test_app.exe"

def test_get_active_window_info_special_chars(mock_window_setup):
    """Test handling of special characters in window title."""
    mock_window_setup['text'].return_value = "Test © Window ! @ # $"
    result = get_active_window_info()
    assert result == "test_app.exe (Test © Window ! @ # $)"

@pytest.mark.parametrize("system_process", [
    "explorer.exe",
    "MemCompression",
    "System"
])
def test_system_processes(mock_window_setup, system_process):
    """Test handling of various system processes."""
    mock_window_setup['process_instance'].name.return_value = system_process
    result = get_active_window_info()
    assert result == system_process

def test_get_active_window_info_long_title(mock_window_setup):
    """Test handling of very long window titles."""
    long_title = "A" * 1000  # Very long title
    mock_window_setup['text'].return_value = long_title
    result = get_active_window_info()
    assert result == f"test_app.exe ({long_title})"

def test_get_active_window_info_multiple_parentheses(mock_window_setup):
    """Test handling of window titles with parentheses."""
    mock_window_setup['text'].return_value = "Test (Window) (More)"
    result = get_active_window_info()
    assert result == "test_app.exe (Test (Window) (More))"

@pytest.mark.parametrize("error_type,expected", [
    (psutil.NoSuchProcess(1234), "Unknown"),
    (psutil.AccessDenied(1234), "Unknown"),
    (psutil.Error(), "Unknown"),
    (ValueError("Test error"), "Unknown"),
])
def test_process_errors(mock_window_setup, error_type, expected):
    """Test handling of various process-related errors."""
    mock_window_setup['process'].side_effect = error_type
    result = get_active_window_info()
    assert result == expected

def test_window_handle_zero(mock_window_setup):
    """Test handling of zero window handle."""
    mock_window_setup['window'].return_value = 0
    result = get_active_window_info()
    assert result == "Unknown"

def test_pid_zero(mock_window_setup):
    """Test handling of zero process ID."""
    mock_window_setup['pid'].return_value = (None, 0)
    result = get_active_window_info()
    assert result == "Unknown"

@pytest.mark.parametrize("window_error", [
    OSError(123, "Test Windows Error"),  # Using OSError instead of WindowsError
    MemoryError(),
    Exception("Unexpected error")
])
def test_window_api_errors(mock_window_setup, window_error):
    """Test handling of various Windows API errors."""
    mock_window_setup['window'].side_effect = window_error
    result = get_active_window_info()
    assert result == "Unknown"

def test_process_name_none(mock_window_setup):
    """Test handling of None process name."""
    mock_window_setup['process_instance'].name.return_value = None
    result = get_active_window_info()
    assert result == "Unknown"

def test_concurrent_window_switch(mock_window_setup):
    """Test handling of window switching during process."""
    # Simulate window switch during process
    mock_window_setup['window'].side_effect = [12345, 67890]
    mock_window_setup['text'].side_effect = ["Window1", "Window2"]
    result = get_active_window_info()
    assert "test_app.exe" in result

def test_special_characters_process_name(mock_window_setup):
    """Test handling of special characters in process names."""
    mock_window_setup['process_instance'].name.return_value = "special-app_v1.2.exe"
    mock_window_setup['text'].return_value = "Test Window"
    result = get_active_window_info()
    assert result == "special-app_v1.2.exe (Test Window)"

def test_extended_ascii_process_name(mock_window_setup):
    """Test handling of extended ASCII characters in process names."""
    mock_window_setup['process_instance'].name.return_value = "app_with_accent_é.exe"
    mock_window_setup['text'].return_value = "Test Window"
    result = get_active_window_info()
    assert result == "app_with_accent_é.exe (Test Window)" 