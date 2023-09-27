#This Python script automates the complete flow from ServiceNow to GitHub Enterprise Cloud to create repos
# Steps:
#Use ServiceNow API to get the necessary details.
#Authenticate with Conjur to get the GitHub Personal Access Token (PAT).
#Use the PAT to create a repository on GitHub.
# Here is a high-level overview of the workflow:

#The requester fills a ServiceNow form to request a new GitHub Enterprise Cloud repo.
#The form is sent to the requester's supervisor for approval.
#Once the supervisor approves the request, a ticket or webhook is generated and sent to the requester and the GitHub admin, who:
#Ycreates a private repo for the requester in GitHub Enterprise Cloud.
#generates a PAT for the requester and store it in CyberArk.
#notifies the requester that the repo has been created and provide them with the PAT.

import requests
import json
from jenkins import Jenkins

class GitHubEnterpriseCloud:
    def __init__(self, url, service_account_token):
        self.url = url
        self.service_account_token = service_account_token
        self.session = requests.Session()
        self.session.headers = {"Authorization": f"Bearer {self.service_account_token}"}

    def create_repo(self, name, owner, permissions, tags):
        url = f"{self.url}/api/v3/repos"
        data = json.dumps({
            "name": name,
            "owner": owner,
            "permissions": permissions,
            "tags": tags
        })
        headers = {"Content-Type": "application/json"}
        response = self.session.post(url, data=data, headers=headers)
        if response.status_code == 201:
            return json.loads(response.content)
        else:
            raise Exception(f"Failed to create repo: {response.content}")

class ServiceNow:
    def __init__(self, url, service_account_token):
        self.url = url
        self.service_account_token = service_account_token
        self.session = requests.Session()
        self.session.headers = {"Authorization": f"Bearer {self.service_account_token}"}

    def get_request_info(self, request_id):
        url = f"{self.url}/api/now/table/incident/{request_id}"
        response = self.session.get(url)
        if response.status_code == 200:
            return json.loads(response.content)
        else:
            raise Exception(f"Failed to get request info: {response.content}")

def create_repo_from_servicenow_request(request_id):
    # Get the request info from ServiceNow
    servicenow = ServiceNow("<ServiceNow URL>", "<ServiceNow service account token>")
    request_info = servicenow.get_request_info(request_id)

    # Get the approver ID
    approver_id = request_info["assignment_group"]["sys_id"]

    # Generate a timestamp
    timestamp = datetime.datetime.now().isoformat()

    # Create the repo in GitHub Enterprise Cloud
    github_enterprise_cloud = GitHubEnterpriseCloud("<GitHub Enterprise Cloud URL>", "<GitHub Enterprise Cloud service account token>")
    repo = github_enterprise_cloud.create_repo(
        name=request_info["name"],
        owner=request_info["requester"]["sys_id"],
        permissions=[
            "read",
            "write"
        ],
        tags=[
            approver_id,
            timestamp
        ]
    )

    # Update the ServiceNow record to indicate that the repo has been created
    servicenow.update_record(request_id, repo["url"])

    # Send a webhook to ADMIN_GITHUB
    webhook_payload = {
        "repo_name": repo["name"],
        "repo_url": repo["url"],
        "requester_name": request_info["requester"]["name"],
        "approver_name": request_info["assignment_group"]["name"],
        "timestamp": timestamp
    }
    requests.post("<ADMIN_GITHUB webhook URL>", json=webhook_payload)

if __name__ == "__main__":
    request_id = 1234567890
    create_repo_from_servicenow_request(request_id)
