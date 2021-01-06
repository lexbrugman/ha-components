import datetime
import logging
import voluptuous as vol
from netaddr import (
    IPAddress,
    IPNetwork,
)

from homeassistant.components.device_tracker import PLATFORM_SCHEMA
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import (
    Config,
    HomeAssistant,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.components.device_tracker import DOMAIN as DEVICE_TRACKER
from homeassistant.const import (
    DEVICE_DEFAULT_NAME,
    CONF_NAME,
    CONF_HOST,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
)

from .const import (
    DOMAIN,
    CONF_SITE_ID,
    CONF_HOME_SUBNET,
    CONF_FIXED_DEVICES,
    DEFAULT_SCAN_INTERVAL,
)
from .unifi import UnifiClient

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEVICE_DEFAULT_NAME): cv.string,
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_SITE_ID): cv.string,
    vol.Required(CONF_HOME_SUBNET): cv.string,
    vol.Optional(CONF_FIXED_DEVICES, default=[]): cv.ensure_list,
})


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hostname = entry.options.get(CONF_HOST)
    username = entry.options.get(CONF_USERNAME)
    password = entry.options.get(CONF_PASSWORD)
    site_id = entry.options.get(CONF_SITE_ID)
    home_subnet = entry.options.get(CONF_HOME_SUBNET)
    fixed_devices = entry.options.get(CONF_FIXED_DEVICES)
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    unifi_client = UnifiClient(
        hostname,
        username,
        password,
        port=443,
        version="v5",
        site_id=site_id,
    )

    async def async_update_data():
        online_hosts = []

        try:
            wireless_clients = unifi_client.get_wireless_clients()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with UniFi controller: {err}")

        for wireless_client in wireless_clients:
            ip_address = wireless_client.get("ip", "")
            if not ip_address or not IPAddress(ip_address) in IPNetwork(home_subnet):
                continue

            client_hostname = wireless_client.get("name", wireless_client.get("hostname", ""))
            if not client_hostname or client_hostname in fixed_devices:
                continue

            online_hosts.append(client_hostname)

        return online_hosts

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_interval=datetime.timedelta(minutes=scan_interval),
        update_method=async_update_data,
    )
    await coordinator.async_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, DEVICE_TRACKER)
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, DEVICE_TRACKER)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)
