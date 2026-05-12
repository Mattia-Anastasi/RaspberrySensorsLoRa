import time
import board
import adafruit_dht
import os
import redis
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT =int(os.getenv('REDIS_PORT', 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

ts = r.ts()

try:
    ts.create("hum")
except redis.exceptions.ResponseError as error:
    print("Humidity time series already exists")

try:
    ts.create("temp")
except redis.exceptions.ResponseError as error:
    print("Temperature time series already exists")

try:
    ts.create("dist")
except redis.exceptions.ResponseError as error:
    print("Distance time series already exists")

# Configurazione sensore.
dht_gpio = board.D10

dht_device = adafruit_dht.DHT11(dht_gpio)

GPIO.setmode(GPIO.BCM)
trig = 22
echo = 23

GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)

GPIO.output(trig, GPIO.LOW)
print("Waiting for distance sensor to settle")
time.sleep(2)

GPIO.output(trig, GPIO.HIGH)
time.sleep(0.00001)
GPIO.output(trig, GPIO.LOW)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect("192.168.1.238", int(os.getenv('MQTT_PORT', 1883)))


print("Inizio test DHT11... Premi Ctrl+C per fermare")

while True:
    try:
        # Lettura dati
        e = int(time.time())
        temp = dht_device.temperature
        hum = dht_device.humidity

        GPIO.output(trig, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(trig, GPIO.LOW)

        while GPIO.input(echo) == 0:
            pulse_start = time.time()

        while GPIO.input(echo) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start

        distance = round(17150*pulse_duration, 2)


        if temp is not None and hum is not None and distance is not None:
            print(f"Temp: {temp:.1f}°C | Umidità: {hum}% | Distanza: {distance}cm")

            ts.add("hum", e, hum)
            ts.add("temp", e, temp)
            ts.add("dist", e, distance)

            client.publish("sensors", f"DHT temperature={temp},humidity={hum}  {e}")#influxdb vuole i nanosecondi
            client.publish("sensors", f"HC-SR04 distance={distance} {e}")
        else:
            print("Lettura fallita (riprovo...)")

    except RuntimeError as error:
        #Possibli errori di lettura
        print(f"Errore di lettura: {error.args[0]}")
        time.sleep(3.0)
        continue
    except Exception as error:
        dht_device.exit()
        raise error

    time.sleep(3.0) #basterebbero due secondi al fine di permettere al sensore di tornare operativo