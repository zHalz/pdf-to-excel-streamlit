import streamlit as st
from pipeline import processar_arquivo

def executar_folha_analitica():

    # -------------------------------
    # HEADER
    # -------------------------------
    st.title("📄 Folha Analítica")
    st.caption("Envie seus PDFs que eu resolvo tudo pra você 😉")

    # -------------------------------
    # SESSION STATE
    # -------------------------------
    if "historico" not in st.session_state:
        st.session_state.historico = []

    if "arquivos_processados" not in st.session_state:
        st.session_state.arquivos_processados = {}

    # -------------------------------
    # LAYOUT
    # -------------------------------
    col_process, col_hist = st.columns([2, 1], gap="medium")

    # -------------------------------
    # PROCESSAMENTO
    # -------------------------------
    with col_process:

        st.subheader("💌 Processamento dos PDFs")

        uploaded_files = st.file_uploader(
            "📥 Arraste ou selecione seus arquivos PDF",
            type=["pdf"],
            accept_multiple_files=True,
            key="folha_upload"
        )

        if uploaded_files:

            for file in uploaded_files:

                col1, col2, col3 = st.columns([4, 1, 1])

                # -------------------------------
                # ARQUIVO JÁ PROCESSADO
                # -------------------------------
                if file.name in st.session_state.arquivos_processados:

                    col1.markdown(f"✅ {file.name}")

                    col2.button(
                        "Processado",
                        disabled=True,
                        key=f"processed_{file.name}"
                    )

                    col3.download_button(
                        "Baixar",
                        st.session_state.arquivos_processados[file.name]["file"],
                        file_name=file.name.replace(".pdf", ".xlsx"),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"download_{file.name}"
                    )

                    resumo = st.session_state.arquivos_processados[file.name]["resumo"]

                    st.caption(
                        f"📊 Registros: {resumo['registros']:,} · "
                        f"👥 Colaboradores: {resumo['colaboradores']:,}"
                    )

                # -------------------------------
                # NOVO ARQUIVO
                # -------------------------------
                else:

                    col1.markdown(f"📎 {file.name}")

                    if col2.button("Processar", key=f"process_{file.name}"):

                        with st.spinner("🔄 Processando arquivo... isso pode levar alguns segundos"):

                            try:
                                excel, resumo = processar_arquivo(file)

                                if excel is None:
                                    st.error("⚠️ Não foi possível extrair dados desse PDF.")
                                else:

                                    # salva na sessão
                                    st.session_state.arquivos_processados[file.name] = {
                                        "file": excel,
                                        "resumo": resumo
                                    }

                                    # adiciona histórico
                                    st.session_state.historico.append({
                                        "arquivo": file.name,
                                        "registros": resumo["registros"],
                                        "colaboradores": resumo["colaboradores"]
                                    })

                                    st.rerun()

                            except Exception as e:
                                st.error(f"Erro: {str(e)}")

    # -------------------------------
    # HISTÓRICO
    # -------------------------------
    with col_hist:

        st.subheader("📋 Histórico de Processamentos")

        if st.session_state.historico:

            df_hist = st.session_state.historico[::-1]  # mais recente primeiro

            st.dataframe(
                df_hist,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.caption("Ainda não há processamentos.")