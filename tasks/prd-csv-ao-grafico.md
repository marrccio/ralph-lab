# PRD: do CSV ao gráfico (ralph-lab)

## Introduction / Overview

Transformar `vendas.csv` (423 vendas) e `lojas.csv` (8 lojas) em um relatório de receita por região e por mês: um inner join em `vendas_lojas.csv`, um pivot em `pivot_receita.csv` e uma página estática `index.html` com um gráfico e um parágrafo de conclusão. Os dados têm duas armadilhas propositais: 3 vendas apontam para um `id_loja` que não existe (`id_loja=999`) e a loja 108 (Batel, região Sul) não teve nenhuma venda. O pipeline deve tratá-las de forma explícita e documentá-las.

Este PRD foi escrito a partir do enunciado oficial do ia-3.1; as respostas às perguntas de esclarecimento da skill `/prd` são as decisões abaixo (escopo mínimo, só biblioteca padrão do Python, tudo gerado por um único comando).

## Goals

- Gerar `vendas_lojas.csv` com **420 linhas de dados** e receita total de **R$ 931.274,06** (coluna `receita_brl` com o nome original).
- Gerar `pivot_receita.csv` com o cabeçalho exato `regiao,2026-01,2026-02,2026-03,2026-04,2026-05,2026-06`, 4 linhas de dados e soma das células igual a **931274.06** (tolerância de R$ 0,50).
- Gerar `index.html` autocontido, com um gráfico (SVG inline) da receita mensal por região e um parágrafo de conclusão de pelo menos 300 caracteres.
- Registrar as duas anomalias dos dados em `anomalias.md`.
- Ter pelo menos 4 testes pytest passando com `python -m pytest -q`.

## Valores de conferência (do enunciado)

| | |
|---|---|
| Linhas do inner join | 420 |
| Receita total | R$ 931.274,06 |
| Região líder | Sudeste, R$ 265.077,49 |
| Vendas órfãs (`id_loja=999`) | 3 vendas, R$ 8.120,00 no total, fora de qualquer região |
| Loja sem vendas | 108, Batel, região Sul |

## User Stories

### US-001: Carregar os dados de origem
**Description:** Como analista, quero carregar `vendas.csv` e `lojas.csv` em estruturas Python para poder juntá-los sem perder precisão monetária.

**Acceptance Criteria:**
- [ ] `pipeline.py` na raiz tem funções que leem `vendas.csv` e `lojas.csv` com o módulo `csv`, com `receita_brl` convertida para `Decimal`
- [ ] Carrega 423 vendas e 8 lojas
- [ ] `vendas.csv` e `lojas.csv` não são modificados
- [ ] `tests/test_dados.py` tem pelo menos 2 testes (contagens e tipo numérico da receita)
- [ ] `python -m pytest -q` passa

### US-002: Inner join em vendas_lojas.csv
**Description:** Como analista, quero o inner join de vendas e lojas por `id_loja` para saber a receita por região.

**Acceptance Criteria:**
- [ ] `python pipeline.py` grava `vendas_lojas.csv` na raiz com cabeçalho e 420 linhas de dados
- [ ] Mantém as colunas de `vendas.csv` (inclusive `receita_brl` com esse nome) e acrescenta `nome_loja`, `regiao` e `uf`
- [ ] A soma de `receita_brl` é 931274.06
- [ ] As 3 vendas com `id_loja=999` não entram no arquivo e não são apagadas de `vendas.csv`
- [ ] `tests/test_join.py` verifica as 420 linhas e a soma
- [ ] `python -m pytest -q` passa

### US-003: Registrar as anomalias dos dados
**Description:** Como leitor do relatório, quero saber quem ficou de fora e por quê.

**Acceptance Criteria:**
- [ ] `python pipeline.py` grava `anomalias.md`
- [ ] Lista as 3 vendas órfãs (`id_venda`, `data`, `id_loja`, `receita_brl`) e o total de R$ 8.120,00
- [ ] Informa que a loja 108 (Batel, Sul) não teve vendas e não aparece no pivot
- [ ] Explica a consequência: a receita das órfãs não aparece em nenhuma região, e o Sul do relatório descreve uma operação menor do que a real
- [ ] `tests/test_anomalias.py` confere 3 órfãs, total 8120.00 e a loja 108
- [ ] `python -m pytest -q` passa

