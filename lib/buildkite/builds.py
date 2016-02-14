import json
import os
import requests
import sys

import requests
from cog.logger import Logger
from cog.command import Command

class BuildsCommand(Command):
    def buildkite_get(self, url):
        headers = {"Authorization": "Bearer %s" % (self.api_token)}
        api_resp = requests.get(url, headers=headers)
        if not api_resp.ok:
            self.api_error(api_resp.reason)
        return api_resp

    def api_error(self, reason):
        self.resp.send_error("Buildkite API returned '%s'." % (reason))

    def resolve_github_repo(self, project):
        url = "https://api.buildkite.com/v2/organizations/%s/pipelines" % (self.org_name)
        api_resp = self.buildkite_get(url)
        for pipeline in api_resp.json():
            if pipeline["repository"].find(project) > -1:
                return pipeline["name"].lower()
        return None

    def get_project_name(self):
        project_name = self.req.option("project")
        if project_name.find("/") > -1:
            project_name = self.resolve_github_repo(project_name)
        if project_name is None:
            self.resp.send_error("Buildkite pipeline for github repo %s not found" % (project_name))
        return project_name

    def make_build_result(self, project, build):
        return {"url": build["web_url"],
                "buildnum": build["number"],
                "project": project,
                "started": build["started_at"],
                "finished": build["finished_at"],
                "status": build["state"],
                "branch": build["branch"]}

    # cog.Command interface methods

    def handle_list(self):
        project = self.get_project_name()
        branch = self.req.option("branch", default="master")
        url = "https://api.buildkite.com/v2/organizations/%s/pipelines/%s/builds?branch=%s" % (self.org_name, project, branch)
        api_resp = self.buildkite_get(url)
        builds = sorted(api_resp.json(), key=lambda build: (build["created_at"], build["finished_at"]), reverse=True)
        builds = builds[0:4]
        result = []
        for build in builds:
            result.append(self.make_build_result(project, build))
        self.resp.append_body({"builds": result}, template="list")

    def handle_status(self):
        project = self.get_project_name()
        branch = self.req.option("branch", default="master")
        url = "https://api.buildkite.com/v2/organizations/%s/pipelines/%s/builds?branch=%s" % (self.org_name, project, branch)
        api_resp = self.buildkite_get(url)
        builds = sorted(api_resp.json(), key=lambda build: build["started_at"], reverse=True)
        if len(builds) > 0:
            self.resp.append_body({"builds": self.make_build_result(project, builds[0])}, template="status")

    def prepare(self):
        # Load API_TOKEN from environment
        self.api_token = self.req.config("api_token")
        if self.api_token is None:
            self.resp.send_error("Missing configuration variable API_TOKEN.")
        # Load ORG_NAME from environment
        self.org_name = self.req.config("org_name")
        if self.org_name is None:
            self.resp.send_error("Missing configuration variable ORG_NAME.")

    def usage_error(self):
        self.resp.send_error("Must specify one of the following actions: list or status")
