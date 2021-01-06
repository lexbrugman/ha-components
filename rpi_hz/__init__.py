import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME,
    CONF_UNIT_OF_MEASUREMENT,
)
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_PORTS,
    CONF_MULTIPLIER,
)

PORT_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): cv.string,
    vol.Optional(CONF_MULTIPLIER, default=1): cv.positive_int,
    vol.Optional(CONF_UNIT_OF_MEASUREMENT, default="Hz"): cv.string,
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_PORTS): vol.Schema({cv.positive_int: PORT_SCHEMA}),
})
