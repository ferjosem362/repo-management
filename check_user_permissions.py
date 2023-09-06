# This script scans permissions in a given repo to see whether a particular user is authorized to PRs or commits
import os
from github import Github

# Assume GitHub Token is stored as an environment variable (not ideal solution, should be fetched from CyberArk, or any other Secrets manager tool)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

# Initialize GitHub API client
g = Github(GITHUB_TOKEN)

# Your GitHub Organization
org = g.get_organization("YourOrgName")

def check_repo_permissions(repo):
    collaborators = repo.get_collaborators()
    for collaborator in collaborators:
        permissions = repo.get_collaborator_permission(collaborator)
        if permissions == 'write' or permissions == 'admin':
            print(f"User {collaborator.login} has write or admin permissions on {repo.full_name}")
            # Here, you can add logic to check if this collaborator is authorized
            # If not, take appropriate action, like sending an alert

# Paginate through repositories in the organization
repos = org.get_repos(type='all')
for repo in repos:
    check_repo_permissions(repo)
