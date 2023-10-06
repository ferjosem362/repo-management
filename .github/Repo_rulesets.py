import requests
import csv
import time
import os

ORG_NAME = os.environ.get('ORG_NAME')
TOKEN_ID = os.environ.get('TOKEN_ID')

BASE_URL_REPOS = f'https://api.github.com/orgs/{ORG_NAME}/repos'
BASE_URL_RULESET = 'https://api.github.com/repos/{}/{}/rulesets'
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

def fetch_paginated_data(url):
    """Fetch data from paginated API endpoints."""
    all_data = []
    while url:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        check_rate_limit(response)
        all_data.extend(response.json())
        if 'next' in response.links:
            url = response.links['next']['url']
        else:
            url = None
    return all_data

def get_rulesets_for_repos():
    repos = fetch_paginated_data(BASE_URL_REPOS)
    all_rulesets = []

    for repo in repos:
        repo_name = repo["name"]
        rulesets = fetch_paginated_data(BASE_URL_RULESET.format(ORG_NAME, repo_name))
        for ruleset in rulesets:
            ruleset_data = {
                "Repo Name": repo_name,
                "Ruleset Name": ruleset.get('name', 'N/A'),
                "Ruleset ID": ruleset.get('id', 'N/A'),
                "Created At": ruleset.get('created_at', 'N/A')
            }
            all_rulesets.append(ruleset_data)

    return all_rulesets

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
    rulesets = get_rulesets_for_repos()
    write_to_csv('rulesets_output.csv', rulesets)
