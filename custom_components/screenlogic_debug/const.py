"""Constants for screenlogic_debug."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "ScreenLogic Debug"
DOMAIN = "screenlogic_debug"
VERSION = "0.0.1"

DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 10
