import qi
import logging

from flask_socketio import emit
from time import time

from ..server import app
from .connection_helper import get_service, connect
from ..mqtt import socketio_wrapper

logger = logging.getLogger(__name__)

is_disconnected = False
session, connection_type = connect()
logger.info("Connection type: " + connection_type)
print("Connection type:", connection_type)

with app.test_request_context():
    emit("/update/connection_type", connection_type, broadcast=True, namespace="/")

animation = get_service(session, "ALAnimationPlayer")
awareness = get_service(session, "ALBasicAwareness")
audio = get_service(session, "ALAudioDevice")
behavior = get_service(session, "ALBehaviorManager")
barcode = get_service(session, "ALBarcodeReader")
battery = get_service(session, "ALBattery")
compass = get_service(session, "ALVisualCompass")
connection_manager = get_service(session, "ALConnectionManager")
face_detection = get_service(session, "ALFaceDetection")
led = get_service(session, "ALLeds")
life = get_service(session, "ALAutonomousLife")
memory = get_service(session, "ALMemory")
motion = get_service(session, "ALMotion")
navigation = get_service(session, "ALNavigation")
photo = get_service(session, "ALPhotoCapture")
posture = get_service(session, "ALRobotPosture")
speaking_movement = get_service(session, "ALSpeakingMovement")
speech_recognition = get_service(session, "ALSpeechRecognition")
system = get_service(session, "ALSystem")
tablet = get_service(session, "ALTabletService")
temperature = get_service(session, "ALBodyTemperature")
touch = get_service(session, "ALTouch")
tts = get_service(session, "ALTextToSpeech")
tts_animated = get_service(session, "ALAnimatedSpeech")
video = get_service(session, "ALVideoDevice")
waving_detection = get_service(session, "ALWavingDetection")

def periodic_task():
    global is_disconnected
    global memory

    if not session.isConnected() and not is_disconnected:
        logger.error("Connection to robot lost")
        is_disconnected = True
        connection_type = "Disconnected"

        socketio_wrapper("/update/connection_type", connection_type)

    if not is_disconnected:
        try:
            knee_temp = memory.getData("Device/SubDeviceList/KneePitch/Temperature/Sensor/Value")
            socketio_wrapper("/update/temperature", knee_temp)
        except Exception as e:
            logger.error(e)

if connection_type != "Disconnected":
    connection_task = qi.PeriodicTask()
    connection_task.setCallback(periodic_task)
    connection_task.setUsPeriod(30000000) # 10s
    connection_task.start(True)
