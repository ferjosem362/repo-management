import requests
import yaml
from datetime import datetime, timedelta

# Configuration
config_data = """
OWNER: SKY-UK
GITHUB_ENTERPRISE_DOMAIN: https://github.com/orgs/sky-uk
"""

config = yaml.safe_load(config_data)

OWNER = config['OWNER']
BASE_URL = f"https://{config['GITHUB_ENTERPRISE_DOMAIN']}/api/v3"
HEADERS = {
    "Accept": "application/vnd.github.v3+json"
}

def get_repos_without_recent_activity():
    """Return a list of repositories without recent activity (90 days)."""
    repos_without_activity = []
    repos_url = f"{BASE_URL}/users/{OWNER}/repos"
    response = requests.get(repos_url, headers=HEADERS)
    repos = response.json()

    for repo in repos:
        repo_name = repo['name']
        commits_url = f"{BASE_URL}/repos/{OWNER}/{repo_name}/commits"
        commits_response = requests.get(commits_url, headers=HEADERS)
        commits = commits_response.json()

        if not commits:
            repos_without_activity.append(repo_name)
            continue

        latest_commit_date = datetime.strptime(commits[0]['commit']['committer']['date'], '%Y-%m-%dT%H:%M:%SZ')
        if latest_commit_date < datetime.now() - timedelta(days=90):
            repos_without_activity.append(repo_name)

    return repos_without_activity

def get_repos_without_admin_access():
    """Return a list of repositories where the user does not have admin access."""
    repos_without_admin = []
    repos_url = f"{BASE_URL}/users/{OWNER}/repos"
    response = requests.get(repos_url, headers=HEADERS)
    repos = response.json()

    for repo in repos:
        repo_name = repo['name']
        permissions = repo['permissions']
        if not permissions.get('admin'):
            repos_without_admin.append(repo_name)

    return repos_without_admin

def main():
    try:
        repos_no_activity = get_repos_without_recent_activity()
        repos_no_admin = get_repos_without_admin_access()

        print("Repositories without activity in the last 90 days:")
        for repo in repos_no_activity:
            print(f"- {repo}")

        print("\nRepositories without admin access:")
        for repo in repos_no_admin:
            print(f"- {repo}")

    except requests.RequestException as e:
        if e.response and e.response.status_code == 401:
            print("Authentication error. Please ensure you're authenticated to your GitHub Enterprise Cloud instance.")
        else:
            print(f"Error occurred: {e}")
# ... [Previous code]

def get_all_pages(url):
    """Fetch all pages of data for a given API endpoint."""
    all_data = []
    while url:
        response = requests.get(url, headers=HEADERS)
        all_data.extend(response.json())
        
        # Check for pagination in the 'Link' header
        link_header = response.headers.get('Link', '')
        if '<' in link_header and '>' in link_header:
            links = {rel[6:-1]: url[url.index('<')+1:url.index('>')].strip('<').strip('>') for url, rel in (link.split(';') for link in link_header.split(','))}
            url = links.get('next')
        else:
            url = None

        # Check rate limits and potentially wait or exit
        remaining_calls = int(response.headers.get('X-RateLimit-Remaining', 0))
        if remaining_calls == 0:
            reset_time = datetime.fromtimestamp(int(response.headers.get('X-RateLimit-Reset')))
            wait_time = (reset_time - datetime.now()).seconds + 1
            print(f"Rate limit reached. Waiting for {wait_time} seconds.")
            time.sleep(wait_time)
    
    return all_data




if __name__ == "__main__":
    main()
