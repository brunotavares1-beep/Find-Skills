#!/usr/bin/env python3
"""
Funcoes comuns aos scripts do controller-empreiteira (AW Empreiteira).

Centraliza as regras que precisam ser IGUAIS em todos os scripts: normalizacao de nome de
unidade, extracao do codigo de projeto, deteccao de cabecalho/colunas por rotulo e
classificacao banco x conta virtual. Mudou uma regra de negocio? Mude aqui, nao em cada
script. Fonte das regras: references/mapa-aw.md e references/relatorios-aw.md.
"""
import re
import unicodedata
from datetime import datetime, date

# ---------------------------------------------------------------- unidades de negocio

UNIDADES_ATIVAS = [
    "AW Civil SP", "AW Civil RJ", "AW Hidráulica SP", "AW Hidráulica RJ", "AW DRYWALL SP",
    "AW PINTURA SP", "AW PINTURA RJ", "AW Canteiro de Obra SP", "AW Canteiro de Obra RJ",
    "AW Portaria SP", "AW ACABAMENTOS", "AW SEGURANÇA", "AW Empreiteira +",
]
UNIDADES_DESATIVADAS = ["AW DRYWALL RJ", "AW Topografia SP"]
UNIDADES_CONTROLE_A_PARTE = ["AW Elétrica", "AW Canteiro Produtos"]

SITUACAO_ATIVA = "ativa"
SITUACAO_DESATIVADA = "desativada"
SITUACAO_A_PARTE = "controle à parte"
SITUACAO_FORA = "fora do cadastro"


def norm(texto):
    """Sem acento, minusculo, sem espacos nas pontas. Para comparar rotulos."""
    if texto is None:
        return ""
    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", t).strip().lower()


def chave_unidade(nome):
    """Chave de comparacao de unidade: sem acento, sem caixa, hifen = espaco, espacos
    colapsados, sem ' DESATIVADA'. 'AW SEGURANÇA' == 'AW - Segurança' == 'aw seguranca'."""
    t = norm(nome).replace("-", " ").replace("–", " ")
    t = re.sub(r"\bdesativad[ao]\b", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    if not t.startswith("aw "):
        t = "aw " + t if t else t
    return t


_MAPA_UNIDADES = {}
for _n in UNIDADES_ATIVAS:
    _MAPA_UNIDADES[chave_unidade(_n)] = (_n, SITUACAO_ATIVA)
for _n in UNIDADES_DESATIVADAS:
    _MAPA_UNIDADES[chave_unidade(_n)] = (_n, SITUACAO_DESATIVADA)
for _n in UNIDADES_CONTROLE_A_PARTE:
    _MAPA_UNIDADES[chave_unidade(_n)] = (_n, SITUACAO_A_PARTE)


def classificar_unidade(nome):
    """Retorna (nome_canonico, situacao). Unidade nao reconhecida volta com o texto original e
    situacao 'fora do cadastro' -- nunca e descartada."""
    if nome is None or not str(nome).strip():
        return ("SEM UNIDADE", SITUACAO_FORA)
    k = chave_unidade(nome)
    if k in _MAPA_UNIDADES:
        return _MAPA_UNIDADES[k]
    # 'AW Empreiteira +' vs 'AW Empreiteira+' / 'AW Empreiteira Mais'
    k2 = k.replace(" +", "+").replace(" mais", "+")
    for chave, v in _MAPA_UNIDADES.items():
        if chave.replace(" +", "+") == k2:
            return v
    return (str(nome).strip(), SITUACAO_FORA)


# ---------------------------------------------------------------- projeto

CODIGO_RE = re.compile(r"^\s*(\d{3,4}/\d{2}(?:-\d{2})?)\b")
SUFIXO_RE = re.compile(r"\s*\(([A-Za-z0-9]{2,10})\)\s*$")


def parse_projeto(texto):
    """'5102/25 - Confidencial 210 Obr - AW ACABAMENTOS (LEV)' ->
    {'codigo': '5102/25', 'unidade_texto': 'AW ACABAMENTOS', 'status': 'LEV', 'nome': ...}.
    Codigo com '-NN' e preservado (nao unir 4662/24 com 4662/24-00 sem confirmacao)."""
    if texto is None:
        return None
    t = re.sub(r"\s+", " ", str(texto)).strip()
    if not t:
        return None
    m = CODIGO_RE.match(t)
    codigo = m.group(1) if m else None
    status = None
    ms = SUFIXO_RE.search(t)
    if ms:
        status = ms.group(1).upper()
        t_sem = t[:ms.start()].rstrip()
    else:
        t_sem = t
    unidade = None
    pos = t_sem.upper().rfind(" - AW ")
    if pos >= 0:
        unidade = t_sem[pos + 3:].strip()
        miolo = t_sem[:pos]
    else:
        miolo = t_sem
    nome = miolo
    if codigo and nome.startswith(codigo):
        nome = nome[len(codigo):].lstrip(" -")
    return {"codigo": codigo, "unidade_texto": unidade, "status": status, "nome": nome.strip(),
            "descritivo": t}


# ---------------------------------------------------------------- banco x virtual

CONTA_BANCARIA_RE = re.compile(r"^\d{4,6}-[\dXx]$")


def eh_conta_bancaria(valor):
    if valor is None:
        return False
    return bool(CONTA_BANCARIA_RE.match(str(valor).strip()))


# ---------------------------------------------------------------- datas e numeros

def parse_data(valor):
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, date):
        return datetime(valor.year, valor.month, valor.day)
    if isinstance(valor, str):
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S",
                    "%d/%m/%Y %H:%M"):
            try:
                return datetime.strptime(valor.strip(), fmt)
            except ValueError:
                continue
    return None


