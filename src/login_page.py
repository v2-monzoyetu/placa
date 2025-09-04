import flet as ft
import requests
from api_client import API_URL
from widget import button

def login(page: ft.Page, go_home):
    """Tela de Login"""

    snack_bar = ft.SnackBar(content=ft.Text("", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.GREY)
    page.snack_bar = snack_bar
    
    # Variável de estado
    is_loading = False
    
    def update_loading():
        """Atualiza o botão para exibir o loading ou o texto"""
        login_button.content.content = (
            ft.Text("Carregando...", color=ft.Colors.WHITE) if is_loading else ft.Text("Login", color=ft.Colors.WHITE)
        )
        phone_field.disabled  = is_loading
        pass_field.disabled   = is_loading
        login_button.disabled = is_loading
        page.update()  
    
    def show_snack_bar(message, bgcolor=ft.Colors.GREY):
        """Exibe o SnackBar com a mensagem desejada"""
        snack_bar.content.value = message
        snack_bar.bgcolor = bgcolor
        snack_bar.open = True
        page.update()
    
    def login_attempt(e):
        nonlocal is_loading
        telefone = phone_field.value
        password = pass_field.value

        if not telefone:
            show_snack_bar("Insira o seu contacto telefônico!", ft.Colors.RED)
            phone_field.focus()
            return

        elif not password:
            show_snack_bar("Insira uma senha válida!", ft.Colors.RED)
            pass_field.focus()
            return
        
        # Ativa o loading
        is_loading = True
        update_loading()

        # Parâmetros da requisição
        params = {"telefone": telefone, "password": password}

        try:
            response = requests.post(API_URL+'/concierge/auth/login', params=params)
            data = response.json()

            if response.status_code == 200 and "access_token" in data:
                req  = requests.post(API_URL+'/concierge/auth/me', headers={"Authorization": f"Bearer {data['access_token']}"})
                user = req.json()
                
                if req.status_code == 200:
                    page.client_storage.set("user", user)
                    page.client_storage.set("token", data["access_token"])
                    page.update()
                    go_home()
                else:
                    show_snack_bar("Não foi possível obter os dados do usuário!", ft.Colors.RED)
            else:
                show_snack_bar("Login falhou! Verifique as credenciais.", ft.Colors.ORANGE)
        
        except requests.RequestException:
            show_snack_bar("Erro de conexão com o servidor!", ft.Colors.RED)
            
        # Desativa o loading
        is_loading = False
        update_loading()

    # Campos de login
    phone_field  = ft.TextField(label="Telefone", autofocus=True)
    pass_field = ft.TextField(
        label="Senha",
        password=True,
    )
    
    login_button = button("Login", on_click=login_attempt)
    
    container = ft.Container(
        content=ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    margin=8.0,
                    padding=8.0,
                    width=412.0,
                    content=ft.Column(
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=16.0,
                        controls=[
                                ft.Text("MonzoYetu Portaria", 
                                    size=20, 
                                    weight=ft.FontWeight.BOLD,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Card(
                                    content=ft.Container(
                                    alignment=ft.alignment.center,
                                    margin=12.0,
                                    content=ft.Column(
                                        spacing=16.0,
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Text("Seja Bem-Vindo", size=16, weight=ft.FontWeight.BOLD),
                                            phone_field,
                                            pass_field,
                                            login_button,
                                        ]
                                    )
                                )
                            )
                        ]
                    )
                ),
            ]
        ),
        alignment=ft.alignment.center,
        expand=True,
    )

    # Layout da tela de login
    page.clean()
    page.add(container)
    page.on_keyboard_event = lambda e: login_attempt(e) if e.key == "Enter" and not is_loading else None
    page.add(snack_bar)
    page.update()