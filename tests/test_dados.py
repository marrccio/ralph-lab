import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pipeline


def test_contagens():
    assert len(pipeline.carregar_vendas()) == 423
    assert len(pipeline.carregar_lojas()) == 8


def test_receita_decimal():
    assert all(isinstance(v["receita_brl"], Decimal) for v in pipeline.carregar_vendas())
