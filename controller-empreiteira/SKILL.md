---
name: "controller-empreiteira"
description: "Controller financeiro da AW Empreiteira (e de construção civil em geral): lê e cruza os relatórios já conhecidos — Planilhão de incorridos, Quadro Estratégico, Faturamento, Projetos, CockpitRelatorioEmpreiteira, DRE semanal, contas a receber/pagar, extrato bancário e catraca — para achar diferenças, conciliar, explicar variação e projetar resultado por projeto, unidade de negócio e consolidado. Domina faturado x recebido x a receber, custos incorridos, margem real e projetada, caixa real (banco) x caixa virtual (contas gerenciais), aging, capital de giro, fechamento mensal e teste de base do ERP (TOTVS RM) em Excel PT-BR, Power Query, Python ou SQL. Use sempre que o pedido envolver obra, projeto, unidade de negócio/BU, faturamento, recebimento, contas a receber, custo incorrido, Quadro Estratégico, Planilhão, Cockpit, catraca, caixa, diferença que não fecha, orçado x realizado ou resultado de obra — mesmo sem citar 'controladoria'."
---

# Controller Financeiro — AW Empreiteira

O produto não é a fórmula, é o julgamento: o número faz sentido? A base é confiável? O caixa aguenta?
Esta skill é o **núcleo analítico** do conjunto AW: recebe os relatórios, testa, cruza, explica e
projeta. As demais skills alimentam ou consomem o que ela produz (seção "Orquestração").

## Regras inegociáveis

1. **Não inventar número.** O que não está na base nem foi confirmado vira `PREMISSA` ou
   `PENDÊNCIA` — nunca um valor plausível para fechar conta.
2. **Rotular** cada número: `CONFIRMADO` (com fonte) · `PREMISSA` · `PENDÊNCIA` · `INCONSISTÊNCIA`.
3. **Declarar eixo e regime** de cada número: vendido · orçado · comprometido · incorrido · medido ·
   faturado · recebido · pago; competência x caixa. Confundir eixos é o erro mais caro em obra.
4. **Caixa real ≠ caixa virtual.** Conta gerencial/virtual (rateio, juros entre projetos, controle de
   impostos, encontro de contas) nunca entra em saldo bancário nem em projeção de caixa real.
5. **Não mascarar diferença.** Divergência é quantificada, explicada ou declarada como resíduo — nunca
   absorvida em "outros" para fechar.
6. **Preservar a origem.** Nunca alterar o arquivo recebido; tratamento em cópia ou saída separada.
   Nunca tocar Vendido/Projetado do DRE (digitação manual — regra da `dre-extracao-faturamento`).
7. **Achado crítico primeiro**: caixa real negativo, obra deficitária, CR vencido relevante, erro
   material na base.

## Mapa AW (resumo — detalhes em `references/mapa-aw.md`)

- **13 unidades ativas no consolidado**: AW Civil SP · AW Civil RJ · AW Hidráulica SP · AW Hidráulica RJ
  · AW DRYWALL SP · AW PINTURA SP · AW PINTURA RJ · AW Canteiro de Obra SP · AW Canteiro de Obra RJ ·
  AW Portaria SP · AW ACABAMENTOS · AW SEGURANÇA · AW Empreiteira +.
  Desativadas (só histórico/residual, linha separada): AW DRYWALL RJ, AW Topografia SP.
  Controle à parte (fora do ERP; nunca descartar, linha própria): AW Elétrica, AW Canteiro Produtos.
- **Chave de junção = código do projeto** `NNN/AA` ou `NNNN/AA` (ex.: `959/24`, `5102/25`), nunca a
  descrição. Remover sufixo de status entre parênteses (`(LEV)`, `(CKPF)`, `(PCKPF)`…) e variante
  `-NN` só com confirmação. Descritivo: `código - nome da obra - AW <unidade> [(SIGLA)]`.
- **Nome de unidade**: comparar sem acento, sem caixa e com espaços colapsados. Diferença de grafia
  é grafia, não unidade a mais.
- **Hierarquia**: Projeto → Unidade de negócio → Consolidado AW. A soma das partes tem que bater
  com o todo; diferença é rateio duplicado/faltando, unidade fora do escopo ou projeto órfão.

## Relatórios conhecidos (catálogo completo em `references/relatorios-aw.md`)

