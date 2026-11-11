import csv
from decimal import Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parent

COLUNAS_VENDAS = ["id_venda", "data", "id_loja", "categoria", "unidades", "receita_brl"]


def carregar_vendas(caminho=None):
    caminho = caminho or RAIZ / "vendas.csv"
    with open(caminho, newline="", encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    for linha in linhas:
        linha["receita_brl"] = Decimal(linha["receita_brl"])
    return linhas


def carregar_lojas(caminho=None):
    caminho = caminho or RAIZ / "lojas.csv"
    with open(caminho, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def juntar(vendas, lojas):
    """Inner join por id_loja; vendas sem loja correspondente ficam de fora."""
    por_id = {l["id_loja"]: l for l in lojas}
    resultado = []
    for v in vendas:
        loja = por_id.get(v["id_loja"])
        if loja is None:
            continue
        linha = dict(v)
        linha["nome_loja"] = loja["nome_loja"]
        linha["regiao"] = loja["regiao"]
        linha["uf"] = loja["uf"]
        resultado.append(linha)
    return resultado


def gravar_vendas_lojas(linhas, caminho=None):
    caminho = caminho or RAIZ / "vendas_lojas.csv"
    campos = COLUNAS_VENDAS + ["nome_loja", "regiao", "uf"]
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for l in linhas:
            w.writerow({**l, "receita_brl": f"{l['receita_brl']:.2f}"})


def _brl(valor):
    inteiro, dec = f"{valor:.2f}".split(".")
    return f"R$ {int(inteiro):,}".replace(",", ".") + "," + dec


def encontrar_anomalias(vendas, lojas):
    ids_lojas = {l["id_loja"] for l in lojas}
    orfas = [v for v in vendas if v["id_loja"] not in ids_lojas]
    com_venda = {v["id_loja"] for v in vendas}
    sem_vendas = [l for l in lojas if l["id_loja"] not in com_venda]
    return orfas, sem_vendas


def gerar_anomalias_md(vendas, lojas):
    orfas, sem_vendas = encontrar_anomalias(vendas, lojas)
    total = sum((v["receita_brl"] for v in orfas), Decimal("0"))
    linhas = ["# Anomalias dos dados", ""]
    linhas.append(f"## Vendas órfãs ({len(orfas)})")
    linhas.append("")
    linhas.append(
        "Vendas cujo id_loja não existe em lojas.csv. Ficam fora do inner join "
        "(continuam em vendas.csv)."
    )
    linhas.append("")
    linhas.append("| id_venda | data | id_loja | receita_brl |")
    linhas.append("|---|---|---|---|")
    for v in orfas:
        linhas.append(
            f"| {v['id_venda']} | {v['data']} | {v['id_loja']} | {v['receita_brl']:.2f} |"
        )
    linhas.append("")
    linhas.append(f"Total das órfãs: {_brl(total)}")
    linhas.append("")
    linhas.append("## Lojas sem vendas")
    linhas.append("")
    for l in sem_vendas:
        linhas.append(
            f"- Loja {l['id_loja']} ({l['nome_loja']}, {l['regiao']}) não teve vendas "
            "e não aparece no pivot."
        )
    linhas.append("")
    linhas.append("## Consequência")
    linhas.append("")
    linhas.append(
        "A receita das vendas órfãs não aparece em nenhuma região, e o Sul do "
        "relatório descreve uma operação menor do que a real: a loja 108 não tem "
        "vendas registradas e a receita das órfãs não é atribuída a ninguém."
    )
    linhas.append("")
    return "\n".join(linhas)


def gravar_anomalias(vendas, lojas, caminho=None):
    caminho = caminho or RAIZ / "anomalias.md"
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(gerar_anomalias_md(vendas, lojas))


MESES = ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]


def calcular_pivot(linhas_join):
    """Receita por região (ordem alfabética) e mês; células sem venda valem 0."""
    regioes = sorted({l["regiao"] for l in linhas_join})
    pivot = {r: {m: Decimal("0") for m in MESES} for r in regioes}
    for l in linhas_join:
        mes = l["data"][:7]
        if mes in pivot[l["regiao"]]:
            pivot[l["regiao"]][mes] += l["receita_brl"]
    return pivot


def gravar_pivot(pivot, caminho=None):
    caminho = caminho or RAIZ / "pivot_receita.csv"
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["regiao"] + MESES)
        for regiao in sorted(pivot):
            w.writerow([regiao] + [f"{pivot[regiao][m]:.2f}" for m in MESES])


def main():
    vendas = carregar_vendas()
    lojas = carregar_lojas()
    j = juntar(vendas, lojas)
    gravar_vendas_lojas(j)
    gravar_pivot(calcular_pivot(j))
    gravar_anomalias(vendas, lojas)


if __name__ == "__main__":
    main()
