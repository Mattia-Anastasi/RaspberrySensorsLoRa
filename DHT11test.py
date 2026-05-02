import time
import board
import adafruit_dht

# Configurazione sensore.
pin_gpio = board.D10

dht_device = adafruit_dht.DHT11(pin_gpio)

print("Inizio test DHT11... Premi Ctrl+C per fermare")

while True:
    try:
        # Lettura dati
        temperatura = dht_device.temperature
        umidita = dht_device.humidity

        if temperatura is not None and umidita is not None:
            print(f"Temp: {temperatura:.1f}°C | Umidità: {umidita}%")
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