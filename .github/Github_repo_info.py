import octokit
import csv

# Set the GitHub Enterprise API token
GITHUB_ENTERPRISE_API_TOKEN = "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"

# Create an Octokit client
octokit_client = octokit(github_token=GITHUB_ENTERPRISE_API_TOKEN)

# Get the name of the Enterprise
enterprise_name = octokit_client.enterprise.get()["name"]

# Get a list of all of the repositories in the Enterprise
repositories = octokit_client.enterprise.repositories.list(organization=enterprise_name)

# Extract the information you need for each repository
extracted_info = []
for repository in repositories:
    repository_info = octokit_client.repositories.get(repository_id=repository["id"])
    extracted_info.append({
        "date_of_creation": repository_info["created_at"],
        "creator": repository_info["owner"]["login"],
        "last_commit_date": repository_info["pushed_at"],
        "last_committer": repository_info["pushed_by"]["login"],
        "public": repository_info["public"]
    })

# Write the extracted information to a CSV file
with open("repository_info.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["date_of_creation", "creator", "last_commit_date", "last_committer", "public"])
    for repository_info in extracted_info:
        writer.writerow([repository_info["date_of_creation"], repository_info["creator"], repository_info["last_commit_date"], repository_info["last_committer"], repository_info["public"]])
