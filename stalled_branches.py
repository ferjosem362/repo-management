import requests
import json
import time
import os
from datetime import datetime, timedelta

# Access token (to be set up as env variable)
token = os.getenv('GITHUB_TOKEN')
# Webhook URL for sending notifications
webhook_url = os.getenv('WEBHOOK_URL')

headers = {"Authorization": f"Bearer {token}"}

six_months_ago = datetime.now() - timedelta(days=180)

def run_query(query): 
    for _ in range(3):  # Retry up to 3 times
        response = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            # We hit the rate limit, wait until it resets before trying again
            reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
            sleep_time = max(reset_time - time.time(), 0)
            time.sleep(sleep_time)
        else:
            # Other error, wait a bit before trying again
            time.sleep(1)
    # If we haven't returned by now, all retries have failed, raise an exception
    raise Exception(f"Query failed after multiple attempts: {response.content}")

def get_repos():
    repos = []
    end_cursor = None
    has_next_page = True

    while has_next_page:
        if end_cursor:
            after_argument = f', after: "{end_cursor}"'
        else:
            after_argument = ""

        query = f"""
        {{
            viewer {{
                repositories(first: 100{after_argument}) {{
                    pageInfo {{
                        endCursor
                        hasNextPage
                    }}
                    nodes {{
                        name
                    }}
                }}
            }}
        }}
        """
        result = run_query(query)
        repos_data = result["data"]["viewer"]["repositories"]
        repos.extend([repo["name"] for repo in repos_data["nodes"]])
        has_next_page = repos_data["pageInfo"]["hasNextPage"]
        end_cursor = repos_data["pageInfo"]["endCursor"]

    return repos

def get_branches(repo):
    branches = []
    end_cursor = None
    has_next_page = True

    while has_next_page:
        if end_cursor:
            after_argument = f', after: "{end_cursor}"'
        else:
            after_argument = ""

        query = f"""
        {{
            repository(owner:"your-github-login", name:"{repo}") {{
                refs(refPrefix:"refs/heads/", first: 100{after_argument}) {{
                    pageInfo {{
                        endCursor
                        hasNextPage
                    }}
                    nodes {{
                        name
                        target {{
                            ... on Commit {{
                                committedDate
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        result = run_query(query)
        branches_data = result["data"]["repository"]["refs"]
        branches.extend(branches_data["nodes"])
        has_next_page = branches_data["pageInfo"]["hasNextPage"]
        end_cursor = branches_data["pageInfo"]["endCursor"]

    return branches

def check_branches():
    report = []
    for repo in get_repos():
        for branch in get_branches(repo):
            commit_date = datetime.strptime(branch["target"]["committedDate"], "%Y-%m-%dT%H:%M:%Z")
            if commit_date < six_months_ago:
                report.append((repo, branch["name"]))
    return report

def send_notification(report):
    report_string = "\n".join([f"Repo: {repo}, Branch: {branch}" for repo, branch in report])
    data = {"text": report_string}
    response = requests.post(webhook_url, json=data)
    print(response.status_code)
    print(response.text)

report = check_branches()
send_notification(report)
