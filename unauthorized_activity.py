# This script source information from GitHub audit logs via GITHUB REST API Calls and obtain whether a particular user is authorized to make commits / PRs in a repo
import os
import requests
import json
import time

# Get GitHub Token and Org from Environment Variables //ideally should be recovered (fetched) from VAULT (CyberArk API), but I am not familiar yet with the REST API connection points
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_ORG = os.getenv("GITHUB_ORG")

# GitHub API Header
HEADERS = {
    'Authorization': f"token {GITHUB_TOKEN}",
    'Accept': 'application/vnd.github.v3+json'
}

# Function to get all repositories with pagination
def get_all_repositories():
    all_repos = []
    page = 1
    while True:
        url = f"https://api.github.com/orgs/{GITHUB_ORG}/repos?page={page}&per_page=100"
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to get repositories: {response.content}")
            break
        repos = json.loads(response.text)
        if not repos:
            break
        all_repos.extend(repos)
        page += 1
        time.sleep(1)  # To avoid hitting rate limits
    return all_repos

# Function to check if a user is authorized to commit to a repo
def is_user_authorized(repo_name, user_login):
    url = f"https://api.github.com/repos/{GITHUB_ORG}/{repo_name}/collaborators/{user_login}/permission"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to get permissions for {user_login} on {repo_name}: {response.content}")
        return False
    permission_data = json.loads(response.text)
    return permission_data['permission'] in ['admin', 'write']

# Function to check unauthorized commit attempts in Audit Logs
def check_unauthorized_commits(repo_name):
    url = f"https://api.github.com/orgs/{GITHUB_ORG}/audit-log?phrase=repo.name:{repo_name}+action:git.push+is:not"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to get audit logs for {repo_name}: {response.content}")
        return
    logs = json.loads(response.text)
    for log in logs:
        user_login = log['user_login']
        if not is_user_authorized(repo_name, user_login):
            print(f"Unauthorized push attempt by {user_login} on {repo_name}")

# Main logic
if __name__ == '__main__':
    all_repos = get_all_repositories()
    print(f"Total Repositories: {len(all_repos)}")

    for repo in all_repos:
        repo_name = repo['name']
        check_unauthorized_commits(repo_name)
        time.sleep(1)  # To avoid hitting rate limits
