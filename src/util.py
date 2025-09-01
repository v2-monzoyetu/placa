import base64
import re

def is_valid_base64(data: str) -> bool:
    try:
        if len(data.strip()) % 4 != 0:
            return False

        if not re.fullmatch(r'^[A-Za-z0-9+/=]+$', data.strip()):
            return False

        decoded = base64.b64decode(data, validate=True)

        decoded.decode("utf-8")  

        return True
    except Exception:
        return False
