import requests
from bs4 import BeautifulSoup
import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

LOGIN_URL = "https://click4food.compass-group.be/check.cfm"
DATA_PAGE_URL = "https://click4food.compass-group.be/WORK/ELL/view/ellclient.cfm"
DATA_URL = "https://click4food.compass-group.be/Template/cfcFunction.cfm"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": LOGIN_URL,
    "X-Requested-With": "XMLHttpRequest",
}

async def login_to_click4food(username, password):
    """
    Asynchronous login to Click4Food and return an aiohttp.ClientSession.
    """
    session = aiohttp.ClientSession()
    login_payload = {
        "txtLogin": username,
        "txtPassword": password,
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        async with session.post(LOGIN_URL, data=login_payload, headers=headers) as response:
            if response.status != 200:
                _LOGGER.error(f"Login failed with status code: {response.status}")
                raise Exception("Invalid username or password")

            cookies = response.cookies
            if "JSESSIONID" not in cookies:
                _LOGGER.error("JSESSIONID cookie not found after login")
                raise Exception("Invalid username or password")

            _LOGGER.debug("Login successful")
            return session  # Retourneer de sessie voor verder gebruik

    except Exception as e:
        await session.close()  # Zorg dat de sessie wordt gesloten bij fouten
        _LOGGER.error(f"Login error: {e}")
        raise

def fetch_click4food_data(session):
    """
    Fetch data from Click4Food using an active session.
    """
    # Haal client details op
    html_response = session.get(DATA_PAGE_URL, headers=HEADERS)
    if html_response.status_code != 200:
        _LOGGER.error(f"Failed to fetch HTML page with status code: {html_response.status_code}")
        raise Exception("Failed to fetch HTML page")

    soup = BeautifulSoup(html_response.text, "html.parser")
    option = soup.find("select", {"id": "client"}).find("option", {"value": True, "data-msinstanceno": True})

    if not option:
        _LOGGER.error("Client option not found in HTML response")
        raise Exception("Client option not found")

    client_no = option["value"]
    ms_instance_no = option["data-msinstanceno"]

    # Haal gegevens op
    data_payload = {
        "cfc": "ELL.ellClient",
        "method": "GetClientTicketDetails",
        "dateFrom": "20241107",  # Pas aan naar wens
        "dateUntil": "20250107",
        "clientNo": client_no,
        "msInstanceNo": ms_instance_no,
    }
    data_response = session.post(DATA_URL, data=data_payload, headers=HEADERS)

    if data_response.status_code != 200:
        _LOGGER.error(f"Failed to fetch data with status code: {data_response.status_code}")
        _LOGGER.debug(f"Response text: {data_response.text}")
        raise Exception("Failed to fetch data")

    return data_response.json()
