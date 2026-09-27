# Fórmulas Excel PT-BR — empreiteira multi-BU

Convenções: funções em português, separador `;`, Tabela estruturada. Nomes de tabela/coluna seguem o
Planilhão e o Faturamento (`references/relatorios-aw.md`); ajuste à base do usuário.

## Soma por BU/obra e mês

```
=SOMASES(Planilhao[Valor];Planilhao[Unidade de Negocio];$A2;Planilhao[Ano];$B2;Planilhao[Mes];$C2)
```
Sem colunas Ano/Mes, por intervalo de data:
```
=SOMASES(Planilhao[Valor];Planilhao[Unidade de Negocio];$A2;
         Planilhao[Data Incorrido];">="&DATA($B2;$C2;1);Planilhao[Data Incorrido];"<"&DATA($B2;$C2+1;1))
```

## Busca com tratamento

```
=SEERRO(PROCX($A2;PlanoDeContas[Codigo];PlanoDeContas[Descricao]);"Verificar código")
```

## Banco x conta virtual

Padrão `NNNNN-N` = conta bancária (confirme na base antes de usar):
```
=SE(É.NÚM(LOCALIZAR("-";[@[Conta Corrente]]))*É.NÚM(--SUBSTITUIR([@[Conta Corrente]];"-";""));"Banco";"Conta Virtual")
```
Em base grande, faça a mesma classificação como coluna condicional no Power Query.

## DRE resumido por BU

```
Receita   =SOMASES(Planilhao[Valor];Planilhao[Unidade de Negocio];$A2;Planilhao[Plano de Contas Pai];"001*")
Custo     =SOMASES(Planilhao[Valor];Planilhao[Unidade de Negocio];$A2;Planilhao[Plano de Contas Pai];"003*")
Resultado =[@Receita]+[@Custo]        ← só se custo vier negativo; se positivo: =[@Receita]-[@Custo]
Margem %  =SE([@Receita]=0;"n/d";[@Resultado]/[@Receita])
```
`"001*"`/`"003*"` pressupõem essa numeração do plano de contas — confirme.

## Variação

```
Variação R$ =[@Atual]-[@Anterior]
Variação %  =SE([@Anterior]=0;"n/d";([@Atual]-[@Anterior])/ABS([@Anterior]))
```
Acompanhe com nota: sazonal esperado (rescisão, 13º) ou a investigar.

## Candidato a duplicidade real

Rateio repete o Id com BU/Projeto diferente; duplicidade repete a linha inteira.
```
=SE(CONT.SES(Planilhao[Id Lançamento];[@[Id Lançamento]];Planilhao[Unidade de Negocio];[@[Unidade de Negocio]];
             Planilhao[Valor];[@Valor];Planilhao[Data Incorrido];[@[Data Incorrido]])>1;"Verificar";"")
```

## Aging

Use a data-base do fechamento (célula de parâmetro), não `HOJE()` — senão o aging muda sozinho a
cada abertura e deixa de bater com o relatório entregue:
```
=LET(d;Parametros[DataBase]-[@Vencimento];
     SE(d<=0;"A vencer";SES(d<=30;"1-30";d<=60;"31-60";d<=90;"61-90";VERDADEIRO;">90")))
```

## Base > 50 mil linhas

Power Query (`Dados > Obter Dados`): tipar colunas, coluna condicional Banco/Virtual, `Agrupar Por`
BU + Ano + Mês, e Tabela Dinâmica/Power Pivot no cruzamento final. Para um raio-x sem Excel:
`scripts/analisar_planilhao.py`.

## Chave de projeto (código sem sufixo)

Extrai `NNN/AA` ou `NNNN/AA` do descritivo (`5102/25 - Obra X - AW ACABAMENTOS (LEV)` → `5102/25`):
```
=SEERRO(ESQUERDA(ARRUMAR([@Projeto]);LOCALIZAR(" ";ARRUMAR([@Projeto])&" ")-1);"SEM PROJETO")
```
Código com `-NN` (`4662/24-00`) fica como está — não unir sem confirmação.
Unidade do descritivo (texto após o último " - AW "), sem sufixo entre parênteses:
```
=LET(u;TEXTODEPOIS(ARRUMAR([@Projeto]);" - AW ";-1;;;"");
     SE(u="";"SEM UNIDADE";"AW "&ARRUMAR(SE(DIREITA(u;1)=")";TEXTOANTES(u;" (";-1);u))))
```
Em base grande, faça o mesmo no Power Query (`Text.BeforeDelimiter`, `Text.AfterDelimiter(..., " - AW ", {0, RelativePosition.FromEnd})`).

