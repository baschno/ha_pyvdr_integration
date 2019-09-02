import logging

import voluptuous as vol

from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import (PLATFORM_SCHEMA)
from homeassistant.const import CONF_HOST, CONF_PORT
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default=6419): cv.port,
})

STATE_ATTR_CHANNEL_NAME = 'name'
STATE_ATTR_CHANNEL_NUMBER = 'number'
STATE_ATTR_RECORDING_NAME = 'name'
STATE_ATTR_RECORDING_INSTANT = 'instant'

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    from pyvdr import PYVDR

    pyvdr_con = PYVDR(hostname='easyvdr.fritz.box')

    _LOGGER.info('vor setup')
    for sensor in pyvdr_con.sensors():
        _LOGGER.info('Setting up sensortype {}'.format(sensor))
        add_entities([VdrSensor(sensor, pyvdr_con)])


class VdrSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, name, pyvdr):
        """Initialize the sensor."""
        self._state = None
        self._attributes = None
        self._name = name
        self._pyvdr = pyvdr

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

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        if self._name is 'channel':
            response = self._pyvdr.get_channel()
            self._state = response['name'];

            self._attributes = {}
            self._attributes.update({
                STATE_ATTR_CHANNEL_NAME: response['name'],
                STATE_ATTR_CHANNEL_NUMBER: response['number']
            })

        if self._name is 'is_recording':
            response = self._pyvdr.is_recording()
            if response is None:
                self._state = 'off'
                self._attributes = {}
            else:
                self._state = 'on'
                self._attributes = {}
                self._attributes.update({
                    STATE_ATTR_RECORDING_NAME: response['name'],
                    STATE_ATTR_RECORDING_INSTANT: response['instant'],
                    'icon': 'mdi:record-rec' })

