#!/usr/bin/env python

import json
import os
import requests
import cog

def usage_error():
    cog.send_error("Must specify one of the following actions: list or status")
    os.exit(1)

def send_api_error(reason):
    cog.send_error("Buildkite API returned error: %s" (reason))
    os.exit(1)

def api_token():
    return os.getenv("API_TOKEN")

def org_name():
    return os.getenv("ORG_NAME")

def resolve_github_repo(project):
    url = "https://api.buildkite.com/v2/organizations/%s/pipelines" % (org_name())
    headers = {"Authorization", "Bearer %s" % (api_token())}
    resp = requests.get(url, headers=headers)
    if not resp.ok:
        send_api_error(resp.reason)
    for pipeline in resp.json():
        if pipeline["repository"].find(project) > -1:
            return pipeline["name"]
    return None

def list_builds():
    project_name = get_option("project")
    if project_name.find("/"):
        project = resolve_github_repo(project_name)
    else:
        project = project_name
    if project is None:
        cog.send_error("Buildkite pipeline for github repo %s not found" % (project_name))
        os.exit(1)
    url = "https://api.buildkite.com/v2/organization/%s/pipelines/%s/builds" % (org_name(), project)
    headers = {"Authorization", "Bearer %s" % (api_token())}
    resp = requests.get(url, headers=headers)
    if not resp.ok:
        send_api_error(resp.reason)
    builds = sorted(resp.json(), key=lambda build: (build["created_at"], build["finished_at"]), reverse=True)
    cog.send_json(builds[0:5])

if __name__ == "__main__":
    action = cog.get_arg(0)
    if action == None:
        usage_error()
    else:
        action = action.lower()
        if action not in ["list", "status"]:
            usage_error()
        if action == "list":
            list_builds()
        elif action == "status":
            build_status()
