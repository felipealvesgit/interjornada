import streamlit as st
import pandas as pd
from datetime import datetime

st.title("📂 Processamento de Interjornada em Lote")

# Upload do arquivo
uploaded_file = st.file_uploader("Suba sua planilha de ponto (Excel ou CSV)", type=["xlsx", "csv"])

if uploaded_file:
    # Lógica para ler diferentes formatos
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Garantir que as colunas de data sejam objetos datetime
    try:
        df['Fim_Jornada_1'] = pd.to_datetime(df['Fim_Jornada_1'])
        df['Inicio_Jornada_2'] = pd.to_datetime(df['Inicio_Jornada_2'])

        # Cálculo da diferença em horas
        df['Horas_Descanso'] = (df['Inicio_Jornada_2'] - df['Fim_Jornada_1']).dt.total_seconds() / 3600

        # Identificar irregularidades
        df['Status'] = df['Horas_Descanso'].apply(lambda x: "✅ OK" if x >= 11 else "⚠️ IRREGULAR")
        df['Horas_Faltantes'] = df['Horas_Descanso'].apply(lambda x: max(0, 11 - x))

        # Mostrar resumo
        st.subheader("Resumo do Processamento")
        total_irregularidades = len(df[df['Status'] == "⚠️ IRREGULAR"])
        st.warning(f"Foram encontradas {total_irregularidades} infrações na planilha.")

        # Exibir a tabela formatada
        st.dataframe(df.style.applymap(
            lambda x: 'background-color: #ffcccc' if x == "⚠️ IRREGULAR" else '',
            subset=['Status']
        ))

        # --- DASHBOARD GERENCIAL ---
        st.divider()
        st.header("📊 Painel de Auditoria")

        if not df.empty:
            col_dash1, col_dash2 = st.columns(2)

            # 1. Ranking de quem mais teve infrações
            with col_dash1:
                st.subheader("Top Infrações por Funcionário")
                ranking = df[df['Status'] == "⚠️ IRREGULAR"]['Funcionario'].value_counts()
                if not ranking.empty:
                    st.bar_chart(ranking)
                else:
                    st.success("Nenhuma infração detectada!")

            # 2. Impacto Financeiro (Simulação rápida)
            with col_dash2:
                st.subheader("Custo Estimado de Multas")
                # Supondo valor médio de hora extra de R$ 25,00 para o cálculo rápido
                custo_total = df['Horas_Faltantes'].sum() * 25.0

                st.metric("Total de Horas Devidas", f"{df['Horas_Faltantes'].sum():.2f}h")
                st.metric("Passivo Estimado (R$)", f"R$ {custo_total:,.2f}", delta="Risco Trabalhista",
                          delta_color="inverse")

        # 3. Filtro Dinâmico
        st.subheader("🔍 Filtrar por Funcionário")
        nome_filtro = st.selectbox("Selecione um nome para ver o histórico isolado:",
                                   ["Todos"] + list(df['Funcionario'].unique()))

        if nome_filtro != "Todos":
            df_filtrado = df[df['Funcionario'] == nome_filtro]
            st.table(df_filtrado[['Fim_Jornada_1', 'Inicio_Jornada_2', 'Horas_Descanso', 'Status']])

        # Botão para baixar o resultado
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Baixar Relatório de Erros", csv, "relatorio_interjornada.csv", "text/csv")

    except Exception as e:
        st.error(f"Erro ao processar colunas. Verifique se os nomes estão corretos. Detalhe: {e}")