import argparse

from .handler import EventTicketHandler
from .models import OpeventsEvent
from .servicenow import ServiceNowClient


def parse_args():
    parser = argparse.ArgumentParser(description="Create, update, or close ServiceNow incidents from Opevents arguments.")
    parser.add_argument("mode", choices=["open", "open-update", "close"], help="Ticket lifecycle action")
    parser.add_argument("opevents_args", nargs=8, metavar="OPEVENTS_ARG", help="priority details tag node event element time event_id")
    return parser.parse_args()


def main():
    args = parse_args()
    event = OpeventsEvent.from_argv(args.opevents_args)
    client = ServiceNowClient.from_env()
    handler = EventTicketHandler.from_env(client)

    if args.mode in ["open", "open-update"]:
        result = handler.open_or_update(event)
    else:
        result = handler.close_recovered(event)
    print(result)


if __name__ == "__main__":
    main()
