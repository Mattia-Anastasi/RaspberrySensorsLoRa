FROM python:3.11
WORKDIR /local/sensing-app

COPY DHT11test.py .
CMD ["python3", "DHT11test.py"]

# Install the application dependencies
RUN pip3 install adafruit-circuitpython-dht adafruit-blinka gpiozero redis RPi.GPIO

ENV PYTHONUNBUFFERED=1