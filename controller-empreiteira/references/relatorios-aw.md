# Catálogo dos relatórios AW — estrutura, eixo e armadilhas

Layouts observados em bases reais. Nomes de coluna variam por exportação: **localize pelo rótulo do
cabeçalho, nunca pela posição**, e confirme com o usuário quando divergir. Entrada padrão desde
20/08/2026: um único `.xlsx` com as abas Faturamento, Projetos, CockpitRelatorioEmpreiteira e DRE.

---

## 1. Planilhão — base bruta de incorridos (TOTVS RM)

Uma linha por lançamento.

| Campo | O que é | Armadilha |
|---|---|---|
| Unidade de Negocio | BU a que o lançamento pertence | Inclui guarda-chuvas (Serviço Compartilhado, Taxa CostSharing) = rateio, não obra |
| Plano de Contas Pai | 1º nível (`001 - RECEITAS`, `002 - IMPOSTOS`, `003 - CUSTO DE SERVIÇOS`…) | Confirmar sinal predominante por pai |
| Plano de Contas | detalhe (`003.002.001 - SALÁRIOS`) | — |
| Data Incorrido | competência | Não é data de pagamento |
| Id Lançamento | Id na origem | **Não é único**: rateio repete o Id em Projeto/BU diferentes. Duplicidade real = linha inteira igual |
| Mes / Ano | competência numérica | redundante com a data; útil para agregar |
| Projeto | `NNNN/AA - Descrição - Unidade` | extrair o código antes de cruzar |
| Funcionario | pessoa (folha/reembolso) | dado pessoal — LGPD |
| Conta Corrente | origem/destino | **define caixa real x virtual** (abaixo) |
| Descricao | texto livre | fornecedor, referência de rateio |
| Valor | valor | custo negativo / receita positiva é o mais comum — confirmar |

### Banco x conta virtual — o cuidado mais importante

- **Conta bancária real**: código numérico `NNNNN-N` (ex.: `97418-4`, `80004-1`) → dinheiro que passou
  por banco → **caixa real**.
- **Conta gerencial/virtual**: rótulo textual (`Controle de Impostos`, `Taxa Núcleos`,
  `Juros entre Projetos`, `Cobrança de 11% de Férias`, `Encontro de Contas/Outros`) → realocação
  interna entre BUs ou controle de apuração → **caixa virtual**, não é caixa.
- Somar os dois como "movimento financeiro" infla ou distorce o caixa por BU.
- No **consolidado AW**, as virtuais devem se compensar (≈ 0) no período. Se não zeram: perna
  faltante, pernas em meses diferentes ou virtual lançada contra conta bancária.

### Plano de contas típico

`001` Receitas · `002` Impostos · `003` Custo de Serviços (MO direta, INSS, VR, EPI…) · `005` Despesas
operacionais de projeto/obra (inclui "Reembolso") · `006` Ocupação · `007` Administrativas · `010`
Telecom · `011` Serviços profissionais · `047` Software · `015` Empréstimos e financiamentos · `025`
Juros entre projetos (virtual, não é juro bancário).

---

## 2. Quadro Estratégico — consolidado gerencial

Pivot Unidade de Negócio (linha) x Mês (colunas JAN…DEZ), já no escopo do gestor.
- BU no Planilhão e fora do Quadro **pode ser recorte intencional** (administrativas/compartilhadas).
  Confirme o critério antes de chamar de inconsistência.
- Pode ter linhas de TOTAL/subtotal: **excluir antes de somar** (dupla contagem).
- O ano costuma estar só no título — informe `--ano` no `cruzar_periodos.py` se houver dúvida.

---

## 3. Faturamento — notas fiscais

Uma NF por linha. Colunas observadas (confirmar pelos rótulos da linha 1):

| Coluna (modelo) | Rótulo | Uso |
|---|---|---|
| W | Projeto | chave (extrair código) |
| I | Valor Bruto | **Faturado** |
| U | Valor Recebido Líquido | **Recebido** |
| — | Emissão / Vencimento / Data de recebimento | aging, PMR, corte |
| — | Cliente | concentração |
| — | Retenções (INSS, ISS, PIS/COFINS/CSLL, IR) / Valor Líquido | CR líquido real |
| — | Situação (cancelada, substituída) | NF cancelada não soma |

