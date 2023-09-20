import requests
import json

ORG_NAME = 'SKY-UK'
TOKEN = 'YOUR_OAUTH_TOKEN'  

HEADERS = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def rest_call(url):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response

def last_commit(repo):
    url = f"https://api.github.com/repos/{ORG_NAME}/{repo}/commits"
    response = rest_call(url)
    content = response.json()
    try:
        commit_date = content[0]["commit"]["author"]["date"]
        author = content[0]["commit"]["author"]["name"]
        return (commit_date, author)
    except (KeyError, IndexError):
        if "message" in content and content["message"] == "Git Repository is empty.":
            return ("<empty_repo>", "")
        raise Exception(f"Unexpected content for repo {repo}: {content}")

def list_repos():
    repos = []
    url = f"https://api.github.com/orgs/{ORG_NAME}/repos"
    while url:
        print(f"processing repo list {url}")
        response = rest_call(url)
        content = response.json()
        for item in content:
            repo = item["name"]
            print(f"processing repo {repo}")
            commit_date, author = last_commit(repo)
            repos.append((repo, commit_date, author))
        url = response.links.get("next", {}).get("url")
    return repos

try:
    repos = list_repos()
    repos_sorted = sorted(repos, key=lambda r: r[1])
    for r in repos_sorted:
        print(f"{r[0]},{r[1]},{r[2]}")
except requests.RequestException as e:
    print(f"Error making request: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
