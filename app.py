import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sistema Interjornada", page_icon="⚖️", layout="wide")

# --- MENU LATERAL ---
st.sidebar.title("📌 Menu")
menu = st.sidebar.selectbox(
    "Escolha uma funcionalidade:",
    ["Calculadora Individual", "Processamento em Lote (Excel)", "Dashboard de Gestão"]
)

# Variáveis globais de configuração no rodapé da sidebar
st.sidebar.divider()
st.sidebar.subheader("⚙️ Configurações Financeiras")
salario_mensal = st.sidebar.number_input("Salário Mensal (R$)", min_value=0.0, value=2500.0)
jornada_mensal = st.sidebar.selectbox("Jornada Mensal", [220, 200, 180, 44], index=0)
adicional_extra = st.sidebar.slider("Adicional Hora Extra (%)", 50, 200, 50)

valor_hora_base = salario_mensal / jornada_mensal
valor_hora_extra = valor_hora_base * (1 + adicional_extra / 100)

# --- LÓGICA DAS PÁGINAS ---

if menu == "Calculadora Individual":
    st.header("🧮 Calculo Interjonada")
    st.info("Use esta opção para consultas rápidas de um único intervalo.")

    col1, col2 = st.columns(2)
    with col1:
        d1 = st.date_input("Fim da Jornada 1", value=datetime.now() - timedelta(days=1))
        h1 = st.time_input("Hora de Término", value=datetime.strptime("22:00", "%H:%M").time())
    with col2:
        d2 = st.date_input("Início da Jornada 2", value=datetime.now())
        h2 = st.time_input("Hora de Início", value=datetime.strptime("07:00", "%H:%M").time())

    dt_fim = datetime.combine(d1, h1)
    dt_inicio = datetime.combine(d2, h2)

    if st.button("Analisar Intervalo"):
        diff = (dt_inicio - dt_fim).total_seconds() / 3600
        if diff >= 11:
            st.success(f"✅ Intervalo de {diff:.2f}h respeitado.")
        else:
            faltante = 11 - diff
            valor_devido = faltante * valor_hora_extra
            st.error(f"⚠️ Interjornada desrespeitada! Faltam {faltante:.2f}h.")
            st.metric("Indenização Estimada", f"R$ {valor_devido:.2f}")

elif menu == "Processamento em Lote (Excel)":
    st.header("📂 Processamento de Planilhas")
    st.markdown("Suba um arquivo com as colunas: `Funcionario`, `Fim_Jornada_1`, `Inicio_Jornada_2`")

    uploaded_file = st.file_uploader("Selecione o arquivo", type=["xlsx", "csv"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)

        # Lógica de cálculo
        df['Fim_Jornada_1'] = pd.to_datetime(df['Fim_Jornada_1'])
        df['Inicio_Jornada_2'] = pd.to_datetime(df['Inicio_Jornada_2'])
        df['Descanso'] = (df['Inicio_Jornada_2'] - df['Fim_Jornada_1']).dt.total_seconds() / 3600
        df['Horas_Devidas'] = df['Descanso'].apply(lambda x: max(0, 11 - x))
        df['Valor_Indenizar'] = df['Horas_Devidas'] * valor_hora_extra

        st.dataframe(df.style.highlight_max(axis=0, subset=['Horas_Devidas'], color='#ffcccc'))
        st.session_state['df_processado'] = df  # Salva para o Dashboard

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Relatório", csv, "resultado.csv", "text/csv")

elif menu == "Dashboard de Gestão":
    st.header("📊 Dashboard de Dados")

    if 'df_processado' in st.session_state:
        df = st.session_state['df_processado']

        # Métricas
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Infrações", len(df[df['Horas_Devidas'] > 0]))
        c2.metric("Total a Pagar (R$)", f"R$ {df['Valor_Indenizar'].sum():.2f}")
        c3.metric("Média de Descanso", f"{df['Descanso'].mean():.1f}h")

        # Gráfico
        st.subheader("Ocorrências por Funcionário")
        ranking = df[df['Horas_Devidas'] > 0]['Funcionario'].value_counts()
        st.bar_chart(ranking)
    else:
        st.warning("⚠️ Primeiro, processe uma planilha na aba 'Processamento em Lote' para visualizar o dashboard.")