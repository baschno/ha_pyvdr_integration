import logging
from datetime import timedelta

import voluptuous as vol

from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import (PLATFORM_SCHEMA)
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_TIMEOUT
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
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
ATTR_DISKSTAT_USED_PERCENT = "disksize_used_percent"
ATTR_ICON = "icon"

ICON_VDR_ONLINE = "mdi:television-box"
ICON_VDR_OFFLINE = "mdi:television-classic-off"
ICON_VDR_RECORDING_INSTANT = "mdi:record-rec"
ICON_VDR_RECORDING_TIMER = "mdi:history"
ICON_VDR_RECORDING_NONE = "mdi:close-circle-outline"


STATE_ONLINE = "on"
STATE_OFFLINE = "off"

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=5)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    from pyvdr import PYVDR

    _LOGGER.info('Set up VDR with hostname {}, timeout={}'.format(config['host'], config['timeout']))

    pyvdr_con = PYVDR(hostname=config['host'], timeout=config['timeout'])

    for sensor in pyvdr_con.sensors():
        _LOGGER.info('Setting up sensortype {}'.format(sensor))
        add_entities([VdrSensor(sensor, pyvdr_con)])


class VdrSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, name, pyvdr):
        """Initialize the sensor."""
        self._state = STATE_OFFLINE
        self._name = name
        self._pyvdr = pyvdr
        self._attributes = { 
            ATTR_CHANNEL_NAME: '',
            ATTR_CHANNEL_NUMBER: 0,
            ATTR_DISKSTAT_TOTAL: 0,
            ATTR_DISKSTAT_FREE: 0,
            ATTR_DISKSTAT_USED_PERCENT: 0,
            ATTR_IS_RECORDING: False,
            ATTR_RECORDING_NAME: '',
            ATTR_RECORDING_INSTANT: False,          
        }

    def _initAttributes(self):
        return 
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name.capitalize()

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def state_attributes(self):
        """Return device specific state attributes."""
        return self._attributes

    @property
    def state_icon(self):
        """Return device specific state attributes."""
        return 'mdi:record_rec'

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return ""

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        if self._name is 'Vdrinfo':
            response = self._pyvdr.get_channel()
            self._attributes = {}

            if response is None:
                self._state = STATE_OFFLINE
                self._attributes.update({ATTR_ICON: ICON_VDR_OFFLINE})
                return

            self._state = STATE_ONLINE;
            self._attributes.update({
                ATTR_CHANNEL_NAME: response['name'],
                ATTR_CHANNEL_NUMBER: response['number'],
                ATTR_ICON: ICON_VDR_ONLINE
            })

            response = self._pyvdr.is_recording()
            if response is not None:
                self._attributes.update({
                    ATTR_IS_RECORDING: True,
                    ATTR_RECORDING_NAME: response['name'],
                    ATTR_RECORDING_INSTANT: response['instant'],
                    ATTR_ICON: 
                        ICON_VDR_RECORDING_INSTANT 
                            if response['instant'] == True 
                            else ICON_VDR_RECORDING_TIMER })
            else:
                self._attributes.update({
                    ATTR_IS_RECORDING: False
                })

            response = self._pyvdr.stat()
            if response is not None:
                self._attributes.update({
                    ATTR_DISKSTAT_TOTAL: response[0],
                    ATTR_DISKSTAT_FREE: response[1],
                    ATTR_DISKSTAT_USED_PERCENT: response[2]
                })
