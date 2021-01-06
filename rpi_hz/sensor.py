import logging
from time import time

from homeassistant.components import rpi_gpio
from homeassistant.const import (
    CONF_NAME,
    DEVICE_DEFAULT_NAME,
    CONF_UNIT_OF_MEASUREMENT,
)
from homeassistant.helpers.entity import Entity

from .const import (
    DOMAIN,
    CONF_PORTS,
    CONF_MULTIPLIER,
    PULL_MODE,
)

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, discovery_info=None):
    sensors = []
    ports = config.get(CONF_PORTS)

    for port, config_data in ports.items():
        name = config_data.get(CONF_NAME)
        multiplier = config_data.get(CONF_MULTIPLIER)
        unit = config_data.get(CONF_UNIT_OF_MEASUREMENT)
        sensors.append(RPiGPIOSensor(name, port, multiplier, unit))

    add_devices(sensors)


class RPiGPIOSensor(Entity):
    def __init__(self, name, port, multiplier, unit):
        self._name = name or DEVICE_DEFAULT_NAME
        self._port = port
        self._multiplier = multiplier
        self._unit = unit
        self._counter = 0
        self._state = None
        self._last_update_time = time()

        rpi_gpio.setup_input(self._port, PULL_MODE)
        rpi_gpio.edge_detect(self._port, self._edge_detected, 1)

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return self._unit

    @property
    def should_poll(self):
        return True

    def update(self):
        now = time()

        seconds_since_last_update = now - self._last_update_time
        counter = self._counter

        self._counter = 0
        self._last_update_time = now

        self._state = round(counter / seconds_since_last_update * self._multiplier)

    def _edge_detected(self, port):
        self._counter += 0.5
