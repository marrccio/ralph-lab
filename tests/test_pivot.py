import csv
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pipeline


def _linhas(tmp_path):
    destino = tmp_path / "pivot.csv"
    j = pipeline.juntar(pipeline.carregar_vendas(), pipeline.carregar_lojas())
    pipeline.gravar_pivot(pipeline.calcular_pivot(j), destino)
    with open(destino, newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


def test_cabecalho_e_forma(tmp_path):
    linhas = _linhas(tmp_path)
    assert linhas[0] == ["regiao", "2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]
    assert len(linhas) == 5
    assert all(len(l) == 7 for l in linhas)
    assert [l[0] for l in linhas[1:]] == ["Centro-Oeste", "Nordeste", "Sudeste", "Sul"]


def test_total_e_sudeste(tmp_path):
    dados = _linhas(tmp_path)[1:]
    total = sum(Decimal(c) for l in dados for c in l[1:])
    assert abs(total - Decimal("931274.06")) <= Decimal("0.50")
    sudeste = next(l for l in dados if l[0] == "Sudeste")
    assert sum(Decimal(c) for c in sudeste[1:]) == Decimal("265077.49")
