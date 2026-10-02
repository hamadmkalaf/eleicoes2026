#!/usr/bin/env python3
"""Renderiza uma peça de sinalização (.dc.html) em JPG de alta resolução e PDF vetorial.

Uso:
    python3 scripts/render_arte.py saidas/artes_sinalizacao/P6-Painel_FimAvenidaB.dc.html \
        --largura-mm 1000 --altura-mm 2000 --escala 16 --qualidade 92

O que faz, na ordem:
1. Extrai o miolo do `.dc.html` (o conteúdo de `<x-dc>`, sem o runtime do tipo Design)
   e grava um `.html` autônomo ao lado, que abre em qualquer navegador.
2. Baixa a Montserrat (Google Fonts) para um cache local e a declara por
   `@font-face`, para que o Chromium headless não caia na fonte substituta.
3. Renderiza com o Chromium do Playwright em `--escala`× (16× → 8000 × 16000 px para
   uma arte de 500 × 1000 px), recorta exatamente a arte (sem margem) e grava o
   JPG na `--qualidade` pedida (ou na que mais se aproxima de `--alvo-mb`, se dado).
4. Imprime o mesmo HTML em PDF na medida física da peça (`--largura-mm` × `--altura-mm`),
   com o texto vetorial e a Montserrat embutida como TrueType (instâncias estáticas
   geradas da fonte variável com o fontTools).

Sem parâmetros, o script trata a arte como 500 × 1000 px e 1000 × 2000 mm.
"""
import argparse
import io
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops

Image.MAX_IMAGE_PIXELS = None  # a arte em 16× passa de 180 Mpx; não é bomba de descompressão

RAIZ = pathlib.Path(__file__).resolve().parents[1]
CACHE_FONTES = RAIZ / "saidas" / "artes_sinalizacao" / ".fontes"  # ao lado do HTML gerado; não versionado
CSS_FONTES = "https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
CANDIDATOS_CHROMIUM = [
    "/opt/pw-browsers/chromium-*/chrome-linux/chrome",
    "chromium", "chromium-browser", "google-chrome", "chrome",
]


def acha_chromium():
    import glob
    for c in CANDIDATOS_CHROMIUM:
        if "*" in c:
            hits = sorted(glob.glob(c))
            if hits:
                return hits[-1]
        elif shutil.which(c):
            return shutil.which(c)
    sys.exit("Chromium não encontrado; instale-o ou ajuste CANDIDATOS_CHROMIUM")


def instancia_estatica(woff2: pathlib.Path, peso: str) -> pathlib.Path:
    """Gera uma instância estática (TTF) do peso pedido a partir da Montserrat variável.

    O Google Fonts serve a Montserrat como fonte variável (eixo wght). O Chromium
    imprime fontes variáveis em PDF como Type3 (contornos, mas sem nome de fonte e
    mal aceitas por alguns RIPs de gráfica); com instâncias estáticas o PDF sai com
    a Montserrat embutida como TrueType (CIDFontType2), que é o que se espera.
    """
    destino = woff2.with_name(woff2.stem + "-static.ttf")
    if destino.exists():
        return destino
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    fonte = TTFont(woff2)
    if "fvar" in fonte:
        try:
            fonte = instancer.instantiateVariableFont(fonte, {"wght": int(peso)}, updateFontNames=True)
        except Exception:  # sem STAT utilizável: instancia sem renomear e corrige o nome à mão
            fonte = instancer.instantiateVariableFont(fonte, {"wght": int(peso)})
        estilo = {"400": "Regular", "500": "Medium", "600": "SemiBold", "700": "Bold", "800": "ExtraBold", "900": "Black"}.get(peso, peso)
        nomes = fonte["name"]
        for rec in nomes.names:
            if rec.nameID in (1, 4, 6):
                rec.string = {1: "Montserrat", 4: f"Montserrat {estilo}", 6: f"Montserrat-{estilo}"}[rec.nameID]
            elif rec.nameID == 2:
                rec.string = estilo
        fonte["OS/2"].usWeightClass = int(peso)
    fonte.flavor = None
    fonte.save(destino)
    return destino


