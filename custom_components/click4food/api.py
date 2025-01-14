import requests
from bs4 import BeautifulSoup
import logging

_LOGGER = logging.getLogger(__name__)

def fetch_click4food_data(username, password, test=False):
    """Fetch data from Click4Food."""
    login_url = "https://click4food.compass-group.be/check.cfm"
    data_page_url = "https://click4food.compass-group.be/WORK/ELL/view/ellclient.cfm"
    data_url = "https://click4food.compass-group.be/Template/cfcFunction.cfm"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        with requests.Session() as session:
            # Login
            login_payload = {
                "txtLogin": username,
                "txtPassword": password,
            }
            login_response = session.post(login_url, data=login_payload, headers=headers)
            if login_response.status_code != 200:
                raise Exception("Login failed: Invalid username or password")

            if test:
                # Als alleen credentials getest moeten worden
                return True

            # Get client details
            html_response = session.get(data_page_url, headers=headers)
            soup = BeautifulSoup(html_response.text, "html.parser")
            option = soup.find("select", {"id": "client"}).find("option", {"value": True, "data-msinstanceno": True})
            client_no = option["value"]
            ms_instance_no = option["data-msinstanceno"]

            # Fetch data
            data_payload = {
                "cfc": "ELL.ellClient",
                "method": "GetClientTicketDetails",
                "dateFrom": "20241107",  # Pas deze aan naar wens
                "dateUntil": "20250107",
                "clientNo": client_no,
                "msInstanceNo": ms_instance_no,
            }
            data_response = session.post(data_url, data=data_payload, headers=headers)
            if data_response.status_code == 200:
                return data_response.json()
            else:
                raise Exception(f"Failed to fetch data: {data_response.status_code}")
    except Exception as e:
        _LOGGER.error(f"Error fetching data from Click4Food: {e}")
        raise
