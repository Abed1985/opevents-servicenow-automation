from opevents_snow.priority import map_priority


def test_map_priority_known_value():
    mapping = {"8": {"impact": "1", "urgency": "1", "priority": "1"}}
    assert map_priority("8", mapping) == {"impact": "1", "urgency": "1", "priority": "1"}


def test_map_priority_default_value():
    assert map_priority("99", {}) == {"impact": "3", "urgency": "3", "priority": "4"}
