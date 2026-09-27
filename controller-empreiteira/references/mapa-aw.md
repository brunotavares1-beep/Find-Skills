# Mapa AW Empreiteira — unidades, chaves e normalização

Fonte: cadastro confirmado com o usuário em 27/09/2026 (mesmo mapa da skill `superpowers`). Se o
usuário informar mudança de cadastro, a informação mais recente dele prevalece — atualize os dois
arquivos juntos.

## Unidades de negócio

| Situação | Unidades | Tratamento |
|---|---|---|
| Ativas (13) — consolidado corrente | AW Civil SP · AW Civil RJ · AW Hidráulica SP · AW Hidráulica RJ · AW DRYWALL SP · AW PINTURA SP · AW PINTURA RJ · AW Canteiro de Obra SP · AW Canteiro de Obra RJ · AW Portaria SP · AW ACABAMENTOS · AW SEGURANÇA · AW Empreiteira + | Somam o consolidado AW |
| Desativadas | AW DRYWALL RJ - DESATIVADA · AW Topografia SP - DESATIVADA | Só histórico ou custo/recebimento residual, em linha separada |
| Controle à parte (fora do ERP) | AW Elétrica · AW Canteiro Produtos | Não buscar no ERP; se aparecerem, manter em linha própria "controle à parte" — nunca descartar, nunca somar às 13 |
| Guarda-chuva / rateio | Empreiteira - Serviço Compartilhado · Taxa CostSharing (e similares) | Não é obra física; é estrutura a ratear. Fora do Quadro Estratégico pode ser recorte de escopo, não erro |

- **Corte regional SP/RJ**: AW ACABAMENTOS, AW SEGURANÇA e AW Empreiteira + não têm sufixo regional —
  confirme o critério antes de quebrar por região.
- **Cobertura da automação do DRE semanal** (confirmada em 10/09 e 27/09/2026): AW Hidráulica SP,
  AW Civil RJ, AW ACABAMENTOS, AW PINTURA SP, AW DRYWALL SP, AW Canteiro de Obra SP. Para as demais,
  pergunte a fonte do realizado.

## Chave de projeto

- Formato do código: `NNN/AA` ou `NNNN/AA` (3 ou 4 dígitos, barra, ano com 2 dígitos). Ex.: `959/24`,
  `5102/25`. Regex: `(\d{3,4}/\d{2})`.
- Descritivo: `código - nome da obra - AW <unidade> [(SIGLA)]`.
  Ex.: `5102/25 - Confidencial 210 Obr - AW ACABAMENTOS (LEV)`.
- **Sufixo de status**: sempre sigla entre parênteses no fim, lista aberta (`(LEV)`, `(CKPF)`,
  `(PCKPF)`…). Pode existir numa base e não na outra → **remova antes de cruzar**; senão o cruzamento
  volta zero sem erro visível. "Obra" e "Checklist" fazem parte do nome, não são sufixo.
- **Variante `-NN`** (`4662/24` x `4662/24-00`): pode ser o mesmo contrato ou aditivo. Não una sem
  confirmação — trate como `PENDÊNCIA`.
- **Unidade no descritivo**: tudo depois do último ` - AW ` (inclusive nomes com espaço, como
  "Canteiro de Obra SP"). Espaço nunca é sufixo.
- Nunca vincule pela descrição textual — ela varia entre bases.

## Normalização de nomes de unidade

Comparar sempre por: sem acento → maiúsculas → hífen/traço substituído por espaço → espaços
colapsados → remover prefixo "AW" duplicado. "AW SEGURANÇA", "AW Segurança" e "AW - Segurança" são a
mesma unidade. Remova também " - DESATIVADA" para achar a unidade, mas mantenha a marcação de
situação.

## Sinais (convenção do DRE/Cockpit)

- Receita positiva, custo negativo.
- Cockpit: **Salários/Mão de obra e Materiais vêm positivos → inverter para negativo**;
  **Mobilização já vem negativa → não inverter**. Confirme em base nova: se Mobilização vier
  positiva, é `INCONSISTÊNCIA` a reportar, não a corrigir em silêncio.
- Planilhão: confirmar o sinal predominante por Plano de Contas Pai antes de somar.
