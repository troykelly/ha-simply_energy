"""Constants for the Solar-Log integration."""
from datetime import datetime, date, timedelta

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
    POWER_WATT,
    CONF_CURRENCY,
    DEVICE_CLASS_TIMESTAMP,
)

DOMAIN = "simplyenergy"

"""Default config for simplyenergy."""
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


"""Fixed constants."""
SCAN_INTERVAL = timedelta(seconds=60)

"""Supported sensor types."""
SENSOR_TYPES = {
    "time": ["TIME", "last update", None, "mdi:calendar-clock"],
    "power_ac": ["powerAC", "power AC", POWER_WATT, "mdi:solar-power"],
    "power_dc": ["powerDC", "power DC", POWER_WATT, "mdi:solar-power"],
    "voltage_ac": ["voltageAC", "voltage AC", "V", "mdi:flash"],
    "voltage_dc": ["voltageDC", "voltage DC", "V", "mdi:flash"],
    "yield_day": ["yieldDAY", "yield day", ENERGY_KILO_WATT_HOUR, "mdi:solar-power"],
    "yield_yesterday": [
        "yieldYESTERDAY",
        "yield yesterday",
        ENERGY_KILO_WATT_HOUR,
        "mdi:solar-power",
    ],
    "yield_month": [
        "yieldMONTH",
        "yield month",
        ENERGY_KILO_WATT_HOUR,
        "mdi:solar-power",
    ],
    "yield_year": ["yieldYEAR", "yield year", ENERGY_KILO_WATT_HOUR, "mdi:solar-power"],
    "yield_total": [
        "yieldTOTAL",
        "yield total",
        ENERGY_KILO_WATT_HOUR,
        "mdi:solar-power",
    ],
    "consumption_ac": ["consumptionAC", "consumption AC", POWER_WATT, "mdi:power-plug"],
    "consumption_day": [
        "consumptionDAY",
        "consumption day",
        ENERGY_KILO_WATT_HOUR,
        "mdi:power-plug",
    ],
    "consumption_yesterday": [
        "consumptionYESTERDAY",
        "consumption yesterday",
        ENERGY_KILO_WATT_HOUR,
        "mdi:power-plug",
    ],
    "consumption_month": [
        "consumptionMONTH",
        "consumption month",
        ENERGY_KILO_WATT_HOUR,
        "mdi:power-plug",
    ],
    "consumption_year": [
        "consumptionYEAR",
        "consumption year",
        ENERGY_KILO_WATT_HOUR,
        "mdi:power-plug",
    ],
    "consumption_total": [
        "consumptionTOTAL",
        "consumption total",
        ENERGY_KILO_WATT_HOUR,
        "mdi:power-plug",
    ],
    "total_power": ["totalPOWER", "total power", "Wp", "mdi:solar-power"],
    "alternator_loss": [
        "alternatorLOSS",
        "alternator loss",
        POWER_WATT,
        "mdi:solar-power",
    ],
    "capacity": ["CAPACITY", "capacity", "%", "mdi:solar-power"],
    "efficiency": ["EFFICIENCY", "efficiency", "% W/Wp", "mdi:solar-power"],
    "power_available": [
        "powerAVAILABLE",
        "power available",
        POWER_WATT,
        "mdi:solar-power",
    ],
    "usage": ["USAGE", "usage", None, "mdi:solar-power"],
}
