import pytest
import json
from pathlib import Path
from unittest.mock import patch, mock_open
from time_tracker.data_handlers.storage import DataStorage
from time_tracker.data_handlers.formatters import group_application_data

@pytest.fixture
def storage():
    """Create a storage instance with a test directory."""
    return DataStorage(data_dir="test_data")

def test_group_application_data():
    """Test grouping application data."""
    test_data = {
        "chrome.exe (Google)": 60,
        "chrome.exe (YouTube)": 30,
        "notepad.exe (Document)": 45
    }
    
    result = group_application_data(test_data)
    
    assert "chrome.exe" in result
    assert result["chrome.exe"]["total"] == 90
    assert result["chrome.exe"]["windows"]["Google"] == 60
    assert result["chrome.exe"]["windows"]["YouTube"] == 30
    
    assert "notepad.exe" in result
    assert result["notepad.exe"]["total"] == 45
    assert result["notepad.exe"]["windows"]["Document"] == 45

@patch('json.dump')
@patch('builtins.open', new_callable=mock_open)
def test_save_data(mock_file, mock_json_dump, storage):
    """Test saving application data."""
    test_data = {
        "test_app.exe (Test Window)": 60
    }
    
    storage.save_data(test_data)
    
    # Verify file was opened
    mock_file.assert_called_once()
    # Verify json.dump was called
    mock_json_dump.assert_called_once()
    
    # Get the data that would have been written
    saved_data = mock_json_dump.call_args[0][0]
    assert 'date' in saved_data
    assert 'total_tracking_time' in saved_data
    assert saved_data['total_tracking_time'] == 60 