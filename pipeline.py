import csv
import html
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


CORES = ["#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02"]


def gerar_svg(pivot):
    regioes = sorted(pivot)
    largura, altura = 760, 380
    esq, dir_, topo, base = 80, 20, 20, 60
    area_w, area_h = largura - esq - dir_, altura - topo - base
    maximo = max((v for r in pivot.values() for v in r.values()), default=Decimal("0"))
    maximo = float(maximo) or 1.0
    passo = 50000.0
    while maximo / passo > 8:
        passo *= 2
    teto = passo * (int(maximo // passo) + 1)
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura} {altura}" '
        f'width="{largura}" height="{altura}" role="img" '
        'aria-label="Receita mensal por região">'
    ]
    y = 0.0
    while y <= teto:
        py = topo + area_h - area_h * y / teto
        p.append(f'<line x1="{esq}" y1="{py:.1f}" x2="{esq + area_w}" y2="{py:.1f}" stroke="#ddd"/>')
        p.append(
            f'<text x="{esq - 6}" y="{py + 4:.1f}" text-anchor="end" font-size="11">'
            f"{int(y):,}".replace(",", ".") + "</text>"
        )
        y += passo
    p.append(f'<line x1="{esq}" y1="{topo}" x2="{esq}" y2="{topo + area_h}" stroke="#333"/>')
    p.append(
        f'<line x1="{esq}" y1="{topo + area_h}" x2="{esq + area_w}" y2="{topo + area_h}" stroke="#333"/>'
    )
    grupo = area_w / len(MESES)
    barra = grupo * 0.8 / len(regioes)
    for i, m in enumerate(MESES):
        x0 = esq + i * grupo + grupo * 0.1
        for k, r in enumerate(regioes):
            h = area_h * float(pivot[r][m]) / teto
            p.append(
                f'<rect x="{x0 + k * barra:.1f}" y="{topo + area_h - h:.1f}" '
                f'width="{barra:.1f}" height="{h:.1f}" fill="{CORES[k % len(CORES)]}">'
                f"<title>{r} {m}: {_brl(pivot[r][m])}</title></rect>"
            )
        p.append(
            f'<text x="{esq + i * grupo + grupo / 2:.1f}" y="{topo + area_h + 16}" '
            f'text-anchor="middle" font-size="11">{m}</text>'
        )
    p.append(
        f'<text x="{esq + area_w / 2}" y="{altura - 22}" text-anchor="middle" '
        'font-size="12">Mês</text>'
    )
    p.append(
        f'<text transform="rotate(-90 16 {topo + area_h / 2})" x="16" y="{topo + area_h / 2}" '
        'text-anchor="middle" font-size="12">Receita (R$)</text>'
    )
    for k, r in enumerate(regioes):
        lx = esq + k * 140
        p.append(
            f'<rect x="{lx}" y="{altura - 14}" width="10" height="10" fill="{CORES[k % len(CORES)]}"/>'
            f'<text x="{lx + 14}" y="{altura - 5}" font-size="11">{html.escape(r)}</text>'
        )
    p.append("</svg>")
    return "\n".join(p)


def gerar_conclusao(pivot, vendas, lojas):
    totais = {r: sum(v.values(), Decimal("0")) for r, v in pivot.items()}
    lider = max(sorted(totais), key=lambda r: totais[r])
    total = sum(totais.values(), Decimal("0"))
    orfas, sem_vendas = encontrar_anomalias(vendas, lojas)
    total_orfas = sum((v["receita_brl"] for v in orfas), Decimal("0"))
    lojas_txt = ", ".join(f"{l['id_loja']} ({l['nome_loja']}, {l['regiao']})" for l in sem_vendas)
    return (
        f"A região líder em receita é {lider}, com {_brl(totais[lider])}, de uma receita "
        f"total de {_brl(total)} entre janeiro e junho de 2026. Duas anomalias limitam a "
        f"leitura: {len(orfas)} vendas órfãs, cujo id_loja não existe em lojas.csv, somam "
        f"{_brl(total_orfas)} e ficam fora do relatório, de modo que a receita real é maior "
        f"que a exibida; e a loja {lojas_txt} não teve vendas e não aparece no pivot, o que "
        "faz o Sul descrever uma operação menor do que a real."
    )


def gerar_index_html(pivot, vendas, lojas):
    return (
        '<!DOCTYPE html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
        "<title>Receita por região e mês</title>\n"
        "<style>body{font-family:sans-serif;max-width:800px;margin:2em auto;padding:0 1em}</style>\n"
        "</head>\n<body>\n<h1>Receita mensal por região</h1>\n"
        + gerar_svg(pivot)
        + "\n<h2>Conclusão</h2>\n<p>"
        + html.escape(gerar_conclusao(pivot, vendas, lojas))
        + "</p>\n</body>\n</html>\n"
    )


def gravar_index(pivot, vendas, lojas, caminho=None):
    caminho = caminho or RAIZ / "index.html"
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(gerar_index_html(pivot, vendas, lojas))


def main():
    vendas = carregar_vendas()
    lojas = carregar_lojas()
    j = juntar(vendas, lojas)
    gravar_vendas_lojas(j)
    pivot = calcular_pivot(j)
    gravar_pivot(pivot)
    gravar_anomalias(vendas, lojas)
    gravar_index(pivot, vendas, lojas)


if __name__ == "__main__":
    main()
