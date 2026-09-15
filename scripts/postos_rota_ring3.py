"""Mapa dos postos de voluntario na rota do eleitor e no Ring 3.

Desenho esquematico: a topologia (calcada da Merrion Road -> portao unico ->
caminho interno -> Ring 3 -> portas do Hall 2) esta correta; distancias,
proporcoes e o formato do recinto NAO -- o site map do RDS nao pode ser
obtido nesta sessao. Corrigir a geometria antes de usar como sinalizacao.

Os codigos desenhados sao conferidos contra saidas/postos_voluntarios.json,
para que o mapa nao possa divergir do modelo.

Saida: saidas/postos_rota_ring3.png
"""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent.parent
SAIDAS = BASE / "saidas"
FONTE = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTE_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

L, A = 1560, 1250          # area de desenho
PAINEL = 560               # painel de legenda a direita

FAMILIAS = {
    "porta": ("#0F4C81", "Portão, porta e dosagem de fluxo"),
    "triagem": ("#C2521A", "Triagem, despacho e casos"),
    "fila": ("#1F6F54", "Organização de fila"),
    "apoio": ("#6B3FA0", "Apoio ao eleitor e acessibilidade"),
    "servico": ("#5A6472", "Serviço, saída e enlace"),
}

# (codigo, x, y, familia, rotulo)
POSTOS = [
    ("R2", 215, 1079, "fila", "Fim de fila móvel — placa que anda com a fila"),
    ("R1", 615, 1079, "fila", "Cabeça de fila na calçada — mantém o passeio livre"),
    ("R3", 750, 1048, "porta", "Portão da Merrion Road — 1º contato, documento em mãos"),
    ("R4", 862, 1002, "apoio", "Desvio prioritário — tira o prioritário da fila geral"),
    ("R5", 750, 942, "servico", "Balizamento da curva — 1 posto por bifurcação real"),
    ("R6", 150, 700, "servico", "Rota de saída — separa quem sai de quem entra"),

    ("G1", 430, 903, "fila", "Boca da serpentina — entrada da baia, fila única"),
    ("G2", 700, 830, "triagem", "Triagem móvel 1"),
    ("G3", 500, 755, "triagem", "Triagem móvel 2"),
    ("G4", 800, 680, "triagem", "Triagem móvel 3"),
    ("G5", 450, 530, "triagem", "Triagem móvel 4"),
    ("G6", 1063, 478, "triagem", "Balcão de casos 1"),
    ("G7", 1110, 478, "triagem", "Balcão de casos 2"),
    ("G8", 1157, 478, "triagem", "Balcão de casos 3"),
    ("G9", 560, 370, "porta", "Bifurcação A / B — lê o cartão de cor"),
    ("G10", 1260, 700, "apoio", "Fila prioritária — acesso direto à porta"),
    ("G11", 258, 845, "apoio", "Apoio da espera — água, abrigo, mal-estar"),
    ("G12", 942, 845, "servico", "Enlace com segurança e RDS (inglês)"),
]

SERPENTINA = [
    (430, 830), (930, 830), (930, 755), (270, 755), (270, 680), (930, 680),
    (930, 605), (270, 605), (270, 530), (930, 530), (930, 455), (560, 455),
    (560, 398),
]

NOTAS = [
    "Geometria ESQUEMÁTICA. A sequência rua → portão → Ring 3 → portas",
    "está correta; distâncias, proporções e formato do recinto não —",
    "o site map do RDS não foi obtido. Corrigir antes de virar sinalização.",
    "",
    "A triagem foi movida para dentro da fila (G2–G5). O eleitor espera",
    "de qualquer jeito; usar essa espera para descobrir a seção dele e",
    "entregar o cartão A/B tira a triagem do caminho crítico da porta.",
    "Quem escapar é recuperado no nó de despacho, dentro do Hall 2.",
    "",
    "G6–G8 ficam FORA da fila: quem tem problema sai da serpentina e não",
    "trava os 300 que estão atrás dele.",
    "",
    "Portão único = entrada e saída pelo mesmo ponto. R6 existe só por",
    "causa disso; se o RDS liberar um segundo portão para saída, este",
    "posto some e o risco de contrafluxo com ele.",
    "",
    "O número de baias da serpentina desenhado é ilustrativo. Dimensionar",
    "contra a área real do Ring 3 e o pico de 28,5 eleitores por minuto.",
]


