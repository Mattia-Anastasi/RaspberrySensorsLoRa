FROM python:3.12
WORKDIR /local/sensing-app

# Avoid output buffering
ENV PYTHONUNBUFFERED=1

# Install the application dependencies
RUN pip3 install RPi.GPIO adafruit-circuitpython-dht adafruit-blinka redis paho-mqtt

COPY Sensors.py .
CMD ["python3", "Sensors.py"]