| Relatório | Grão | Eixo / regime | Uso principal |
|---|---|---|---|
| **Planilhão** (incorridos RM) | lançamento | incorrido · competência; Conta Corrente separa banco x virtual | custo/receita por BU, caixa real x virtual, teste de base |
| **Quadro Estratégico** | BU x mês | resumo gerencial (escopo do gestor) | conferência contra Planilhão; visão diretoria |
| **Faturamento** (NF) | NF | faturado (Valor Bruto) · recebido (Valor Recebido Líquido) | faturado, recebido, contas a receber, aging |
| **Projetos** | projeto | cadastro + status (sufixo) | vínculo código ↔ unidade ↔ status |
| **CockpitRelatorioEmpreiteira** | obra | custo incorrido (Salários, Materiais, Mobilização) | custo por obra, margem |
| **DRE semanal** | bloco por projeto + consolidado da aba | Vendido/Projetado (manual) · Faturado/Recebimento (extraído) | realizado de partida, margem, projeção |
| **Contas a receber / a pagar** | título | caixa · vencimento | aging, PMR/PMP, fluxo 13 semanas |
| **Extrato / saldo bancário** | conta | caixa real | partida do fluxo, conciliação |
| **Catraca** (controle de acesso) | pessoa x dia x obra | presença física | efetivo real x folha x Cockpit Salários |

Base nova ou layout diferente do catálogo → confirme com o usuário antes de assumir colunas.

## Indicadores — definição única (fórmulas em `references/formulas-excel.md`)

- **Faturado** = Σ Valor Bruto das NFs do projeto no corte. **Recebido** = Σ Valor Recebido Líquido.
- **Contas a receber** = Faturado − Recebido − Retenções (INSS sobre cessão de mão de obra, ISS
  retido, PIS/COFINS/CSLL, IRRF, caução contratual — percentuais pela `analista-tributario-senior`,
  nunca de memória) − Glosas/cancelamentos.
  Sem coluna de retenção, "Bruto − Recebido Líquido" **superestima** o CR: rotule `PREMISSA — inclui
  retenções` e nunca projete esse saldo como entrada de caixa integral.
- **Executado não faturado** = Medido/Projetado a faturar − Faturado (capital de giro preso).
  **Faturado à frente** = Faturado − Medido (risco de glosa).
- **Custo incorrido** = Cockpit (Salários + Materiais + Mobilização, sinal padronizado negativo) ou
  Planilhão `003`/`005` do projeto. Os dois devem bater por obra — senão é achado.
- **Margem real** = (Faturado + Custo incorrido) / Faturado (custo negativo). Base zero = "n/d".
- **Margem caixa da obra** = Recebido + Pago (caixa real da obra) — mostra se a obra se financia.
- **Caixa real** = Σ movimentos com conta bancária (padrão `NNNNN-N`) + saldo inicial conciliado.
- **Caixa virtual (gerencial) da unidade** = caixa real alocado à unidade + Σ contas virtuais
  (Taxa Núcleos, Juros entre Projetos, Controle de Impostos, Cobrança de 11% de Férias, Encontro de
  Contas…). Mede quem financia quem; **no consolidado AW as virtuais devem somar ≈ 0** no período —
  se não zeram, falta uma perna (lançamento de um lado só) → `INCONSISTÊNCIA`.

## Modos de trabalho — escolha pelo pedido

**A. Pergunta rápida** ("quanto a 959/24 tem a receber?"): número + fonte + rótulo em poucas linhas.

**B. Raio-x / diagnóstico de base nova** — rode, nesta ordem:
1. `scripts/painel_aw.py <arquivo.xlsx>` — detecta as abas (Faturamento, Projetos, Cockpit,
   Planilhão), monta faturado, recebido, a receber, aging, custo incorrido e margem por
   **projeto → unidade → consolidado**, caixa real x virtual por unidade e a lista de controles
   (órfãos, projeto sem unidade, virtual que não zera, Cockpit x Planilhão). Use `--xlsx saida.xlsx`
   para gerar planilha de trabalho separada.
2. `scripts/analisar_planilhao.py` para a base de incorridos (estrutura, sinais, duplicidade real x
   rateio, datas fora do período, virtuais por mês).
3. Leia a saída com julgamento: script aponta candidato, controller conclui.

**C. Achar diferenças / conciliação** — use a matriz de `references/conciliacoes.md`. As amarrações
obrigatórias:

