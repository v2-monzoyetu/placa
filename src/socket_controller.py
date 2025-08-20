# socket_controller.py
import json
import flet as ft
import socketio
from functools import partial
from gpio_controller import ligar_rele1, ligar_rele2

sio = socketio.Client()
sio_url = "https://socket.monzoyetu.com"

# Variáveis da interface
socket_status = ft.CircleAvatar(
    bgcolor=ft.Colors.RED,
    content=ft.Text("OFF", size=12),
)
socket_id = ft.Text("ID: n/a", size=13, overflow=ft.TextOverflow.ELLIPSIS, max_lines=1, width=150)
socket_code = ft.Text("Code: n/a", size=13, overflow=ft.TextOverflow.ELLIPSIS, max_lines=1, width=150)

def conectar(e=None):
    """Tenta conectar ao servidor Socket.IO"""
    try:
        sio.connect(sio_url)
    except Exception as e:
        print(f"Erro ao conectar ao Socket.IO: {e} ❌")

def desconectar(e=None):
    """Desconecta do servidor Socket.IO"""
    if sio.connected:
        sio.disconnect()
    else:
        conectar()

def atualizar_status(data):
    """Processa mensagens recebidas do servidor"""
    if sio.connected:
        try:
            item = json.loads(data)
            if all(key in item for key in ["id", "referencia", "password", "comando"]):
                if item["referencia"] == "rasperry-pi4" and item["password"] == "123456":
                    match item["comando"]:
                        case "openDoor1":
                            ligar_rele1()
                        case "openDoor2":
                            ligar_rele2()
            else:
                print("Chave 'referencia' não encontrada ❌")
        except Exception as e:
            pass

def on_connect(page: ft.Page):
    """Atualiza o status da conexão"""
    try:
        socket_status.bgcolor = ft.Colors.GREEN
        socket_status.content = ft.Text("ON")
        socket_id.value = f"ID: {sio.sid}"
        socket_code.value = f"Code: {sio.transport()}"
    except Exception as e:
        print(f"Erro na conexão: {e}")
    page.update()

def on_disconnect(page: ft.Page):
    """Atualiza o status da interface ao desconectar"""
    try:
        socket_status.bgcolor = ft.Colors.RED
        socket_status.content = ft.Text("OFF")
        socket_id.value = "ID: n/a"
        socket_code.value = "Code: n/a"
    except Exception as e:
        print(f"Erro na desconexão: {e}")
    page.update()

def register_socket_events(page):
    sio.on("message", atualizar_status)
    sio.on("connect", partial(on_connect, page=page))
    sio.on("disconnect", partial(on_disconnect, page=page))
