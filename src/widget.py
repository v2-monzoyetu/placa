import flet as ft

def menubutton(name, icon, color, on_click):
    return ft.ElevatedButton(
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8.0)
        ),
        content=ft.Container(
            padding=8.0,
            border_radius=8.0,
            alignment=ft.alignment.center,
            content=ft.Column(
                spacing=8.0,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        name=icon, 
                        color=color,
                        size=28,
                    ),
                    ft.Text(name, color=ft.Colors.WHITE),
                ]
            ),
        ),
        on_click=on_click
    )
    
def button(name, on_click):
    return ft.ElevatedButton(
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8.0),
            bgcolor="#063b92"
        ),
        content=ft.Container(
            padding=12.0,
            border_radius=12.0,
            alignment=ft.alignment.center,
            content=ft.Text(name, color=ft.Colors.WHITE)
        ),
        on_click=on_click
    )

def create_drawer(page: ft.Page):
    
    user_data = page.client_storage.get("user") or {}
    nome      = user_data.get("nome", "Usuário")
    building  = user_data.get("condominio_id", "Condomínio")

    drawer = ft.NavigationDrawer(
        controls=[
            ft.Container(
                width=page.width,
                height=160.0,
                bgcolor=ft.Colors.BLUE,
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(
                            ft.Icons.ACCOUNT_CIRCLE,
                            size=80,
                            color=ft.Colors.WHITE,
                        ),
                        ft.Container(
                            padding=ft.padding.only(top=3.0),
                            content=ft.Text(
                                value=nome,
                                color=ft.Colors.WHITE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ),
                        ft.Container(
                            padding=ft.padding.only(top=3.0),
                            content=ft.Text(
                                value=building,
                                color=ft.Colors.WHITE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ),
                    ],
                ),
            ),
            ft.Container(
                expand=True,
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(
                            padding=ft.padding.only(top=16.0, bottom=16.0),
                            content=ft.Column(
                                controls=[
                                    ft.Container(
                                        padding=ft.padding.only(left=24.0, right=24.0),
                                        content=ft.Divider(height=1.0),
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            ),
        ],
    )
    
    return drawer