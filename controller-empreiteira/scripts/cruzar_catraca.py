#!/usr/bin/env python3
"""
Cruza catraca (presenca fisica) x folha/alocacao por obra. Layout da catraca e PREMISSA a
confirmar com o usuario: colunas de pessoa (matricula/CPF/nome), data e obra/local.

Aponta:
  - pessoa na folha da obra SEM registro de catraca no periodo  -> alocacao errada / pago sem presenca
  - pessoa na catraca SEM folha                                  -> terceiro nao identificado (risco
                                                                    trabalhista, custo nao capturado)
  - homem-dia por obra e, se a folha tiver valor, custo de MO por homem-dia.
CPF e mascarado na saida (LGPD).

Uso:
    python cruzar_catraca.py catraca.xlsx folha.xlsx [--sheet-catraca X] [--sheet-folha Y] [--json saida.json]
"""
import argparse
import json
import re
import sys
from collections import defaultdict

try:
    import openpyxl
except ImportError:
    print("Instale openpyxl: pip install openpyxl --break-system-packages", file=sys.stderr)
    sys.exit(1)

from aw_comum import col_index, fmt_brl, get, ler_tabela, norm, parse_data, parse_numero, parse_projeto


def chave_pessoa(header, r, idx):
    for k in ("matricula", "cpf", "nome"):
        i = idx.get(k)
        if i is not None and get(r, i) not in (None, ""):
            v = str(get(r, i)).strip()
            return (k, re.sub(r"\D", "", v) if k in ("matricula", "cpf") else norm(v))
    return None


def mascarar(k):
    tipo, v = k
    if tipo == "cpf" and len(v) == 11:
        return f"***.{v[3:6]}.{v[6:9]}-**"
    return f"{tipo}:{v}"


def obra_de(v):
    p = parse_projeto(v)
    return p["codigo"] if p and p["codigo"] else (norm(v) or "(sem obra)")


def indices(header):
    return {"matricula": col_index(header, "matricula", "chapa", "registro"),
            "cpf": col_index(header, "cpf"),
            "nome": col_index(header, "nome", "funcionario", "colaborador"),
            "obra": col_index(header, "obra", "projeto", "local", "centro de custo", "lotacao"),
            "data": col_index(header, "data", "data acesso", "dia"),
            "valor": col_index(header, "valor", "salario", "custo", "total")}


def abrir(path, sheet):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    return ler_tabela(wb[sheet] if sheet else wb.worksheets[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("catraca")
    ap.add_argument("folha")
    ap.add_argument("--sheet-catraca")
    ap.add_argument("--sheet-folha")
    ap.add_argument("--json")
    a = ap.parse_args()

    hc, cc, _ = abrir(a.catraca, a.sheet_catraca)
    hf, cf, _ = abrir(a.folha, a.sheet_folha)
    ic, jf = indices(hc), indices(hf)
    if ic["obra"] is None or ic["data"] is None or not any(ic[k] is not None for k in ("matricula", "cpf", "nome")):
        sys.exit(f"Catraca: não achei pessoa/data/obra no cabeçalho {hc}. Confirme o layout.")
    if jf["obra"] is None or not any(jf[k] is not None for k in ("matricula", "cpf", "nome")):
        sys.exit(f"Folha: não achei pessoa/obra no cabeçalho {hf}. Confirme o layout.")

    dias = defaultdict(set)  # (pessoa, obra) -> datas
    for r in cc:
        p, d = chave_pessoa(hc, r, ic), parse_data(get(r, ic["data"]))
        if p and d:
            dias[(p, obra_de(get(r, ic["obra"])))].add(d.date())
    folha = defaultdict(float)
    for r in cf:
        p = chave_pessoa(hf, r, jf)
        if p:
            v, _ = parse_numero(get(r, jf["valor"])) if jf["valor"] is not None else (0.0, False)
            folha[(p, obra_de(get(r, jf["obra"])))] += abs(v or 0.0)

    pessoas_cat = {p for p, _ in dias}
    pessoas_fol = {p for p, _ in folha}
    sem_catraca = [{"pessoa": mascarar(p), "obra": o, "valor_folha": round(v, 2)}
                   for (p, o), v in folha.items() if (p, o) not in dias]
    sem_folha = [{"pessoa": mascarar(p), "obra": o, "dias": len(ds)}
                 for (p, o), ds in dias.items() if p not in pessoas_fol]
    obra_divergente = [{"pessoa": mascarar(p), "obra_catraca": o, "obras_folha": sorted(ob for (pp, ob) in folha if pp == p)}
                       for (p, o) in dias if p in pessoas_fol and (p, o) not in folha]
    por_obra = defaultdict(lambda: {"homem_dia": 0, "pessoas": set(), "custo_folha": 0.0})
    for (p, o), ds in dias.items():
        por_obra[o]["homem_dia"] += len(ds)
        por_obra[o]["pessoas"].add(p)
    for (p, o), v in folha.items():
        por_obra[o]["custo_folha"] += v
    resumo = {o: {"homem_dia": d["homem_dia"], "pessoas_catraca": len(d["pessoas"]),
                  "custo_folha": round(d["custo_folha"], 2),
                  "custo_por_homem_dia": round(d["custo_folha"] / d["homem_dia"], 2) if d["homem_dia"] else None}
              for o, d in por_obra.items()}
    out = {"premissa": "layout da catraca e critério de presença (≥1 passagem no dia) a confirmar",
           "pessoas_catraca": len(pessoas_cat), "pessoas_folha": len(pessoas_fol),
           "na_folha_sem_catraca": sem_catraca, "na_catraca_sem_folha": sem_folha,
           "obra_catraca_diferente_da_folha": obra_divergente, "por_obra": resumo}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"\nFolha sem catraca: {len(sem_catraca)} ({fmt_brl(sum(x['valor_folha'] for x in sem_catraca))}) · "
          f"catraca sem folha: {len(sem_folha)} · obra divergente: {len(obra_divergente)}", file=sys.stderr)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
