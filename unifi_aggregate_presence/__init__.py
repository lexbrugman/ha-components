import datetime
import logging
import voluptuous as vol
from syncasync import sync_to_async
from netaddr import (
    IPAddress,
    IPNetwork,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.core_config import Config
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
    CONFIG,
    ENTRIES,
    CONF_SITE_ID,
    CONF_HOME_SUBNET,
    CONF_FIXED_HOSTS,
    DEFAULT_SCAN_INTERVAL,
)
from .unifi import UnifiClient

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_NAME, default=DEVICE_DEFAULT_NAME): cv.string,
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Required(CONF_SITE_ID): cv.string,
                vol.Required(CONF_HOME_SUBNET): cv.string,
                vol.Optional(CONF_FIXED_HOSTS, default=[]): cv.ensure_list,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)
DEVICE_TRACKERS = [DEVICE_TRACKER]


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    hass.data[DOMAIN] = {
        ENTRIES: {},
        CONFIG: config[DOMAIN],
    }
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    config_data = hass.data[DOMAIN][CONFIG]

    hostname = config_data.get(CONF_HOST)
    username = config_data.get(CONF_USERNAME)
    password = config_data.get(CONF_PASSWORD)
    site_id = config_data.get(CONF_SITE_ID)
    home_subnet = config_data.get(CONF_HOME_SUBNET)
    fixed_hosts = [h.lower() for h in config_data.get(CONF_FIXED_HOSTS)]
    scan_interval = config_data.get(CONF_SCAN_INTERVAL)

    unifi_client = await _async_get_unifi_client(
        hostname,
        username,
        password,
        port=443,
        version="v5",
        site_id=site_id,
    )

    @sync_to_async
    def _async_update_data():
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
            if not client_hostname or client_hostname.lower() in fixed_hosts:
                continue

            online_hosts.append(client_hostname)

        return online_hosts

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_interval=datetime.timedelta(seconds=scan_interval),
        update_method=_async_update_data,
    )
    await coordinator.async_refresh()

    hass.data[DOMAIN][ENTRIES][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, DEVICE_TRACKERS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload.ok = await hass.config_entries.async_unload_platforms(entry, DEVICE_TRACKERS)

    if unload_ok:
        hass.data[DOMAIN][ENTRIES].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)


@sync_to_async
def _async_get_unifi_client(*args, **kwargs):
    return UnifiClient(*args, **kwargs)
