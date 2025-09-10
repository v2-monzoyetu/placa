import requests
import flet as ft
from api_client import API_URL

def validateResident(page: ft.Page, id, status, reader_type: str = ''):
    """Verifica o QRCode."""

    token = page.client_storage.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    route = f"{API_URL}/v1/concierge/valid/resident/{page.client_storage.get('condominio_id')}"

    try:
        response = requests.post(route, params={"id": id, "status": status, "type": reader_type}, headers=headers, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            return True
        else:
            return False
            
    except Exception as e:
        return False
        
def validateEmployee(page: ft.Page, id, situation, reader_type: str = ''):
    """Verifica o QRCode."""

    token = page.client_storage.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    route = f"{API_URL}/v1/concierge/valid/employee/{page.client_storage.get('condominio_id')}"

    try:
        response = requests.post(route, params={"id": id, "situation": situation, "type": reader_type}, headers=headers, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            return True
        else:
            return False  
    except Exception as e:
        return False   

def validateVehicle(page: ft.Page, id, motoristaId, status, reader_type: str = ''):
    """Verifica o QRCode."""

    token = page.client_storage.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    route = f"{API_URL}/v1/concierge/viatura/{page.client_storage.get('condominio_id')}"

    try:
        response = requests.post(route, params={"id": id, "status": status, "motoristaId": motoristaId, "type": reader_type}, headers=headers, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            return True
        else:
            return False  
    except Exception as e:
        return False

def validateVisitor(page: ft.Page, code):
    """Verifica o QRCode."""

    token = page.client_storage.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    params = {
        "code": code, 
        "is_accompanied"    : "0", 
        "number_companions" : "0",
        "came_by_car"       : "0",
        "plate"             : "n/a",
        "obs"               : "n/a",
    }
    route = f"{API_URL}/v1/concierge/valid/visitor/{page.client_storage.get('condominio_id')}"

    try:
        response = requests.post(route, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            return True
        else:
            return False  
    except Exception as e:
        return False