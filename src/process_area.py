import flet as ft
import requests
from api_client import API_URL
from gpio_controller import ativar_relay
from validator import validateResident, validateEmployee, validateVehicle, validateVisitor

imageLink = "https://painel.monzoyetu.com"

class ProcessItem(ft.Column):
    def __init__(self, page: ft.Page, show_snack_bar, process_area, qrdata: dict, gpio_number: int, reader_type: str = "UNKNOWN", on_complete_callback=None):
        try:    
            self.process_area   = process_area
            self.show_snack_bar = show_snack_bar
            self.page           = page
            self.qrdata         = qrdata
            self.gpio_number    = gpio_number
            self.reader_type    = reader_type
            self.on_complete_callback = on_complete_callback
            
            self.message = "Processando..."
            if self.qrdata["type"] == "employee":
                self.message = "Funcionário"
            elif self.qrdata["type"] == "resident":
                self.message = "Morador"
            elif self.qrdata["type"] == "vehicle":
                self.message = "Veículo"
                
            # Aqui cria o primeiro tile
            self.tile = process_list_item(self.message, "n/a", "load")

            # Column precisa de controls
            super().__init__(controls=[self.tile])
                            
        except Exception as e:
            print(f"DEBUG: Erro ao inicializar ProcessItem: {str(e)}")
            raise e

    def process(self):
        try:
            verify: dict = self.check()
            response     = verify.get("body", {})
            result       = response.get("result", {})

            if result.get("success"):
                item = result.get("data", {})
                if self.qrdata["type"] == "employee":
                    ativar_relay(self.gpio_number)
                    checkValidation = validateEmployee(self.page, item[0].get("id", "0"), item[0].get("situation", "n/a"))
                    if checkValidation:
                        self.tile.title.value = "Funcionário"
                        self.tile.subtitle.value = item[0].get("nome", "n/a")
                        self.tile.trailing.content = ft.Icon(ft.Icons.CHECK, color=ft.Colors.GREEN)
                        self.process_area.controls.clear()
                        self.process_area.controls.append(process_status("Funcionário", funcionario=item[0]))
                        self.process_area.update()
                    else:
                        self.tile.title.value = "Funcionário"
                        self.tile.subtitle.value = item[0].get("nome", "n/a")
                        self.tile.trailing.content = ft.Icon(ft.Icons.ERROR, color=ft.Colors.YELLOW)
                elif self.qrdata["type"] == "resident":
                    ativar_relay(self.gpio_number)
                    checkValidation = validateResident(self.page, item[0].get("id", "0"), item[0].get("status", "1"))
                    if checkValidation:
                        self.tile.title.value = "Morador"
                        self.tile.subtitle.value = item[0].get("nome", "n/a")
                        self.tile.trailing.content = ft.Icon(ft.Icons.CHECK, color=ft.Colors.GREEN)
                        self.process_area.controls.clear()
                        self.process_area.controls.append(process_status("Morador", morador=item[0]))
                        self.process_area.update()
                    else:
                        self.tile.title.value = "Morador"
                        self.tile.subtitle.value = item[0].get("nome", "n/a")
                        self.tile.trailing.content = ft.Icon(ft.Icons.ERROR, color=ft.Colors.YELLOW)
                elif self.qrdata["type"] == "vehicle":
                    ativar_relay(self.gpio_number)
                    checkValidation = validateVehicle(self.page, item.get("id", "0"), item.get("motoristas", {})[0].get("id", "0"), item.get("situation", "1"))
                    if checkValidation:
                        self.tile.title.value = "Veículo"
                        self.tile.subtitle.value = item.get("matricula", "n/a")
                        self.tile.trailing.content = ft.Icon(ft.Icons.CHECK, color=ft.Colors.GREEN)
                        self.process_area.controls.clear()
                        self.process_area.controls.append(process_status("Veículo", veiculo=item))
                        self.process_area.update()
                    else:
                        self.tile.title.value = "Veículo"
                        self.tile.subtitle.value = item[0].get("matricula", "n/a")
                        self.tile.trailing.content = ft.Icon(ft.Icons.ERROR, color=ft.Colors.YELLOW)
                elif self.qrdata["type"] == "visitor":
                    ativar_relay(self.gpio_number)
                    checkValidation = validateVisitor(self.page, self.qrdata["code"])
                    if checkValidation:
                        self.tile.title.value = "Visitante"
                        self.tile.subtitle.value = item.get("nome", "n/a")
                        self.tile.trailing.content = ft.Icon(ft.Icons.CHECK, color=ft.Colors.GREEN)
                        self.process_area.controls.clear()
                        self.process_area.controls.append(process_status("Visitante", visitor=item))
                        self.process_area.update()
                    else:
                        self.tile.title.value = "Visitante"
                        self.tile.subtitle.value = item[0].get("nome", "n/a")
                        self.tile.trailing.content = ft.Icon(ft.Icons.ERROR, color=ft.Colors.YELLOW)
                self.update()
            else:
                if(self.message == "Processando..."):
                    self.message = "Desconhecido"
                    
                self.tile.title.value = self.message
                self.tile.subtitle.value = "Negado"
                self.tile.trailing.content = ft.Icon(ft.Icons.ERROR, color=ft.Colors.YELLOW)
                self.update()
                        
        except Exception as e:
            message = "Desconhecido"
            self.tile.title.value = message
            self.tile.subtitle.value = "Negado"
            self.tile.trailing.content = ft.Icon(ft.Icons.ERROR, color=ft.Colors.YELLOW)
            self.update()
            raise e

    def check(self):
        """Verifica o QRCode."""
        token = self.page.client_storage.get("token")
        headers = {"Authorization": f"Bearer {token}"}
        if self.qrdata.get("code"):
            param = f"?code={self.qrdata.get('code')}"
            route = f"{API_URL}/v1/concierge/check/visitor/{self.page.client_storage.get('condominio_id')}{param}"
        else:
            param = f"?id={self.qrdata.get('id')}&type={self.qrdata.get('type')}&code={self.qrdata.get('code')}"
            route = f"{API_URL}/v1/concierge/check/qrcode/{self.page.client_storage.get('condominio_id')}{param}"
        try:
            response = requests.get(route, headers=headers, timeout=10)
            res_body = response.json()
            return {'body': res_body}
        except Exception as e:
            self.show_snack_bar(f"Erro de conexão: {str(e)}", ft.Colors.RED)
            return {}

