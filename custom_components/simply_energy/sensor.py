"""Support for Simply Energy data collection."""
import json
import logging
import time
import datetime

import requests
import voluptuous as vol

from homeassistant.components import mqtt
from homeassistant.components.sensor import DEVICE_CLASSES_SCHEMA, PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_ACCESS_TOKEN,
    CONF_PROTOCOL,
    CONF_HOST,
    CONF_RESOURCE,
    CONF_FORCE_UPDATE,
    CONF_HEADERS,
    CONF_METHOD,
    CONF_NAME,
    CONF_TIMEOUT,
    CONF_VERIFY_SSL,
    ENERGY_KILO_WATT_HOUR,
    CONF_CURRENCY,
    DEVICE_CLASS_TIMESTAMP,
)
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

METHODS = ["POST", "GET"]
PROTOCOLS = ["HTTPS", "HTTP"]

DEFAULT_PROTOCOL = "HTTPS"
DEFAULT_HOST = "tracker.simplyenergy.com.au"
DEFAULT_RESOURCE = "/api/tracker/usage?account_id={access_token}&from={date}"
DEFAULT_CURRENCY = "$"
DEFAULT_METHOD = "GET"
DEFAULT_NAME = "Simply Energy"
DEFAULT_VERIFY_SSL = True
DEFAULT_FORCE_UPDATE = False
DEFAULT_TIMEOUT = 10

CONF_TOPIC = "topic"
DEFAULT_TOPIC = "simply-energy/cost"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Exclusive(CONF_ACCESS_TOKEN, CONF_ACCESS_TOKEN): cv.string,
        vol.Optional(CONF_PROTOCOL, default=DEFAULT_PROTOCOL): vol.In(PROTOCOLS),
        vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
        vol.Optional(CONF_RESOURCE, default=DEFAULT_RESOURCE): cv.string,
        vol.Optional(CONF_HEADERS): vol.Schema({cv.string: cv.string}),
        vol.Optional(CONF_METHOD, default=DEFAULT_METHOD): vol.In(METHODS),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): cv.boolean,
        vol.Optional(CONF_FORCE_UPDATE, default=DEFAULT_FORCE_UPDATE): cv.boolean,
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
        vol.Optional(CONF_CURRENCY, default=DEFAULT_CURRENCY): cv.string,
        vol.Optional(CONF_TOPIC, default=DEFAULT_TOPIC): mqtt.valid_subscribe_topic,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""

    name = config.get(CONF_NAME)
    access_token = config.get(CONF_ACCESS_TOKEN)
    resource = config.get(CONF_RESOURCE)
    protocol = config.get(CONF_PROTOCOL)
    host = config.get(CONF_HOST)
    method = config.get(CONF_METHOD)
    verify_ssl = config.get(CONF_VERIFY_SSL)
    headers = config.get(CONF_HEADERS)
    force_update = config.get(CONF_FORCE_UPDATE)
    timeout = config.get(CONF_TIMEOUT)
    currency = config.get(CONF_CURRENCY)
    topic = config.get(CONF_TOPIC)

    uri = resource.replace("{access_token}", access_token)
    url = "%s://%s%s" % (protocol.lower(), host.lower(), uri)

    rest = RestData(method, url, None, headers, None, verify_ssl, timeout)

    today = datetime.date.today()
    energy_date = today.strftime("%Y-%m-%d")

    rest.update(energy_date)
    if rest.data is None:
        raise PlatformNotReady

    add_entities(
        [SimplyEnergy(hass, rest, name, force_update, currency, topic)], True,
    )


class SimplyEnergy(Entity):
    """Representation of a Sensor."""

    def __init__(
        self, hass, rest, name, force_update, currency, topic,
    ):
        """Initialize the sensor."""
        self._hass = hass
        self.rest = rest
        self._name = name
        self._state = None
        self._force_update = force_update
        self._currency = currency
        self._topic = topic
        self.mqtt = hass.components.mqtt
        self._sent = []

    def process(self, intervals):
        """Processes the timestamped data"""
        for interval_id in intervals:
            interval = intervals[interval_id]
            if "intervals" in interval:
                self.process(interval["intervals"])
            if (
                "data" in interval
                and "interval_range" in interval
                and "total_spend" in interval["data"]
            ):
                start_time_str = (
                    interval["interval_range"]["starts_at"]["time"]
                    + " "
                    + interval["interval_range"]["starts_at"]["yyyymmdd"]
                )
                end_time_str = (
                    interval["interval_range"]["ends_at"]["time"]
                    + " "
                    + interval["interval_range"]["ends_at"]["yyyymmdd"]
                )
                date_format = "%H:%M %Y%m%d"
                start_time = datetime.datetime.strptime(start_time_str, date_format)
                end_time = datetime.datetime.strptime(end_time_str, date_format)
                start_timestamp = time.mktime(start_time.timetuple())
                end_timestamp = time.mktime(end_time.timetuple())
                period = str(start_timestamp) + "-" + str(end_timestamp)
                if interval["data"]["total_spend"] and not period in self._sent:
                    _LOGGER.info(period + " - " + str(interval["data"]["total_spend"]))
                    payload = {
                        "value": interval["data"]["total_spend"],
                        "since": end_timestamp,
                    }
                    self.mqtt.publish(self._topic + "/historical", json.dumps(payload))
                    self._sent.append(period)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def available(self):
        """Return if the sensor data are available."""
        return self.rest.data is not None

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._currency

    @property
    def force_update(self):
        """Force update."""
        return self._force_update

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        today = datetime.date.today()
        energy_date = today.strftime("%Y-%m-%d")

        self.rest.update(energy_date)
        if self.rest.data is None:
            _LOGGER.error("No data from Simply Energy for : %s", energy_date)
            return

        if not self.rest.data["current_week"]["metadata"]["has_data"]:
            if not self.rest.data["previous_week"]["has_data"]:
                _LOGGER.error("Energy not available for period : %s", energy_date)
                return

            self.rest.update(self.rest.data["previous_week"]["from"])
            if not self.rest.data["current_week"]["metadata"]["has_data"]:
                _LOGGER.error("Energy not available for period : %s", energy_date)
                return

        self._state = self.rest.data["current_week"]["insights"]["weekly_total"]
        self.mqtt.publish(self._topic + "/state", self._state)
        if self.rest.data["current_week"]["intervals"]:
            self.process(self.rest.data["current_week"]["intervals"])


class RestData:
    """Class for handling the data retrieval."""

    def __init__(
        self, method, resource, auth, headers, data, verify_ssl, timeout=DEFAULT_TIMEOUT
    ):
        """Initialize the data object."""
        self._method = method
        self._resource = resource
        self._auth = auth
        self._headers = headers
        self._request_data = data
        self._verify_ssl = verify_ssl
        self._timeout = timeout
        self.data = None

    def set_url(self, url):
        """Set url."""
        self._resource = url

    def update(self, energy_date):
        """Get the latest data from REST service with provided method."""
        resource = self._resource.replace("{date}", energy_date)
        _LOGGER.info("Updating from %s", resource)
        try:
            response = requests.request(
                self._method,
                resource,
                headers=self._headers,
                auth=self._auth,
                data=self._request_data,
                timeout=self._timeout,
                verify=self._verify_ssl,
            )
            try:
                self.data = json.loads(response.text)
            except ValueError:
                _LOGGER.warning(
                    "JSON result was not a dictionary"
                    " or list with 0th element a dictionary"
                )
                self.data = None

        except requests.exceptions.RequestException as ex:
            _LOGGER.error("Error fetching data: %s failed with %s", self._resource, ex)
            self.data = None
