import logging
import traceback

from flask import Response

from .awareness import _set_awareness
from ...config import CAMERA_UPDATE_INTERVAL
from ...decorator import log
from ...mqtt import socketio_wrapper
from ...pepper.connection import waving_detection
from ...pepper.event_subscriber import Subscriber
from ...pepper.event_helper import pepper_event_publisher
from ...pepper.event_enum import PepperEvents
from ...server import app, socketio

logger = logging.getLogger(__name__)


@socketio.on("/robot/waving/start")
@app.route("/robot/waving/start", methods=["POST"])
@log("/robot/waving/start")
def start_wave_detection():
    try:
        _set_awareness(False, pitch=-20)

        waving_detection.subscribe("wave_detection", CAMERA_UPDATE_INTERVAL, 0)

        if pepper_event_publisher:
            pepper_event_publisher.subscribe(wave_detected_subscriber)
        else:
            logger.warning("Can't subscribe to wave detection event. Subscriber is not intialized.")

        return Response(status=200)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return Response(str(e), status=500)


@socketio.on("/robot/waving/stop")
@app.route("/robot/waving/stop", methods=["POST"])
@log("/robot/waving/stop")
def stop_wave_detection():
    try:
        _set_awareness(True)
        waving_detection.unsubscribe("wave_detection", _async=True)

        if pepper_event_publisher:
            pepper_event_publisher.unsubscribe(wave_detected_subscriber)

        return Response(status=200)
    except Exception as e:
        logger.warning(e)
        return Response(str(e), status=400)


def on_wave_detected(event, value):
    if len(value) == 0:
        return

    stop_wave_detection()

    socketio_wrapper("/event/waving/detected")


wave_detected_subscriber = Subscriber(PepperEvents.WAVE_DETECTED.value, on_wave_detected)
