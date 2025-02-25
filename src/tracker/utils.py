import psutil
import win32gui
import win32process
from win32gui import GetWindowText, GetForegroundWindow

def get_active_window_info():
    """Get information about the currently active window."""
    try:
        window = GetForegroundWindow()
        window_title = GetWindowText(window)
        
        _, pid = win32process.GetWindowThreadProcessId(window)
        
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            
            if window_title and process_name not in ['explorer.exe', 'MemCompression', 'System']:
                return f"{process_name} ({window_title})"
            return process_name
            
        except psutil.NoSuchProcess:
            return "Unknown"
            
    except Exception:
        return "Unknown" 