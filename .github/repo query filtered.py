import csv
import datetime
import time
from github import Github, GithubException

# Constants
GITHUB_API_TOKEN = "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"
ORG_NAME = "SKY-UK"
INPUT_CSV = "repository_info.csv"
OUTPUT_CSV = "filtered_repos_info.csv"
SLEEP_DURATION = 60  # Duration to sleep when rate limit is reached, in seconds

# Initialize GitHub client
gh_client = Github(GITHUB_API_TOKEN)

# Calculate the cutoff date for filtering repositories
cutoff_date = datetime.datetime.now() - datetime.timedelta(days=18*30)

filtered_repos = []

# Read the CSV and filter repositories
# Read the CSV and filter repositories
with open(INPUT_CSV, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Handle date-time format in the CSV
        creation_date = datetime.datetime.strptime(row['creation_date'], '%Y-%m-%d %H:%M:%S')
        if creation_date >= cutoff_date:
            filtered_repos.append(row['repo_name'])

# Extract required information for each filtered repository
repo_data = []
for repo_name in filtered_repos:
    try:
        repo = gh_client.get_repo(f"{ORG_NAME}/{repo_name}")
        
        # Get the latest commit and committer's name
        try:
            last_commit = repo.get_commits()[0]
            committer_name = last_commit.committer.login
        except Exception:
            committer_name = repo.owner.login  # Fallback to repo creator's name
        
        # Get repo size
        repo_size = repo.size
        
        # Get languages used in the repo
        languages = ", ".join(repo.get_languages().keys())
        
        # Check for admin other than GitHub Enterprise ones
        has_external_admin = False
        for collaborator in repo.get_collaborators():
            if collaborator.permissions.admin and not collaborator.site_admin:
                has_external_admin = True
                break
        
        repo_data.append({
            "repo_name": repo_name,
            "committer_name": committer_name,
            "repo_size_kb": repo_size,
            "languages": languages,
            "has_external_admin": has_external_admin
        })
    except GithubException as e:
        if e.status == 403 and "API rate limit exceeded" in e.data.get("message", ""):
            print("API rate limit reached. Sleeping for a while...")
            time.sleep(SLEEP_DURATION)
        else:
            print(f"Error processing repo {repo_name}: {e}")

# Write the extracted information to a new CSV file
with open(OUTPUT_CSV, 'w', newline='') as csvfile:
    fieldnames = ["repo_name", "committer_name", "repo_size_kb", "languages", "has_external_admin"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for data in repo_data:
        writer.writerow(data)

print(f"Data written to {OUTPUT_CSV}")
