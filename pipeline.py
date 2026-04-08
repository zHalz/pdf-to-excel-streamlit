from src.extraction.pdf_extractor import extract_pdf_data
from src.processing.planilhas import gerar_planilhas
from src.processing.totvs import criar_base_totvs
from src.export.excel_exporter import exportar_para_excel_completo


def processar_arquivo(file):

    df = extract_pdf_data(file)

    if df.empty:
        return None, None

    _, pivot, analise = gerar_planilhas(df)
    df_totvs = criar_base_totvs(analise)

    excel = exportar_para_excel_completo(df, pivot, analise, df_totvs)

    resumo = {
        "registros": len(df),
        "colaboradores": df["matricula"].nunique()
    }

    return excel, resumo