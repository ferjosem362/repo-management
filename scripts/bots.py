import requests

# Constants
BASE_URL = "https://api.github.com"
ENTERPRISE_URL = "https://github.com/sky-uk/api/v3"

def get_headers(token):
    """Return the headers with the provided token."""
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

def get_bot_accounts(token):
    """Retrieve a list of bot accounts."""
    bots = []
    page = 1
    while True:
        users_url = f"{ENTERPRISE_URL}/users?page={page}"
        response = requests.get(users_url, headers=get_headers(token))
        users = response.json()
        if not users:
            break
        for user in users:
            if user['type'] == 'Bot':
                bots.append(user['login'])
        page += 1
    return bots

def get_bot_activity(bot_name, token):
    """Retrieve bot activity."""
    activity = {}
    page = 1
    while True:
        events_url = f"{ENTERPRISE_URL}/users/{bot_name}/events?page={page}"
        response = requests.get(events_url, headers=get_headers(token))
        events = response.json()
        if not events:
            break
        for event in events:
            event_type = event['type']
            if event_type in activity:
                activity[event_type] += 1
            else:
                activity[event_type] = 1
        page += 1
    return activity

def get_bot_repositories(bot_name, token):
    """Retrieve repositories to which the bot has permissions."""
    repos = []
    page = 1
    while True:
        repos_url = f"{ENTERPRISE_URL}/users/{bot_name}/repos?page={page}"
        response = requests.get(repos_url, headers=get_headers(token))
        repos_data = response.json()
        if not repos_data:
            break
        for repo in repos_data:
            repos.append(repo['name'])
        page += 1
    return repos

def get_bot_teams(bot_name, token):
    """Retrieve teams which the bot is part of."""
    teams = []
    page = 1
    while True:
        teams_url = f"{ENTERPRISE_URL}/orgs/{bot_name}/teams?page={page}"
        response = requests.get(teams_url, headers=get_headers(token))
        teams_data = response.json()
        if not teams_data:
            break
        for team in teams_data:
            teams.append(team['name'])
        page += 1
    return teams

def main():
    token = input("Please enter your GitHub token: ")
    bots = get_bot_accounts(token)
    for bot in bots:
        print(f"Bot Name: {bot}")
        print("Activity:", get_bot_activity(bot, token))
        print("Repositories:", get_bot_repositories(bot, token))
        print("Teams:", get_bot_teams(bot, token))
        print("-" * 50)

if __name__ == "__main__":
    main()
