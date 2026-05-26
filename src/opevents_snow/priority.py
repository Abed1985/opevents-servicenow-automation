import csv
from pathlib import Path


DEFAULT_PRIORITY = {"impact": "3", "urgency": "3", "priority": "4"}


def load_priority_map(path="config/priority_map.csv"):
    mapping = {}
    with Path(path).open(newline="", encoding="utf-8") as csv_file:
        for row in csv.DictReader(csv_file):
            mapping[row["opevents_priority"]] = {
                "impact": row["snow_impact"],
                "urgency": row["snow_urgency"],
                "priority": row["snow_priority"],
            }
    return mapping


def map_priority(opevents_priority, mapping):
    return mapping.get(str(opevents_priority), DEFAULT_PRIORITY)
