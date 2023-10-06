import requests
import time
import csv
import os

ORG_NAME = os.environ.get('ORG_NAME')
TOKEN_ID = os.environ.get('TOKEN_ID')

BASE_URL = f'https://api.github.com/orgs/{ORG_NAME}/members'
HEADERS = {
    'Authorization': f'token {TOKEN_ID}',
    'Accept': 'application/vnd.github.v3+json'
}

def write_to_csv(filename, data_list):
    if not data_list:
        print(f"No data to write to {filename}!")
        return

    keys = data_list[0].keys()
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data_list)

def check_rate_limit(response):
    """Check the rate limits and pause if needed."""
    if 'X-RateLimit-Remaining' in response.headers and 'X-RateLimit-Reset' in response.headers:
        remaining = int(response.headers['X-RateLimit-Remaining'])
        reset_time = int(response.headers['X-RateLimit-Reset'])

        if remaining == 0:
            delay = reset_time - time.time()
            print(f"Rate limit exceeded. Sleeping for {delay} seconds...")
            time.sleep(delay)

def get_bot_accounts():
    params = {
        'filter': '2fa_disabled' # This parameter helps in filtering users without 2FA which are likely to be bots.
    }
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    response.raise_for_status()

    check_rate_limit(response)

    # Filter out members based on some criteria for bots. 
    # Here, I'm assuming accounts without 2FA are bots.
    # Modify as per your criteria.
    return [member for member in response.json() if not member.get('two_factor_authentication')]



if __name__ == '__main__':
    bot_accounts = get_bot_accounts()
    write_to_csv('bots_output.csv', bot_accounts)