def fonte(tamanho, negrito=False):
    return ImageFont.truetype(FONTE_BOLD if negrito else FONTE, tamanho)


def marcador(d, x, y, codigo, cor, r=19):
    d.ellipse([x - r - 3, y - r - 3, x + r + 3, y + r + 3], fill="white")
    d.ellipse([x - r, y - r, x + r, y + r], fill=cor, outline="white", width=3)
    f = fonte(17 if len(codigo) < 3 else 14, True)
    a, b, c, e = d.textbbox((0, 0), codigo, font=f)
    d.text((x - (c - a) / 2, y - (e - b) / 2 - 1), codigo, font=f, fill="white")


def seta(d, p1, p2, cor, largura=3, tam=13):
    import math
    d.line([p1, p2], fill=cor, width=largura)
    ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    for s in (2.6, -2.6):
        d.line([p2, (p2[0] + tam * math.cos(ang + s),
                     p2[1] + tam * math.sin(ang + s))], fill=cor, width=largura)


def desenha_cenario(d):
    # --- rua e calcada -------------------------------------------------
    d.rectangle([0, 1105, L, A], fill="#DFE3E6")
    d.rectangle([0, 1060, L, 1105], fill="#F2F4F5", outline="#C3C9CD")
    d.text((40, 1148), "MERRION ROAD", font=fonte(26, True), fill="#6A737B")
    d.text((40, 1183), "chegada a pé: DART, ônibus e estacionamento",
           font=fonte(17), fill="#8A9298")

    # muro do recinto, com o portao unico
    for x0, x1 in ((40, 690), (810, 1500)):
        d.line([(x0, 1057), (x1, 1057)], fill="#3A4147", width=7)
    d.text((824, 1068), "PORTÃO ÚNICO", font=fonte(15, True), fill="#3A4147")

    # fila da calcada
    d.rounded_rectangle([185, 1064, 680, 1098], 16, fill="#DCEBE4",
                        outline="#1F6F54", width=2)
    seta(d, (686, 1081), (742, 1068), "#1F6F54", 4)

    # --- caminho interno do portao ate a boca do Ring 3 ----------------
    d.line([(750, 1050), (750, 942), (430, 942), (430, 890)],
           fill="#E4E9ED", width=46, joint="curve")
    d.line([(750, 1050), (750, 942), (430, 942), (430, 890)],
           fill="#B9C3CB", width=2, joint="curve")
    seta(d, (712, 942), (462, 942), "#5A6472", 4)

    # --- rota prioritaria, por fora da area de espera ------------------
    prio = [(880, 1002), (1260, 1002), (1260, 330), (985, 268)]
    d.line(prio, fill="#6B3FA0", width=4, joint="curve")
    seta(d, (1100, 300), (975, 266), "#6B3FA0", 4)
    d.text((1282, 880), "rota prioritária", font=fonte(15, True), fill="#6B3FA0")

    # --- rota de saida, pelo lado oposto ao da entrada -----------------
    d.line([(760, 262), (150, 320), (150, 1008), (700, 1048)],
           fill="#C0392B", width=4, joint="curve")
    seta(d, (300, 1030), (694, 1048), "#C0392B", 4)
    d.text((60, 470), "saída", font=fonte(17, True), fill="#C0392B")

    # --- Ring 3 --------------------------------------------------------
    d.rounded_rectangle([200, 320, 1000, 890], 26, fill="#F7F9F8",
                        outline="#1F6F54", width=3)
    d.text((222, 332), "RING 3", font=fonte(29, True), fill="#1F6F54")
    d.text((222, 370), "área de espera a céu aberto",
           font=fonte(16), fill="#5A7A6C")
    d.text((222, 392), "o pulmão da operação", font=fonte(16), fill="#5A7A6C")
    d.line(SERPENTINA, fill="#BBD4C7", width=26, joint="curve")
    d.line(SERPENTINA, fill="#1F6F54", width=2, joint="curve")
    seta(d, (560, 430), (560, 350), "#1F6F54", 4)

    # balcao de casos, fora da fila
    d.line([(935, 455), (1030, 455)], fill="#C2521A", width=2)
    d.rounded_rectangle([1020, 425, 1200, 520], 12, fill="#FBEDE4",
                        outline="#C2521A", width=3)
    d.text((1030, 433), "Balcão de casos", font=fonte(15, True), fill="#C2521A")
    d.text((1030, 528), "fora da fila", font=fonte(14), fill="#C2521A")

    # --- Hall 2 --------------------------------------------------------
    d.rounded_rectangle([300, 60, 1220, 250], 14, fill="#EEF2F6",
                        outline="#0F4C81", width=3)
    d.text((330, 82), "HALL 2 — SHELBOURNE HALL", font=fonte(29, True),
           fill="#0F4C81")
    d.text((330, 122), "50,2 × 44,5 m · 28 urnas · 18 postos internos",
           font=fonte(18), fill="#41668C")
    d.text((330, 150), "ver o mapa dos postos do Hall 2 (H1–H18)",
           font=fonte(16), fill="#7A93AC")
    for x, rot, cor in ((620, "A", "#17A2B8"), (760, "EXIT", "#2E7D32"),
                        (900, "B", "#8E44AD")):
        d.rectangle([x - 34, 238, x + 34, 262], fill=cor)
        largura = 13 if rot != "EXIT" else 30
        d.text((x - largura, 268), rot, font=fonte(19, True), fill=cor)
    seta(d, (545, 352), (612, 272), "#17A2B8", 5)
    seta(d, (582, 352), (886, 272), "#8E44AD", 5)


