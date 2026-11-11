import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pipeline


def _dados():
    return pipeline.carregar_vendas(), pipeline.carregar_lojas()


def test_tres_orfas_total_8120():
    orfas, _ = pipeline.encontrar_anomalias(*_dados())
    assert len(orfas) == 3
    assert sum(v["receita_brl"] for v in orfas) == Decimal("8120.00")


def test_loja_108_sem_vendas():
    _, sem = pipeline.encontrar_anomalias(*_dados())
    assert [l["id_loja"] for l in sem] == ["108"]


def test_markdown_gerado(tmp_path):
    destino = tmp_path / "anomalias.md"
    pipeline.gravar_anomalias(*_dados(), destino)
    texto = destino.read_text(encoding="utf-8")
    for esperado in ["V00421", "V00422", "V00423", "R$ 8.120,00", "Batel", "108", "Sul"]:
        assert esperado in texto
