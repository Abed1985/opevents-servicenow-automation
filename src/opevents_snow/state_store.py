import sqlite3
import time
from pathlib import Path


class EventStateStore:
    def __init__(self, database_path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def initialize(self):
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    node TEXT NOT NULL,
                    event TEXT NOT NULL,
                    element TEXT NOT NULL,
                    details TEXT,
                    priority TEXT,
                    event_time INTEGER,
                    incident_number TEXT,
                    sys_id TEXT,
                    state TEXT,
                    created_at INTEGER,
                    PRIMARY KEY (node, event, element, incident_number)
                )
                """
            )

    def recent_event(self, event, window_seconds=300):
        threshold = int(time.time()) - window_seconds
        query = """
            SELECT node, event, element, incident_number, sys_id, state, created_at
            FROM events
            WHERE node = ? AND event = ? AND element = ? AND created_at >= ?
            ORDER BY created_at DESC
            LIMIT 1
        """
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(query, (event.node, event.event, event.element, threshold)).fetchone()
            return dict(row) if row else None

    def record_event(self, event, incident_number, sys_id=None, state="open"):
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO events
                (node, event, element, details, priority, event_time, incident_number, sys_id, state, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.node,
                    event.event,
                    event.element,
                    event.details,
                    event.priority,
                    int(float(event.epoch_time)),
                    incident_number,
                    sys_id,
                    state,
                    int(time.time()),
                ),
            )

    def mark_closed(self, incident_number):
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("UPDATE events SET state = 'closed' WHERE incident_number = ?", (incident_number,))
