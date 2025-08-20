import flet as ft

imageLink = "https://painel.monzoyetu.com"

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
                ft.Image(
                    src=f"{imageLink}/storage/resident/{morador['foto'] if morador['foto'] else 'default.png'}",	
                    width=250.0,
                    height=250.0,
                    fit=ft.ImageFit.COVER,
                    repeat=ft.ImageRepeat.NO_REPEAT,
                    border_radius=ft.border_radius.all(250),
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
                ft.Image(
                    src=f"{imageLink}/storage/employees/{funcionario['foto'] if funcionario['foto'] else 'default.png'}",	
                    width=250.0,
                    height=250.0,
                    fit=ft.ImageFit.COVER,
                    repeat=ft.ImageRepeat.NO_REPEAT,
                    border_radius=ft.border_radius.all(250),
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