RECOVERY_EVENT_MAP = {
    "Node Up": "Node Down",
    "Alert: High CPU Usage Closed": "Alert: High CPU Usage",
    "Alert: High Memory Usage Closed": "Alert: High Memory Usage",
}


def opening_event_for(recovery_event_name):
    return RECOVERY_EVENT_MAP.get(recovery_event_name)
