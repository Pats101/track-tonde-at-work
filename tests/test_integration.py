import pytest
import time
from time_tracker.tracker.utils import get_active_window_info

@pytest.mark.integration
def test_actual_window_info():
    """Integration test for getting actual window information."""
    # Get actual window info
    result = get_active_window_info()
    
    # Basic validation
    assert isinstance(result, str)
    assert len(result) > 0
    assert result != "Unknown"

@pytest.mark.integration
def test_multiple_window_calls():
    """Test multiple consecutive calls to get_active_window_info."""
    results = []
    for _ in range(5):
        results.append(get_active_window_info())
        time.sleep(0.1)
    
    # Verify we got valid results
    assert all(isinstance(r, str) for r in results)
    assert all(len(r) > 0 for r in results) 