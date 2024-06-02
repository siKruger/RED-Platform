import logging
import threading
import hashlib
import os
import platform

from .connection import memory, session
from ..mqtt import socketio_wrapper
from ..pepper.event_publisher import Publisher
from ..pepper.event_subscriber import Subscriber
from ..pepper.event_enum import PepperEvents

logger = logging.getLogger(__name__)
pepper_event_publisher = None


def send_event(name, value=None):
    memory.declareEvent(name)
    memory.raiseEvent(name, value)


def on_battery_charge_changed(event, data):
    logger.info("Battery charge update: " + str(data))
    socketio_wrapper("/update/BatteryChargeChanged", str(data))


def get_system_properties():
    return {
        'architecture': platform.architecture(),
        'system': platform.system(),
        'version': platform.version(),
        'machine': platform.machine(),
        'node': platform.node(),
        'release': platform.release(),
        'cpu_count': os.cpu_count(),
        'processor': platform.processor(),
        'os_name': os.name
    }


if session:
    concatenated_system_properties = ''.join(
        f'{key}:{value};' for key, value in sorted(get_system_properties().items()))
    session_hash = hashlib.md5(concatenated_system_properties.encode('utf-8')).hexdigest()
    print(session_hash)
    pepper_event_publisher = Publisher()
    session.registerService(session_hash, pepper_event_publisher)

    on_battery_subscriber = Subscriber(PepperEvents.BATTERY_CHARGE_CHANGED.value, on_battery_charge_changed)

    pepper_event_publisher.subscribe(on_battery_subscriber)
else:
    logger.warning("Didn't create PubSub event objects due to missing robot connection.")