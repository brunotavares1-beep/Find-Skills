#!/usr/bin/env python3
"""
Raio-x de uma base de incorridos estilo "Planilhao" de empreiteira.

Nao substitui a analise do controller: sinaliza candidatos a anomalia e
resume a estrutura da base para orientar a leitura. Sempre revise a saida
com juizo de negocio antes de repassar ao usuario.

Uso:
    python analisar_planilhao.py <arquivo.xlsx> [--sheet NOME] [--out relatorio.json]
"""
import argparse
import json
import re
import unicodedata
import sys
from collections import Counter, defaultdict
from datetime import datetime

try:
    import openpyxl
except ImportError:
    print("Instale openpyxl: pip install openpyxl --break-system-packages", file=sys.stderr)
    sys.exit(1)

CONTA_BANCARIA_RE = re.compile(r"^\d{4,6}-\d$")


def parse_data(valor):
    """Aceita datetime nativo ou string dd/mm/aaaa (comum em export de ERP)."""
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, str):
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(valor.strip(), fmt)
            except ValueError:
                continue
    return None


def eh_conta_bancaria(valor):
    if valor is None:
        return False
    return bool(CONTA_BANCARIA_RE.match(str(valor).strip()))


def carregar(path, sheet=None):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[sheet] if sheet else wb.worksheets[0]
    rows = ws.iter_rows(values_only=True)
    header = next(rows)
    header = [str(h).strip() if h is not None else f"col_{i}" for i, h in enumerate(header)]
    return header, rows


def _norm(t):
    t = unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode()
    return t.lower().strip()


