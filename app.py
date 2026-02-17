# -*- coding: utf-8 -*-
"""
Created on Sun Feb  1 14:33:11 2026

@author: estev
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

from google_sheets import adicionar_movimentacao, carregar_dados

# -----------------------------
# Configuração da página
# -----------------------------
st.set_page_config(
    page_title="Joca Gasta-gasta",
    layout="centered"
)

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Constantes
# -----------------------------
CATEGORIAS = [
    "Comida-mercado",
    "Comida-feira",
    "Ifood",
    "Comer fora",
    "Aluguel",
    "Contas",
    "Babá",
    "Gasolina",
    "Carro-manutenção",
    "Compras",
    "Farmácia",
    "Salário",
    "Poupança",
    "Investimento",
    "Outros"
]

PESSOAS = ["Estêvão", "Luana"]
TIPOS = ["Saída", "Entrada"]

# -----------------------------
# Abas
# -----------------------------
#tab_add, tab_visao = st.tabs(["➕ Movimentação", "📊 Visão financeira"])
tab_visao, tab_add = st.tabs(["📊 Visão financeira", "➕ Movimentação"])

# =================================================
# ABA 1 — ADICIONAR MOVIMENTAÇÃO
# =================================================
with tab_add:
    st.subheader("Adicionar movimentação")

    valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
    #valor = valor.replace(".","").replace(",",".")  # ajustar para decimal com ponto, para conseguir trabalhar com float em Python
    data_mov = st.date_input("Data", value=date.today())
    tipo = st.selectbox("Tipo", TIPOS)
    categoria = st.selectbox("Categoria", CATEGORIAS)
    comentario = st.text_input("Comentário extra")
    quem = st.selectbox("Quem lançou", PESSOAS)

    if st.button("Adicionar"):
        mov = {
            "data": data_mov.strftime("%Y-%m-%d"),
            "valor": valor,
            "tipo": tipo,
            "categoria": categoria,
            "comentario": comentario,
            "quem": quem
        }

        adicionar_movimentacao(mov)
        st.success("Movimentação adicionada com sucesso!")

# =================================================
# ABA 2 — VISÃO FINANCEIRA
# =================================================
with tab_visao:
    st.subheader("Joca gasta-gasta (Resumo financeiro)")

    df = carregar_dados()

    if df.empty:
        st.info("Nenhuma movimentação registrada.")
    else:
        df["data"] = pd.to_datetime(df["data"])

        # Aplicar sinal
        df["valor_signed"] = df.apply(
            lambda r: r["valor"] if r["tipo"] == "Entrada" else -r["valor"],
            axis=1
        )

        # -----------------------------
        # Seletor de visualização
        # -----------------------------
        visao = st.radio(
            "Escolha a visualização",
            ["Saldo acumulado", "Fluxo diário", "Gastos por categoria", "Tabela"]
        )

        # =============================
        # FLUXO DIÁRIO
        # =============================
        if visao == "Fluxo diário":
            df_fluxo = (
                df.groupby("data", as_index=False)["valor_signed"]
                .sum()
                .sort_values("data")
            )

            fig = px.bar(
                df_fluxo,
                x="data",
                y="valor_signed",
                title="Fluxo financeiro diário"
            )

        # =============================
        # SALDO ACUMULADO
        # =============================
        elif visao == "Saldo acumulado":
            df_saldo = df.sort_values("data")
            df_saldo["saldo"] = df_saldo["valor_signed"].cumsum()

            fig = px.line(
                df_saldo,
                x="data",
                y="saldo",
                markers=True,
                title="Saldo acumulado ao longo do tempo"
            )

        # =============================
        # PIZZA POR CATEGORIA
        # =============================
        elif  visao == "Gastos por categoria":
            
            df_gastos = df[(df["tipo"] == "Saída") & (df["categoria"] != "Poupança")]


            fig = px.pie(
                df_gastos,
                values="valor",
                names="categoria",
                title="Distribuição de gastos por categoria"
            )

        # =============================
        # TABELA
        # =============================
        else:
            df_tabela = df[['categoria', 'valor','data']].copy()
            st.dataframe(df_tabela)
            

        

        # Estilo escuro
        fig.update_layout(
            plot_bgcolor="black",
            paper_bgcolor="black",
            font=dict(color="white")
        )

        st.plotly_chart(fig, use_container_width=True)













