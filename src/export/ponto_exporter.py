import pandas as pd
from io import BytesIO


def exportar_ponto_excel(df_final, df_resumo):

    if df_final is None or df_resumo is None:
        return None

    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_final.to_excel(writer, sheet_name="Espelho_Ponto", index=False)
        df_resumo.to_excel(writer, sheet_name="Resumo", index=False)

    buffer.seek(0)

    return buffer