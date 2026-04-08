import pandas as pd
import re
from datetime import datetime
import holidays


# =============================
# FUNÇÕES DE REGRA
# =============================

br_feriados = holidays.Brazil()


def tem_marcacao_entrada_row(row_dict):
    cols_entrada = ["1a E.", "2a E.", "3a E.", "4a E."]
    for col in cols_entrada:
        if col in row_dict:
            horario = row_dict[col]
            if horario and re.match(r'^\d{2}:\d{2}$', str(horario)):
                return True
    return False


def contar_ausencias(row_dict):
    """Regra: conta apenas '** Ausente **' na 1a E."""
    col_1aE = None
    col_observacao = None

    for col, valor in row_dict.items():
        if "1a e." in col.lower():
            col_1aE = valor
        if "observa" in col.lower():
            col_observacao = valor

    if col_1aE and "** Ausente **" in str(col_1aE):
        if col_observacao and "SERVICO EXTERNO" in str(col_observacao).upper():
            return 0
        return 1

    return 0


def eh_final_de_semana(data_str):
    try:
        data = datetime.strptime(data_str, '%d/%m/%Y')
        return data.weekday() >= 5
    except:
        return False


def eh_feriado(data_str):
    try:
        data = datetime.strptime(data_str, '%d/%m/%Y').date()
        return data in br_feriados
    except:
        return False


# =============================
# PROCESSAMENTO PRINCIPAL
# =============================

def processar_ponto(df):

    if df.empty:
        return None, None

    # Identifica coluna de data automaticamente
    cabecalho = df.columns.tolist()
    data_col = next((col for col in cabecalho if "data" in col.lower()), None)

    colunas_fixas = ["Nome", "Matricula", "Admissao", "Categoria", "Funcao", "Departamento", "Situacao"]

    df_final = df.copy()

    # =============================
    # RESUMO
    # =============================

    resumo = []

    for (matricula, nome, funcao), grupo in df_final.groupby(['Matricula', 'Nome', 'Funcao']):

        linhas_com_entrada = grupo[
            grupo.apply(lambda row: tem_marcacao_entrada_row(row.to_dict()), axis=1)
        ]

        finais_semana = sum(
            1 for _, row in linhas_com_entrada.iterrows()
            if data_col and eh_final_de_semana(str(row[data_col]))
        )

        feriados_trab = sum(
            1 for _, row in linhas_com_entrada.iterrows()
            if data_col and eh_feriado(str(row[data_col]))
        )

        ausencias = sum(
            contar_ausencias(row.to_dict())
            for _, row in grupo.iterrows()
        )

        resumo.append({
            'Matricula': matricula,
            'Nome': nome,
            'Funcao': funcao,
            'Situacao': grupo['Situacao'].iloc[0] if len(grupo) > 0 else None,
            '🗓️ Finais de Semana': finais_semana,
            '🎉 Feriados': feriados_trab,
            '🚫 Ausências': ausencias,

            # totais ajustados
            '📊 TOTAL (Finais de Semana + Feriados)': finais_semana + feriados_trab,
            '📊 TOTAL (Finais de Semana - Ausências)': finais_semana - ausencias
        })

    df_resumo = pd.DataFrame(resumo)

    return df_final, df_resumo