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
                    ft.Text(name, color=ft.Colors.WHITE)
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