def process_list_item(message: str, sub_message: str, trailing: str):
    return ft.ListTile(
        leading=ft.Icon(ft.Icons.CHEVRON_RIGHT),
        title=ft.Text(message, size=14, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
        subtitle=ft.Text(sub_message, size=13, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
        trailing=ft.Container(
            width=16,
            height=16,
            content=ft.ProgressRing() if trailing == "load" else \
                ft.Icon(ft.Icons.CHECK, color=ft.Colors.GREEN) if trailing == "success" else \
                ft.Icon(ft.Icons.ERROR, color=ft.Colors.YELLOW)
        ),
    )

def process_status(tipo: str, veiculo=None, morador=None, funcionario=None, visitor=None):
    style = ft.TextStyle(size=30)
    if tipo == "Veículo" and veiculo:
        return ft.Column(
            controls=[
                ft.Text(tipo, style=style),
                ft.Text(f"{veiculo['categoria']}: {veiculo['quadra']} - {veiculo['subCategoria']}: {veiculo['lote']}", style=style),
                ft.Text(f"Matrícula: {veiculo['matricula']}", style=style),
                ft.Text(f"Marca: {veiculo['marca']} | Modelo: {veiculo['modelo']}", style=style),
                ft.Text(f"Motorista: {veiculo['motoristas'][0]['nome']}", style=style),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    elif tipo == "Morador" and morador:
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Image(
                        src=f"{imageLink}/storage/resident/{morador['foto'] if morador['foto'] else 'default.png'}",
                        width=250,
                        height=250,
                        fit=ft.ImageFit.COVER,
                        repeat=ft.ImageRepeat.NO_REPEAT,
                        border_radius=ft.border_radius.all(250),),
                    width=260,
                    height=260,
                    border=ft.border.all(5, ft.Colors.WHITE),
                    border_radius=ft.border_radius.all(260),
                    padding=5,
                    alignment=ft.alignment.center,
                ),
                ft.Text(tipo, style=style),
                ft.Text(morador['nome'], style=style),
                ft.Text(f"{morador['categoria']}: {morador['quadra']} - {morador['sub_categoria']}: {morador['lote']}", style=style),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    elif tipo == "Funcionário" and funcionario:
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Image(
                    src=f"{imageLink}/storage/employees/{funcionario['foto'] if funcionario['foto'] else 'default.png'}",
                    width=250.0,
                    height=250.0,
                    fit=ft.ImageFit.COVER,
                    repeat=ft.ImageRepeat.NO_REPEAT,
                    border_radius=ft.border_radius.all(250),),
                    width=260,
                    height=260,
                    border=ft.border.all(5, ft.Colors.WHITE),
                    border_radius=ft.border_radius.all(260),
                    padding=5,
                    alignment=ft.alignment.center,
                ),
                ft.Text(tipo, style=style),
                ft.Text(funcionario['nome'], style=style),
                ft.Text(f"{funcionario['categoria']}: {funcionario['quadra']} - {funcionario['sub_categoria']}: {funcionario['lote']}", style=style),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    elif tipo == "Visitante" and visitor:
        return ft.Column(
            controls=[
                ft.Text(tipo, style=style),
                ft.Text(visitor['nome'], style=style),
                ft.Text(f"{visitor['categoria']}: {visitor['quadra']} - {visitor['sub_categoria']}: {visitor['lote']}", style=style),
                ft.Text("Entrada" if visitor['status'] == "2" else "Saída", style=style),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    else:
        return ft.Container()