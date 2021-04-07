"""Support for Switchbot Curtain."""
from typing import Any, Dict
from datetime import timedelta

# pylint: disable=import-error, no-member
from . import SwitchbotCurtain
import voluptuous as vol
import logging

from homeassistant.const import CONF_MAC, CONF_NAME, CONF_PASSWORD, STATE_OPEN, STATE_CLOSED, STATE_OPENING, \
    STATE_CLOSING
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.restore_state import RestoreEntity

# Import the device class
from homeassistant.components.cover import (
    CoverEntity, PLATFORM_SCHEMA, DEVICE_CLASS_CURTAIN, ATTR_POSITION,
    SUPPORT_OPEN, SUPPORT_CLOSE, SUPPORT_STOP, SUPPORT_SET_POSITION,
)

# Initialize the logger
_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Switchbot Curtain"
SCAN_INTERVAL = timedelta(seconds=3600)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MAC): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_PASSWORD): cv.string,
        vol.Optional("reverse", default=False): cv.boolean,
        vol.Optional("time_between_update_command", default=10): cv.positive_int
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Perform the setup for Switchbot devices."""
    name = config.get(CONF_NAME)
    mac_addr = config[CONF_MAC]
    password = config.get(CONF_PASSWORD)
    reverse = config.get("reverse")
    time_between_update_command = config.get("time_between_update_command")
    add_entities([SwitchBotCurtain(mac=mac_addr, name=name, password=password, reverse_mode=reverse,
                                   time_between_update_command=time_between_update_command)], True)


class SwitchBotCurtain(CoverEntity, RestoreEntity):
    """Representation of a Switchbot."""

    def __init__(self, mac, name, password, reverse_mode=False, time_between_update_command=10) -> None:
        """Initialize the Switchbot."""

        self._state = None
        self._last_run_success = None
        self._name = name
        self._mac = mac
        self._device = SwitchbotCurtain(mac=mac, password=password, reverse_mode=reverse_mode,
                                        time_between_update_command=time_between_update_command)

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        if not state:
            return
        _LOGGER.info('Switchbot state %s', state)
        self._state = state.state

    @property
    def assumed_state(self) -> bool:
        """Return true if unable to access real state of entity.

        Should return False, but default cover card disables
        open if position=100 / close if position=0. See frontend/src/util/cover-model.js
        This is a problem if reversed=False. Easy fix return not is_reversed """
        return not self._device.is_reversed()

    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state.

        False if entity pushes its state to HA.
        """
        return True

    def update(self):
        """Do some stuff"""
        _LOGGER.info('Switchbot %s updating', self._mac)
        self._device.update()
        _LOGGER.info('Switchbot %s updating done', self._mac)

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return self._mac.replace(":", "")

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return self._name

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        return {"last_run_success": self._last_run_success,
                "battery": self._device.get_battery_percent(),
                "light_level": self._device.get_light_level(),
                "reversed": self._device.is_reversed()}

    @property
    def device_class(self) -> str:
        """Return the class of this device."""
        return DEVICE_CLASS_CURTAIN

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_STOP | SUPPORT_SET_POSITION

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        return (self.current_cover_position >= 100) if self._device.is_reversed() else True

    def open_cover(self, **kwargs) -> None:
        """Open the curtain with using this device."""

        _LOGGER.info('Switchbot to open curtain %s...', self._mac)

        """Open curtain"""
        self._last_run_success = self._device.open()

    def close_cover(self, **kwargs) -> None:
        """Close the curtain with using this device."""

        _LOGGER.info('Switchbot to close the curtain %s...', self._mac)

        """Close curtain"""
        self._last_run_success = self._device.close()

    def stop_cover(self, **kwargs) -> None:
        """Stop the moving of this device."""

        _LOGGER.info('Switchbot to stop %s...', self._mac)

        """Stop curtain"""
        self._last_run_success = self._device.stop()

    def set_cover_position(self, **kwargs):
        """Move the cover shutter to a specific position."""
        position = kwargs.get(ATTR_POSITION)

        _LOGGER.info('Switchbot to move at %d %s...', position, self._mac)
        self._last_run_success = self._device.set_position(position)

    @property
    def current_cover_position(self):
        """Return the current position of cover shutter."""
        return self._device.get_position()
