import streamlit as st

# IMPORT DAS TELAS
from src.apps.folha_analitica import executar_folha_analitica
from src.apps.espelho_ponto import executar_espelho_ponto

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(
    page_title="Plataforma de Conversões",
    layout="wide"
)

# -------------------------------
# SIDEBAR (MENU)
# -------------------------------
st.sidebar.title("⚙️ Ferramentas")

opcao = st.sidebar.selectbox(
    "Escolha a funcionalidade",
    [
        "📄 Folha Analítica",
        "🕒 Espelho de Ponto"
    ]
)

st.sidebar.divider()
st.sidebar.caption("by Raul 😏")

# -------------------------------
# ROTEAMENTO
# -------------------------------
if opcao == "📄 Folha Analítica":
    executar_folha_analitica()

elif opcao == "🕒 Espelho de Ponto":
    executar_espelho_ponto()