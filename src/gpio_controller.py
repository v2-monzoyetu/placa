import time
import platform

RUNNING_ON_PI = platform.system() == "Linux"

if RUNNING_ON_PI:
    from periphery import GPIO
    # Funções para controlar os relés
    def ativar_relay(gpio_number: int):
        try:
            # Configura o pino GPIO como saída
            gpio = GPIO(gpio_number, "out")
            # Ativa o relé (definir como baixo, já que active_high=False no código original)
            gpio.write(False)
            time.sleep(0.5)
            # Desativa o relé
            gpio.write(True)
            # Fecha o pino GPIO
            gpio.close()
        except Exception as e:
            print(f"Erro ao controlar o relé no GPIO {gpio_number}: {e}")
else:
    def ativar_relay(gpio_number: int):
        try:
            print(f"Simulando ativação do relé no GPIO {gpio_number}")
        except Exception as e:
            print(e)