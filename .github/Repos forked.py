import github
import csv
import time

# Set the GitHub Enterprise API token
GITHUB_ENTERPRISE_API_TOKEN = "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"
ORG_NAME = "SKY-UK"

# Initialize the GitHub client
gh_client = github.Github(GITHUB_ENTERPRISE_API_TOKEN)

def fetch_repo_info(repo):
    try:
        # Fetch the most recent commit
        last_commit = repo.get_commits().get_page(0)[0] if repo.get_commits().totalCount > 0 else None
        
        # Extract the required information
        repo_name = repo.name
        last_commit_date = last_commit.commit.committer.date if last_commit else "N/A"
        creation_date = repo.created_at
        is_archived = repo.archived

        # Check if the repo is a fork and fetch the original repo's details if it is
        original_repo_date = None
        original_repo_public = None
        original_repo_inside_org = None
        if repo.fork:
            original_repo = gh_client.get_repo(repo.parent.full_name)
            original_repo_date = original_repo.created_at
            original_repo_public = not original_repo.private
            original_repo_inside_org = original_repo.owner.login == ORG_NAME
        
        return {
            "repo_name": repo_name,
            "last_commit_date": last_commit_date,
            "creation_date": creation_date,
            "archived": is_archived,
            "original_repo_date": original_repo_date,
            "original_repo_public": original_repo_public,
            "original_repo_inside_org": original_repo_inside_org
        }
    except github.RateLimitExceededException:
        print("Rate limit exceeded. Waiting for 60 seconds before retrying...")
        time.sleep(60)
        return fetch_repo_info(repo)
    except github.GithubException as e:
        if e.status == 409:
            print(f"Repo {repo.name} is empty. Including repo name and creation date...")
            return {
                "repo_name": repo.name,
                "last_commit_date": "N/A",
                "creation_date": repo.created_at,
                "archived": repo.archived,
                "original_repo_date": None,
                "original_repo_public": None,
                "original_repo_inside_org": None
            }
        else:
            print(f"Error fetching info for repo {repo.name}: {e.status} \"{e.data['message']}\"")
            return None

# Fetch repositories from the specified organization and process them
org = gh_client.get_organization(ORG_NAME)
repos = org.get_repos()
extracted_info = []

for repo in repos:
    repo_data = fetch_repo_info(repo)
    if repo_data:
        extracted_info.append(repo_data)

# Write the extracted information to a CSV file
with open("repository_info.csv", "w", newline="") as csvfile:
    fieldnames = ["repo_name", "last_commit_date", "creation_date", "archived", "original_repo_date", "original_repo_public", "original_repo_inside_org"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for repo_info in extracted_info:
        writer.writerow(repo_info)

print("CSV file has been created!")
