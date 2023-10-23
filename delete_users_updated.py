from github import Github, GithubException
import time
import datetime
import os
import csv
MAX_RETRIES = 3
RETRY_WAIT_TIME = 60  # 60 seconds

# Retrieve the GitHub token from the environment variable
os.environ['GITHUB_TOKEN'] = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
github_token = os.environ.get('GITHUB_TOKEN')
if not github_token:
    raise ValueError("Please set the GITHUB_TOKEN environment variable.")

# Start a GitHub session using the token from the environment variable
g = Github(github_token)

# Get the organization object by its name
enterprise_organization = ["SKY-UK"]

# Get the current time
now = datetime.datetime.now()

# Threshold for account inactivity (in days)
inactivity_threshold = 180  # 6 months

# List to store potentially affected users
users_to_remove = []
def check_rate_limit():
    rate_limit = g.get_rate_limit()
    remaining = rate_limit.core.remaining
    if remaining < 10:  # Adjust this threshold as needed
        print(f"Low rate limit detected: {remaining} remaining. Waiting for {RETRY_WAIT_TIME} seconds...")
        time.sleep(RETRY_WAIT_TIME)

def get_organization_repos(org_name):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            check_rate_limit()
            org = g.get_organization(org_name)
            return org.get_repos()
        except GithubException as e:
            print(f"Error fetching repos for organization {org_name}: {e}. Retrying...")
            retries += 1
            time.sleep(RETRY_WAIT_TIME)
    print(f"Failed to fetch repos for organization {org_name} after {MAX_RETRIES} retries.")
    return []
# Get a list of all organizations in the enterprise
for org_name in enterprise_organization:
    org=g.get_organization(org_name)
    print(f"Organization: {org.login}")

    # List all users in the organization
    for user in org.get_members():
        print(f"User: {user.login}")

        # Find the most recent activity for this user
        most_recent_activity = None
        for repo in user.get_repos():
            if most_recent_activity is None or repo.updated_at > most_recent_activity:
                most_recent_activity = repo.updated_at

        # If the user has no activity or their most recent activity is older than the threshold, add them to the list
        if most_recent_activity is None or (now - most_recent_activity).days > inactivity_threshold:
            users_to_remove.append({'username': user.login, 'email': user.email, 'last_activity_date': most_recent_activity})

# Write potentially affected users to a CSV file
csv_filename = 'users_to_remove.csv'
with open(csv_filename, 'w', newline='') as csvfile:
    fieldnames = ['Username', 'Email', 'Last Activity Date']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for user in users_to_remove:
        writer.writerow(user)

print(f"Potentially affected users written to {csv_filename}.")

# Confirm removal of users
confirmation = input("Do you want to remove the listed users? (yes/no): ")
if confirmation.lower() == 'yes':
    for user_info in users_to_remove:
        user = g.get_user(user_info['username'])
        org.remove_from_members(user)
        print(f"Removed user {user_info['username']} from the organization.")
else:
    print("No users were removed.")
