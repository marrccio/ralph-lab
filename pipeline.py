import csv
from decimal import Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parent


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
