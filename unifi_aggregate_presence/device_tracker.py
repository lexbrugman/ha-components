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
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([UnifiAggregateEntity(
        entry,
        coordinator,
    )], True)


class UnifiAggregateEntity(CoordinatorEntity, TrackerEntity):
    def __init__(self, entry: ConfigEntry, coordinator):
        super(UnifiAggregateEntity, self).__init__(coordinator)

        self._entry = entry

    @property
    def location_name(self):
        return STATE_HOME if self._is_someone_home() else STATE_NOT_HOME

    @property
    def name(self):
        return self._entry.options.get(CONF_NAME)

    @property
    def source_type(self):
        return SOURCE_TYPE_ROUTER

    @property
    def icon(self):
        return "mdi:map-marker-outline"

    def _online_hosts(self):
        return self.coordinator.data

    def _is_someone_home(self):
        return len(self._online_hosts()) > 0
