# Projeção de resultado — obra, unidade e consolidado

Divisão de responsabilidades: **esta skill projeta resultado (competência) e entrega os insumos de
caixa**; a `superpowers` projeta o **caixa** (curva de recebimento, pagamentos, Reforma Tributária).

## Ponto de partida

Realizado conciliado, nunca orçado: DRE semanal mais recente (data de corte confirmada) + Cockpit/
Planilhão do mesmo corte, já passados pelas amarrações 2, 3 e 5 de `conciliacoes.md`.

## Por obra/projeto

| Linha | Fórmula | Fonte | Rótulo típico |
|---|---|---|---|
| Receita contratada | Vendido | DRE (manual) | CONFIRMADO |
| Aditivos aprovados | Σ aditivos assinados | contrato | CONFIRMADO |
| Pleitos em negociação | — | engenharia/comercial | só cenário otimista |
| **Receita final (RF)** | Vendido + aditivos aprovados | | |
| Custo incorrido (CI) | Cockpit ou Planilhão (negativo) | | CONFIRMADO |
| Custo a incorrer (CAI) | reestimativa da engenharia | Projetado (DRE) / engenharia | PREMISSA |
| **Custo final estimado (EAC)** | CI + CAI | | |
| **Resultado projetado** | RF + EAC | | |
| **Margem projetada** | (RF + EAC) / RF | | |
| Avanço físico-financeiro (POC) | CI / EAC | | |
| Receita reconhecível | POC × RF | | |
| Executado não faturado | Receita reconhecível − Faturado | | > 0: giro preso; < 0: faturamento antecipado |
| A receber | Faturado − Recebido − Retenções | Faturamento | |
| A faturar | RF − Faturado | | |

Regras:
- **CAI = Orçado − Incorrido é otimista**: pressupõe que não haverá mais desvio. Use a reestimativa da
  engenharia (coluna Projetado do DRE, quando existir); sem ela, rotule `PREMISSA — CAI linear do
  orçado` e mostre o cenário conservador com a eficiência de custo real até hoje (exige avanço
  físico medido; sem ele, `PENDÊNCIA`):
  `Valor agregado (VA) = Orçado total × % avanço físico` ·
  `IDC = VA / |CI|` ·
  `CAI conservador = (Orçado total − VA) / IDC`. IDC < 1 = obra gastando mais que o orçado para o
  mesmo avanço.
- **EAC > RF = obra deficitária**: achado crítico; a perda projetada inteira é reconhecida agora, não
  diluída no restante da obra.
- **Margem projetada < margem vendida** em mais de 2 p.p. → ponte: preço, produtividade (efetivo da
  catraca x previsto), material, mobilização, aditivo não formalizado.
- Obra encerrada (sufixo/cadastro): CAI = 0; resíduo de custo pós-encerramento é achado.

## Por unidade de negócio

Resultado projetado da unidade = Σ resultado das obras da unidade + estrutura/rateio projetado da
unidade (uma vez, na unidade) + obras novas **só se contratadas** (pipeline = cenário).

## Consolidado AW

Σ 13 unidades ativas + corporativo não rateado. Desativadas e controle à parte em linhas separadas.
Conferir: Σ unidades = consolidado calculado (diferença = rateio duplicado ou faltando).

## Cenários

| Cenário | Receita | Custo a incorrer | Recebimento (insumo para `superpowers`) |
|---|---|---|---|
| Conservador | Vendido + aprovados; glosa histórica aplicada | produtividade real até hoje | PMR real + 30 dias no maior cliente |
| Base | Vendido + aprovados | reestimativa da engenharia | PMR real por cliente |
| Otimista | + pleitos com alta chance | orçado | prazo contratual |

## Insumos que esta skill entrega para a projeção de caixa

1. Saldo de caixa real conciliado na data-base (só contas bancárias).
2. CR por projeto/cliente, **líquido de retenções**, com aging e PMR real.
3. A faturar por obra e cronograma de medição (se houver; sem cronograma = `PENDÊNCIA`).
4. Custo a incorrer por obra e natureza (MO, material, mobilização, subempreitada).
5. Posição de caixa virtual por unidade (quem financia quem) — informativa, fora do caixa real.
6. Lista de pendências e premissas rotuladas.

## Tabela de premissas (obrigatória na entrega)

| Premissa | Valor | Fonte | Data | Sensibilidade (efeito de ±10%) |
|---|---|---|---|---|
