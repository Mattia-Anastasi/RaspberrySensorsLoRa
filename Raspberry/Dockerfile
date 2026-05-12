FROM python:3.11
WORKDIR /local/sensing-app

COPY Sensors.py .
CMD ["python3", "Sensors.py"]

# Install the application dependencies
RUN pip3 install adafruit-circuitpython-dht adafruit-blinka RPi.GPIO gpiozero redis paho-mqtt

ENV PYTHONUNBUFFERED=1