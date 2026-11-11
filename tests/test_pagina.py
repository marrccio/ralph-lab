import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pipeline


def _html(tmp_path):
    vendas = pipeline.carregar_vendas()
    lojas = pipeline.carregar_lojas()
    pivot = pipeline.calcular_pivot(pipeline.juntar(vendas, lojas))
    destino = tmp_path / "index.html"
    pipeline.gravar_index(pivot, vendas, lojas, destino)
    return destino.read_text(encoding="utf-8")


def test_svg_inline_e_autocontido(tmp_path):
    h = _html(tmp_path)
    assert "<svg" in h and "</svg>" in h
    assert "<script" not in h
    assert "http://" not in h.replace("http://www.w3.org/2000/svg", "")
    assert "https://" not in h
    for regiao in ["Centro-Oeste", "Nordeste", "Sudeste", "Sul"]:
        assert regiao in h
    assert "2026-01" in h and "Receita (R$)" in h


def test_paragrafo_conclusao(tmp_path):
    h = _html(tmp_path)
    p = re.search(r"<p>(.*?)</p>", h, re.S).group(1)
    assert len(p) >= 300
    assert "Sudeste" in p
    assert "R$ 265.077,49" in p
    assert "R$ 931.274,06" in p
    assert "R$ 8.120,00" in p
    assert "108" in p
