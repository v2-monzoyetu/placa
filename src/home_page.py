import json
import time
import serial
import base64
import platform
import threading
import flet as ft
from pynput import keyboard
from util import is_valid_base64
from api_client import get
from widget import menubutton, button
from gpio_controller import desativar_relay
from process_area import ProcessItem
from socket_controller import conectar, desconectar, socket_status, socket_id, socket_code, register_socket_events

RUNNING_ON_PI = platform.system() == "Linux"

class Estado:
    def __init__(self):
        self.condominio_id = 0
        self.condominio_list = []
        self.serial_configs = []

estado = Estado()

def home(page: ft.Page, go_login):

    # SnackBar para feedback
    snack_bar = ft.SnackBar(content=ft.Text("", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.GREY)
    page.snack_bar = snack_bar

    def show_snack_bar(message: str, bgcolor=ft.Colors.GREY):
        """Exibe o SnackBar com a mensagem desejada"""
        snack_bar.content.value = message
        snack_bar.bgcolor = bgcolor
        snack_bar.open = True
        page.update()
        
    # Carregar configurações seriais do client_storage (se existirem)
    estado.serial_configs = page.client_storage.get("serial_configs") or [
        {"port": "/dev/ttyS1", "baud_rate": 9600, "gpio_number": 34, "type": "ENTRY"},
    ]

    # Campos para o diálogo de configuração de portas seriais
    gpio_default_field = ft.TextField(
        label="GPIO Number default (ex.: 34)", 
        on_change=lambda e: page.client_storage.set("default_gpio_number", e.control.value), 
        keyboard_type=ft.KeyboardType.NUMBER, 
        value=str(page.client_storage.get("default_gpio_number") or 34)
    )
    port_field = ft.TextField(label="Porta Serial (ex.: /dev/ttyS0)")
    baud_field = ft.TextField(label="Baud Rate (ex.: 9600)", keyboard_type=ft.KeyboardType.NUMBER)
    gpio_field = ft.TextField(label="GPIO Number (ex.: 34)", keyboard_type=ft.KeyboardType.NUMBER)
    type_field = ft.TextField(label="Tipo (ENTRY OR EXIT)", keyboard_type=ft.KeyboardType.TEXT)
    serial_configs_list = ft.ListView(expand=False, spacing=5, padding=10)

    def update_serial_configs_list():
        """Atualiza a lista de configurações seriais exibida no diálogo."""
        serial_configs_list.controls.clear()
        for config in estado.serial_configs:
            serial_configs_list.controls.append(
                ft.Row(
                    controls=[
                        ft.Text(f"Porta: {config['port']}, Baud: {config['baud_rate']}, GPIO: {config['gpio_number']}, Tipo: {config['type']}", size=14),
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
        type = type_field.value.strip()
        if not port or not baud or not gpio:
            show_snack_bar("Preencha porta, baud rate e número do GPIO!", ft.Colors.RED)
            return
        try:
            baud_rate = int(baud)
            gpio_number = int(gpio)
            estado.serial_configs.append({"port": port, "baud_rate": baud_rate, "gpio_number": gpio_number, "type": type})
            page.client_storage.set("serial_configs", estado.serial_configs)
            port_field.value = ""
            baud_field.value = ""
            gpio_field.value = ""
            type_field.value = ""
            update_serial_configs_list()
            serial_configs_list.update()
            show_snack_bar("Configuração adicionada com sucesso!", ft.Colors.GREEN)
        except ValueError:
            show_snack_bar("Baud rate e GPIO devem ser números!", ft.Colors.RED)

    def remove_serial_config(config):
        """Remove uma configuração de porta serial."""
        estado.serial_configs.remove(config)
        page.client_storage.set("serial_configs", estado.serial_configs)
        update_serial_configs_list()
        serial_configs_list.update()
        show_snack_bar("Configuração removida com sucesso!", ft.Colors.GREEN)

    def show_serial_config_dialog(e):
        """Abre o diálogo de configuração de portas seriais."""
        update_serial_configs_list()
        page.open(serial_config_modal)
        serial_configs_list.update()

    # Diálogo para gerenciar portas seriais
    serial_config_modal = ft.AlertDialog(
        modal=True,
        title_text_style=ft.TextStyle(size=17),
        title=ft.Text("Gerenciar portas seriais"),
        content=ft.Column(
            width=440,
            wrap=False,
            spacing=10.0,
            tight=True,
            controls=[
                gpio_default_field,
                ft.Divider(),
                ft.Row(
                    wrap=True,
                    expand=False,
                    width=440,
                    spacing=10.0,
                    controls=[
                        ft.Container(
                            content=port_field,
                            width=215
                        ),
                        ft.Container(
                            content=baud_field,
                            width=215
                        ),
                    ]
                ),
                ft.Row(
                    wrap=True,
                    expand=False,
                    width=440,
                    spacing=10.0,
                    controls=[
                        ft.Container(
                            content=gpio_field,
                            width=215
                        ),
                        ft.Container(
                            content=type_field,
                            width=215
                        ),
                    ]
                ),
                serial_configs_list,
                button("Adicionar porta", on_click=add_serial_config),
            ],
        ),
        actions=[
            ft.TextButton("Fechar", on_click=lambda e: page.close(serial_config_modal)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def show_gpio_config_dialog(e):
        update_serial_configs_list()
        page.open(gpio_config_modal)
        serial_configs_list.update()
        
    # Diálogo para gerenciar portas gpio
    gpio_config_modal = ft.AlertDialog(
        modal=True,
        title_text_style=ft.TextStyle(size=17),
        title=ft.Text("Gerenciar portas gpio"),
        content=ft.Column(
            width=400,
            wrap=False,
            spacing=10.0,
            tight=True,
            controls=[
                ft.Row(
                    wrap=True,
                    expand=False,
                    width=400,
                    spacing=10.0,
                    controls=[
                        ft.Container(
                            content=port_field,
                            width=215
                        ),
                        ft.Container(
                            content=baud_field,
                            width=215
                        ),
                    ]
                ),
                button("Adicionar porta", on_click=add_serial_config),
            ],
        ),
        actions=[
            ft.TextButton("Fechar", on_click=lambda e: page.close(serial_config_modal)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
        
    #checar codigo
    def manual_check(check_type, modal, field):
        code = field.value.strip()
        if not code:
            field.focus()
            show_snack_bar("Insira um código válido!", ft.Colors.RED)
            return
        page.close(modal)
        field.value = ""
        add_item({"type": check_type, "code": code}, int(page.client_storage.get("default_gpio_number") or 34))
    
    def logout(e=None):
        page.close(dlg_modal)
        page.client_storage.clear()
        go_login()
        
    # Criando o AlertDialog
    dlg_modal = ft.AlertDialog(
        modal=True,
        title_text_style=ft.TextStyle(size=17),
        title=ft.Text("Pretende mesmo terminar a sessão?"),
        content=ft.Text("Tem certeza que deseja sair?"),
        actions=[
            ft.TextButton("Sim", on_click=logout),
            ft.TextButton("Não", on_click=lambda e:page.close(dlg_modal)),
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
    list_process  = ft.ListView(expand=True, spacing=1, padding=0.0, reverse=False)
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

    def add_item(qrdata: dict, gpio_number: int, type: str = "ENTRY"):
        """Adiciona um novo item à lista compartilhada."""
        # Cria o item independente
        try:
            print("Adicionando item...")
            process_item = ProcessItem(page, show_snack_bar, process_area, qrdata, gpio_number, type, on_complete_callback=update_length)
            
            if len(list_process.controls) > 100:
                clear_process(None)
            list_process.controls.insert(0, process_item)
            update_length()
            list_process.scroll_to(offset=0, duration=500)
            page.update() 
                
            # Inicia o processamento independente do item
            process_item.process()
        except Exception as e:
            print(f"Erro ao adicionar item: {str(e)}")
            raise e

    def update_length():
        """Atualiza o contador da lista compartilhada."""
        count_process.value = f"Processos ativos: {len(list_process.controls)}"
        count_process.update()
        list_process.update()

    def clear_process(e):
        """Limpa a lista compartilhada."""
        if list_process.controls:
            list_process.controls.clear()
            update_length()
            list_process.scroll_to(offset=0, duration=500)
            page.update()
            
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
                                        menubutton("GPIO", ft.Icons.VIEW_COZY, ft.Colors.WHITE, show_gpio_config_dialog),
                                        #menubutton("Veículos", ft.Icons.CAR_RENTAL_SHARP, "#A8E349", lambda e: page.open(veiculo_modal)),
                                        #menubutton("Moradores", ft.Icons.PERSON, "#F858A2", lambda e: page.open(morador_modal)),
                                        #menubutton("Funcionários", ft.Icons.GROUP, "#CB9EF6", lambda e: page.open(funcionario_modal)),
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
                                                                    on_click=lambda e: page.open(dlg_modal),
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
                    try:
                        scan_result(qr_code, int(page.client_storage.get("default_gpio_number")), "ENTRY")
                    except Exception as e:
                        scan_result(qr_code, 34, "ENTRY")
                    
        last_key_time = current_time

    # Inicia o listener de teclado em uma thread separada
    def start_listener():
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

    # Inicia a thread do pynput
    threading.Thread(target=start_listener, daemon=True).start()
    
    def scan_result(result: str, gpio_number: int, type: str = "ENTRY"):
        """Processa o resultado escaneado."""
        if is_valid_base64(result):
            try:
                value = base64.b64decode(result).decode("utf-8")
                qrdata = json.loads(value)
                add_item(qrdata, gpio_number, type)
            except Exception as e:
                show_snack_bar(f"Erro ao processar o QRCode: {str(e)}", ft.Colors.RED)
        elif len(result.strip()) == 20 or len(result.strip()) == 10:
            add_item({"code": result}, gpio_number, 'Entry')
        else:
            show_snack_bar("QRCode inválido!", ft.Colors.RED)
    
    # Configuração da porta serial
    if RUNNING_ON_PI:
        serial_connections = []
        for config in estado.serial_configs:
            try:
                
                # Inicializa o GPIO como desligado
                try:
                    desativar_relay(config["gpio_number"])
                except Exception as e:
                    print(f"Erro ao inicializar GPIO {config['gpio_number']} como desligado: {e}")
                    continue
            
                ser = serial.Serial(
                    port=config["port"],
                    baudrate=config["baud_rate"],
                    timeout=1,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS
                )
                serial_connections.append({"serial": ser, "gpio_number": config["gpio_number"], "type": config["type"]})
                print(f"Conectado à porta {config['port']} com baud rate {config['baud_rate']}, GPIO {config['gpio_number']}")
            except serial.SerialException as e:
                print(f"Erro ao abrir a porta {config['port']}: {e}")
                continue

        def ler_uart(ser, port_name, gpio_number, type):
            """Lê dados de uma porta serial específica e passa o gpio_number."""
            while True:
                try:
                    if ser.in_waiting > 0:
                        data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore').strip()
                        if data:  # Processa apenas se houver dados válidos
                            print(f"Dados brutos recebidos de {port_name} (GPIO {gpio_number}): {repr(data)}")
                            print(f"QR code processado de {port_name} (GPIO {gpio_number}): {data}")
                            scan_result(data, gpio_number, type)
                    time.sleep(0.1)  # Igual ao código de teste
                except serial.SerialException as e:
                    print(f"Erro na leitura da porta {port_name}: {e}")
                    time.sleep(1)

        for conn in serial_connections:
            ser = conn["serial"]
            gpio_number = conn["gpio_number"]
            type = conn["type"]
            port_name = ser.port
            thread = threading.Thread(target=ler_uart, args=(ser, port_name, gpio_number, type), daemon=True)
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
    #Socket
    register_socket_events(page)
    conectar()
