import json
import os
import requests
from pprint import pprint as pp
from collections import namedtuple
from datetime import datetime
import time

from google.cloud import logging


LOG_STORY_MOMENT = True
try:
    logging_client = logging.Client()
    logger = logging_client.logger("StoryMomentLogger")
except:
    logger = None


def log_struct(l):
    if logger:
        logger.log_struct(l)
    else:
        print(l)


StoryMoment = namedtuple("Story",
    ("time "
     "id archived blocked completed completed_at created_at description "
     "deadline epic_id estimate project_id owner_ids name story_type "
     "workflow_state_id requested_by_id"
    )
)


CLUBHOUSE_API_TOKEN = os.environ["CLUBHOUSE_API_TOKEN"]


host = "https://api.clubhouse.io"

def search(query):
    return requests.get(
        "{}/api/v2/search/stories?token={}".format(
            host,
            CLUBHOUSE_API_TOKEN,
        ),
        data={
            "query": query,
        }
    ).json()


def get_next(results):
    url = "{}{}".format(host, results["next"])
    return requests.get(
        url,
        data={
            "token": CLUBHOUSE_API_TOKEN
        }
    ).json()


def get_resources(resource_type):
    resources_response = requests.get(
        "{}/api/v2/{}?token={}".format(host, resource_type, CLUBHOUSE_API_TOKEN)
    ).json()
    resources = {}
    for r in resources_response:
        resources[r['id']] = r
    return resources


members = get_resources("members")
projects = get_resources("projects")
epics = get_resources("epics")

workflows = get_resources("workflows")
workflow_states = {}
for id_, w in workflows.items():
    for s in w["states"]:
        workflow_states[s['id']] = s


def translate_field(field_name, value):
    if field_name in ["member_id", "requested_by_id"]:
        member = members.get(value)
        if member:
            return member["profile"]["name"]
        else:
            return "Unknown Member"
    if field_name == "owner_ids":
        return [a for a in map(
            lambda x: translate_field("member_id", x),
            value,
        )]
    if field_name == "workflow_state_id":
        return workflow_states.get(value, {"name": None})["name"]
    if field_name == "project_id":
        return projects.get(value, {"name": None})["name"]
    if field_name == "epic_id":
        return epics.get(value, {"name": None})["name"]
    return value


def log_story_moment(sm):
    fields = {"type": "StoryMoment"}
    excluded_fields = ["description"]

    for f in StoryMoment._fields:
        translated_fieldname = f
        if f.endswith("_id"):
            translated_fieldname = f[:-3]
        if f.endswith("_ids"):
            translated_fieldname = "{}s".format(f[:-4])
        fields[translated_fieldname] = translate_field(f, getattr(sm, f))

    log_struct(
        {
            k:v
            for (k, v)
            in fields.items()
            if k not in excluded_fields
        }
    )


def process_story(story):
    sm = StoryMoment(
        datetime.now().isoformat(),
        *[story[f]
          for f
          in StoryMoment._fields
          if f != "time"
        ]
    )
    if LOG_STORY_MOMENT:
        log_story_moment(sm)
    return sm


def process_results(results, stories=[]):
    print("processed {} stories, processing {} stories".format(
        len(stories),
        len(results["data"]),
    ))
    stories += [process_story(s) for s in results['data']]
    if results['next']:
        stories = process_results(get_next(results), stories)
    return stories


def main():
    stories = process_results(search("is:unstarted"))
    stories += process_results(search("is:started"))


if __name__ == "__main__":
    while True:
        main()
        minute = 60
        hour = 60 * minute
        time.sleep(12 * hour)
