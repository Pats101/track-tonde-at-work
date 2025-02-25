def group_application_data(app_times):
    """Group application data by process name."""
    app_groups = {}
    
    for app_window, duration in app_times.items():
        app_name = app_window.split(" (")[0]
        window_title = app_window.split(" (")[1][:-1] if " (" in app_window else ""
        
        if app_name not in app_groups:
            app_groups[app_name] = {"total": 0, "windows": {}}
        
        app_groups[app_name]["total"] += duration
        if window_title:
            app_groups[app_name]["windows"][window_title] = duration
    
    return app_groups 