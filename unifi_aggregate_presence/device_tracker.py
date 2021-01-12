import logging
from time import time

from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.device_tracker.const import SOURCE_TYPE_ROUTER
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    STATE_HOME,
    STATE_NOT_HOME,
)
from homeassistant.core import (
    callback,
    HomeAssistant,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    AWAY_GRACE_TIME,
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
        self._last_home_time = time()

    @property
    def unique_id(self):
        return "unifi-aggregate-anyone"

    @property
    def location_name(self):
        if self._seconds_since_last_home() <= AWAY_GRACE_TIME:
            return STATE_HOME

        return STATE_NOT_HOME

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
            "online_device_count": self._online_host_count(),
        }
    
    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_listener(self._state_updated)
        )
    
    @callback
    def _state_updated(self) -> None:
        if self._is_someone_home():
            self._last_home_time = time()

    def _online_hosts(self) -> list:
        return self.coordinator.data

    def _online_host_count(self) -> int:
        return len(self._online_hosts())

    def _is_someone_home(self) -> bool:
        return self._online_host_count() > 0

    def _seconds_since_last_home(self) -> float:
        return time() - self._last_home_time