def col_index(header, *candidatos):
    lower = [_norm(h) if h is not None else "" for h in header]
    # 1) match exato primeiro (evita "ano" casar com "plano de contas")
    for cand in candidatos:
        for i, h in enumerate(lower):
            if h == _norm(cand):
                return i
    # 2) match por palavra inteira dentro do texto do cabecalho
    for cand in candidatos:
        padrao = re.compile(r"\b" + re.escape(_norm(cand)) + r"\b")
        for i, h in enumerate(lower):
            if padrao.search(h):
                return i
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo")
    ap.add_argument("--sheet", default=None)
    ap.add_argument("--out", default=None, help="salvar relatorio em JSON")
    args = ap.parse_args()

    header, rows = carregar(args.arquivo, args.sheet)

    idx_unidade = col_index(header, "unidade de negocio", "unidade")
    idx_plano_pai = col_index(header, "plano de contas pai")
    idx_plano = col_index(header, "plano de contas")
    if idx_plano == idx_plano_pai:
        idx_plano = None
    idx_data = col_index(header, "data incorrido", "data")
    idx_id = col_index(header, "id lan", "id")
    idx_mes = col_index(header, "mes")
    idx_ano = col_index(header, "ano")
    idx_projeto = col_index(header, "projeto")
    idx_conta = col_index(header, "conta corrente", "conta")
    idx_desc = col_index(header, "descricao", "descri")
    idx_valor = col_index(header, "valor")

    unidades = Counter()
    contas = Counter()
    planos_pai = Counter()
    linha_completa = Counter()  # (id, unidade, valor, data) -> candidato a duplicidade REAL
    id_unidades = defaultdict(set)  # id -> unidades onde aparece (>1 unidade = rateio, nao duplicidade)
    valores_zero = 0
    linhas_sem_data = 0
    linhas_sem_valor = 0
    linhas_valor_texto = 0
    amostras_valor_texto = []
    total_banco = 0.0
    total_virtual = 0.0
    n_banco = 0
    n_virtual = 0
    datas = []
    valor_por_bu_mes = defaultdict(float)
    n = 0
    amostras_zero = []
    amostras_sem_data = []

    for r in rows:
        if r is None or all(c is None for c in r):
            continue
        n += 1

        def get(i):
            return r[i] if i is not None and i < len(r) else None

        unidade = get(idx_unidade)
        conta = get(idx_conta)
        plano_pai = get(idx_plano_pai)
        data = get(idx_data)
        valor = get(idx_valor)
        lanc_id = get(idx_id)
        mes = get(idx_mes)
        ano = get(idx_ano)

        if unidade is not None:
            unidades[unidade] += 1
        if plano_pai is not None:
            planos_pai[plano_pai] += 1
        if conta is not None:
            contas[str(conta)] += 1
            if eh_conta_bancaria(conta):
                n_banco += 1
                if isinstance(valor, (int, float)):
                    total_banco += valor
            else:
                n_virtual += 1
                if isinstance(valor, (int, float)):
                    total_virtual += valor

        data_parseada = parse_data(data)
        if data_parseada is None:
            linhas_sem_data += 1
            if len(amostras_sem_data) < 5:
                amostras_sem_data.append({"linha": n, "id": lanc_id, "valor_bruto": data})
        else:
            datas.append(data_parseada)

        if valor is None:
            linhas_sem_valor += 1
        elif isinstance(valor, str):
            linhas_valor_texto += 1
            if len(amostras_valor_texto) < 5:
                amostras_valor_texto.append({"linha": n, "id": lanc_id, "valor_bruto": valor})
        elif isinstance(valor, (int, float)) and valor == 0:
            valores_zero += 1
            if len(amostras_zero) < 5:
                amostras_zero.append({"linha": n, "id": lanc_id, "unidade": unidade})

        if lanc_id is not None:
            # Rateio legitimo repete o Id em Unidades diferentes (ver
            # references/estrutura-dados-empreiteira.md) -- por isso o Id sozinho NUNCA e usado
            # para marcar duplicidade. So a linha inteira repetida (mesmo Id, mesma Unidade, mesmo
            # Valor, mesma Data -- a mesma logica da formula CONT.SES em references/formulas-excel.md
            # secao 6) e candidata a duplicidade real.
            if unidade is not None:
                id_unidades[lanc_id].add(unidade)
            chave_linha = (lanc_id, unidade, valor, data_parseada if data_parseada else data)
            linha_completa[chave_linha] += 1

        if unidade is not None and mes is not None and ano is not None and isinstance(valor, (int, float)):
            valor_por_bu_mes[(unidade, ano, mes)] += valor

    duplicados_reais = {k: v for k, v in linha_completa.items() if v > 1}
    ids_rateio = {i: sorted(str(u) for u in us) for i, us in id_unidades.items() if len(us) > 1}

    def _chave_legivel(chave):
        lanc_id, unidade, valor, data = chave
        return f"id={lanc_id} | unidade={unidade} | valor={valor} | data={data}"

    periodo = None
    if datas:
        periodo = {
            "inicio": min(datas).strftime("%d/%m/%Y"),
            "fim": max(datas).strftime("%d/%m/%Y"),
        }

    relatorio = {
        "arquivo": args.arquivo,
        "total_linhas": n,
        "colunas_detectadas": {
            "unidade_de_negocio": header[idx_unidade] if idx_unidade is not None else None,
            "plano_de_contas_pai": header[idx_plano_pai] if idx_plano_pai is not None else None,
            "plano_de_contas": header[idx_plano] if idx_plano is not None else None,
            "data_incorrido": header[idx_data] if idx_data is not None else None,
            "id_lancamento": header[idx_id] if idx_id is not None else None,
            "conta_corrente": header[idx_conta] if idx_conta is not None else None,
            "valor": header[idx_valor] if idx_valor is not None else None,
        },
        "periodo_coberto": periodo,
        "unidades_de_negocio": dict(unidades.most_common()),
        "plano_de_contas_pai_top20": dict(planos_pai.most_common(20)),
        "split_banco_x_virtual": {
            "nota": "Conta com padrao NNNNN-N e tratada como conta bancaria real; o restante e "
                    "considerado conta gerencial/virtual. Confirme esse padrao com o usuario antes "
                    "de tratar como definitivo.",
            "linhas_banco": n_banco,
            "linhas_virtual": n_virtual,
            "soma_valor_banco": round(total_banco, 2),
            "soma_valor_virtual": round(total_virtual, 2),
        },
        "contas_correntes_mais_frequentes": dict(contas.most_common(15)),
        "anomalias_candidatas": {
            "linhas_sem_data": linhas_sem_data,
            "amostra_sem_data": amostras_sem_data,
            "linhas_sem_valor": linhas_sem_valor,
            "linhas_valor_texto": linhas_valor_texto,
            "amostra_valor_texto": amostras_valor_texto,
            "nota_valor_texto": "Valor gravado como texto fica FORA de todas as somas deste relatorio "
                                "-- converta na origem antes de fechar qualquer total.",
            "linhas_valor_zero": valores_zero,
            "amostra_valor_zero": amostras_zero,
            "nota_duplicidade": "Id repetido em Unidades diferentes e rateio normal, nao "
                                 "duplicidade -- so entra em 'ids_lancamento_duplicados_reais' quando "
                                 "Id, Unidade, Valor e Data se repetem juntos (linha inteira igual).",
            "ids_lancamento_duplicados_reais": len(duplicados_reais),
            "amostra_ids_duplicados_reais": [
                {"chave": _chave_legivel(k), "ocorrencias": v}
                for k, v in list(duplicados_reais.items())[:10]
            ],
            "ids_lancamento_rateados": len(ids_rateio),
            "amostra_ids_rateados": dict(list(ids_rateio.items())[:10]),
        },
    }

    print(json.dumps(relatorio, ensure_ascii=False, indent=2, default=str))

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(relatorio, f, ensure_ascii=False, indent=2, default=str)
        print(f"\nRelatorio salvo em {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
