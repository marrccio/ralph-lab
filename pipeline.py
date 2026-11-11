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


def main():
    vendas = carregar_vendas()
    lojas = carregar_lojas()
    gravar_vendas_lojas(juntar(vendas, lojas))


if __name__ == "__main__":
    main()
