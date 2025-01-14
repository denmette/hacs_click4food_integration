from homeassistant.helpers.entity import Entity
import logging
from .api import fetch_click4food_data

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup the Click4Food sensor via the UI."""
    username = config_entry.data["username"]
    password = config_entry.data["password"]

    async_add_entities([Click4FoodSensor("Click4Food Running Total", username, password)])


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
