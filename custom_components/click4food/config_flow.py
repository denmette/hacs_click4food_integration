from homeassistant import config_entries
import voluptuous as vol
from homeassistant.core import callback

DOMAIN = "click4food"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

class Click4FoodConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Click4Food."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]

            # Valideer de inloggegevens
            if await self._test_credentials(username, password):
                return self.async_create_entry(
                    title="Click4Food",
                    data={CONF_USERNAME: username, CONF_PASSWORD: password},
                )
            else:
                errors["base"] = "invalid_auth"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def _test_credentials(self, username, password):
        """Test de inloggegevens."""
        try:
            from .api import login_to_click4food

            # Test alleen de login
            login_to_click4food(username, password)
            return True
        except Exception as e:
            _LOGGER.error(f"Credential test failed: {e}")
            return False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return Click4FoodOptionsFlow(config_entry)


class Click4FoodOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Click4Food."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME, default=self.config_entry.data[CONF_USERNAME]): str,
                vol.Required(CONF_PASSWORD, default=self.config_entry.data[CONF_PASSWORD]): str,
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)
