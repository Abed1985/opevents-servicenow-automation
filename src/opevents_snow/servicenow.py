import os
from dataclasses import dataclass
from urllib.parse import quote_plus

import requests


@dataclass
class ServiceNowClient:
    instance_url: str
    username: str
    password: str
    dry_run: bool = True

    @classmethod
    def from_env(cls):
        instance_url = os.getenv("SERVICENOW_INSTANCE_URL", "https://example.service-now.com")
        username = os.getenv("SERVICENOW_USERNAME", "replace-in-lab")
        password = os.getenv("SERVICENOW_PASSWORD", "replace-in-lab")
        dry_run = os.getenv("DRY_RUN", "true").lower() != "false"
        return cls(instance_url.rstrip("/"), username, password, dry_run)

    def _request(self, method, path, **kwargs):
        url = f"{self.instance_url}{path}"
        if self.dry_run:
            return {"dry_run": True, "method": method, "url": url, "payload": kwargs.get("json")}
        response = requests.request(
            method,
            url,
            auth=(self.username, self.password),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=30,
            **kwargs,
        )
        response.raise_for_status()
        return response.json()

    def find_open_incidents(self, node, event_name):
        query = quote_plus(
            f"short_descriptionLIKE{node} - {event_name}^incident_stateIN1,2,3,6"
        )
        payload = self._request("GET", f"/api/now/table/incident?sysparm_query={query}")
        if payload.get("dry_run"):
            return []
        return payload.get("result", [])

    def create_incident(self, event, description, priority, account_id, created_by, assignment_group):
        payload = {
            "AccountId": account_id,
            "CreatedBy": created_by,
            "AssignedToGroup": assignment_group,
            "ShortDescription": event.short_description,
            "Description": description,
            "Category": "communications",
            "Impact": priority["impact"],
            "Urgency": priority["urgency"],
            "Comments": "Created from Opevents automation",
            "WorkNotes": "Event created by monitoring integration",
        }
        response = self._request("POST", "/api/example/internal/Incident", json=[payload])
        if response.get("dry_run"):
            return "DRYRUN0001", None
        valid = response.get("result", {}).get("Valid", [])
        if not valid:
            raise RuntimeError(f"ServiceNow create response did not include a valid incident: {response}")
        return valid[0].get("IncidentNumber"), valid[0].get("SysId")

    def update_incident(self, sys_id, comments):
        payload = {"u_additional_comments": comments}
        return self._request("PUT", f"/api/now/table/incident/{sys_id}?sysparm_exclude_reference_link=true", json=payload)

    def close_incident(self, incident_number):
        payload = {
            "IncidentNumber": incident_number,
            "State": "7",
            "CloseCode": "Closed/Resolved by External System",
            "CloseCategory": "Networking and Connectivity",
            "CloseSubcategory": "Proactive Monitoring",
            "CloseNotes": "Closed by Opevents automation after event recovery",
        }
        return self._request("PUT", "/api/example/internal/Incident", json=[payload])
