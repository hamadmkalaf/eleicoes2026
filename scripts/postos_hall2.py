"""Marca os postos de voluntario sobre o desenho de fluxo atual do Hall 2.

Le "PLANO COM FLUXOS MELHORADO.png", desenha um marcador numerado em cada
posto e acrescenta um painel de legenda a direita. Nao altera o desenho
original: as coordenadas de POSTOS foram lidas sobre a imagem e ficam aqui
para serem corrigidas se o desenho mudar.

Saida: saidas/postos_hall2.png
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent.parent
FONTE = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTE_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

FAMILIAS = {
    "porta": ("#0F4C81", "Porta e dosagem de entrada"),
    "despacho": ("#C2521A", "Despacho e confirmação de destino"),
    "corredor": ("#1F6F54", "Orientação de corredor (bloco de mesas)"),
    "apoio": ("#6B3FA0", "Apoio ao eleitor e acessibilidade"),
    "servico": ("#5A6472", "Serviço, saída e coordenação"),
}

# (codigo, x, y, familia, rotulo curto). Coordenadas lidas sobre o desenho
# original de 1536 x 1024 px.
POSTOS = [
    ("H1", 788, 900, "porta", "Porta A — dosagem de entrada"),
    ("H2", 1028, 900, "porta", "Porta B — dosagem de entrada"),
    ("H3", 700, 508, "despacho", "Nó de despacho A"),
    ("H4", 1110, 510, "despacho", "Nó de despacho B"),
    ("H5", 455, 305, "corredor", "Bloco 1 — 4 mesas (parede O, norte)"),
    ("H6", 455, 650, "corredor", "Bloco 2 — 4 mesas (parede O, sul)"),
    ("H7", 600, 845, "corredor", "Bloco 3 — 2 mesas (canto SO)"),
    ("H8", 658, 210, "corredor", "Bloco 4 — 2 mesas (parede N, oeste)"),
    ("H9", 1005, 210, "corredor", "Bloco 5 — 4 mesas (parede N, leste)"),
    ("H10", 1180, 205, "corredor", "Bloco 6 — 4 mesas (parede L, norte)"),
    ("H11", 1180, 450, "corredor", "Bloco 7 — 4 mesas (parede L, centro-N)"),
    ("H12", 1180, 655, "corredor", "Bloco 8 — 3 mesas (parede L, centro-S)"),
    ("H13", 1180, 820, "corredor", "Bloco 9 — 3 mesas (parede L, sul)"),
    ("H14", 320, 470, "apoio", "Acessibilidade e fila prioritária"),
    ("H15", 170, 300, "servico", "WC — orientação de ida e volta"),
    ("H16", 163, 142, "servico", "Sala de transmissão — acesso restrito"),
    ("H17", 895, 900, "servico", "Saída — pós-voto e contrafluxo"),
    ("H18", 430, 480, "servico", "Posto de comando (coordenação)"),
]

NOTAS = [
    "Nenhum voluntário opera dentro da mesa: identificação do eleitor,",
    "caderno de votação e urna são dos mesários nomeados.",
    "",
    "H3 e H4 não são triagem. A triagem acontece antes, na fila do Ring 3",
    "(postos G2–G6): o eleitor chega à porta já sabendo sua mesa. Aqui só",
    "se confirma o destino e se recupera quem escapou da triagem.",
    "",
    "H1 e H2 dosam a entrada: só admitem enquanto houver fila útil dentro.",
    "Se o salão encher, a espera fica no Ring 3, que tem espaço; fila",
    "dentro do salão bloqueia a circulação e o acesso às mesas.",
    "",
    "Não há balcão de casos aqui: o que não se resolve de pé é resolvido",
    "no Ring 3 (G11–G13), antes da porta. Dentro do salão, caso de eleitor",
    "é do presidente da mesa.",
    "",
    "O desenho tem 30 posições de mesa (10 O + 6 N + 14 L); a agregação do",
    "TSE fecha em 28 urnas. Confirmar as 2 posições sobrando — servem de",
    "reserva se uma urna falhar.",
]


def marcador(d, x, y, codigo, cor, r=19):
    d.ellipse([x - r - 3, y - r - 3, x + r + 3, y + r + 3], fill="white")
    d.ellipse([x - r, y - r, x + r, y + r], fill=cor, outline="white", width=3)
    f = ImageFont.truetype(FONTE_BOLD, 17 if len(codigo) < 3 else 15)
    cx, cy, cx2, cy2 = d.textbbox((0, 0), codigo, font=f)
    d.text((x - (cx2 - cx) / 2, y - (cy2 - cy) / 2 - 1), codigo, font=f, fill="white")


def main() -> None:
    base = Image.open(BASE / "PLANO COM FLUXOS MELHORADO.png").convert("RGB")
    larg_painel = 560
    altura = base.height + 130  # folga para o painel de notas
    tela = Image.new("RGB", (base.width + larg_painel, altura), "white")
    tela.paste(base, (0, 0))
    d = ImageDraw.Draw(tela)

    for codigo, x, y, familia, _ in POSTOS:
        marcador(d, x, y, codigo, FAMILIAS[familia][0])

    px = base.width + 34
    f_tit = ImageFont.truetype(FONTE_BOLD, 27)
    f_sub = ImageFont.truetype(FONTE, 16)
    f_fam = ImageFont.truetype(FONTE_BOLD, 16)
    f_item = ImageFont.truetype(FONTE, 15)
    f_nota = ImageFont.truetype(FONTE, 14)

    d.line([(base.width + 8, 40), (base.width + 8, altura - 40)],
           fill="#C9D1D9", width=2)
    y = 48
    d.text((px, y), "Postos de voluntário", font=f_tit, fill="#111111"); y += 36
    d.text((px, y), "Hall 2 — RDS Shelbourne Hall (50,2 × 44,5 m)",
           font=f_sub, fill="#444444"); y += 24
    d.text((px, y), f"{len(POSTOS)} postos no pico. Não são pessoas: um posto",
           font=f_sub, fill="#444444"); y += 21
    d.text((px, y), "pode ter 1 ou 2 voluntários e trocar por turno.",
           font=f_sub, fill="#444444"); y += 36

    for fam, (cor, titulo) in FAMILIAS.items():
        itens = [(c, r) for c, _, _, f_, r in POSTOS if f_ == fam]
        d.ellipse([px, y + 3, px + 15, y + 18], fill=cor)
        d.text((px + 25, y), titulo, font=f_fam, fill=cor); y += 25
        for codigo, rotulo in itens:
            d.text((px + 25, y), f"{codigo}  {rotulo}", font=f_item, fill="#222222")
            y += 20
        y += 12

    y += 8
    d.line([(px, y), (px + 490, y)], fill="#C9D1D9", width=2); y += 16
    for linha in NOTAS:
        d.text((px, y), linha, font=f_nota, fill="#333333"); y += 19

    destino = BASE / "saidas" / "postos_hall2.png"
    tela.save(destino)
    print(f"{destino} — {len(POSTOS)} postos marcados")


if __name__ == "__main__":
    main()