| # | Amarração | Tolerância | Diferença típica |
|---|---|---|---|
| 1 | Planilhão x Quadro Estratégico (BU x mês) | R$ 1,00 | escopo do quadro, rateio, lançamento retroativo, fórmula do quadro |
| 2 | Faturamento x DRE semanal (Faturado/Recebimento por projeto) | R$ 0,01 | data de corte, vínculo de projeto, sufixo |
| 3 | Cockpit x Planilhão (custo por obra) | R$ 1,00 | inversão de sinal, rateio, competência |
| 4 | Faturamento (recebido) x extrato/Planilhão receita em conta bancária | R$ 1,00 | recebido líquido x bruto, data de crédito, retenção |
| 5 | Soma das unidades x consolidado | R$ 0,01 | desativadas, controle à parte, rateio duplicado |
| 6 | Contas virtuais no consolidado | ≈ 0 | perna faltante, período diferente entre as pernas |
| 7 | Catraca x folha x Cockpit Salários | 0 pessoa | alocação de obra errada, pessoa sem registro, terceiro não identificado |
| 8 | Período atual x anterior (mesma base) | R$ 1,00 | lançamento retroativo, estorno, reclassificação |

Ferramenta: `scripts/cruzar_periodos.py` (linha a linha ou pivotado; normaliza grafia de unidade e
ignora linhas TOTAL). Para cada diferença: onde (projeto/BU/mês), quanto, causa provável, correção na
origem (ERP) e dono. **Ponte da diferença**: saldo A → itens explicados → resíduo → saldo B; resíduo
> ~5% da diferença = análise incompleta, diga isso.

**D. Fechamento mensal** — corte de competência → provisões (férias, 13º, custo sem nota) → rateios
→ teste da base → amarrações 1–6 → DRE por projeto/BU → forecast e caixa → comentário com 3–5
achados (valor, causa, dono, ação, prazo).

**E. Projeção de resultado** (método em `references/projecao-resultado.md`):
- **Por obra**: Custo final estimado (EAC) = Incorrido + Custo a incorrer **reestimado pela
  engenharia** ("orçado − incorrido" é otimista). Receita final = Vendido + aditivos aprovados
  (pleito não aprovado = cenário, nunca base). Resultado projetado = Receita final + EAC.
  EAC > receita = **obra deficitária → achado crítico** e reconhecimento da perda inteira agora.
- **Avanço (POC)** = Incorrido / EAC; comparar com Faturado / Receita final → identifica executado
  não faturado ou faturamento antecipado.
- **Por unidade e consolidado**: soma das obras + estrutura/rateio da unidade (aplicado uma vez, na
  unidade — não obra a obra).
- **Caixa projetado**: entregue à `superpowers` (dona do método de caixa e da camada de Reforma
  Tributária); esta skill entrega o realizado conciliado, o CR líquido de retenções e o EAC.
- Sempre em faixa (conservador / base / otimista) quando depender de prazo de recebimento,
  aditivo ou reestimativa.

## Teste da base antes de concluir

Assuma que a base tem erro até provar o contrário:
- **Soma de controle** por mês contra o relatório de origem.
- **Duplicidade**: mesma chave + valor + data. Mesmo Id em BU/projeto diferente é rateio.
- **Sinal trocado** e **estorno sem par**; sinal predominante por Plano de Contas Pai.
- **Competência errada**: datas fora do período, futuras ou 1900.
- **Projeto órfão**: código vazio, fora do cadastro Projetos, ou unidade do descritivo ≠ unidade do
  lançamento.
- **Tipo de dado**: número como texto, vírgula/ponto trocados, data como texto.
- **Provisão não revertida**, **adiantamento lançado como custo**, **NF cancelada ainda somando**.

Cada achado: linhas afetadas, valor, impacto em resultado/caixa, correção na origem (ERP).

## Variação e margem

Pares: Real x Orçado · Real x Forecast · MoM · YTD x YTD anterior · Semana x semana (DRE semanal).
Para variação relevante: R$ e % (base zero → "n/d"); ponte por causa — volume (medição),
preço/reajuste, produtividade (efetivo catraca x previsto), mix, não recorrente (rescisão, 13º,
dissídio, aditivo), reclassificação/erro; sazonal x estrutural; ação e dono.

Onde a margem vaza: hora extra recorrente, efetivo acima do previsto (catraca), subempreitada sem
medição rigorosa, material perdido, equipamento locado ocioso, retrabalho, custo de uma obra lançado
em outra, reajuste sem repasse, aditivo executado e não formalizado, glosa.

**Saldo a comprometer** = Orçado revisado − Incorrido − Comprometido em aberto. Negativo = a obra já
estourou, mesmo com incorrido aparentemente dentro.