def parse_numero(valor):
    """Aceita numero nativo ou texto BR ('1.234,56', 'R$ -1.234,56'). Retorna (float|None, era_texto)."""
    if isinstance(valor, bool):
        return None, False
    if isinstance(valor, (int, float)):
        return float(valor), False
    if isinstance(valor, str):
        t = valor.strip().replace("R$", "").replace(" ", "")
        if not t:
            return None, False
        neg = t.startswith("(") and t.endswith(")")
        t = t.strip("()")
        if "," in t:
            t = t.replace(".", "").replace(",", ".")
        try:
            v = float(t)
            return (-v if neg else v), True
        except ValueError:
            return None, True
    return None, False


def fmt_brl(v):
    if v is None:
        return "n/d"
    s = f"{abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-R$ " if v < 0 else "R$ ") + s


# ---------------------------------------------------------------- planilhas

def achar_aba(wb, *palavras, excluir=()):
    """Primeira aba cujo nome normalizado contem alguma das palavras."""
    for ws in wb.worksheets:
        n = norm(ws.title)
        if any(norm(e) in n for e in excluir):
            continue
        if any(norm(p) in n for p in palavras):
            return ws
    return None


def ler_tabela(ws, max_busca=15):
    """Localiza a linha de cabecalho (a com mais celulas de texto nas primeiras linhas) e devolve
    (header, linhas, n_linha_cabecalho). Linhas totalmente vazias sao descartadas."""
    linhas = list(ws.iter_rows(values_only=True))
    melhor, idx = -1, 0
    for i, r in enumerate(linhas[:max_busca]):
        if not r:
            continue
        n_txt = sum(1 for c in r if isinstance(c, str) and c.strip())
        if n_txt > melhor:
            melhor, idx = n_txt, i
    if not linhas:
        return [], [], 0
    header = [str(h).strip() if h is not None else f"col_{j}" for j, h in enumerate(linhas[idx])]
    corpo = [r for r in linhas[idx + 1:] if r and any(c is not None and str(c).strip() for c in r)]
    return header, corpo, idx + 1


def col_index(header, *candidatos, evitar=()):
    """Match exato primeiro, depois por palavra inteira. 'evitar' descarta cabecalhos que
    contenham esses termos (ex.: procurar 'valor' sem pegar 'valor recebido')."""
    lower = [norm(h) for h in header]
    ev = [norm(e) for e in evitar]

    def ok(h):
        return not any(e in h for e in ev)

    for cand in candidatos:
        c = norm(cand)
        for i, h in enumerate(lower):
            if h == c and ok(h):
                return i
    for cand in candidatos:
        padrao = re.compile(r"\b" + re.escape(norm(cand)) + r"\b")
        for i, h in enumerate(lower):
            if padrao.search(h) and ok(h):
                return i
    return None


def letra_para_indice(letra):
    n = 0
    for ch in letra.upper():
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def get(r, i):
    return r[i] if i is not None and i < len(r) else None
