import requests
import csv
import time
import os

ORG_NAME = os.environ.get('ORG_NAME')
TOKEN_ID = os.environ.get('TOKEN_ID')

BASE_URL = f'https://api.github.com/orgs/{ORG_NAME}/installations'
HEADERS = {
    'Authorization': f'token {TOKEN_ID}',
    'Accept': 'application/vnd.github.v3+json'
}

def check_rate_limit(response):
    """Check the rate limits and pause if needed."""
    if 'X-RateLimit-Remaining' in response.headers and 'X-RateLimit-Reset' in response.headers:
        remaining = int(response.headers['X-RateLimit-Remaining'])
        reset_time = int(response.headers['X-RateLimit-Reset'])

        if remaining == 0:
            delay = reset_time - time.time()
            print(f"Rate limit exceeded. Sleeping for {delay} seconds...")
            time.sleep(delay)

def get_installed_apps():
    response = requests.get(BASE_URL, headers=HEADERS)
    response.raise_for_status()

    check_rate_limit(response)

    return response.json()['installations']

def get_last_commit_date(repo_name):
    commits_url = f'https://api.github.com/repos/{ORG_NAME}/{repo_name}/commits'
    commits_response = requests.get(commits_url, headers=HEADERS)
    check_rate_limit(commits_response)

    commits = commits_response.json()
    if isinstance(commits, list) and commits and 'commit' in commits[0] and 'committer' in commits[0]['commit']:
        return commits[0]['commit']['committer']['date']
    return 'N/A'


def extract_app_details():
    installed_apps = get_installed_apps()

    detailed_apps = []
    for app in installed_apps:
        app_id = app['app_id']
        app_slug = app['app_slug']

        app_url = f"https://api.github.com/apps/{app_slug}"
        app_details_response = requests.get(app_url, headers=HEADERS)
        app_details = app_details_response.json()

        last_commit_date = get_last_commit_date(app_slug)  
        detailed_apps.append({
            "App Name": app_details.get('name', 'N/A'),
            "App ID": app_id,
            "Description": app_details.get('description', 'N/A'),
            "Homepage": app_details.get('homepage_url', 'N/A'),
            "Created At": app_details.get('created_at', 'N/A'),
            "Last Commit Date": last_commit_date,
            "Authentication": app_details.get('authentication', 'N/A')  # Assuming 'authentication' key exists
        })

    return detailed_apps

def write_to_csv(filename, data_list):
    if not data_list:
        print(f"No data to write to {filename}!")
        return

    keys = data_list[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data_list)

if __name__ == '__main__':
    apps = extract_app_details()
    write_to_csv('apps_output.csv', apps)