def painel(d, postos):
    px = L + 34
    y = 48
    d.line([(L + 8, 40), (L + 8, A - 40)], fill="#C9D1D9", width=2)
    d.text((px, y), "Postos de voluntário", font=fonte(27, True), fill="#111111")
    y += 36
    d.text((px, y), "Zona 1 (rota até o Ring 3) e Zona 2 (Ring 3)",
           font=fonte(16), fill="#444444"); y += 23
    d.text((px, y), f"{len(postos)} postos no pico. Não são pessoas: um posto",
           font=fonte(16), fill="#444444"); y += 21
    d.text((px, y), "pode ter 1 ou 2 voluntários e trocar por turno.",
           font=fonte(16), fill="#444444"); y += 34

    for fam, (cor, titulo) in FAMILIAS.items():
        itens = [(c, r) for c, _, _, f_, r in postos if f_ == fam]
        if not itens:
            continue
        d.ellipse([px, y + 3, px + 15, y + 18], fill=cor)
        d.text((px + 25, y), titulo, font=fonte(16, True), fill=cor); y += 25
        for codigo, rotulo in itens:
            d.text((px + 25, y), f"{codigo}  {rotulo}", font=fonte(14),
                   fill="#222222")
            y += 19
        y += 11

    y += 6
    d.line([(px, y), (px + 490, y)], fill="#C9D1D9", width=2); y += 15
    for linha in NOTAS:
        d.text((px, y), linha, font=fonte(14), fill="#333333"); y += 19


def main() -> None:
    modelo = json.loads((SAIDAS / "postos_voluntarios.json").read_text(
        encoding="utf-8"))
    # Confere os codigos desenhados contra os codigos do modelo.
    esperados = set()
    for r in modelo["postos"]:
        if r["Zona"].startswith("3."):
            continue
        if "-" in r["Codigo"]:
            ini, fim = r["Codigo"].split("-")
            pref = ini[0]
            esperados |= {f"{pref}{n}" for n in range(int(ini[1:]), int(fim[1:]) + 1)}
        else:
            esperados.add(r["Codigo"])
    desenhados = {c for c, *_ in POSTOS}
    if desenhados != esperados:
        raise SystemExit(
            f"mapa fora de sincronia com o modelo: "
            f"so no mapa {sorted(desenhados - esperados)}, "
            f"so no modelo {sorted(esperados - desenhados)}")

    tela = Image.new("RGB", (L + PAINEL, A), "white")
    d = ImageDraw.Draw(tela)
    desenha_cenario(d)
    for codigo, x, y, familia, _ in POSTOS:
        marcador(d, x, y, codigo, FAMILIAS[familia][0])
    painel(d, POSTOS)

    destino = SAIDAS / "postos_rota_ring3.png"
    tela.save(destino)
    print(f"{destino} — {len(POSTOS)} postos, códigos conferidos com o modelo")


if __name__ == "__main__":
    main()
