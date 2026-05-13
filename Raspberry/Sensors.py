import time
import board
import adafruit_dht
import os
import redis
import digitalio
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

# Configurazione sensori
dht_gpio = getattr(board, f'D{os.getenv('DHT_PIN_NUMBER','10')}')

dht_device = adafruit_dht.DHT11(dht_gpio)

trig_num = int(os.getenv('HC_SR04_TRIG_NUMBER','22'))
echo_num = int(os.getenv('HC_SR04_ECHO_NUMBER','23'))

trig = digitalio.DigitalInOut(getattr(board, f'D{trig_num}'))
trig.direction = digitalio.Direction.OUTPUT
echo = digitalio.DigitalInOut(getattr(board, f'D{echo_num}'))
echo.direction = digitalio.Direction.INPUT

trig.value=False
trig.echo=False

print("Waiting for distance sensor to settle")
time.sleep(2)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(str(os.getenv('MQTT_IP','192.168.1.238')), int(os.getenv('MQTT_PORT', 1883))) #anche l'indirizzo IP deve diventare una variabile
                                                                                            #ambientale
print("Inizio test DHT11... Premi Ctrl+C per fermare")

while True:
    try:
        # Lettura dati
        e = int(time.time())
        temp = dht_device.temperature
        hum = dht_device.humidity

        trig.value = True
        time.sleep(0.00001)
        trig.value = False

        pulse_start=0
        pulse_end=0

        while not echo.value:
            pulse_start = time.time()

        while echo.value:
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