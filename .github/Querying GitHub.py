import os

GITHUB_TOKEN = os.environ.get('GITHUB_PAT')

if not GITHUB_TOKEN:
    raise ValueError("Please set the GITHUB_PAT environment variable with your GitHub token.")

import sqlite3
import requests

# GitHub Configuration
org_name = "SKY-UK"
token = GITHUB_TOKEN
headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"Bearer {token}"
}

# Database Configuration
conn = sqlite3.connect('github_data.db')
cursor = conn.cursor()

# Create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS repos (
    name TEXT,
    commit_date TEXT,
    committer TEXT,
    admin_access BOOLEAN,
    creation_date TEXT,
    creator TEXT,
    archived BOOLEAN,
    size INTEGER
)
''')

# Fetch data from GitHub and store in the database
page = 1
while True:
    response = requests.get(f"https://api.github.com/orgs/{org_name}/repos?per_page=100&page={page}", headers=headers)
    repos = response.json()

    if not repos:
        break

    for repo in repos:
        repo_name = repo['name']
        commits_endpoint = f"https://api.github.com/repos/{org_name}/{repo_name}/commits"
        commits_response = requests.get(commits_endpoint, headers=headers)
        commits = commits_response.json()

    # Check if commits exist for the repo
    if commits and isinstance(commits, list) and 'commit' in commits[0]:
        commit_date = commits[0]['commit']['author']['date']
    else:
        commit_date = "No commits"

        # Insert data into the database
        cursor.execute('''
        INSERT INTO repos (name, commit_date, committer, admin_access, creation_date, creator, archived, size)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (repo['name'], commit_date, committer, repo['permissions']['admin'], repo['created_at'], repo['owner']['login'], repo['archived'], repo['size']))

    page += 1

conn.commit()
conn.close()
