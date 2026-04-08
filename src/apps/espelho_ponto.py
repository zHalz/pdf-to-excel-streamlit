import streamlit as st
from pipeline_ponto import processar_ponto_arquivo


def executar_espelho_ponto():

    # -------------------------------
    # HEADER
    # -------------------------------
    st.title("🕒 Espelho de Ponto")
    st.caption("Envie o PDF do ponto que eu analiso e gero o resumo pra você 😉")

    # -------------------------------
    # SESSION STATE
    # -------------------------------
    if "historico_ponto" not in st.session_state:
        st.session_state.historico_ponto = []

    if "arquivos_processados_ponto" not in st.session_state:
        st.session_state.arquivos_processados_ponto = {}

    # -------------------------------
    # LAYOUT
    # -------------------------------
    col_process, col_hist = st.columns([2, 1], gap="medium")

    # -------------------------------
    # PROCESSAMENTO
    # -------------------------------
    with col_process:

        st.subheader("📥 Processamento dos PDFs de Ponto")

        uploaded_files = st.file_uploader(
            "Arraste seus PDFs aqui",
            type=["pdf"],
            accept_multiple_files=True,
            key="ponto_upload"
        )

        if uploaded_files:

            for file in uploaded_files:

                col1, col2, col3 = st.columns([4, 1, 1])

                # -------------------------------
                # JÁ PROCESSADO
                # -------------------------------
                if file.name in st.session_state.arquivos_processados_ponto:

                    col1.markdown(f"✅ {file.name}")

                    col2.button(
                        "Processado",
                        disabled=True,
                        key=f"processed_ponto_{file.name}"
                    )

                    col3.download_button(
                        "Baixar",
                        st.session_state.arquivos_processados_ponto[file.name]["file"],
                        file_name=file.name.replace(".pdf", "_ponto.xlsx"),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"download_ponto_{file.name}"
                    )

                    resumo = st.session_state.arquivos_processados_ponto[file.name]["resumo"]

                    st.caption(
                        f"📊 Registros: {resumo['registros']:,} · "
                        f"👥 Colaboradores: {resumo['colaboradores']:,}"
                    )

                # -------------------------------
                # NOVO ARQUIVO
                # -------------------------------
                else:

                    col1.markdown(f"📎 {file.name}")

                    if col2.button("Processar", key=f"process_ponto_{file.name}"):

                        with st.spinner("🔄 Processando ponto..."):

                            try:
                                excel, resumo = processar_ponto_arquivo(file)

                                if excel is None:
                                    st.error("⚠️ Não foi possível extrair dados desse PDF.")
                                else:

                                    st.success("✅ Processamento concluído!")

                                    # salva na sessão
                                    st.session_state.arquivos_processados_ponto[file.name] = {
                                        "file": excel,
                                        "resumo": resumo
                                    }

                                    # histórico
                                    st.session_state.historico_ponto.append({
                                        "arquivo": file.name,
                                        "registros": resumo["registros"],
                                        "colaboradores": resumo["colaboradores"]
                                    })

                                    st.rerun()

                            except Exception as e:
                                st.error(f"❌ Erro ao processar: {str(e)}")

    # -------------------------------
    # HISTÓRICO
    # -------------------------------
    with col_hist:

        st.subheader("📋 Histórico")

        if st.session_state.historico_ponto:

            df_hist = st.session_state.historico_ponto[::-1]

            st.dataframe(
                df_hist,
                use_container_width=True
            )

        else:
            st.caption("Ainda não há processamentos.")