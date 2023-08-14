from github import Github
import datetime
import os

# Retrieve the GitHub token from the environment variable
github_token = os.environ.get('GITHUB_TOKEN')
if not github_token:
    raise ValueError("Please set the GITHUB_TOKEN environment variable.")

# Start a GitHub session using the token from the environment variable
g = Github(github_token)

# Get the enterprise object by its name
enterprise = g.get_enterprise("SKY-UK")

# Get the current time
now = datetime.datetime.now()

# Threshold for account inactivity (in days)
inactivity_threshold = 365  # 1 year

# Get a list of all organizations in the enterprise
for org in enterprise.get_organizations():
    print(f"Organization: {org.login}")

    # List all users in the organization
    for user in org.get_members():
        print(f"User: {user.login}")

        # Find the most recent activity for this user
        most_recent_activity = None
        for repo in user.get_repos():
            if repo.updated_at > most_recent_activity:
                most_recent_activity = repo.updated_at

        # If the user has no activity or their most recent activity is older than the threshold, remove them
        if most_recent_activity is None or (now - most_recent_activity).days > inactivity_threshold:
            print(f"Removing user {user.login} due to inactivity.")
            org.remove_from_members(user)
