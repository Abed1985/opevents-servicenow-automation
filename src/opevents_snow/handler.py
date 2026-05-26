import os

from .description import build_description
from .priority import load_priority_map, map_priority
from .recovery import opening_event_for
from .state_store import EventStateStore


class EventTicketHandler:
    def __init__(self, servicenow_client, state_store, priority_map, opevents_base_url):
        self.servicenow = servicenow_client
        self.state_store = state_store
        self.priority_map = priority_map
        self.opevents_base_url = opevents_base_url

    @classmethod
    def from_env(cls, servicenow_client):
        return cls(
            servicenow_client=servicenow_client,
            state_store=EventStateStore(os.getenv("STATE_DB_PATH", "artifacts/opevents_snow_state.db")),
            priority_map=load_priority_map(os.getenv("PRIORITY_MAP_PATH", "config/priority_map.csv")),
            opevents_base_url=os.getenv("OPEVENTS_BASE_URL", "https://opevents.example.invalid/en/omk/opEvents"),
        )

    def open_or_update(self, event):
        recent = self.state_store.recent_event(event)
        if recent and recent.get("sys_id"):
            comment = f"Repeated event: {event.event} - {event.element} - {event.details}"
            self.servicenow.update_incident(recent["sys_id"], comment)
            return f"updated {recent['incident_number']}"

        existing = self.servicenow.find_open_incidents(event.node, event.event)
        if existing:
            incident = existing[0]
            sys_id = incident.get("sys_id")
            number = incident.get("number")
            if sys_id:
                self.servicenow.update_incident(sys_id, f"Repeated Opevents event: {event.details}")
            self.state_store.record_event(event, number, sys_id, "open")
            return f"updated {number}"

        priority = map_priority(event.priority, self.priority_map)
        description = build_description(event, self.opevents_base_url)
        number, sys_id = self.servicenow.create_incident(
            event,
            description,
            priority,
            os.getenv("SERVICENOW_ACCOUNT_ID", "00000"),
            os.getenv("SERVICENOW_CREATED_BY", "automation@example.com"),
            os.getenv("SERVICENOW_ASSIGNMENT_GROUP", "Network Operations"),
        )
        self.state_store.record_event(event, number, sys_id, "open")
        return f"created {number}"

    def close_recovered(self, event):
        opening_event = opening_event_for(event.event)
        if not opening_event:
            return "no recovery mapping"

        existing = self.servicenow.find_open_incidents(event.node, opening_event)
        if not existing:
            return "no open incidents to close"

        closed = []
        for incident in existing:
            number = incident.get("number")
            if not number:
                continue
            self.servicenow.close_incident(number)
            self.state_store.mark_closed(number)
            closed.append(number)
        return "closed " + ",".join(closed)
