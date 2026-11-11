# Anomalias dos dados

## Vendas órfãs (3)

Vendas cujo id_loja não existe em lojas.csv. Ficam fora do inner join (continuam em vendas.csv).

| id_venda | data | id_loja | receita_brl |
|---|---|---|---|
| V00421 | 2026-02-15 | 999 | 1200.00 |
| V00422 | 2026-03-15 | 999 | 4520.00 |
| V00423 | 2026-04-15 | 999 | 2400.00 |

Total das órfãs: R$ 8.120,00

## Lojas sem vendas

- Loja 108 (Batel, Sul) não teve vendas e não aparece no pivot.

## Consequência

A receita das vendas órfãs não aparece em nenhuma região, e o Sul do relatório descreve uma operação menor do que a real: a loja 108 não tem vendas registradas e a receita das órfãs não é atribuída a ninguém.