def baixa_fontes():
    """Baixa as faces latin/latin-ext da Montserrat; devolve as regras @font-face locais."""
    CACHE_FONTES.mkdir(parents=True, exist_ok=True)
    css_path = CACHE_FONTES / "montserrat.css"
    if not css_path.exists():
        subprocess.run(["curl", "-sS", "--max-time", "60", "-A", UA, CSS_FONTES, "-o", str(css_path)], check=True)
    css = css_path.read_text()
    regras = []
    vistos = set()
    for subset, corpo in re.findall(r"/\* ([\w-]+) \*/\s*@font-face \{(.*?)\}", css, re.S):
        if subset not in ("latin", "latin-ext"):
            continue
        peso = re.search(r"font-weight: (\d+)", corpo).group(1)
        url = re.search(r"url\((\S+?)\)", corpo).group(1)
        faixa = re.search(r"unicode-range: ([^;]+);", corpo).group(1)
        nome = f"montserrat-{peso}-{subset}.woff2"
        destino = CACHE_FONTES / nome
        if not destino.exists():
            subprocess.run(["curl", "-sS", "--max-time", "60", "-o", str(destino), url], check=True)
        chave = (peso, subset)
        if chave in vistos:
            continue
        vistos.add(chave)
        estatica = instancia_estatica(destino, peso)
        regras.append(
            "@font-face { font-family: 'Montserrat'; font-style: normal; "
            f"font-weight: {peso}; font-display: block; "
            f"src: url('{CACHE_FONTES.name}/{estatica.name}') format('truetype'); unicode-range: {faixa}; }}"
        )
    # O @import fica na frente para quem abrir o HTML numa máquina sem o cache `.fontes/`.
    return f"@import url('{CSS_FONTES}');\n" + "\n".join(regras)


