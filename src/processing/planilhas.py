import pandas as pd


def gerar_planilhas(df_consolidado):

    pivot_completa = df_consolidado.pivot_table(
        values="valor",
        index=["nome", "matricula", "tipo"],
        columns="codigo",
        aggfunc="sum",
        fill_value=0
    ).round(2).reset_index()

    mapa_codigos = {
        "455": "Assistência Médica Titular",
        "454": "Assistência Odontológica Titular",
        "458": "Coparticipação",
        "456": "Assistência Médica Dependente",
        "461": "Assistência Odontológica Dependente",
        "694": "Assistência Odontológica R (694)",
        "696": "Assistência Odontológica D (696)"
    }

    codigos = list(mapa_codigos.keys())

    for col in codigos:
        if col not in pivot_completa.columns:
            pivot_completa[col] = 0

    analise_plano = pivot_completa[
        ["nome", "matricula"] + codigos
    ].copy().rename(columns=mapa_codigos)

    analise_plano = analise_plano.groupby(
        ["nome", "matricula"]
    ).sum().reset_index()

    analise_plano["Total Titular"] = (
        analise_plano["Assistência Médica Titular"] +
        analise_plano["Assistência Odontológica Titular"] +
        analise_plano["Coparticipação"]
    )

    analise_plano["Total Dependente"] = (
        analise_plano["Assistência Médica Dependente"] +
        analise_plano["Assistência Odontológica Dependente"]
    )

    return df_consolidado, pivot_completa, analise_plano