# -*- coding: utf-8 -*-
"""
Created on Sun Feb  1 14:32:07 2026

@author: estev
"""
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

import streamlit as st
import gspread

##SPREADSHEET_ID = "1o06Ef6zUhm2LaLd5FII-CgGpoBkPkUL8cb0XDlhA1eg" # pedaco do site do nome

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]



#def conectar_planilha():
#    creds = Credentials.from_service_account_file(
#        "credentials.json",
#        scopes=SCOPES
#    )
#    client = gspread.authorize(creds)
#    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
#    return sheet
def conectar_planilha(): # new version to work online using streamlite cloude system. The previous would work fine, but locally
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    client = gspread.authorize(creds)
    sheet = client.open_by_key(st.secrets["spreadsheet_id"]).sheet1
    return sheet

def adicionar_movimentacao(mov):
    sheet = conectar_planilha()

    # converter/salvar como ponto para decimal (se entrada for com virgula para decimal), para conseguir trabalhar em Python como float
    ##valor_br = f"{mov['valor']:.2f}".replace(".",",")
    
    sheet.append_row([
        mov["data"],
        float(mov["valor"])#valor_br,  # nao puxar valor original, converter antes para decimal em ponto
        mov["tipo"],
        mov["categoria"],
        mov["comentario"],
        mov["quem"]
    ])

def carregar_dados():
    sheet = conectar_planilha()
    dados = sheet.get_all_records()
    #return pd.DataFrame(dados)
    df = pd.DataFrame(dados)
    #df["valor"] = df["valor"].apply(br_to_float)  # apply conversao de decimal de virgula para ponto para conseguir trabalhar com float no python
    return df


def br_to_float(valor):
    if valor is None or valor == "":
        return None

    # se já for número (caso correto do sheets)
    if isinstance(valor, (int, float)):
        return float(valor)

    # se vier como string
    valor = str(valor).strip()

    # formato brasileiro
    valor = valor.replace(".", "").replace(",", ".")

    try:
        return float(valor)
    except:
        return None





    






