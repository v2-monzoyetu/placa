import time
import platform
from gpiozero import OutputDevice

RUNNING_ON_PI = platform.system() == "Linux"

if RUNNING_ON_PI:
    # Funções para controlar os relés
    def activar_relay(gpio_number):
        try:
            relay = OutputDevice(gpio_number, active_high=False, initial_value=False)
            relay.on()
            time.sleep(0.5)
            relay.off()
        except Exception as e:
            print(e)
else:
    def activar_relay(gpio_number):
        try:
            print(gpio_number)
        except Exception as e:
            print(e)