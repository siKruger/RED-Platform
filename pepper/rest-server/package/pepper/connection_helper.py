import qi
import logging
import os

import package.config as config

from functools import lru_cache

from ..dummy import Dummy
from ..utilities import get_ip, is_host_reachable

logger = logging.getLogger(__name__)

if not config.IP:
    config.IP = os.environ["ROBOT_IP"]

if not config.FLASK_IP:
    config.FLASK_IP = get_ip()

if not config.FLASK_PORT:
    config.FLASK_PORT = int(os.environ["FLASK_PORT"])

if not config.MQTT_IP:
    config.MQTT_IP = get_ip()

if not config.MQTT_PORT:
    config.MQTT_PORT = int(os.environ["MQTT_PORT"])

logger.info("Using {} as Flask server IP.".format(config.FLASK_IP))

def get_service_list(session):
    list = []
    for service in session.services():
        list.append(service["name"])
    
    return list

def get_service(session, service):
    if not session or not session.isConnected():
        return Dummy(service)

    if service in get_service_list(session):
        return session.service(service)

    return Dummy(service)

def connect():
    logger.debug("Trying to connect to the robot with IP {} and port {}.".format(config.IP, config.PORT))
    
    if not is_host_reachable(config.IP, config.PORT):
        logger.info("The robot at {}:{} is not reachable.".format(config.IP, config.PORT))
        return None, "Disconnected"
    else:
        logger.debug("The robot at {}:{} is reachable.".format(config.IP, config.PORT))
    
    try:
        pepper = qi.Application(url="tcp://{}:{}".format(config.IP, config.PORT))
        pepper.start()
        session = pepper.session

        service_list = get_service_list(session)
        if len(service_list) <= 104:
            connection_type = "Virtual robot"
        else:
            connection_type = "Real robot"
            session.listen("tcp://0.0.0.0:0") # actively listen for events from the robot, otherwise events won't reach our flask application

        logger.debug("Connected to robot with ip {} and port {}.".format(config.IP, config.PORT))
        return session, connection_type
    except RuntimeError as e:
        logger.debug("Can't connect to robot with ip {} and port {}.".format(config.IP, config.PORT))    
        return None, "Disconnected"
