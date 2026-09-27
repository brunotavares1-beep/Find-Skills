# Matriz de conciliação AW — como achar e explicar diferenças

Princípio: **toda diferença tem endereço** (projeto/BU/mês), **valor**, **causa** e **dono**. O script
aponta onde; o controller explica por quê.

## Roteiro padrão (qualquer par de relatórios)

1. **Mesmo corte**: período, data de corte, escopo de unidades (13 ativas? desativadas? controle à
   parte?), regime (competência x caixa), bruto x líquido. Metade das "diferenças" morre aqui.
2. **Mesma chave**: código de projeto sem sufixo; unidade normalizada.
3. **Total geral** A x B. Bateu no total e diverge no detalhe = reclassificação entre projetos/BUs.
4. **Descer o nível**: BU → mês → projeto → lançamento. Pare no nível em que a diferença se isola.
5. **Classificar cada diferença**:

| Causa | Assinatura típica |
|---|---|
| Escopo | BU/projeto inteiro presente só de um lado |
| Corte / competência | diferença some ao somar dois meses vizinhos |
| Sinal | diferença = 2 × valor de um item |
| Duplicidade | diferença = valor exato de um lançamento |
| Rateio | diferença proporcional em várias BUs, soma zero no consolidado |
| Vínculo de projeto | valor aparece em "sem projeto"/órfão de um lado |
| Bruto x líquido | diferença ≈ % fixo do faturado (retenções) |
| Fórmula do consolidado | total ≠ soma das linhas do próprio relatório |
| Lançamento retroativo | período fechado mudou entre duas extrações |

6. **Ponte**: Saldo A → (±) cada causa quantificada → resíduo → Saldo B. Resíduo > ~5% da diferença =
   análise incompleta; declarar.
7. **Correção na origem** (ERP/cadastro), não só na planilha, com dono e prazo.

## Amarrações obrigatórias

### 1. Planilhão x Quadro Estratégico
`cruzar_periodos.py planilhao.xlsx quadro.xlsx --pivotado2 --ano2 AAAA`.
Esperado: BU x mês bate dentro de R$ 1,00 para as BUs do escopo do Quadro. BU só no Planilhão →
confirmar escopo antes de apontar.

### 2. Faturamento x DRE semanal
Por projeto: `SOMASE` do Faturamento (Valor Bruto / Valor Recebido Líquido) = Faturado/Recebimento do
bloco. Diferença → data de corte da aba, projeto vinculado errado, sufixo, NF sem projeto.

### 3. Cockpit x Planilhão (custo por obra)
Salários/Materiais/Mobilização do Cockpit (sinal padronizado) x Planilhão `003`/`005` do projeto no
mesmo período. Diferença → rateio de estrutura presente só no Planilhão, sinal, competência.

### 4. Recebido x caixa real
Recebido (Faturamento) do período x receitas do Planilhão em conta bancária x extrato. Diferença →
data de crédito x data de baixa, recebimento sem NF (adiantamento), baixa por encontro de contas
(virtual — não é caixa).

### 5. Soma das partes x consolidado
Σ projetos = BU; Σ 13 BUs ativas = consolidado AW. Desativadas e controle à parte em linha separada.
Diferença → rateio duplicado/faltando, projeto sem unidade, unidade com grafia divergente.

### 6. Contas virtuais no consolidado
Σ valores em contas virtuais, por mês, no consolidado AW ≈ 0. Por conta virtual também (ex.: Juros
entre Projetos: receita de um projeto = despesa de outro). Não zerou → perna faltante; listar a conta e
o mês.

### 7. Catraca x folha x Cockpit
Pessoa x obra x mês: dias de catraca x dias pagos x R$ Salários do Cockpit. Pessoa paga sem catraca,
catraca sem folha, obra com R$ de MO sem efetivo correspondente.

### 8. Duas extrações da mesma base
`cruzar_periodos.py base_semana1.xlsx base_semana2.xlsx`. Mudança em mês fechado = lançamento
retroativo/estorno — identificar e questionar.

### 9. CR financeiro x CR derivado
CR do contas a receber x (Faturado − Recebido − Retenções) do Faturamento, por projeto/cliente.

## Formato do relatório de diferenças

| Amarração | Nível | Chave | Valor A | Valor B | Diferença | Causa | Rótulo | Ação / dono |
|---|---|---|---|---|---|---|---|---|

Ordene por |diferença| decrescente; destaque as que afetam caixa real.