### US-004: Pivot de receita por região e mês
**Description:** Como analista, quero a receita por região e por mês para comparar o desempenho.

**Acceptance Criteria:**
- [ ] `python pipeline.py` grava `pivot_receita.csv` com o cabeçalho exato `regiao,2026-01,2026-02,2026-03,2026-04,2026-05,2026-06`
- [ ] 4 linhas de dados, em ordem alfabética: Centro-Oeste, Nordeste, Sudeste, Sul
- [ ] Valores com ponto decimal e 2 casas (por exemplo `265077.49`), sem `R$` e sem separador de milhar; célula sem venda vale `0.00`
- [ ] A soma de todas as células numéricas é 931274.06 (tolerância 0,50) e o total do Sudeste é 265077.49
- [ ] `tests/test_pivot.py` verifica cabeçalho, forma 4x7, total e Sudeste
- [ ] `python -m pytest -q` passa

### US-005: Página index.html com gráfico e conclusão
**Description:** Como leitor, quero ver a receita mensal por região em um gráfico e uma conclusão em texto.

**Acceptance Criteria:**
- [ ] `python pipeline.py` grava `index.html` na raiz, autocontido: sem `<script src>`, sem CSS externo e sem CDN
- [ ] Contém um elemento `<svg>` inline com a receita mensal por região, com legenda e eixos rotulados
- [ ] Contém um `<p>` de conclusão com pelo menos 300 caracteres, gerado a partir dos dados: região líder (Sudeste, R$ 265.077,49), receita total (R$ 931.274,06), e as duas anomalias (3 vendas órfãs de R$ 8.120,00 fora do relatório; loja 108 sem vendas)
- [ ] `tests/test_pagina.py` verifica o `<svg`, o `<p>` com 300+ caracteres e a menção ao Sudeste
- [ ] `python -m pytest -q` passa

### US-006: Pipeline reproduzível e suíte final
**Description:** Como mantenedor, quero um único comando que regenere tudo e uma suíte que prove que está certo.

**Acceptance Criteria:**
- [ ] `python pipeline.py` regenera `vendas_lojas.csv`, `pivot_receita.csv`, `anomalias.md` e `index.html` a partir de `vendas.csv` e `lojas.csv` sem erro, e rodar duas vezes dá o mesmo resultado
- [ ] A suíte tem pelo menos 4 testes e `python -m pytest -q` passa com nenhum teste falhando
- [ ] `progress.txt` registra o que foi feito em cada história

## Functional Requirements

- FR-1: O pipeline é um único arquivo `pipeline.py` na raiz, executado com `python pipeline.py`.
- FR-2: Ler `receita_brl` como número decimal (`Decimal`), nunca como texto.
- FR-3: O join é um inner join por `id_loja`; as vendas órfãs ficam de fora do join e são registradas em `anomalias.md`.
- FR-4: Não apagar linhas problemáticas de `vendas.csv` nem de `lojas.csv`, e não inventar dados.
- FR-5: Os arquivos de saída ficam na **raiz** do repositório.
- FR-6: Usar apenas a biblioteca padrão do Python e o pytest.

## Non-Goals (Out of Scope)

- Não usar pandas, Chart.js, CDN ou qualquer dependência externa.
- Não tratar as vendas órfãs com um left join nem criar uma região "desconhecida" no pivot.
- Não fazer deploy nem publicar nada.

## Technical Considerations

- O inner join, e não o left join, é o que dá 420 linhas e R$ 931.274,06; deixar as órfãs entrarem erra as duas contas.
- Usar `Decimal` e arredondar para 2 casas só na escrita, para a soma do pivot bater com a do join.
- O SVG deve ser gerado por Python (sem bibliotecas), com as quatro regiões e os seis meses.

## Success Metrics

- `python -m pytest -q`: pelo menos 4 testes, todos passando.
- 420 linhas no join, R$ 931.274,06 no total, 4 x 7 no pivot.
- `index.html` com `<svg>` e um `<p>` de conclusão com 300 ou mais caracteres.

## Open Questions

- Nenhuma. O enunciado define os valores de conferência.
