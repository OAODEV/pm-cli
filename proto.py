import json
from dateutil import parser
import math
from datetime import datetime, timezone
import sys
import requests
import os
from pprint import pprint as pp
from collections import namedtuple


Milestone = namedtuple("Milestone", "name start end")

CLUBHOUSE_API_TOKEN = os.environ["CLUBHOUSE_API_TOKEN"]


milestones = requests.get(
    "https://api.clubhouse.io/api/v2/milestones?token={}".format(
        CLUBHOUSE_API_TOKEN,
    ),
).json()


def make_scheduled_milestone(m):
    start = m["started_at_override"] or m["started_at"]
    end = m["completed_at_override"] or m["completed_at"]
    return Milestone(
        m["name"],
        parser.parse(start),
        parser.parse(end),
    )


scheduled = sorted(
    [
        make_scheduled_milestone(m)
        for m
        in milestones
        if m["started_at"] or m["started_at_override"]
        if not m['state'] == "done"
    ],
    key=lambda m: m.end,
)


def view_schedule():
    today = datetime.now(timezone.utc)

    factor = 2
    earliest_start_date = min(scheduled, key=lambda m: m.start).start
    earliest_start_to_today = today - earliest_start_date
    for name, start, end in scheduled:
        td_span = end - start
        td_to_start = start - earliest_start_date
        to_start_str = "".join([" "
                                for d
                                in range(
                                    math.floor(td_to_start.days / factor),
                                )])
        span_str = "".join(["-"
                            for d
                            in range(
                                math.floor(td_span.days / factor),
                            )])
        view = to_start_str + span_str
        d = math.floor(earliest_start_to_today.days / factor)
        view = "{}{}{}".format(view[:d], "*", view[d:])
        print(view, name)


def view_unscheduled():
    unscheduled_milestones = filter(
        lambda x: x["started_at_override"] == None and x["started_at"] == None,
        milestones,
    )
    print("\n".join([m["name"] for m in unscheduled_milestones]))

if __name__ == "__main__":
    print("Scheduled:")
    print()
    view_schedule()
    print()
    print("Unscheduled:")
    print()
    view_unscheduled()
