#!/bin/sh

# build rest-server container
sudo docker build -t rest-server rest-server/

# build mosquitto container
sudo docker build -t mosquitto mosquitto/
