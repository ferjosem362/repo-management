# This script source information from GitHub audit logs via GITHUB REST API Calls and obtain whether a particular user is authorized to make commits / PRs in a repo
# Then, if this happens, send an event to SPLUNK and a WEBHOOK alert to an Slack Channel
import os
import requests
import json
import time

# Fetch GitHub Token and other necessary tokens from the environment
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
SPLUNK_HEC_TOKEN = os.environ.get("SPLUNK_HEC_TOKEN") # Splunk HEC (HTTP Event Collector) Token
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL") # Slack Incoming Webhook URL

# GitHub API Header
HEADERS = {
    'Authorization': f"token {GITHUB_TOKEN}",
    'Accept': 'application/vnd.github.v3+json'
}

GITHUB_ORG = "SKY-UK"  

# Splunk Configuration
SPLUNK_ENDPOINT = "https://splunk_instance_url:8088" # we need to change this to our Splunk instance URL

# Function to send event to Splunk
def send_to_splunk(event):
    headers = {
        "Authorization": f"Splunk {SPLUNK_HEC_TOKEN}"
    }
    data = {
        "event": event
    }
    response = requests.post(f"{SPLUNK_ENDPOINT}/services/collector/event", headers=headers, json=data)
    if response.status_code != 200:
        print(f"Failed to send event to Splunk. Status code: {response.status_code}, Response: {response.text}")

# Function to send a message to Slack
def send_to_slack(message):
    data = {
        "text": message
    }
    response = requests.post(SLACK_WEBHOOK_URL, json=data)
    if response.status_code != 200:
        print(f"Failed to send message to Slack. Status code: {response.status_code}, Response: {response.text}")

# Main logic for checking unauthorized commits and sending alarms
# Function to get all repositories
def get_all_repositories():
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/orgs/{GITHUB_ORG}/repos?type=all&per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS)
        response_data = json.loads(response.text)
        if not response_data or response.status_code != 200:
            if response.headers.get('X-RateLimit-Remaining') == '0':
                reset_time = int(response.headers['X-RateLimit-Reset'])
                sleep_duration = reset_time - int(time.time()) + 5
                print(f"Rate limit exceeded. Waiting for {sleep_duration} seconds")
                time.sleep(sleep_duration)
                continue
            break
        repos.extend(response_data)
        page += 1
    return repos
# Function to check unauthorized commit attempts in Audit Logs
def check_unauthorized_commits(repo):
    repo_name = repo['name']
    url = f"https://api.github.com/orgs/{GITHUB_ORG}/audit-log?phrase=repo.name:{repo_name}+action:git.push+is:not" 
    response = requests.get(url, headers=HEADERS)
    logs = json.loads(response.text)

# Fetch repo collaborators (members with push access, includes teams, admins)
    collaborators = [collab.login for collab in repo.get_collaborators()]
    for log in logs:
        user_login = log['user_login']
        if user_login not in collaborators:
            print(f"Unauthorized push attempt by {user_login} on {repo_name}")
            # Logic to trigger an alarm. Depending on your infrastructure, this can be an API call, an email, etc.
            trigger_alarm(user_login, repo_name)
# Main logic
if __name__ == '__main__':
    repos = get_all_repositories()
    for repo in repos:
        repo_name = repo['name']
        check_unauthorized_commits(repo_name)

def trigger_alarm(user_login, repo_name):
    # Send event to Splunk
    event = {
        "user": user_login,
        "repository": repo_name,
        "action": "Unauthorized push"
    }
    send_to_splunk(event)
    
    # Send alert to Slack
    slack_message = f"ALARM: User {user_login} tried an unauthorized push to {repo_name}!"
    send_to_slack(slack_message)

