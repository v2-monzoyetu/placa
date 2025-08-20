import flet as ft
from login_page import login
from home_page import home

def main(page: ft.Page):
    page.theme_mode        = 'dark' 
    page.title             = 'MonzoYetu'
    page.window.width      = 1100
    page.window.height     = 700
    page.window.min_width  = 1100
    page.window.min_height = 700
    page.window.bgcolor    = "#141314"
    page.padding           = 0
    
    page.theme         = ft.Theme(
        text_theme     = ft.TextTheme(
            body_medium= ft.TextStyle(color=ft.Colors.WHITE),
            title_large= ft.TextStyle(color=ft.Colors.WHITE),
        ),
    )
    
    # Funções para alternar entre login e home
    def go_home():
        home(page, go_login)

    def go_login():
        login(page, go_home)
    
    # Verifica se o usuário já está logado
    if page.client_storage.get("token"):
        go_home()
    else:
        go_login()
                

ft.app(target=main, assets_dir="assets")