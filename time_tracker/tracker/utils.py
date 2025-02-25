import psutil
import win32gui
import win32process
from win32gui import GetWindowText, GetForegroundWindow
from win32process import GetWindowThreadProcessId

def get_active_window_info():
    """Get information about the currently active window."""
    try:
        window = GetForegroundWindow()
        # Check for invalid window handle
        if not window:
            return "Unknown"
            
        window_title = GetWindowText(window)
        
        _, pid = GetWindowThreadProcessId(window)
        # Check for invalid process ID
        if not pid:
            return "Unknown"
        
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            
            # Check for None or empty process name
            if not process_name:
                return "Unknown"
                
            if window_title and process_name not in ['explorer.exe', 'MemCompression', 'System']:
                return f"{process_name} ({window_title})"
            return process_name
            
        except psutil.NoSuchProcess:
            return "Unknown"
            
    except Exception:
        return "Unknown" 