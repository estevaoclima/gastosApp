# -*- coding: utf-8 -*-
"""
Created on Sun Feb  1 14:32:07 2026

@author: estev
"""
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

SPREADSHEET_ID = "1o06Ef6zUhm2LaLd5FII-CgGpoBkPkUL8cb0XDlhA1eg" # pedaco do site do nome

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def conectar_planilha():
    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    return sheet

def adicionar_movimentacao(mov):
    sheet = conectar_planilha()
    sheet.append_row([
        mov["data"],
        mov["valor"],
        mov["tipo"],
        mov["categoria"],
        mov["comentario"],
        mov["quem"]
    ])

def carregar_dados():
    sheet = conectar_planilha()
    dados = sheet.get_all_records()
    return pd.DataFrame(dados)

