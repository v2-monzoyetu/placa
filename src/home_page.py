import base64
import json
import platform
import requests
import flet as ft
from util import is_valid_base64
from process_status import process_list_item, process_status 
from widget import menubutton, button
from api_client import get, API_URL
from gpio_controller import ativar_relay
from socket_controller import conectar, desconectar, socket_status, socket_id, socket_code, register_socket_events
import serial
import threading
from pynput import keyboard
import time

RUNNING_ON_PI = platform.system() == "Linux"

class Estado:
    def __init__(self):
        self.condominio_id = 0
        self.condominio_list = []
        self.serial_configs = []

estado = Estado()

def home(page: ft.Page, go_login):

    # Carregar configurações seriais do client_storage (se existirem)
    estado.serial_configs = page.client_storage.get("serial_configs") or [
        {"port": "/dev/ttyS0", "baud_rate": 9600, "gpio_number": 17},
    ]

    # Campos para o diálogo de configuração de portas seriais
    port_field = ft.TextField(label="Porta Serial (ex.: /dev/ttyS0)")
    baud_field = ft.TextField(label="Baud Rate (ex.: 9600)", keyboard_type=ft.KeyboardType.NUMBER)
    gpio_field = ft.TextField(label="GPIO Number (ex.: 17)", keyboard_type=ft.KeyboardType.NUMBER)
    serial_configs_list = ft.ListView(expand=False, spacing=5, padding=10)

    def update_serial_configs_list():
        """Atualiza a lista de configurações seriais exibida no diálogo."""
        serial_configs_list.controls.clear()
        for config in estado.serial_configs:
            serial_configs_list.controls.append(
                ft.Row(
                    controls=[
                        ft.Text(f"Porta: {config['port']}, Baud: {config['baud_rate']}, GPIO: {config['gpio_number']}", size=14),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.RED,
                            on_click=lambda e, cfg=config: remove_serial_config(cfg),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )

    def add_serial_config(e):
        """Adiciona uma nova configuração de porta serial."""
        port = port_field.value.strip()
        baud = baud_field.value.strip()
        gpio = gpio_field.value.strip()
        if not port or not baud or not gpio:
            page.snack_bar.content.value = "Preencha porta, baud rate e número do GPIO!"
            page.snack_bar.bgcolor = ft.Colors.RED
            page.snack_bar.open = True
            page.update()
            return
        try:
            baud_rate = int(baud)
            gpio_number = int(gpio)
            estado.serial_configs.append({"port": port, "baud_rate": baud_rate, "gpio_number": gpio_number})
            page.client_storage.set("serial_configs", estado.serial_configs)
            port_field.value = ""
            baud_field.value = ""
            gpio_field.value = ""
            update_serial_configs_list()
            serial_configs_list.update()  # Agora seguro, pois o diálogo está na página
            page.snack_bar.content.value = "Configuração adicionada com sucesso!"
            page.snack_bar.bgcolor = ft.Colors.GREEN
            page.snack_bar.open = True
            page.update()
        except ValueError:
            page.snack_bar.content.value = "Baud rate e GPIO devem ser números!"
            page.snack_bar.bgcolor = ft.Colors.RED
            page.snack_bar.open = True
            page.update()

    def remove_serial_config(config):
        """Remove uma configuração de porta serial."""
        estado.serial_configs.remove(config)
        page.client_storage.set("serial_configs", estado.serial_configs)
        update_serial_configs_list()
        serial_configs_list.update()
        page.snack_bar.content.value = "Configuração removida com sucesso!"
        page.snack_bar.bgcolor = ft.Colors.GREEN
        page.snack_bar.open = True
        page.update()

    def show_serial_config_dialog(e):
        """Abre o diálogo de configuração de portas seriais."""
        update_serial_configs_list()
        page.open(serial_config_modal)
        serial_configs_list.update()

    # Diálogo para gerenciar portas seriais
    serial_config_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Gerenciar portas seriais"),
        content=ft.Column(
            width=400,
            wrap=False,
            spacing=12.0,
            tight=True,
            controls=[
                port_field,
                baud_field,
                gpio_field,
                button("Adicionar porta", on_click=add_serial_config),
                ft.Divider(),
                ft.Text("Portas configuradas:", weight=ft.FontWeight.BOLD),
                serial_configs_list,
            ],
        ),
        actions=[
            ft.TextButton("Fechar", on_click=lambda e: page.close(serial_config_modal)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # SnackBar para feedback
    snack_bar = ft.SnackBar(content=ft.Text("", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.GREY)
    page.snack_bar = snack_bar

    def show_snack_bar(message, bgcolor=ft.Colors.GREY):
        """Exibe o SnackBar com a mensagem desejada"""
        snack_bar.content.value = message
        snack_bar.bgcolor = bgcolor
        snack_bar.open = True
        page.update()
        
    #checar codigo
    def manual_check(type, modal, field):
        code = field.value
        if(code == ''):
            field.focus()
            show_snack_bar('Insira um código valido!', ft.Colors.RED)
            return
        
        page.close(modal)
        field.value = ''
        add_item()
    
    snack_bar = ft.SnackBar(content=ft.Text("", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.GREY)
    page.snack_bar = snack_bar
    
    def show_snack_bar(message, bgcolor=ft.Colors.GREY):
        """Exibe o SnackBar com a mensagem desejada"""
        snack_bar.content.value = message
        snack_bar.bgcolor = bgcolor
        snack_bar.open = True
        page.update()
    
    def logout(e=None):
        page.close(dlg_modal)
        page.client_storage.clear()
        go_login()
        
    def dlg_modal_close(e=None):
        page.close(dlg_modal)
        
    def show_logout_dialog(e=None):
        page.open(dlg_modal)
        
    # Criando o AlertDialog
    dlg_modal = ft.AlertDialog(
        modal=True,
        title_text_style=ft.TextStyle(size=17),
        title=ft.Text("Pretende mesmo terminar a sessão?"),
        content=ft.Text("Tem certeza que deseja sair?"),
        actions=[
            ft.TextButton("Sim", on_click=logout),
            ft.TextButton("Não", on_click=dlg_modal_close),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    morador_field  = ft.TextField(label="", autofocus=True, keyboard_type=ft.KeyboardType.NUMBER)
    morador_modal = ft.AlertDialog(
        modal=True,
        content=ft.Column(
        width=400.0,
        wrap=False,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12.0,
        tight=True,
        controls=[
            ft.Image(
                src=f"code.png",
                width=200.0,
                fit=ft.ImageFit.COVER,
                repeat=ft.ImageRepeat.NO_REPEAT,
            ),
            ft.Text("Insira o número de Telefone do Morador", text_align=ft.TextAlign.CENTER),
            morador_field,
            button("Pesquisar", on_click=lambda e: manual_check('resident', morador_modal, morador_field))
        ]
        ),
        actions=[
            ft.TextButton("Fechar", on_click=lambda e: page.close(morador_modal)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    funcionario_field  = ft.TextField(label="", autofocus=True, keyboard_type=ft.KeyboardType.NUMBER)
    funcionario_modal = ft.AlertDialog(
        modal=True,
        content=ft.Column(
        width=400.0,
        wrap=False,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12.0,
        tight=True,
        controls=[
            ft.Image(
                src=f"code.png",
                width=200.0,
                fit=ft.ImageFit.COVER,
                repeat=ft.ImageRepeat.NO_REPEAT,
            ),
            ft.Text("Insira o código do Funcionário de 9 dígitos", text_align=ft.TextAlign.CENTER),
            funcionario_field,
            button("Pesquisar", on_click=lambda e: manual_check('employee', funcionario_modal, funcionario_field))
        ]
        ),
        actions=[
            ft.TextButton("Fechar", on_click=lambda e: page.close(funcionario_modal)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    veiculo_field  = ft.TextField(label="", autofocus=True)
    veiculo_modal = ft.AlertDialog(
        modal=True,
        content=ft.Column(
        width=400.0,
        wrap=False,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12.0,
        tight=True,
        controls=[
            ft.Image(
                src=f"code.png",
                width=200.0,
                fit=ft.ImageFit.COVER,
                repeat=ft.ImageRepeat.NO_REPEAT,
            ),
            ft.Text("Insira a matrícula do Veículo", text_align=ft.TextAlign.CENTER),
            veiculo_field,
            button("Pesquisar", on_click=lambda e: manual_check('veiculo', veiculo_modal, veiculo_field))
        ]
        ),
        actions=[
            ft.TextButton("Fechar", on_click=lambda e: page.close(veiculo_modal)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    #Socket
    register_socket_events(page)
    conectar()
    
    #Lista de condominios
    list_condominios   = ft.ListView(expand=True, spacing=1, padding=0.0)
    
    def select_condominio(id):
        
        estado.condominio_id = int(id)
        page.client_storage.set("condominio_id", id)
        list_condominios.controls.clear()
        
        for item in estado.condominio_list:
            item_id = item.get('id', '0')
            list_condominios.controls.append(
                ft.ListTile(
                    selected=True if estado.condominio_id == int(item.get('id', '0')) else False,
                    content_padding=8.0,
                    title  =ft.Text(item.get('nome', 'n/a'), size=13),
                    subtitle=ft.Text(item.get('telefone', 'n/a'), size=12),
                    trailing=ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT),
                    on_click=lambda e, item_id=item_id: select_condominio(item_id)
                )
            )
        page.update()
    
    def get_condominios(e=None):
        
        list_condominios.controls.clear()
        list_condominios.controls.append(ft.Container(
            padding=12.0,
            alignment=ft.alignment.center,
            content=ft.ProgressRing()
        ))
        page.update()
        
        data = get(page, "/v1/concierge/condominios")
        list_condominios.controls.clear()
        
        if data:
            estado.condominio_id = page.client_storage.get("condominio_id") or int(data[0].get('id', '0'))
            estado.condominio_list = data

            for item in data:
                item_id = item.get('id', '0')
                list_condominios.controls.append(
                    ft.ListTile(
                        selected=True if estado.condominio_id == int(item.get('id', '0')) else False,
                        content_padding=8.0,
                        title  =ft.Text(item.get('nome', 'n/a'), size=13),
                        subtitle=ft.Text(item.get('telefone', 'n/a'), size=12),
                        trailing=ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT),
                        on_click=lambda e, item_id=item_id: select_condominio(item_id)
                    )
                )
        else:
            list_condominios.controls.append(
            ft.Container(
                padding=12.0,
                content=ft.Text("Nenhum resultado encontrado", 
                    color=ft.Colors.WHITE,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    max_lines=1,
                    text_align=ft.TextAlign.CENTER
                )
            ))
        page.update()
    
    #Lista de processos 
    list_process  = ft.ListView(expand=True, spacing=1, padding=0.0, reverse=True)
    count_process = ft.Text(f"Processos ativos: ({len(list_process.controls)})", size=14, weight=ft.FontWeight.BOLD)
    process_area = ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=8.0,
        expand=True,
        controls=[
            ft.Image(
                src=f"empty.png",
                width=280.0,
                fit=ft.ImageFit.COVER,
                repeat=ft.ImageRepeat.NO_REPEAT,
            ),
            ft.Text(
                "Nenhum processo terminado...", 
                text_align=ft.TextAlign.CENTER,
                width=ft.Window.width,
            )
        ]
    )
    
    def update_length():
        """Atualiza o contador na interface."""
        count_process.value = f"Processos ativos: {len(list_process.controls)}"
        count_process.update()
        list_process.update()

    def add_item(qrdata: dict, gpio_number: int):
        """Adiciona um novo item à lista."""

        try:
            message = "Processando..."
            if qrdata["type"] == "employee":
                message = "Funcionário"
            elif qrdata["type"] == "resident":
                message = "Morador"
            elif qrdata["type"] == "vehicle":
                message = "Veículo"
            
            # Criando o item inicial com status "load"
            tile = process_list_item(message, "n/a", "load")
            list_process.controls.insert(0, tile)
            update_length()
            list_process.scroll_to(offset=0, duration=500)
            
            if(list_process.length > 10):
                clear_process(None)
            
            # Verifica os dados
            verify: dict = check(qrdata)
            response = verify.get("body", {})
            result = response.get("result", {})

            if result.get("success"):
                item = result.get("data", {})
                if qrdata["type"] == "employee":
                    ativar_relay(gpio_number)
                    checkValidation = validateEmployee(item[0].get("id", "0"), item[0].get("situation", "n/a"))
                    if checkValidation:
                        tile.title.value = "Funcionário"
                        tile.subtitle.value = item[0].get("nome", "n/a")
                        tile.trailing.content = ft.Icon(ft.Icons.CHECK, color=ft.Colors.GREEN)
                        process_area.controls.clear()
                        process_area.controls.append(process_status("Funcionário", funcionario=item[0]))
                        process_area.update()
                    else:
                        tile.title.value = "Funcionário"
                        tile.subtitle.value = item[0].get("nome", "n/a")
                        tile.trailing.content = ft.Icon(ft.Icons.ERROR, color=ft.Colors.YELLOW)
                elif qrdata["type"] == "resident":
                    ativar_relay(gpio_number)
                    checkValidation = validateResident(item[0].get("id", "0"), item[0].get("status", "1"))
                    if checkValidation:
                        tile.title.value = "Morador"
                        tile.subtitle.value = item[0].get("nome", "n/a")
                        tile.trailing.content = ft.Icon(ft.Icons.CHECK, color=ft.Colors.GREEN)
                        process_area.controls.clear()
                        process_area.controls.append(process_status("Morador", morador=item[0]))
                        process_area.update()
                    else:
                        tile.title.value = "Morador"
                        tile.subtitle.value = item[0].get("nome", "n/a")
                        tile.trailing.content = ft.Icon(ft.Icons.ERROR, color=ft.Colors.YELLOW)
                elif qrdata["type"] == "vehicle":
                    ativar_relay(gpio_number)
                    checkValidation = validateVehicle(item.get("id", "0"), item.get("motoristas", {})[0].get("id", "0"), item.get("situation", "1"))
                    if checkValidation:
                        tile.title.value = "Veículo"
                        tile.subtitle.value = item.get("matricula", "n/a")
                        tile.trailing.content = ft.Icon(ft.Icons.CHECK, color=ft.Colors.GREEN)
                        process_area.controls.clear()
                        process_area.controls.append(process_status("Veículo", veiculo=item))
                        process_area.update()
                    else:
                        tile.title.value = "Veículo"
                        tile.subtitle.value = item[0].get("matricula", "n/a")
                        tile.trailing.content = ft.Icon(ft.Icons.ERROR, color=ft.Colors.YELLOW)
                elif qrdata["type"] == "visitor":
                    ativar_relay(gpio_number)
                    checkValidation = validateVisitor(qrdata["code"])
                    if checkValidation:
                        tile.title.value = "Visitante"
                        tile.subtitle.value = item.get("nome", "n/a")
                        tile.trailing.content = ft.Icon(ft.Icons.CHECK, color=ft.Colors.GREEN)
                        process_area.controls.clear()
                        process_area.controls.append(process_status("Visitante", visitor=item))
                        process_area.update()
                    else:
                        tile.title.value = "Visitante"
                        tile.subtitle.value = item[0].get("nome", "n/a")
                        tile.trailing.content = ft.Icon(ft.Icons.ERROR, color=ft.Colors.YELLOW)
            else:
                if(message == "Processando..."):
                    message = "Desconhecido"
                    
                tile.title.value = message
                tile.subtitle.value = "Negado"
                tile.trailing.content = ft.Icon(ft.Icons.ERROR, color=ft.Colors.YELLOW)

            list_process.update()
            page.update()
            
        except Exception as e:
            print(f"Erro ao processar o QRCode: {str(e)}")
            message = "Desconhecido"
            tile.title.value = message
            tile.subtitle.value = "Negado"
            tile.trailing.content = ft.Icon(ft.Icons.ERROR, color=ft.Colors.YELLOW)
            list_process.update()


    def clear_process(e):
        """Remove o último item da lista."""
        if list_process.controls:
            list_process.controls.clear()
            update_length()
            list_process.scroll_to(offset=0, duration=500)
            
    #interface
    pagelet = ft.Pagelet(
        content=ft.Container(
            margin=8.0,
            expand=True,
            content=ft.Row(
                spacing=8.0,
                expand=True,
                controls=[
                    ft.Container(
                        width=160.0,
                        height=ft.Window.height,
                        content=ft.Card(
                            expand=True,
                            content=ft.Container(
                                margin=8.0,
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=8.0,
                                    expand=True,
                                    controls=[
                                        menubutton("Menu", ft.Icons.MENU, ft.Colors.WHITE, lambda e:show_snack_bar("Indisponível", ft.Colors.RED)),
                                        menubutton("Veículos", ft.Icons.CAR_RENTAL_SHARP, "#A8E349", lambda e: page.open(veiculo_modal)),
                                        menubutton("Moradores", ft.Icons.PERSON, "#F858A2", lambda e: page.open(morador_modal)),
                                        menubutton("Funcionários", ft.Icons.GROUP, "#CB9EF6", lambda e: page.open(funcionario_modal)),
                                        ft.Container(expand=True),
                                        menubutton("Configurações", ft.Icons.SETTINGS, ft.Colors.WHITE, show_serial_config_dialog),
                                    ]
                                ),
                            )
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        height=ft.Window.height,
                        content=ft.Card(
                            expand=True,
                            content=ft.Container(
                                expand=True,
                                margin=8.0,
                                content=process_area,
                            )
                        ),
                    ),
                    ft.Container(
                        width=250.0,
                        height=ft.Window.height,
                        content=ft.Card(
                            expand=True,
                            content=ft.Container(
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=0.0,
                                    expand=True,
                                    controls=[
                                        ft.Container(
                                            padding=8.0,
                                            content=ft.Row(
                                                controls=[
                                                    ft.GestureDetector(
                                                        content=socket_status,
                                                        on_tap=desconectar
                                                    ),
                                                    ft.Container(
                                                        content=ft.Column(
                                                            spacing=0.0,
                                                            expand=True,
                                                            controls=[
                                                                socket_id,
                                                                socket_code,
                                                            ]
                                                        )
                                                    )
                                                ]
                                            )
                                        ),
                                        ft.Container(
                                            expand=True,
                                            content=ft.Column(
                                                spacing=0.0,
                                                controls=[
                                                    ft.Container(
                                                        bgcolor=ft.Colors.BLACK87,
                                                        padding=10,
                                                        content=ft.Row(
                                                            controls=[
                                                                ft.Text("Condomínios", size=14, weight=ft.FontWeight.BOLD),
                                                                ft.Container(expand=True),
                                                                ft.IconButton(
                                                                    icon=ft.Icons.REFRESH, 
                                                                    icon_color=ft.Colors.WHITE,
                                                                    on_click=lambda e: get_condominios()
                                                                ),
                                                                ft.IconButton(
                                                                    icon=ft.Icons.LOGOUT_ROUNDED, 
                                                                    icon_color=ft.Colors.WHITE,
                                                                    on_click=show_logout_dialog
                                                                )
                                                            ]
                                                        )
                                                    ),
                                                    ft.Container(
                                                        expand=True,
                                                        content=list_condominios
                                                    )
                                                ]
                                            )
                                        ),
                                        ft.Container(
                                            expand=True,
                                                content=ft.Column(
                                                spacing=0.0,
                                                controls=[
                                                    ft.Container(
                                                        bgcolor=ft.Colors.BLACK87,
                                                        padding=10,
                                                        content=ft.Row(
                                                            controls=[
                                                                count_process,
                                                                ft.Container(expand=True),
                                                                ft.IconButton(
                                                                    icon=ft.Icons.CLEAR, 
                                                                    icon_color=ft.Colors.WHITE,
                                                                    on_click=clear_process
                                                                )
                                                            ]
                                                        )
                                                    ),
                                                    ft.Container(
                                                        expand=True,
                                                        content=list_process
                                                    )
                                                ]
                                            )
                                        ),
                                        ft.Divider(height=0.0),
                                        ft.Container(
                                            padding=8.0,
                                            content=ft.Text("Control JP", size=13.0, text_align=ft.TextAlign.LEFT)
                                        )
                                    ]
                                ),
                            )
                        ),
                    ),
                ]
            ),
        ),
        bgcolor=ft.Colors.TRANSPARENT,
        expand=True,
    )
    
    #pynput
    # Variáveis para captura do QR code
    scanned_input = []
    last_key_time = time.time()
    BUFFER_TIMEOUT = 0.2

    def on_press(key):
        nonlocal last_key_time, scanned_input
        current_time = time.time()

        # Limpa o buffer se a sequência for interrompida (pausa maior que BUFFER_TIMEOUT)
        if current_time - last_key_time > BUFFER_TIMEOUT:
            scanned_input.clear()

        try:
            # Captura caracteres alfanuméricos
            char = key.char
            if char:
                scanned_input.append(char)
        except AttributeError:
            # Detecta a tecla Enter para finalizar a leitura
            if key == keyboard.Key.enter:
                qr_code = ''.join(scanned_input)
                if qr_code:
                    scanned_input.clear()
                    scan_result(qr_code, 17)  # Usando GPIO 17 como padrão
                    
        last_key_time = current_time

    # Inicia o listener de teclado em uma thread separada
    def start_listener():
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

    # Inicia a thread do pynput
    threading.Thread(target=start_listener, daemon=True).start()
    
    def scan_result(result: str, gpio_number: int):
        """Processa o resultado escaneado."""
        if is_valid_base64(result):
            try:
                value = base64.b64decode(result).decode("utf-8")
                qrdata = json.loads(value)
                add_item(qrdata, gpio_number)
            except Exception as e:
                show_snack_bar(f"Erro ao processar o QRCode: {str(e)}", ft.Colors.RED)
        elif len(result.strip()) == 20 or len(result.strip()) == 10:
            check({"code": result}, gpio_number)
        else:
            show_snack_bar("QRCode inválido!", ft.Colors.RED)

    def check(qrdata: dict, gpio_number: int = 17):
        """Verifica o QRCode."""
        token = page.client_storage.get("token")
        headers = {"Authorization": f"Bearer {token}"}
        if qrdata.get("code"):
            param = f"?code={qrdata.get('code')}"
            route = f"{API_URL}/v1/concierge/check/visitor/{page.client_storage.get('condominio_id')}{param}"
        else:
            param = f"?id={qrdata.get('id')}&type={qrdata.get('type')}&code={qrdata.get('code')}"
            route = f"{API_URL}/v1/concierge/check/qrcode/{page.client_storage.get('condominio_id')}{param}"
        try:
            response = requests.get(route, headers=headers, timeout=10)
            res_body = response.json()
            return {'body': res_body}
        except Exception as e:
            show_snack_bar(f"Erro de conexão: {str(e)}", ft.Colors.RED)

    def validateResident(id, status):
        """Verifica o QRCode."""

        token = page.client_storage.get("token")
        headers = {"Authorization": f"Bearer {token}"}
        
        route = f"{API_URL}/v1/concierge/valid/resident/{page.client_storage.get('condominio_id')}"

        try:
            response = requests.post(route, params={"id": id, "status": status}, headers=headers, timeout=10)
            response.raise_for_status()
            if response.status_code == 200:
                return True
            else:
                return False
                
        except Exception as e:
            return False
            
    def validateEmployee(id, situation):
        """Verifica o QRCode."""

        token = page.client_storage.get("token")
        headers = {"Authorization": f"Bearer {token}"}
        
        route = f"{API_URL}/v1/concierge/valid/employee/{page.client_storage.get('condominio_id')}"

        try:
            response = requests.post(route, params={"id": id, "situation": situation}, headers=headers, timeout=10)
            response.raise_for_status()
            if response.status_code == 200:
                return True
            else:
                return False  
        except Exception as e:
            return False   
    
    def validateVehicle(id, motoristaId, status):
        """Verifica o QRCode."""

        token = page.client_storage.get("token")
        headers = {"Authorization": f"Bearer {token}"}
        
        route = f"{API_URL}/v1/concierge/viatura/{page.client_storage.get('condominio_id')}"

        try:
            response = requests.post(route, params={"id": id, "status": status, "motoristaId": motoristaId}, headers=headers, timeout=10)
            response.raise_for_status()
            if response.status_code == 200:
                return True
            else:
                return False  
        except Exception as e:
            return False
    
    def validateVisitor(code):
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
            print(f"{str(e)}|")
            return False
    
    # Configuração da porta serial
    if RUNNING_ON_PI:
        serial_connections = []
        for config in estado.serial_configs:
            try:
                ser = serial.Serial(
                    port=config["port"],
                    baudrate=config["baud_rate"],
                    timeout=1,  # Reduzido para leituras mais rápidas
                    parity=serial.PARITY_NONE,  # Configurações padrão, ajuste conforme o dispositivo
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS
                )
                serial_connections.append({"serial": ser, "gpio_number": config["gpio_number"]})
                print(f"Conectado à porta {config['port']} com baud rate {config['baud_rate']}, GPIO {config['gpio_number']}")
            except serial.SerialException as e:
                print(f"Erro ao abrir a porta {config['port']}: {e}")
                continue

        def ler_uart(ser, port_name, gpio_number):
            """Lê dados de uma porta serial específica e passa o gpio_number."""
            while True:
                try:
                    if ser.in_waiting > 0:
                        data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore').strip()
                        if data:  # Processa apenas se houver dados válidos
                            print(f"Dados brutos recebidos de {port_name} (GPIO {gpio_number}): {repr(data)}")
                            print(f"QR code processado de {port_name} (GPIO {gpio_number}): {data}")
                            scan_result(data, gpio_number)
                    time.sleep(0.1)  # Igual ao código de teste
                except serial.SerialException as e:
                    print(f"Erro na leitura da porta {port_name}: {e}")
                    time.sleep(1)

        for conn in serial_connections:
            ser = conn["serial"]
            gpio_number = conn["gpio_number"]
            port_name = ser.port
            thread = threading.Thread(target=ler_uart, args=(ser, port_name, gpio_number), daemon=True)
            thread.start()

        def on_page_close(e):
            """Fecha todas as portas seriais ao encerrar a aplicação."""
            for conn in serial_connections:
                ser = conn["serial"]
                if ser.is_open:
                    ser.close()
                    print(f"Porta {ser.port} fechada.")
            page.close()

        page.on_close = on_page_close

    page.clean()
    page.add(pagelet)
    page.add(snack_bar)
    page.update()
    
    get_condominios()