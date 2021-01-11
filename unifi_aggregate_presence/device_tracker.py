import logging

from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.device_tracker.const import SOURCE_TYPE_ROUTER
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    STATE_HOME,
    STATE_NOT_HOME,
    CONF_NAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONFIG,
    ENTRIES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][ENTRIES][entry.entry_id]
    config_data = hass.data[DOMAIN][CONFIG]
    async_add_entities([UnifiAggregateEntity(
        coordinator,
        config_data,
    )], True)


class UnifiAggregateEntity(CoordinatorEntity, TrackerEntity):
    def __init__(self, coordinator, config_data: dict):
        super(UnifiAggregateEntity, self).__init__(coordinator)

        self._config_data = config_data

    @property
    def unique_id(self):
        return "unifi-aggregate-anyone"

    @property
    def location_name(self):
        return STATE_HOME if self._is_someone_home() else STATE_NOT_HOME

    @property
    def name(self):
        return self._config_data.get(CONF_NAME)

    @property
    def source_type(self):
        return SOURCE_TYPE_ROUTER

    @property
    def icon(self):
        return "mdi:map-marker-outline"

    @property
    def latitude(self):
        return None

    @property
    def longitude(self):
        return None

    @property
    def device_state_attributes(self):
        return {
            "online_device_count": len(self._online_hosts()),
        }

    def _online_hosts(self):
        return self.coordinator.data

    def _is_someone_home(self):
        return len(self._online_hosts()) > 0
