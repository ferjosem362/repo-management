import requests
import time
import csv 
import os

ORG_NAME = os.environ.get('ORG_NAME')
TOKEN_ID = os.environ.get('TOKEN_ID')

# GitHub API URL for fetching teams
TEAMS_API_URL = f'https://api.github.com/orgs/{ORG_NAME}/teams'

# Headers for API requests
HEADERS = {
    'Authorization': f'token {TOKEN_ID}',
    'Accept': 'application/vnd.github.v3+json'
}

# Helper function to handle paginated API endpoints
def fetch_paginated_data(url):
    all_data = []
    while url:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        check_rate_limit(response)
        all_data.extend(response.json())
        # Check if there's a next page
        if 'next' in response.links:
            url = response.links['next']['url']
        else:
            url = None
    return all_data

# Function to handle the API rate limits
def check_rate_limit(response):
    if 'X-RateLimit-Remaining' in response.headers and 'X-RateLimit-Reset' in response.headers:
        remaining = int(response.headers['X-RateLimit-Remaining'])
        reset_time = int(response.headers['X-RateLimit-Reset'])
        if remaining == 0:
            delay = reset_time - time.time()
            print(f"Rate limit exceeded. Sleeping for {delay} seconds...")
            time.sleep(delay)

# Function to write data to CSV
def write_to_csv(filename, data_list):
    if not data_list:
        print(f"No data to write to {filename}!")
        return

    keys = data_list[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:  # Specify encoding as 'utf-8'
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data_list)

# Function to fetch all teams
def fetch_teams():
    return fetch_paginated_data(TEAMS_API_URL)

# Function to fetch members for a specific team
def fetch_team_members(team_slug):
    team_members_url = f"{TEAMS_API_URL}/{team_slug}/members"
    return fetch_paginated_data(team_members_url)

# Main function to fetch team details and their members
def fetch_teams_and_members():
    teams = fetch_teams()
    teams_members_data = []

    for team in teams:
        team_slug = team['slug']
        team_name = team['name']

        members = fetch_team_members(team_slug)

        # Extract member details
        member_details = [{'login': member['login'], 'avatar_url': member['avatar_url']} for member in members]

        teams_members_data.append({
            'team_name': team_name,
            'team_slug': team_slug,
            'members': member_details
        })

    return teams_members_data

if __name__ == '__main__':
    teams_members_data = fetch_teams_and_members()
    flattened_data = []

    # Flatten the data structure for CSV output
    for team_data in teams_members_data:
        for member in team_data['members']:
            flattened_data.append({
                'team_name': team_data['team_name'],
                'team_slug': team_data['team_slug'],
                'member_login': member['login'],
                'member_avatar_url': member['avatar_url']
            })

    # Write to CSV
    write_to_csv('teams_and_members.csv', flattened_data)


