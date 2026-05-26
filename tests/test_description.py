from opevents_snow.description import build_description
from opevents_snow.models import OpeventsEvent


def test_description_escapes_event_fields():
    event = OpeventsEvent("8", "CPU < high", "tag", "edge-1", "Alert", "cpu", "1710000000", "123")
    description = build_description(event, "https://opevents.example.invalid")
    assert "CPU &lt; high" in description
    assert "https://opevents.example.invalid/events/123/event_context" in description
