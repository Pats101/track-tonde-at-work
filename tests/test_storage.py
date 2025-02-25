import pytest
import json
from pathlib import Path
from unittest.mock import patch, mock_open
from datetime import datetime
from time_tracker.data_handlers.storage import DataStorage
from time_tracker.data_handlers.formatters import group_application_data

# Constants for testing
TEST_DATA_DIR = "test_data"
TEST_DATE = "2024-03-21"
TEST_APPS = {
    "chrome.exe (Google)": 60.0,
    "chrome.exe (YouTube)": 30.0,
    "notepad.exe (Document)": 45.0
}

@pytest.fixture
def mock_datetime():
    """Fixture to mock datetime."""
    with patch('time_tracker.data_handlers.storage.datetime') as mock_dt:
        mock_dt.now.return_value.strftime.return_value = TEST_DATE
        yield mock_dt

@pytest.fixture
def storage():
    """
    Fixture to create a storage instance with test directory.
    
    Returns:
        DataStorage: Configured storage instance for testing
    """
    storage = DataStorage(data_dir=TEST_DATA_DIR)
    return storage

class TestDataStorage:
    """Test suite for data storage functionality."""
    
    @pytest.mark.storage
    def test_initialization(self, storage, tmp_path):
        """Test storage initialization and directory creation."""
        test_dir = tmp_path / "test_storage"
        storage = DataStorage(data_dir=test_dir)
        assert test_dir.exists(), "Storage directory should be created"
        assert test_dir.is_dir(), "Storage path should be a directory"

    @pytest.mark.storage
    def test_group_application_data(self):
        """Test grouping of application usage data."""
        result = group_application_data(TEST_APPS)
        
        # Test Chrome grouping
        assert "chrome.exe" in result, "Chrome should be in grouped results"
        assert result["chrome.exe"]["total"] == 90.0, "Chrome total time should be correct"
        assert result["chrome.exe"]["windows"]["Google"] == 60.0, "Window time should be correct"
        assert result["chrome.exe"]["windows"]["YouTube"] == 30.0, "Window time should be correct"
        
        # Test Notepad grouping
        assert "notepad.exe" in result, "Notepad should be in grouped results"
        assert result["notepad.exe"]["total"] == 45.0, "Notepad total time should be correct"
        assert result["notepad.exe"]["windows"]["Document"] == 45.0, "Window time should be correct"

    @pytest.mark.storage
    @patch('json.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_data(self, mock_file, mock_json_dump, storage, mock_datetime):
        """Test saving application data to file."""
        # Save test data
        storage.save_data(TEST_APPS)
        
        # Verify file operations
        expected_filename = Path(TEST_DATA_DIR) / f'app_usage_{TEST_DATE}.json'
        mock_file.assert_called_once_with(expected_filename, 'w')
        
        # Verify saved data structure
        saved_data = mock_json_dump.call_args[0][0]
        assert saved_data['date'] == TEST_DATE, "Date should be correct"
        assert saved_data['total_tracking_time'] == sum(TEST_APPS.values()), \
            "Total time should be sum of all app times"
        assert 'applications' in saved_data, "Should include applications data"

    @pytest.mark.storage
    def test_display_summary(self, storage, capsys):
        """Test display of usage summary."""
        storage.display_summary(TEST_APPS)
        captured = capsys.readouterr()
        
        # Verify output format and content
        assert "Application Usage Summary" in captured.out, \
            "Should show summary header"
        assert "chrome.exe" in captured.out, "Should show Chrome usage"
        assert "notepad.exe" in captured.out, "Should show Notepad usage"
        assert "minutes" in captured.out, "Should show time in minutes" 