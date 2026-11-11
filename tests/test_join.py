import csv
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pipeline


def _linhas(tmp_path):
    destino = tmp_path / "vl.csv"
    j = pipeline.juntar(pipeline.carregar_vendas(), pipeline.carregar_lojas())
    pipeline.gravar_vendas_lojas(j, destino)
    with open(destino, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_420_linhas(tmp_path):
    assert len(_linhas(tmp_path)) == 420


def test_soma_e_colunas(tmp_path):
    linhas = _linhas(tmp_path)
    assert sum(Decimal(l["receita_brl"]) for l in linhas) == Decimal("931274.06")
    assert {"receita_brl", "nome_loja", "regiao", "uf"} <= set(linhas[0])
    assert all(l["id_loja"] != "999" for l in linhas)