def monta_html(dc_html: str, largura_px: float, altura_px: float, largura_mm: float, altura_mm: float,
               fontes_css: str, titulo: str) -> str:
    miolo = re.search(r"<x-dc>(.*?)</x-dc>", dc_html, re.S).group(1)
    estilo = re.search(r"<helmet>\s*<style>(.*?)</style>\s*</helmet>", miolo, re.S).group(1)
    estilo = re.sub(r"@import[^;]+;", "", estilo).strip()
    raiz = miolo[miolo.index("</helmet>") + len("</helmet>"):].strip()
    fator = (largura_mm / 25.4 * 96) / largura_px  # px CSS por px da arte, para o PDF sair na medida
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>{titulo}</title>
<style>
{fontes_css}
{estilo}
html, body {{ margin: 0; padding: 0; width: {largura_px}px; height: {altura_px}px; overflow: hidden; }}
body {{ -webkit-font-smoothing: antialiased; }}
#arte {{ width: {largura_px}px; height: {altura_px}px; transform-origin: top left; }}
@media print {{
  @page {{ size: {largura_mm}mm {altura_mm}mm; margin: 0; }}
  html, body {{ width: {largura_mm}mm; height: {altura_mm}mm; }}
  #arte {{ transform: scale({fator:.9f}); }}
  * {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
}}
</style>
</head>
<body>
<div id="arte">
{raiz}
</div>
</body>
</html>
"""


def chromium(args, chrome):
    base = [chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
            "--allow-file-access-from-files", "--disable-dev-shm-usage",
            "--run-all-compositor-stages-before-draw", "--virtual-time-budget=8000",
            "--no-first-run", "--no-default-browser-check"]
    subprocess.run(base + args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def jpg_no_alvo(im: Image.Image, alvo_bytes: int, dpi: float):
    """Escolhe a qualidade JPEG cujo tamanho mais se aproxima do alvo (croma 4:4:4)."""
    melhor = None
    for q in range(60, 99):
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=q, subsampling=0, optimize=True, dpi=(dpi, dpi))
        dados = buf.getvalue()
        if melhor is None or abs(len(dados) - alvo_bytes) < abs(len(melhor[1]) - alvo_bytes):
            melhor = (q, dados)
        if len(dados) > alvo_bytes * 1.25:
            break
    return melhor


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dc_html", type=pathlib.Path)
    ap.add_argument("--largura-px", type=float, default=500)
    ap.add_argument("--altura-px", type=float, default=1000)
    ap.add_argument("--largura-mm", type=float, default=1000)
    ap.add_argument("--altura-mm", type=float, default=2000)
    ap.add_argument("--escala", type=int, default=16, help="fator de resolução do JPG (16 → 8000 × 16000 px)")
    ap.add_argument("--alvo-mb", type=float, default=0, help="tamanho de arquivo desejado do JPG, em MB (0 = usar --qualidade)")
    ap.add_argument("--qualidade", type=int, default=92, help="qualidade JPEG fixa, quando --alvo-mb é 0")
    ap.add_argument("--so-pdf", action="store_true", help="regenera só o HTML e o PDF, sem tocar no JPG")
    a = ap.parse_args()

    origem = a.dc_html.resolve()
    if not origem.exists():
        sys.exit(f"não achei {origem}")
    base = origem.with_suffix("").with_suffix("") if origem.name.endswith(".dc.html") else origem.with_suffix("")
    chrome = acha_chromium()

    html = monta_html(origem.read_text(encoding="utf-8"), a.largura_px, a.altura_px, a.largura_mm, a.altura_mm,
                      baixa_fontes(), f"{base.name} · {a.largura_mm:g} × {a.altura_mm:g} mm")
    html_path = base.with_suffix(".html")
    html_path.write_text(html, encoding="utf-8")

    pdf_path = base.with_suffix(".pdf")
    chromium(["--no-pdf-header-footer", f"--print-to-pdf={pdf_path}", html_path.as_uri()], chrome)
    if a.so_pdf:
        print(f"{html_path.relative_to(RAIZ)}  HTML autônomo")
        print(f"{pdf_path.relative_to(RAIZ)}  {a.largura_mm:g} × {a.altura_mm:g} mm · vetorial · {pdf_path.stat().st_size/1024:.0f} KB")
        return

    with tempfile.TemporaryDirectory() as tmp:
        # O `--window-size` do headless novo desconta uma barra invisível (~87 px) da
        # altura útil; renderiza-se maior e recorta-se a arte pelo canto superior esquerdo.
        png = pathlib.Path(tmp) / "render.png"
        chromium([f"--window-size={int(a.largura_px) + 100},{int(a.altura_px) + 200}",
                  f"--force-device-scale-factor={a.escala}", f"--screenshot={png}", html_path.as_uri()], chrome)
        im = Image.open(png).convert("RGB")
        w, h = int(round(a.largura_px * a.escala)), int(round(a.altura_px * a.escala))
        im = im.crop((0, 0, w, h))

    dpi = w / (a.largura_mm / 25.4)
    if a.alvo_mb > 0:
        q, dados = jpg_no_alvo(im, int(a.alvo_mb * 1024 * 1024), dpi)
    else:
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=a.qualidade, subsampling=0, optimize=True, dpi=(dpi, dpi))
        q, dados = a.qualidade, buf.getvalue()
    jpg_path = base.with_suffix(".jpg")
    jpg_path.write_bytes(dados)

    # Conferência: nenhuma coluna ou linha inteiramente branca na borda do JPG.
    j = Image.open(jpg_path).convert("RGB")
    lim = j.point(lambda v: 255 if v >= 250 else 0)
    r, g, b = lim.split()
    branco = ImageChops.multiply(ImageChops.multiply(r, g), b)
    caixa = ImageChops.invert(branco).getbbox()
    if caixa != (0, 0, j.width, j.height):
        sys.exit(f"o JPG ficou com margem branca: conteúdo em {caixa} de {j.size}")

    print(f"{html_path.relative_to(RAIZ)}  HTML autônomo")
    print(f"{jpg_path.relative_to(RAIZ)}  {j.width} × {j.height} px · {len(dados)/1024/1024:.2f} MB · qualidade {q} · {dpi:.0f} dpi na medida final")
    print(f"{pdf_path.relative_to(RAIZ)}  {a.largura_mm:g} × {a.altura_mm:g} mm · vetorial · {pdf_path.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
