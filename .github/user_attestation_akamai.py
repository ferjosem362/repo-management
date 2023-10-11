import requests

# Configure the Akamai API endpoints for user and role attestation.
AKAMAI_API_ENDPOINT_USER_ATTEST = "https://api.akamai.com/user/attest"

# Configure GitHub Enterprise Cloud for SAML authentication.
GITHUB_ENTERPRISE_CLOUD_SAML_METADATA_FILE = "github_enterprise_cloud_saml_metadata.xml"

# Get the SAML application ID in Akamai.
def get_akamai_saml_application_id(akamai_api_key):
    """Gets the SAML application ID in Akamai.

    Args:
        akamai_api_key: The Akamai API key.

    Returns:
        The SAML application ID.
    """

    headers = {"Authorization": f"Bearer {akamai_api_key}"}
    response = requests.get("https://api.akamai.com/saml/applications", headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to get SAML applications in Akamai: {response.status_code} {response.content}")

    return response.json()["applications"][0]["id"]

# Attest a user using the Akamai API and GitHub Enterprise Cloud SAML configuration.
def attest_user(akamai_api_key, github_enterprise_cloud_saml_application_id, user_id, role):
    """Attests a user using the Akamai API and GitHub Enterprise Cloud SAML configuration.

    Args:
        akamai_api_key: The Akamai API key.
        github_enterprise_cloud_saml_application_id: The GitHub Enterprise Cloud SAML application ID.
        user_id: The user ID to attest.
        role: The role to attest.

    Returns:
        A dictionary containing the user's attributes.
    """

    headers = {"Authorization": f"Bearer {akamai_api_key}"}
    data = {"id": user_id, "role": role}

    response = requests.post(
        f"https://api.akamai.com/saml/applications/{github_enterprise_cloud_saml_application_id}/attest/users", headers=headers, data=json.dumps(data)
    )

    if response.status_code != 200:
        raise Exception(f"Failed to attest user in Akamai: {response.status_code} {response.content}")

    return response.json()["attributes"]

user_attributes = attest_user(akamai_api_key, github_enterprise_cloud_saml_application_id, user_id)

print(user_attributes)
