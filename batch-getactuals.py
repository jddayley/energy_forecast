from sense_energy import Senseable
import requests
from datetime import datetime

# Function to format dates in the required format for the URL
def format_date_for_url(date):
    return date.strftime('%Y-%m-%dT%H:%M:%S.000Z')

# Your Sense.com credentials
username = 'jddayley@gmail.com'
password = 'sm@rt0neHere'

# Initialize and authenticate
sense = Senseable()
sense.authenticate(username, password)

# Extract the bearer token
bearer_token = sense.get_auth_token()

# Start and end dates as parameters (you can replace these with desired dates)
start_date = datetime(2023, 12, 1)
end_date = datetime(2024, 1, 1)

# Format dates for the URL
formatted_start = format_date_for_url(start_date)
formatted_end = format_date_for_url(end_date)

# API endpoint with dynamic dates
url = f'https://api.sense.com/apiservice/api/v1/monitors/259485/data?start={formatted_start}&end={formatted_end}&time_unit=DAY&device_id='

# Your Sense.com credentials
username = 'your_username'
password = 'your_password'
def authenticate(self, username, password, ssl_verify=True, ssl_cafile=""):
    """Authenticate with username (email) and password. Optionally set SSL context as well.
    This or `load_auth` must be called once at the start of the session."""
    auth_data = {"email": username, "password": password}

    # Get auth token
    try:
        resp = self.s.post(API_URL + "authenticate", auth_data, headers=self.headers, timeout=self.api_timeout)
    except Exception as e:
        raise Exception("Connection failure: %s" % e)

    # check MFA code required
    if resp.status_code == 401:
        data = resp.json()
        if "mfa_token" in data:
            self._mfa_token = data["mfa_token"]
            raise SenseMFARequiredException(data["error_reason"])

    # check for 200 return
    if resp.status_code != 200:
        raise SenseAuthenticationException(
            "Please check username and password. API Return Code: %s" % resp.status_code
        )

    data = resp.json()
    self._set_auth_data(data)
    self.set_monitor_id(data["monitors"][0]["id"])
# Initialize and authenticate

authenticate(username, password)

# Now, the token should be available in the sense instance
# Extracting the token
bearer_token = sense.get_auth_token()

# ... [rest of your API call script] ...

# Headers
headers = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': '*/*',
    'Authorization': f'bearer {bearer_token}',  # Replace with your token
    'Sec-Fetch-Site': 'same-site',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Sec-Fetch-Mode': 'cors',
    'Host': 'api.sense.com',
    'Origin': 'https://home.sense.com',
    'User-Agent': 'Your User Agent',  # Replace with your user agent
    'Referer': 'https://home.sense.com/',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'x-sense-device-id': '8tx0vb41d92uozswbjag4zrnptc95tkqj0fmcf6sdutrh4w4r12ov86jgxpippn1hb8qdnwv03lazj2ibty90tt6ynqsoet1k5la0n1pda8dno9pivpg1l7cljmhzgax',
    'x-sense-protocol': '11',
    'x-sense-ui-language': 'en-US',
    'x-sense-client-type': 'web'
}

# Make the GET request
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print("Failed to retrieve data:", response.status_code)
