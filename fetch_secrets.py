# This scripts uses CyberArk's Conjur Secret Fetcher to retrieve Secrets from CyberArk
# Import requests library
import requests

# Define the Conjur URL, account, authn_id and secrets
conjur_url = "https://conjur.cyberark.com:8443"
conjur_account = "my-account"
conjur_authn_id = "my-authn-id"
conjur_secrets = "github-token"

# Construct the Conjur authentication URL
conjur_authn_url = f"{conjur_url}/authn/{conjur_account}/{conjur_authn_id}/authenticate"

# Get the Conjur access token by sending a POST request with the API key
api_key = "my-api-key"
response = requests.post(conjur_authn_url, data=api_key)
response.raise_for_status()
access_token = response.text

# Encode the access token in base64 format
import base64
encoded_token = base64.b64encode(access_token.encode("utf-8")).decode("utf-8")

# Construct the Conjur secrets URL
conjur_secrets_url = f"{conjur_url}/secrets/{conjur_account}/variable/{conjur_secrets}"

# Get the Conjur secret value by sending a GET request with the access token
headers = {"Authorization": f"Token token=\"{encoded_token}\""}
response = requests.get(conjur_secrets_url, headers=headers)
response.raise_for_status()
secret_value = response.text

# Print the secret value
print(secret_value)