Armadilhas:
- **Bruto x líquido**: Faturado é bruto, Recebido é líquido de retenções. "Bruto − Recebido" nunca
  zera numa NF quitada com retenção → CR superestimado. Use Valor Líquido ou retenções quando houver.
- NF cancelada/substituída ainda somando.
- Projeto em branco ou com código fora do cadastro → faturamento órfão (some do DRE sem avisar).
- Recebimento parcial: mesma NF pode ter mais de uma linha de baixa — não trate como duplicidade
  sem comparar a data de recebimento.

---

## 4. Projetos — cadastro

Uma coluna (A), um projeto por linha: `NNN(N)/AA[-NN] - Nome - AW <Unidade> [(SIGLA)]`.
- Base cresce toda semana: nunca fixe número de linhas.
- Registro sem "- AW ...", grafia divergente ou código só com `-NN` → `PENDÊNCIA` se não casar com
  segurança.
- Sufixo de status (`(LEV)`, `(CKPF)`, `(PCKPF)`) indica fase — útil para separar obra ativa x
  encerrada na projeção.

---

## 5. CockpitRelatorioEmpreiteira — custo por obra

Custos por projeto: **Salários/Mão de obra, Materiais, Mobilização** (pode haver outras linhas).
- Sinal: Salários e Materiais **positivos no relatório → inverter**; Mobilização **já negativa**.
- Deve bater com o Planilhão (`003`/`005` do mesmo projeto e período). Diferença típica: rateio de
  estrutura só no Planilhão, competência, sinal.
- Layout (projeto em linha x colunas, ou blocos por projeto) varia: confirme antes de extrair.

---

## 6. DRE semanal (esqueleto por obra)

Blocos por projeto (célula de cabeçalho ligada a `Projetos!A…`), colunas **Vendido · Projetado ·
Faturado · Recebimento · A Receber/A Pagar**, bloco CUSTOS (Cockpit), e **DRE – <Unidade> –
CONSOLIDADO** = soma dos blocos da própria aba.
- Vendido e Projetado: digitação manual — **nunca calcular ou sobrescrever**.
- Faturado/Recebimento: `SOMASE` por projeto na aba Faturamento (skill `dre-extracao-faturamento`).
- Várias abas por data (`DRE 18-08`…): a mais recente é o realizado de partida; confira a data de
  corte.
- Consolidado ≠ soma dos blocos → fórmula de soma sem o bloco novo (achado).

---

## 7. Contas a receber / a pagar

Título por linha: cliente/fornecedor, projeto, emissão, vencimento, valor, saldo, situação.
- CR do financeiro deve bater com o CR derivado do Faturamento (Faturado − Recebido − Retenções).
  Diferença = retenção, baixa não registrada, NF sem título ou título sem NF.
- CP: separar subempreiteiro, material, folha, tributo, financiamento — natureza define prioridade no
  fluxo.

---

## 8. Extrato / saldo bancário

Única fonte do **caixa real** de partida. Conciliar: saldo inicial + movimentos do Planilhão com conta
bancária = saldo final do extrato. Transferência entre contas próprias aparece duas vezes (sai e
entra) — no consolidado soma zero.

---

## 9. Catraca — controle de acesso às obras

**Layout a confirmar com o usuário** (premissa usada pelo `scripts/cruzar_catraca.py`): uma linha por
passagem ou por dia, com identificação da pessoa (matrícula, CPF ou nome), data (e hora) e
obra/local/equipamento.
- Presença = pelo menos uma passagem no dia na obra.
- Cruzar com a folha (pessoa x obra/centro de custo x dias pagos) e com Cockpit Salários (R$).
- Portaria/Segurança podem ser, elas mesmas, unidades AW (AW Portaria SP, AW SEGURANÇA) — cuidado
  para não misturar o efetivo que presta o serviço com o efetivo da obra cliente.
- Dados pessoais: mascarar CPF (`***.456.789-**`) e restringir a saída ao necessário.

---

## Checklist ao abrir uma base nova

1. `scripts/painel_aw.py <arquivo>` — abas detectadas, colunas usadas, totais e controles.
2. `scripts/analisar_planilhao.py` na base de incorridos.
3. Confirmar com o usuário: padrão de conta bancária, sinal do custo, coluna de Faturado/Recebido,
   data de corte.
4. Separar rateio x duplicidade; banco x virtual.
5. Só então responder à pergunta de negócio.
