from dataclasses import dataclass


@dataclass(frozen=True)
class OpeventsEvent:
    priority: str
    details: str
    tag: str
    node: str
    event: str
    element: str
    epoch_time: str
    event_id: str

    @property
    def short_description(self):
        return f"{self.node} - {self.event}"

    @classmethod
    def from_argv(cls, argv):
        if len(argv) != 8:
            raise ValueError("Expected 8 Opevents arguments: priority details tag node event element time event_id")
        return cls(*argv)
