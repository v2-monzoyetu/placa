import httpx
from httpx import HTTPStatusError, RequestError

API_URL = "https://painel.monzoyetu.com/api"

def get(page, route, params = {}):
    """Faz uma requisição GET autenticada e retorna os dados como uma lista."""
    
    if page.client_storage.get("token"):
        token = page.client_storage.get("token")
        headers = {"Authorization": f"Bearer {token}"}
        
    url = API_URL+route
    
    try:
        response = httpx.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        results = data.get("results", {})  # Obtém o dicionário "results"
        items = results.get("data", [])
        
        if isinstance(items, list):  # Verifica se a resposta é uma lista
            return items
        else:
            return []  # Retorna uma lista vazia se a resposta for inválida

    except HTTPStatusError as e:
        print(f"Erro HTTP: {e.response.status_code} - {e.response.text}")
        return []
    except RequestError as e:
        print(f"Erro de requisição: {e}")
        return []

def post(page, route, params = {}):
    """Faz uma requisição POST autenticada e retorna os dados como uma lista."""
    if page.client_storage.get("token"):
        token = page.client_storage.get("token")
        headers = {"Authorization": f"Bearer {token}"}
        
    url = API_URL+route
    
    try:
        response = httpx.post(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        results = data.get("results", {})  # Obtém o dicionário "results"
        items = results.get("data", [])
        
        if isinstance(items, list):  # Verifica se a resposta é uma lista
            return items
        else:
            return []  # Retorna uma lista vazia se a resposta for inválida

    except HTTPStatusError as e:
        print(f"Erro HTTP: {e.response.status_code} - {e.response.text}")
        return []
    except RequestError as e:
        print(f"Erro de requisição: {e}")
        return []