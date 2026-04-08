import pdfplumber
import pandas as pd
import re
import tempfile


def extract_pdf_data(file):
    """
    Extrai dados de um PDF completo e retorna um DataFrame consolidado
    """

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.read())
        pdf_path = tmp.name

    todos_dados = []

    with pdfplumber.open(pdf_path) as pdf:
        total_paginas = len(pdf.pages)

        for page_num, page in enumerate(pdf.pages):

            texto = (
                page.extract_text()
                or page.extract_text(layout=True)
                or page.extract_text(x_tolerance=3)
            )

            if not texto:
                continue

            linhas = texto.split("\n")

            nome_atual = None
            matricula_atual = None

            for linha_num, linha in enumerate(linhas):

                linha = linha.strip()
                linha = re.sub(r"\s{2,}", " ", linha)

                # MATRÍCULA
                mat_match = re.search(r"MAT\.?\s*:?\s*(\d{5,7})", linha)
                if mat_match:
                    matricula_atual = mat_match.group(1)

                # NOME
                nome_match = re.search(
                    r"NOME\s*:?\s*([A-ZÀ-Ú\s]+?)(?:FUNCAO|FUNC|DT|$)",
                    linha
                )
                if nome_match:
                    nome_atual = nome_match.group(1).strip()

                # EVENTOS
                if "|" in linha and re.search(r"\d{3}", linha):

                    partes = linha.split("|")

                    nome_final = nome_atual or "SEM_NOME"
                    matricula_final = matricula_atual or "SEM_MAT"

                    for idx, parte in enumerate(partes):

                        parte = parte.strip()
                        if not parte:
                            continue

                        evento_match = re.match(
                            r"(\d{3})\s+(.+?)\s+([\d,]+)?\s+([\d.,]+)",
                            parte
                        )

                        if evento_match:

                            codigo, desc, ref, valor = evento_match.groups()

                            tipo = "PROVENTO" if idx == 0 else "DESCONTO"

                            valor = valor.replace(".", "").replace(",", ".")

                            try:
                                valor = float(valor)
                            except:
                                continue

                            todos_dados.append({
                                "pagina": page_num + 1,
                                "linha_original": linha_num + 1,
                                "nome": nome_final,
                                "matricula": matricula_final,
                                "tipo": tipo,
                                "codigo": codigo,
                                "descricao": desc.strip(),
                                "referencia": ref,
                                "valor": valor
                            })

    if not todos_dados:
        return pd.DataFrame()

    df = pd.DataFrame(todos_dados)

    # LIMPEZA FINAL
    df["nome"] = (
        df["nome"]
        .str.replace(r"[:\s]+$", "", regex=True)
        .str.strip()
    )

    return df