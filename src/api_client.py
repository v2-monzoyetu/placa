import httpx
import flet as ft
from httpx import HTTPStatusError, RequestError

API_URL = "https://painel.monzoyetu.com/api"

def get(page: ft.Page, route, params = {}):
    if page.client_storage.get("token"):
        token = page.client_storage.get("token")
        headers = {"Authorization": f"Bearer {token}"}
        
    url = API_URL+route
    
    try:
        response = httpx.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        results = data.get("results", {})
        items = results.get("data", [])
        
        if isinstance(items, list):
            return items
        else:
            return []

    except HTTPStatusError as e:
        print(f"Erro HTTP: {e.response.status_code} - {e.response.text}")
        return []
    except RequestError as e:
        print(f"Erro de requisição: {e}")
        return []

def post(page: ft.Page, route, params = {}):
    if page.client_storage.get("token"):
        token = page.client_storage.get("token")
        headers = {"Authorization": f"Bearer {token}"}
        
    url = API_URL+route
    
    try:
        response = httpx.post(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        results = data.get("results", {}) 
        items = results.get("data", [])
        
        if isinstance(items, list):
            return items
        else:
            return []

    except HTTPStatusError as e:
        print(f"Erro HTTP: {e.response.status_code} - {e.response.text}")
        return []
    except RequestError as e:
        print(f"Erro de requisição: {e}")
        return []