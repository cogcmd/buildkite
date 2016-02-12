#!/usr/bin/env python

import json
import os
import requests
import sys
from cog.logger import Logger
import cog.output
import cog.env

def usage_error():
    cog.output.send_error("Must specify one of the following actions: list or status")
    cog.output.finish(error=True)

def send_api_error(reason):
    cog.output.send_error("Buildkite API returned '%s'." % (reason))
    cog.output.finish(error=True)

def api_token():
    api_token = cog.env.get_config("api_token")
    if api_token is None:
        cog.output.send_error("Missing configuration variable API_TOKEN.")
        cog.output.finish(error=True)
    return api_token

def org_name():
    org_name = cog.env.get_config("org_name")
    if org_name is None:
        cog.output.send_error("Missing configuration variable ORG_NAME.")
        cog.output.finish(error=True)
    return org_name

def resolve_github_repo(project):
    url = "https://api.buildkite.com/v2/organizations/%s/pipelines" % (org_name())
    headers = {"Authorization": "Bearer %s" % (api_token())}
    resp = requests.get(url, headers=headers)
    if not resp.ok:
        send_api_error(resp.reason)
    for pipeline in resp.json():
        if pipeline["repository"].find(project) > -1:
            return pipeline["name"].lower()
    return None

def get_project_name():
    project_name = cog.env.get_option("project")
    if project_name.find("/") > -1:
        project_name = resolve_github_repo(project_name)

    if project_name is None:
        cog.output.send_error("Buildkite pipeline for github repo %s not found" % (project_name))
        cog.output.finish(error=True)
    else:
        return project_name

def branch_name():
    return cog.env.get_option("branch", default="master")

def make_build_result(project, build):
    return {"url": build["web_url"],
            "project": project,
            "started": build["started_at"],
            "finished": build["finished_at"],
            "status": build["state"],
            "branch": build["branch"]}

def list_builds():
    project = get_project_name()
    url = "https://api.buildkite.com/v2/organizations/%s/pipelines/%s/builds?branch=%s" % (org_name(), project, branch_name())
    headers = {"Authorization": "Bearer %s" % (api_token())}
    resp = requests.get(url, headers=headers)
    if not resp.ok:
        send_api_error(resp.reason)
    builds = sorted(resp.json(), key=lambda build: (build["created_at"], build["finished_at"]), reverse=True)
    builds = builds[0:4]
    result = []
    for build in builds:
        result.append(make_build_result(project, build))
    cog.output.send_json(result)

def build_status():
    project = get_project_name()
    url = "https://api.buildkite.com/v2/organizations/%s/pipelines/%s/builds?branch=%s" % (org_name(), project, branch_name())
    headers = {"Authorization": "Bearer %s" % (api_token())}
    resp = requests.get(url, headers=headers)
    if not resp.ok:
        send_api_error(resp.reason)
    builds = sorted(resp.json(), key=lambda build: build["started_at"], reverse=True)
    if len(builds) == 0:
        cog.output.send_json([])
    else:
        cog.output.send_json(make_build_result(project, builds[0]), template="status")


if __name__ == "__main__":
    action = cog.env.get_arg(0)
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
        cog.output.finish()