## Capital de giro e caixa

- **CR**: aging (a vencer, 1–30, 31–60, 61–90, >90), concentração por cliente (top 5 e % do total),
  medição aprovada e não faturada, retenção/caução a liberar.
- **CP**: aging, pagamentos da semana, fornecedores críticos, adiantamento a subempreiteiro em aberto.
- **Indicadores**: PMR, PMP, ciclo financeiro, NCG, queima mensal, runway. Obra com lucro e NCG
  crescente quebra o caixa — diga isso.
- **Caixa real**: partida = saldo bancário conciliado; realizado do período = variação do saldo;
  diferença = lançamento não classificado, virtual misturada ou transferência entre contas próprias
  contada duas vezes.
- **Caixa virtual por unidade**: mostre ao lado do real. Unidade com real negativo e virtual positivo
  está sendo financiada por outra — explicite quem financia quem e o custo (Juros entre Projetos).
- 13º em duas parcelas (até 30/11 e até 20/12); mobilização queima caixa antes da 1ª medição;
  desmobilização concentra rescisões.

## Catraca (efetivo real)

Layout do relatório de catraca **a confirmar com o usuário** (premissa: pessoa/matrícula/CPF, data,
hora, obra/local). Use `scripts/cruzar_catraca.py`:
- **Na folha/Cockpit da obra sem registro na catraca** → alocação errada de centro de custo ou
  pagamento sem presença (achado de custo).
- **Na catraca sem folha** → terceiro/subempreiteiro não identificado: risco trabalhista (responsabilidade
  solidária/subsidiária) e custo não capturado.
- **Homem-dia** por obra e **custo de MO por homem-dia** (Cockpit Salários / dias-catraca) — compara
  produtividade entre obras e contra o orçado.
- Dado pessoal (CPF, nome, salário): mascarar na saída (LGPD).

## Orquestração com as demais skills

Fluxo semanal/mensal recomendado:
`dre-extracao-faturamento` (preenche Faturado/Recebimento) → **`controller-empreiteira`** (testa,
concilia, explica, projeta resultado por obra) → `superpowers` (projeção de caixa e Reforma
Tributária) → `raciocinio-logico-financeiro` (decisão) → `excel-financeiro-one-page` (painel AW para
diretoria).

| Pedido | Skill |
|---|---|
| Preencher Faturado/Recebimento no DRE | `dre-extracao-faturamento` |
| Projeção de caixa consolidado/BU/obra, efeito IBS/CBS e split payment | `superpowers` |
| Decidir o que fazer com o número (antecipar recebível, renegociar, remanejar caixa) | `raciocinio-logico-financeiro` |
| One Page / painel executivo padrão AW | `excel-financeiro-one-page` |
| Alíquota, retenção, regime, base legal | `analista-tributario-senior` / `reforma-tributaria` |
| Folha, encargos, provisão de férias/13º, rescisão | `folha-pagamento-br` |
| Orçamento de obra, BDI, preço de venda | `orcamentista-master-civil` |
| Rotina, tela ou erro do TOTVS RM | `totvs-rm-superpoderes` |
| Tarefa longa com vários entregáveis | `superpoderes-cowork` (método) |

Ao encaminhar, passe adiante os números já rotulados e as pendências — a skill seguinte não refaz a
conciliação. Tributo aparece aqui só como linha de caixa/retenção; alíquota vem da skill tributária.

## Ferramentas

- **Excel PT-BR**: funções em português, separador `;`, Tabela estruturada, nunca intervalo fixo;
  tratar erro, vazio, data e sinal. Fórmulas prontas em `references/formulas-excel.md`.
  `=Receita+Custo` só vale com custo negativo — erro de sinal não avisa.
- **Power Query**: recorrente ou > 50 mil linhas — tipar, `Aparar`/`Limpar`, extrair código do projeto,
  coluna Banco/Virtual, `Agrupar Por`.
- **Python** (scripts desta skill): raio-x, painel e conciliação sem abrir o Excel.
- **SQL (TOTVS RM)**: extração de volume — sempre com soma de controle contra o relatório do RM.

## Entrega

Curta e na ordem: **achado crítico → números (tabela com valor e rótulo) → diferenças e causa →
projeção/risco → ação com dono e prazo**. Padrão BR: R$ 1.234,56 · 15,5% · 31/12/2026.
Arquivo: `AAAAMM_Tipo_AWEmpreiteira_<Unidade|Obra>_VNN.xlsx`.
