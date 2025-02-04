import streamlit as st
import pandas as pd
import plotly.express as px
import pyodbc
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
DB_SERVER = os.getenv("DB_SERVER")
DB_DATABASE = os.getenv("DB_NAME")  # Ajustado para corresponder ao .env
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Verificar se as variáveis de ambiente foram carregadas corretamente
if not all([DB_SERVER, DB_DATABASE, DB_USER, DB_PASSWORD]):
    st.error("Erro: Variáveis de ambiente do banco de dados não carregadas corretamente. Verifique o arquivo .env.")
    st.stop()

# Configuração da página
st.set_page_config(page_title="Análises de Pedidos", layout="wide")

# Conectar ao banco de dados
def get_data():
    try:
        conn = pyodbc.connect(
            f'DRIVER={{SQL Server}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USER};PWD={DB_PASSWORD or ""}'
        )
        query = "SELECT * FROM pedidos"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return pd.DataFrame()

df = get_data()

if df.empty:
    st.warning("Nenhum dado encontrado na tabela de pedidos.")
    st.stop()

# Exibir nomes das colunas para debug
st.write("Colunas disponíveis:", df.columns.tolist())

# Normalizar nomes das colunas
df.columns = df.columns.str.strip().str.lower()

df = df.rename(columns={
    "pedido": "pedido",
    "item do pedido": "item_do_pedido",
    "cod sap": "codigo_sap",
    "cnpj": "cnpj",
    "razão social": "razao_social",
    "canal": "canal",
    "centro": "centro",
    "valor": "valor",
    "referência": "referencia",
    "status": "status"
})

# Verificar se a coluna 'Código SAP' existe e renomear automaticamente
if "codigo_sap" not in df.columns:
    for col in df.columns:
        if "sap" in col.lower():  # Identificar coluna semelhante
            df.rename(columns={col: "codigo_sap"}, inplace=True)
            st.success(f"Coluna '{col}' renomeada para 'codigo_sap'.")
            break

# Exibir primeiras linhas para verificar os dados
st.write("Prévia dos dados:", df.head())

# Indicadores principais
st.title("📊 Análises de Pedidos e Faturamento")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Faturamento Total", f"R$ {df['valor'].sum():,.2f}")
with col2:
    st.metric("Total de Pedidos", df['pedido'].nunique())
with col3:
    st.metric("Ticket Médio", f"R$ {df['valor'].mean():,.2f}")

# Gráfico de faturamento por canal
st.subheader("💰 Faturamento por Canal")
faturamento_canal = df.groupby("canal")["valor"].sum().reset_index()
fig1 = px.bar(faturamento_canal, x="canal", y="valor", text_auto=True, title="Faturamento por Canal")
st.plotly_chart(fig1, use_container_width=True)

# Gráfico de faturamento por centro
st.subheader("📍 Faturamento por Centro")
faturamento_centro = df.groupby("centro")["valor"].sum().reset_index()
fig2 = px.bar(faturamento_centro, x="centro", y="valor", text_auto=True, title="Faturamento por Centro")
st.plotly_chart(fig2, use_container_width=True)

# Top 10 produtos mais vendidos
st.subheader("🔥 Produtos mais vendidos")
if "codigo_sap" in df.columns:
    produtos_mais_vendidos = df.groupby("codigo_sap")["valor"].sum().reset_index().sort_values(by="valor", ascending=False).head(10)
    fig3 = px.bar(produtos_mais_vendidos, x="codigo_sap", y="valor", text_auto=True, title="Top 10 Produtos Mais Vendidos")
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("Coluna 'Código SAP' não encontrada na base de dados.")

# Top 10 clientes
st.subheader("🏅 Top 10 Clientes por Receita")
top_clientes = df.groupby(["razao_social", "cnpj"])["valor"].sum().reset_index().sort_values(by="valor", ascending=False).head(10)
fig4 = px.bar(top_clientes, x="razao_social", y="valor", text_auto=True, title="Top 10 Clientes por Receita")
st.plotly_chart(fig4, use_container_width=True)

# Distribuição por Referência
st.subheader("📌 Pedidos por Referência")
if "referencia" in df.columns:
    referencia_counts = df["referencia"].value_counts().reset_index()
    referencia_counts.columns = ["referencia", "count"]  # Ajustando nome das colunas
    fig5 = px.pie(referencia_counts, names="referencia", values="count", title="Distribuição de Pedidos por Referência")
    st.plotly_chart(fig5, use_container_width=True)
else:
    st.warning("Coluna 'Referência' não encontrada na base de dados.")

# Status dos Pedidos
st.subheader("📋 Status dos Pedidos")
if "status" in df.columns and df["status"].notnull().sum() > 0:
    status_counts = df["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]  # Ajustando nome das colunas
    st.write("Prévia dos dados de status:", status_counts.head())  # Debug
    fig6 = px.bar(status_counts, x="status", y="count", text_auto=True, title="Status dos Pedidos")
    st.plotly_chart(fig6, use_container_width=True)
else:
    st.write("Sem informações de status disponíveis.")

# Conclusão
st.markdown("---")
st.markdown("Criado com 💡 por Streamlit 🚀")
