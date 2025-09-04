import sqlite3
import requests
import flet as ft
from api_client import API_URL

def connection():
    try:
        conn = sqlite3.connect("dbmonzoyetu.db")
        print("Conexão ao SQLite bem-sucedida")
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao SQLite: {e}")
        return None

def dbemployee(page: ft.Page):
    conn = None
    try:
        conn = connection()
        if not conn:
            raise Exception("Falha ao conectar ao banco de dados")
        
        token = page.client_storage.get("token")
        headers = {"Authorization": f"Bearer {token}"}
        route = f"{API_URL}/v1/concierge/db/qrcode/employee/{page.client_storage.get('condominio_id')}"
        res = requests.get(route, headers=headers, timeout=15)
        
        if res.status_code != 200:
            raise Exception(f"Erro na API: status {res.status_code}")
        
        data = res.json()
        result = data.get("result", {})
        if not (result.get("success") and result.get("success") == True):
            raise Exception("Resposta da API não foi bem-sucedida")
        
        item = result.get("data", [])
        if not isinstance(item, list):
            raise Exception("Dados da API não são uma lista")
        
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS funcionarios (
                id TEXT NOT NULL,
                foto TEXT,
                nome TEXT,
                cargo TEXT,
                telefone TEXT,
                status TEXT,
                motivo TEXT,
                morador TEXT,
                telefone_morador TEXT,
                situation TEXT,
                lote TEXT,
                quadra TEXT,
                categoria TEXT,
                sub_categoria TEXT,
                referencia_categoria TEXT,
                referencia_sub_categoria TEXT,
                cartao TEXT,
                rfid TEXT,
                PRIMARY KEY (id)
            )
        """)
        
        for funcionario in item:
            cursor.execute("""
                INSERT OR REPLACE INTO funcionarios (
                    id, foto, nome, cargo, telefone, status, motivo, morador, 
                    telefone_morador, situation, lote, quadra, categoria, 
                    sub_categoria, referencia_categoria, referencia_sub_categoria, cartao, rfid
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(funcionario.get("id", "0")),
                funcionario.get("foto"),
                funcionario.get("nome"),
                funcionario.get("cargo"),
                funcionario.get("telefone"),
                funcionario.get("status"),
                funcionario.get("motivo"),
                funcionario.get("morador"),
                funcionario.get("telefone_morador"),
                funcionario.get("situation"),
                funcionario.get("lote"),
                funcionario.get("quadra"),
                funcionario.get("categoria"),
                funcionario.get("sub_categoria"),
                funcionario.get("referencia_categoria"),
                funcionario.get("referencia_sub_categoria"),
                funcionario.get("cartao"),
                funcionario.get("rfid")
            ))
        
        conn.commit()
        print(f"{len(item)} funcionários inseridos/atualizados no SQLite")
        return len(item)  # Retorna o número de registros processados
    
    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {e}")
        raise e
    finally:
        if conn:
            conn.close()
            print("Conexão ao SQLite fechada")

def dbresident(page: ft.Page):
    conn = None
    try:
        conn = connection()
        if not conn:
            raise Exception("Falha ao conectar ao banco de dados")
        
        token = page.client_storage.get("token")
        headers = {"Authorization": f"Bearer {token}"}
        route = f"{API_URL}/v1/concierge/db/qrcode/resident/{page.client_storage.get('condominio_id')}"
        res = requests.get(route, headers=headers, timeout=15)
        
        if res.status_code != 200:
            raise Exception(f"Erro na API: status {res.status_code}")
        
        data = res.json()
        result = data.get("result", {})
        if not (result.get("success") and result.get("success") == True):
            raise Exception("Resposta da API não foi bem-sucedida")
        
        item = result.get("data", [])
        if not isinstance(item, list):
            raise Exception("Dados da API não são uma lista")
        
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS moradores (
                id TEXT NOT NULL,
                nome TEXT NOT NULL,
                email TEXT,
                foto TEXT,
                telefone TEXT,
                status TEXT,
                morador TEXT,
                telefone_morador TEXT,
                situation TEXT,
                lote TEXT,
                quadra TEXT,
                categoria TEXT,
                sub_categoria TEXT,
                referencia_categoria TEXT,
                referencia_sub_categoria TEXT,
                rfid TEXT,
                PRIMARY KEY (id)
            )
        """)
        
        for morador in item:
            cursor.execute("""
                INSERT OR REPLACE INTO moradores (
                    id, nome, email, foto, telefone, status, morador, 
                    telefone_morador, situation, lote, quadra, categoria, 
                    sub_categoria, referencia_categoria, referencia_sub_categoria, rfid
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(morador.get("id", "0")),
                morador.get("nome", ""),
                morador.get("email"),
                morador.get("foto"),
                morador.get("telefone"),
                morador.get("status"),
                morador.get("morador"),
                morador.get("telefone_morador"),
                morador.get("situation"),
                morador.get("lote"),
                morador.get("quadra"),
                morador.get("categoria"),
                morador.get("sub_categoria"),
                morador.get("referencia_categoria"),
                morador.get("referencia_sub_categoria"),
                morador.get("rfid")
            ))
        
        conn.commit()
        print(f"{len(item)} moradores inseridos/atualizados no SQLite")
        return len(item)  # Retorna o número de registros processados
    
    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {e}")
        raise e
    finally:
        if conn:
            conn.close()
            print("Conexão ao SQLite fechada")

def fetch_employee(qrdata):
    conn = connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM funcionarios WHERE cartao = ? OR rfid = ? OR id = ?",
                (qrdata.get("code"), qrdata.get("code"), qrdata.get("id"))
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    "id": row[0],
                    "foto": row[1],
                    "nome": row[2],
                    "cargo": row[3],
                    "telefone": row[4],
                    "status": row[5],
                    "motivo": row[6],
                    "morador": row[7],
                    "telefone_morador": row[8],
                    "situation": row[9],
                    "lote": row[10],
                    "quadra": row[11],
                    "categoria": row[12],
                    "sub_categoria": row[13],
                    "referencia_categoria": row[14],
                    "referencia_sub_categoria": row[15],
                    "cartao": row[16],
                    "rfid": row[17]
                }
            return None
        except Exception as e:
            print(f"Erro ao consultar SQLite: {e}")
            conn.close()
            raise e
    return None

def fetch_resident(qrdata):
    conn = connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM moradores WHERE rfid = ? OR id = ?",
                (qrdata.get("code"), qrdata.get("id"))
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    "id": row[0],
                    "nome": row[1],
                    "email": row[2],
                    "foto": row[3],
                    "telefone": row[4],
                    "status": row[5],
                    "morador": row[6],
                    "telefone_morador": row[7],
                    "situation": row[8],
                    "lote": row[9],
                    "quadra": row[10],
                    "categoria": row[11],
                    "sub_categoria": row[12],
                    "referencia_categoria": row[13],
                    "referencia_sub_categoria": row[14],
                    "rfid": row[15]
                }
            return None
        except Exception as e:
            print(f"Erro ao consultar SQLite: {e}")
            conn.close()
            raise e
    return None

# Função para limpar o banco de dados
def clear_database():
    conn = connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Limpar tabelas funcionarios e moradores
            cursor.execute("DELETE FROM funcionarios")
            cursor.execute("DELETE FROM moradores")
            conn.commit()
            print("Banco de dados limpo com sucesso: tabelas funcionarios e moradores")
        except Exception as e:
            print(f"Erro ao limpar o banco de dados: {e}")
        finally:
            conn.close()
            print("Conexão ao SQLite fechada")