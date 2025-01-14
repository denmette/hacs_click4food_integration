from homeassistant.helpers.entity import Entity
import logging
from .api import login_to_click4food, fetch_click4food_data

_LOGGER = logging.getLogger(__name__)

async def async_update(self):
    try:
        # Login en verkrijg een sessie
        session = login_to_click4food(self._username, self._password)

        # Haal gegevens op met de sessie
        data = fetch_click4food_data(session)
        running_total = next(
            (group["KEY"]["RUNNING_TOTAL"] for group in data["QRYDETAILSGROUPED"] if "RUNNING_TOTAL" in group["KEY"]),
            None,
        )
        self._state = running_total if running_total is not None else "Niet beschikbaar"
    except Exception as e:
        _LOGGER.error(f"Error updating Click4Food sensor: {e}")

class Click4FoodSensor(Entity):
    def __init__(self, name, username, password):
        self._name = name
        self._username = username
        self._password = password
        self._state = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        try:
            data = await fetch_click4food_data(self._username, self._password)
            running_total = next(
                (group["KEY"]["RUNNING_TOTAL"] for group in data["QRYDETAILSGROUPED"] if "RUNNING_TOTAL" in group["KEY"]),
                None,
            )
            self._state = running_total if running_total is not None else "Niet beschikbaar"
        except Exception as e:
            _LOGGER.error(f"Error updating Click4Food sensor: {e}")
