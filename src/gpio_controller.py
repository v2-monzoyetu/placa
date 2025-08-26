import time
import platform

RUNNING_ON_PI = platform.system() == "Linux"

if RUNNING_ON_PI:
    from periphery import GPIO
    
    def ativar_relay(gpio_number: int):
        try:
            gpio = GPIO(gpio_number, "out")
            gpio.write(False)
            time.sleep(1)
            gpio.write(True)
            gpio.close()
        except Exception as e:
            print(f"Erro ao controlar o relé no GPIO {gpio_number}: {e}")
    
    def desativar_relay(gpio_number: int):
        try:
            gpio = GPIO(gpio_number, "out")
            gpio.write(True)
            gpio.close()
        except Exception as e:
            print(f"Erro ao desativar o relé no GPIO {gpio_number}: {e}")
else:
    def ativar_relay(gpio_number: int):
        try:
            print(f"Simulando ativação do relé no GPIO {gpio_number}")
        except Exception as e:
            print(e)