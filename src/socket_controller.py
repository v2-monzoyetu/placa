# socket_controller.py
import json
import flet as ft
import socketio
from functools import partial
from gpio_controller import ativar_relay
from validator import validateResident

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
        if(sio.connected == False):
            sio.connect(sio_url)
    except Exception as e:
        print(f"Erro ao conectar ao Socket.IO: {e} ❌")

def desconectar(e=None):
    """Desconecta do servidor Socket.IO"""
    if sio.connected:
        sio.disconnect()
    else:
        conectar()

def atualizar_status(page: ft.Page, data):
    """Processa mensagens recebidas do servidor"""
    if sio.connected:
        try:
            condominio_id = page.client_storage.get('condominio_id')
            referencia    = page.client_storage.get('referencia')
            password      = page.client_storage.get('password')
            item = json.loads(data)
            if all(key in item for key in ["condominio_id", "referencia", "password", "comando", "porta", "tipo"]):
                if item["referencia"] == referencia and item["password"] == password and item["condominio_id"] == condominio_id:
                    ativar_relay(int(item["porta"]))
                    message = "O seu pedido foi realizado com sucesso!"
                    if item["tipo"] == "doorman" and item["doorman_id"]:
                        payload = {
                            "doorman_id": item["doorman_id"],
                            "message": message,
                            "status": True,
                            "type": item["tipo"],
                        }
                    elif item["tipo"] == "resident" and item["resident_id"]:
                        payload = {
                            "resident_id": item["resident_id"],
                            "message": message,
                            "status": True,
                            "type": item["tipo"],
                        }
                    elif item["tipo"] == "adm" and item["adm_id"]:
                        payload = {
                            "adm_id": item["adm_id"],
                            "message": message,
                            "status": True,
                            "type": item["tipo"],
                        }
                        
                    json_payload = json.dumps(payload)
                    sio.emit("confirm", json_payload)
                    #registanto entrada / saida
                    if item["tipo"] == "resident" and item["resident_id"]:
                        validateResident(page, item["resident_id"], "1" if item["comando"] == 'ENTRY' else "0")
            else:
                print("Chave não encontrada ❌")
        except Exception as e:
            print(f"erro ao processar mensagem: {e} ❌")

def on_connect(page: ft.Page):
    """Atualiza o status da conexão"""
    try:
        socket_status.bgcolor = ft.Colors.GREEN
        socket_status.content = ft.Text("ON", size=12)
        socket_id.value       = f"ID: {sio.sid}"
        socket_code.value     = f"Code: {sio.transport()}"
    except Exception as e:
        print(f"Erro na conexão: {e}")
    socket_status.update()
    socket_id.update()
    socket_code.update()

def on_disconnect(page: ft.Page):
    """Atualiza o status da interface ao desconectar"""
    try:
        socket_status.bgcolor = ft.Colors.RED
        socket_status.content = ft.Text("OFF", size=12)
        socket_id.value = "ID: n/a"
        socket_code.value = "Code: n/a"
    except Exception as e:
        print(f"Erro na desconexão: {e}")
    socket_status.update()
    socket_id.update()
    socket_code.update()

def register_socket_events(page: ft.Page):
    def handle_message(data):
        atualizar_status(page, data)
        
    sio.on("message", handle_message)
    sio.on("connect", partial(on_connect, page=page))
    sio.on("disconnect", partial(on_disconnect, page=page))
