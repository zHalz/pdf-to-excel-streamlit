from src.extraction.ponto_extractor import extrair_ponto_pdf
from src.processing.ponto_processor import processar_ponto
from src.export.ponto_exporter import exportar_ponto_excel


def processar_ponto_arquivo(file):

    df = extrair_ponto_pdf(file)

    if df.empty:
        return None, None

    df_final, df_resumo = processar_ponto(df)

    excel = exportar_ponto_excel(df_final, df_resumo)

    resumo = {
        "registros": len(df_final),
        "colaboradores": df_final["Matricula"].nunique()
    }

    return excel, resumo