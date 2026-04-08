from src.extraction.pdf_extractor import extract_pdf_data
from src.processing.planilhas import gerar_planilhas
from src.processing.totvs import criar_base_totvs
from src.export.excel_exporter import exportar_para_excel_completo


def processar_arquivo(file, progress_bar=None, status_text=None):

    # 🔄 ETAPA 1 — EXTRAÇÃO
    if status_text:
        status_text.markdown("📄 Extraindo dados do PDF...")

    df = extract_pdf_data(
        file,
        progress_bar=progress_bar,
        status_text=status_text
    )

    if df.empty:
        return None, None

    # 🔄 ETAPA 2 — PROCESSAMENTO
    if status_text:
        status_text.markdown("📊 Gerando planilhas...")

    _, pivot, analise = gerar_planilhas(df)

    # 🔄 ETAPA 3 — BASE TOTVS
    if status_text:
        status_text.markdown("🧩 Montando base TOTVS...")

    df_totvs = criar_base_totvs(analise)

    # 🔄 ETAPA 4 — EXPORTAÇÃO
    if status_text:
        status_text.markdown("📁 Gerando arquivo Excel...")

    excel = exportar_para_excel_completo(df, pivot, analise, df_totvs)

    resumo = {
        "registros": len(df),
        "colaboradores": df["matricula"].nunique()
    }

    return excel, resumo