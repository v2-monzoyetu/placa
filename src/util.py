
import base64

def is_valid_base64(data):
    # Verifica se a string é um Base64 válido
    try:
        # Base64 deve ter um comprimento múltiplo de 4
        if len(data) % 4 != 0:
            return False
        # Tenta decodificar
        base64.b64decode(data)
        return True
    except Exception:
        return False