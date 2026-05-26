from html import escape


def build_description(event, opevents_base_url):
    event_context_url = f"{opevents_base_url.rstrip('/')}/events/{event.event_id}/event_context"
    rows = [
        ("Host", event.node),
        ("Event", event.event),
        ("Element", event.element or "n/a"),
        ("Details", event.details or "n/a"),
        ("Opevents Priority", event.priority),
        ("Event Context", event_context_url),
    ]
    body = "".join(
        f"<tr><th>{escape(label)}</th><td>{escape(value)}</td></tr>" for label, value in rows
    )
    return f"<table>{body}</table>"