## Faturado, recebido e a receber por projeto

```
Faturado  =SOMASES(Faturamento[Valor Bruto];Faturamento[Codigo];$A2)
Recebido  =SOMASES(Faturamento[Valor Recebido Líquido];Faturamento[Codigo];$A2)
Retenções =SOMASES(Faturamento[Retenções];Faturamento[Codigo];$A2)      ← se existir a coluna
A receber =[@Faturado]-[@Recebido]-[@Retenções]
```
Sem coluna de retenção: `A receber` fica rotulado `PREMISSA — inclui retenções`.
Corte por data (até a data-base em `Parametros[DataBase]`):
```
=SOMASES(Faturamento[Valor Bruto];Faturamento[Codigo];$A2;Faturamento[Emissão];"<="&Parametros[DataBase])
```

## Custo incorrido do Cockpit com sinal padronizado

```
Custo MO/Material =-ABS(SOMASES(Cockpit[Valor];Cockpit[Codigo];$A2;Cockpit[Natureza];"Salários"))
Mobilização       =SOMASES(Cockpit[Valor];Cockpit[Codigo];$A2;Cockpit[Natureza];"Mobilização")   ← já negativa
Checagem sinal    =SE(Mobilização>0;"INCONSISTÊNCIA: mobilização positiva";"")
```

## Margem real e margem projetada

```
Margem real       =SE([@Faturado]=0;"n/d";([@Faturado]+[@Custo])/[@Faturado])
EAC               =[@CustoIncorrido]+[@CustoAIncorrer]                 ← ambos negativos
Resultado proj.   =[@ReceitaFinal]+[@EAC]
Margem proj.      =SE([@ReceitaFinal]=0;"n/d";[@ResultadoProj]/[@ReceitaFinal])
POC               =SE([@EAC]=0;"n/d";[@CustoIncorrido]/[@EAC])
Exec. não fatur.  =[@POC]*[@ReceitaFinal]-[@Faturado]
Alerta            =SE([@ResultadoProj]<0;"OBRA DEFICITÁRIA";SE([@MargemProj]<[@MargemVendida]-0,02;"MARGEM EM QUEDA";""))
```

## Caixa real x caixa virtual por unidade

Com a coluna `Tipo` (Banco/Conta Virtual, fórmula acima) no Planilhão:
```
Caixa real    =SOMASES(Planilhao[Valor];Planilhao[Unidade de Negocio];$A2;Planilhao[Tipo];"Banco")
Caixa virtual =SOMASES(Planilhao[Valor];Planilhao[Unidade de Negocio];$A2;Planilhao[Tipo];"Conta Virtual")
Gerencial     =[@CaixaReal]+[@CaixaVirtual]
Teste zero    =SE(ABS(SOMASES(Planilhao[Valor];Planilhao[Tipo];"Conta Virtual";Planilhao[Ano];$B$1;Planilhao[Mes];$C$1))>1;"VIRTUAL NÃO ZERA";"OK")
```

## Conciliação A x B com status

```
Diferença =[@ValorA]-[@ValorB]
Status    =SE(ABS([@Diferença])<=Parametros[Tolerancia];"OK";SE([@ValorB]=0;"SÓ EM A";SE([@ValorA]=0;"SÓ EM B";"DIVERGE")))
```

## Concentração de CR (top clientes)

```
Participação =[@AReceber]/SOMA([AReceber])
Top 5        =SOMA(TOMAR(CLASSIFICAR(Clientes[AReceber];;-1);5))/SOMA(Clientes[AReceber])
```

## Homem-dia (catraca)

```
Dias presentes =SEERRO(LINS(ÚNICO(FILTRO(Catraca[Data];(Catraca[Pessoa]=[@Pessoa])*(Catraca[Obra]=[@Obra]))));0)
Custo MO/HD    =SE([@HomemDia]=0;"n/d";-[@Salarios]/[@HomemDia])
```
