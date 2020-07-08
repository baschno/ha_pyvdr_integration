import logging
from datetime import timedelta

import voluptuous as vol

from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import (PLATFORM_SCHEMA)
from homeassistant.const import (
    CONF_NAME,
    CONF_HOST,
    CONF_PORT,
    CONF_TIMEOUT,
    UNIT_PERCENTAGE,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_DEFAULT_NAME = "vdr"

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=CONF_DEFAULT_NAME): cv.string,
    vol.Optional(CONF_PORT, default=6419): cv.port,
    vol.Optional(CONF_TIMEOUT, default=10): cv.byte,
})

ATTR_CHANNEL_NAME = 'channel_name'
ATTR_CHANNEL_NUMBER = 'channel_number'
ATTR_RECORDING_NAME = 'recording_name'
ATTR_RECORDING_INSTANT = 'recording_instant'
ATTR_IS_RECORDING = "is_recording"
ATTR_DISKSTAT_TOTAL = "disksize_total"
ATTR_DISKSTAT_FREE = "disksize_free"
ATTR_SENSOR_NAME = 0
ATTR_ICON = 1
ATTR_UNIT = 2

ICON_VDR_ONLINE = "mdi:television-box"
ICON_VDR_OFFLINE = "mdi:television-classic-off"
ICON_VDR_RECORDING_INSTANT = "mdi:record-rec"
ICON_VDR_RECORDING_TIMER = "mdi:history"
ICON_VDR_RECORDING_NONE = "mdi:close-circle-outline"

SENSORS = ['vdrinfo', 'diskinfo']
#SENSORS = ['vdrinfo']

SENSOR_TYPES = {
    "vdrinfo" : ['Info', 'mdi:television-box', ""],
    'diskusage': ['Disk usage', 'mdi:harddisk', UNIT_PERCENTAGE]
}

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=5)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    from pyvdr import PYVDR


    conf_name = config.get(CONF_NAME)
    host = config.get(CONF_HOST)
    _LOGGER.info('Config {}, name {}'.format(config, conf_name))
    _LOGGER.info('Set up VDR with hostname {}, timeout={}'.format(host, config['timeout']))

    pyvdr_con = PYVDR(hostname=host)

    entities = []
    for sensor_type in SENSOR_TYPES:
        _LOGGER.info('Setting up sensortype {}'.format(sensor_type))
        entities.append(VdrSensor(sensor_type, conf_name, pyvdr_con))

    add_entities(entities)


class VdrSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, sensor_type, conf_name, pyvdr):
        """Initialize the sensor."""
        self._state = STATE_OFF
        self._sensor_type = sensor_type
        self.type = 'lsfjskd'

        self._name = '_'.join([conf_name, sensor_type])
        self.friendly_name = SENSOR_TYPES[sensor_type][ATTR_SENSOR_NAME]
        self._pyvdr = pyvdr
        self._init_attributes()


    def _init_attributes(self):
        if self._sensor_type == 'vdrinfo':
            self._attributes = {
                ATTR_CHANNEL_NAME: '',
                ATTR_CHANNEL_NUMBER: 0
            }

        if self._sensor_type == 'diskusage':
            self._attributes = {
                ATTR_DISKSTAT_TOTAL: 0,
                ATTR_DISKSTAT_FREE: 0
            }

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def state_attributes(self):
        """Return device specific state attributes."""
        return self._attributes

    @property
    def icon(self):
        """Return device specific state attributes."""
        return SENSOR_TYPES[self._sensor_type][ATTR_ICON]

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return SENSOR_TYPES[self._sensor_type][ATTR_UNIT]

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = STATE_OFF

        if self._sensor_type == 'vdrinfo':
            response = self._pyvdr.get_channel()
            self._attributes = {}

            if response is None:
                return

            self._state = response['name']
            self._attributes.update({
                ATTR_CHANNEL_NAME: response['name'],
                ATTR_CHANNEL_NUMBER: response['number'],
                ATTR_ICON: ICON_VDR_ONLINE
            })

            return

        if self._sensor_type == 'diskusage':
            response = self._pyvdr.stat()
            if response is not None and len(response)==3:
                self._state = response[2]
                self._attributes.update({
                    ATTR_DISKSTAT_TOTAL: int(response[0]),
                    ATTR_DISKSTAT_FREE: int(response[1])
                })
            return