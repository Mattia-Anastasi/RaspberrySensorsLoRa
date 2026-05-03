import time
import board
import adafruit_dht
import os
import redis
import json
from datetime import datetime

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = 6379

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Configurazione sensore.
pin_gpio = board.D10

dht_device = adafruit_dht.DHT11(pin_gpio)

print("Inizio test DHT11... Premi Ctrl+C per fermare")

while True:
    try:
        # Lettura dati
        temp = dht_device.temperature
        hum = dht_device.humidity

        if temp is not None and hum is not None:
            print(f"Temp: {temp:.1f}°C | Umidità: {hum}%")
            payload = {
                "timestamp": datetime.now().isoformat(),
                "temperatura": temp,
                "umidita": hum,
            }

            json_payload = json.dumps(payload)
            r.lpush('sensor_data_list', json_payload)
            r.ltrim('sensor_data_list', 0, 499)
            print(f"Dati inviati: {json_payload}")
        else:
            print("Lettura fallita (riprovo...)")

    except RuntimeError as error:
        #Possibli errori di lettura
        print(f"Errore di lettura: {error.args[0]}")
        time.sleep(2.0)
        continue
    except Exception as error:
        dht_device.exit()
        raise error

    time.sleep(10.0) 