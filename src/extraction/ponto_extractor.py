import pdfplumber
import pandas as pd
import re
import tempfile


# =============================
# FUNÇÕES AUXILIARES
# =============================

def limpa(valor):
    if valor:
        v = valor.replace("\n", " ").strip()
        return v if v not in ["", "-", "**"] else None
    return None


def limpa_horario(horario):
    if not horario:
        return None
    limpo = re.sub(r'[A-ZIOa-zioP\s]+', '', str(horario).strip())
    limpo = re.sub(r'\s+', '', limpo)
    return limpo if re.match(r'^\d{2}:\d{2}$', limpo) else None


def limpa_dia_extenso(texto):
    if not texto:
        return None
    dias_map = {
        'seg': 'Segunda-feira', 'ter': 'Terça-feira', 'qua': 'Quarta-feira',
        'qui': 'Quinta-feira', 'sex': 'Sexta-feira', 'sáb': 'Sábado',
        'sab': 'Sábado', 'dom': 'Domingo'
    }
    texto_limpo = re.sub(r'[^\w\s]', ' ', texto).lower().strip()
    for abrev, extenso in dias_map.items():
        if abrev in texto_limpo:
            return extenso
    return limpa(texto_limpo.title())


def limpa_matricula(texto):
    if not texto:
        return None
    match = re.search(r'-\s*(\d+)(?:\s|$)', texto)
    if match:
        return match.group(1)
    match = re.search(r'(\d{6,})', texto)
    return match.group(1) if match else None


def limpa_funcao_simples(texto):
    if not texto:
        return None
    match = re.search(r'Função:\s(.+?)(?=\s*C\.C\.|CPF|\d{8,})', texto, re.IGNORECASE | re.DOTALL)
    if match:
        funcao = match.group(1).strip()
        funcao = re.sub(r'\s*C\.C\.:.*$', '', funcao, flags=re.IGNORECASE).strip()
        return re.sub(r'\s+', ' ', funcao)
    return None


def extrair_situacao(texto):
    if not texto:
        return None
    padroes = [
        r'Sit\.\.\.:\s*([A-Z]+?)(?:\s*-|$)',
        r'Sit\.\.\.:\s*([A-Z]+?)\s*-\s*Período',
        r'Sit\.\.\.:\s*([A-Z\s]+?)(?=\sDep|Leg|$)'
    ]
    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            situacao = match.group(1).strip().upper()
            situacao = re.sub(r'PERÍODO.*', '', situacao)
            return situacao
    return None


def normaliza_coluna(col):
    return re.sub(r"\s+", " ", col).strip()


def extrair_regex(padrao, texto):
    m = re.search(padrao, texto, re.DOTALL)
    return m.group(1).strip() if m else None


def eh_cabecalho_correto(header):
    header_norm = [normaliza_coluna(h) for h in header]
    essenciais = ["Data", "Dia", "1a E.", "1a S.", "2a E.", "2a S."]
    return len(header_norm) >= 14 and all(any(ess in h for h in header_norm) for ess in essenciais)


# =============================
# EXTRAÇÃO PRINCIPAL
# =============================

def extrair_ponto_pdf(file, progress_bar=None, status_text=None):

    todos_registros = []
    cabecalho_final = None

    # cria arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.read())
        pdf_path = tmp.name

    with pdfplumber.open(pdf_path) as pdf:

        total_paginas = len(pdf.pages)

        for i, page in enumerate(pdf.pages):

            if progress_bar:
                progress_bar.progress((i + 1) / total_paginas)

            if status_text:
                status_text.markdown(
                    f"📄 Processando página {i + 1} de {total_paginas}"
                )

            texto = page.extract_text() or ""

            dados_funcionario = {
                "Nome": extrair_regex(r"Nome:\s(.+?)\sChapa", texto),
                "Matricula": limpa_matricula(extrair_regex(r"Matrícula:\s(.+?)(?:\sNome|$)", texto)),
                "Admissao": extrair_regex(r"Admissão:\s(\d{2}/\d{2}/\d{4})", texto),
                "Categoria": extrair_regex(r"Categoria:\s(.+?)(?=Sit|\sM\s)", texto),
                "Funcao": limpa_funcao_simples(texto),
                "Situacao": extrair_situacao(texto),
                "Departamento": extrair_regex(r"Departamento:\s(.+?)(?=Legenda|$)", texto),
            }

            table_settings = {
                "vertical_strategy": "lines",
                "horizontal_strategy": "lines",
                "intersection_tolerance": 5,
                "snap_tolerance": 3,
                "join_tolerance": 3,
                "edge_min_length": 3,
                "min_words_vertical": 3,
                "min_words_horizontal": 1,
            }

            tables = page.extract_tables(table_settings)

            for table in tables:

                if not table or len(table) < 2:
                    continue

                header_raw = table[0]
                header = [normaliza_coluna(h) for h in header_raw]

                if not eh_cabecalho_correto(header):
                    continue

                if cabecalho_final is None:
                    cabecalho_final = header

                for row in table[1:]:

                    if not row or len(row) == 0:
                        continue

                    if not re.match(r"\d{2}/\d{2}/\d{4}", str(row[0])):
                        continue

                    row = row + [None] * (len(cabecalho_final) - len(row))
                    row = row[:len(cabecalho_final)]

                    row_limpa = []

                    for i, valor in enumerate(row):

                        col_name = cabecalho_final[i]

                        if i == 1 and "Dia" in col_name:
                            row_limpa.append(limpa_dia_extenso(valor))
                        elif i == 0:
                            row_limpa.append(limpa(valor))
                        elif re.search(r'\d{2}:\d{2}', str(valor)):
                            row_limpa.append(limpa_horario(valor))
                        else:
                            row_limpa.append(limpa(valor))

                    row_dict = {cabecalho_final[i]: row_limpa[i] for i in range(len(cabecalho_final))}
                    registro = {**dados_funcionario, **row_dict}

                    todos_registros.append(registro)

    if not todos_registros:
        return pd.DataFrame()

    colunas_fixas = ["Nome", "Matricula", "Admissao", "Categoria", "Funcao", "Departamento", "Situacao"]

    df = pd.DataFrame(todos_registros)

    if cabecalho_final:
        df = df[colunas_fixas + cabecalho_final]

    return df