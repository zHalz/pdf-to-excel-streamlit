import pandas as pd


def criar_base_totvs(analise_plano):

    linhas = []

    for _, row in analise_plano.iterrows():

        nome = row["nome"]
        mat = row["matricula"]

        med_tit = row["Assistência Médica Titular"]
        odo_tit = row["Assistência Odontológica Titular"]

        med_dep_total = row["Assistência Médica Dependente"]
        odo_dep_total = row["Assistência Odontológica Dependente"]

        cop = row["Coparticipação"]

        qtd_dep_med = 0
        qtd_dep_odo = 0

        if med_tit > 0 and med_dep_total > 0:
            qtd_dep_med = int(round(med_dep_total / med_tit))

        if odo_tit > 0 and odo_dep_total > 0:
            qtd_dep_odo = int(round(odo_dep_total / odo_tit))

        qtd_dependentes = max(qtd_dep_med, qtd_dep_odo)

        # TITULAR
        total_linha_titular = med_tit + odo_tit + cop

        linhas.append({
            "nome": nome,
            "matricula": mat,
            "tipo_registro": "TITULAR",
            "dependente_id": 0,
            "vlr_medico": med_tit,
            "vlr_odonto": odo_tit,
            "vlr_copart": cop,
            "total": round(total_linha_titular, 2)
        })

        # DEPENDENTES
        for i in range(qtd_dependentes):

            vlr_med = med_dep_total / qtd_dep_med if i < qtd_dep_med and qtd_dep_med > 0 else 0
            vlr_odo = odo_dep_total / qtd_dep_odo if i < qtd_dep_odo and qtd_dep_odo > 0 else 0

            total_linha_dep = vlr_med + vlr_odo

            linhas.append({
                "nome": nome,
                "matricula": mat,
                "tipo_registro": "DEPENDENTE",
                "dependente_id": i + 1,
                "vlr_medico": round(vlr_med, 2),
                "vlr_odonto": round(vlr_odo, 2),
                "vlr_copart": 0,
                "total": round(total_linha_dep, 2)
            })

    return pd.DataFrame(linhas)