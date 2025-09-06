import flet as ft
import requests
from pathlib import Path
import hashlib
import base64
from io import BytesIO
from PIL import Image

# Diretório para armazenar o cache
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

def get_cache_path(url):
    """Gera um nome de arquivo único para a URL usando hash."""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return CACHE_DIR / f"{url_hash}.jpg"

def download_image(url, cache_path):
    """Baixa a imagem da URL e salva no cache."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(cache_path, "wb") as f:
                f.write(response.content)
            return True
        return False
    except Exception as e:
        print(f"Erro ao baixar imagem: {e}")
        return False

def get_image_path(url):
    """Retorna o caminho da imagem em cache ou baixa a imagem se necessário."""
    cache_path = get_cache_path(url)
    if cache_path.exists():
        return cache_path
    if download_image(url, cache_path):
        return cache_path
    return None

def load_image_to_base64(image_path):
    """Converte a imagem em uma string base64 para evitar problemas de cache."""
    try:
        with Image.open(image_path) as img:
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode("utf-8")
    except Exception as e:
        print(f"Erro ao converter imagem para base64: {e}")
        return None

def cached_network_image(link: str):
    """Carrega uma imagem de rede com cache e retorna um Container com a imagem."""
    # Obtém a imagem em cache ou usa a padrão
    cache_path   = get_image_path(link)
    image_base64 = load_image_to_base64(cache_path) if cache_path else None

    return ft.Container(
        content=ft.Image(
            src_base64=image_base64,
            width=250,
            height=250,
            fit=ft.ImageFit.COVER,
            repeat=ft.ImageRepeat.NO_REPEAT,
            border_radius=ft.border_radius.all(250),
            error_content=ft.Text("Erro ao carregar imagem") if not image_base64 else None
        ),
        width=260,
        height=260,
        border=ft.border.all(5, ft.Colors.WHITE),
        border_radius=ft.border_radius.all(260),
        padding=5,
        alignment=ft.alignment.center,
    )