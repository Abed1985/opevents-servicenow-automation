from opevents_snow.recovery import opening_event_for


def test_recovery_mapping():
    assert opening_event_for("Node Up") == "Node Down"
    assert opening_event_for("Unknown") is None
