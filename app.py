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
            [ "Semana", "Saldo acumulado", "Gastos por categoria", "Tabela", "Fluxo diário"]
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
        # GASTOS NA SEMANA
        # =============================
        elif visao == "Semana":
            
            ## para calculo e plot do grafico
            df_semana = df.copy()


            # SOmente Saidas (gastos) e desconsiderar poupançca
            df_semana = df_semana[(df_semana["tipo"] == "Saída") & (df_semana["categoria"] != "Poupança")]

            # fiiltra pelo userInput
            cat_option = sorted(df_semana["categoria"].unique())
            selection = st.pills("Filtrar categorias", cat_option, selection_mode="multi")

            # apply only if something is selected
            if selection:
                df_semana = df_semana[df_semana['categoria'].isin(selection)]

            # erro: e se nenhum dado nesta categoria
            if df_semana.empty():
                st.warning("Nenhum gasto deste tipo foi encontrado")
            else:
                # Passar para valore spositivos para melhor grafico
                df_semana['valor'] = df_semana['valor_signed']*(-1)
                
                df_semana['data'] = pd.to_datetime(df_semana['data'])
                
                # cria ordenacao numerica para os dias da semana
                df_semana['diaSemana'] = df_semana['data'].dt.day_name()  # name of the weekday (eg, monday)
                df_semana['dia_idx'] = df_semana['data'].dt.weekday  # index of the weekday (eg, 0, 1)
                
                # get mean
                df_media = df_semana.groupby(['dia_idx', 'diaSemana'])['valor'].mean().reset_index()
                df_media = df_media.sort_values('dia_idx')

                #cria ordem
                diasOrdem = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

                fig = px.strip(
                    df_semana, 
                    x="diaSemana", 
                    y="valor", 
                    color_discrete_sequence=["#FF4B4B"], # Streamlit Red
                    category_orders = {"diaSemana":diasOrdem},
                    title="Distribuição e Média de Gastos por Dia"

                )
            # 3. Add the Mean Line (Blue)
                import plotly.graph_objects as go
                fig.add_trace(
                    go.Scatter(
                        x=df_media["diaSemana"],
                        y=df_media["valor"],
                        mode='lines+markers',
                        name='Média',
                        line=dict(color='#1F77B4', width=3),
                        marker=dict(size=10, symbol='diamond')
                    )
                )

            # Improve layout
            #fig.update_layout(showlegend=True, xaxis_title="Dia da Semana", yaxis_title="Valor (R$)")
            #st.plotly_chart(fig)


            #fig = px.line(
            #    df_media,
            #    x="diaSemana",
            #    y="valor_signed",
            #    markers=True,
            #    title="Gastos por dia da semana"
            #)


        
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
        elif visao == "Tabela":
            
            df_tabela = df[['data','categoria', 'valor', "tipo"]].copy()
            df_tabela['data'] = pd.to_datetime(df_tabela['data']).dt.date
            st.dataframe(df_tabela)
            

        # Estilo escuro
    if visao != "Tabela":
        fig.update_layout(
              plot_bgcolor="black",
              paper_bgcolor="black",
              font=dict(color="white")
          )
        st.plotly_chart(fig, use_container_width=True)



















