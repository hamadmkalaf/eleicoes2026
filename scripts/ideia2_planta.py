"""Desenha a planta da ideia 2 a partir de saidas/ideia2_dados.json.

Mesma escala, mesma paleta e mesmas primitivas da planta da ideia 1 — as duas
precisam ser lidas lado a lado, e um desenho que muda de linguagem no meio da
comparacao atrapalha em vez de ajudar.

A diferenca de conteudo esta no modulo: aqui ele fica de fundo para a parede,
com a tela da urna voltada para ela. O eleitor digita de costas para o salao.
"""
import json
import math
import os

from ideia1_planta import (AMBAR, AZUL, COR, EST, H, ML, MODULO, MESA, MR, MT,
                           S, URNA, VERDE, VERM, W, esc, par, ponta, px, rect,
                           rota, txt)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MB = 210          # margem inferior, para a legenda

# Vetor unitario que aponta da parede para dentro do salao.
PARA_DENTRO = {"norte": (0, -1), "oeste": (1, 0), "leste": (-1, 0)}


def modulo(m):
    """Mesa dos mesarios com a urna atras dela, contra a parede.

    Em linha, e nao lado a lado: a urna fica na metade do modulo colada na
    parede e a mesa dos mesarios na metade voltada para a fila. O tra&ccedil;o
    vermelho marca a face bloqueada — a face para onde a tela aponta, que nesta
    ideia e a propria parede do salao.
    """
    x0, y0, x1, y1 = m["modulo"]
    dx, dy = PARA_DENTRO[m["parede"]]
    o = [rect(x0, y0, x1, y1, fill=MODULO)]

    if dy:                                    # parede norte: dentro e para o sul
        mesa = (x0 + 0.2, y0 + 0.15, x1 - 0.2, y0 + 0.90)
        urna = ((x0 + x1) / 2, y1 - 0.75)
        painel = ((x0, y1 - 0.09), (x1, y1 - 0.09))
    elif dx > 0:                              # parede oeste: dentro e para leste
        mesa = (x1 - 0.90, y0 + 0.2, x1 - 0.15, y1 - 0.2)
        urna = (x0 + 0.75, (y0 + y1) / 2)
        painel = ((x0 + 0.09, y0), (x0 + 0.09, y1))
    else:                                     # parede leste: dentro e para oeste
        mesa = (x0 + 0.15, y0 + 0.2, x0 + 0.90, y1 - 0.2)
        urna = (x1 - 0.75, (y0 + y1) / 2)
        painel = ((x1 - 0.09, y0), (x1 - 0.09, y1))

    o.append(rect(*mesa, fill=MESA))
    cx, cy = px(*urna)
    o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.42 * S:.1f}" fill="{URNA}"/>')
    a, b = px(*painel[0]), px(*painel[1])
    o.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
             f'y2="{b[1]:.1f}" stroke="{VERM}" stroke-width="2.6"/>')
    return "".join(o)


def rotulo_da_baia(m):
    """Codigo da urna e eleitores esperados, dentro da baia quando ela cabe."""
    x0, y0, x1, y1 = m["baia"]
    claro = m["classe"] in ("alta", "critica")
    if m["parede"] == "norte":
        return par((x0 + x1) / 2, y1 - 1.05, m["urna"], m["esperado"], claro)
    # Nas paredes laterais a baia e rasa, mas larga o bastante para o rotulo.
    return par((x0 + x1) / 2, (y0 + y1) / 2 - 0.15, m["urna"], m["esperado"], claro)


def main():
    d = json.load(open(os.path.join(RAIZ, "saidas", "ideia2_dados.json"),
                       encoding="utf-8"))
    esp = d["espinha_saida"]
    faixas = d["faixas"]
    LG, AL = ML + W * S + MR, MT + H * S + MB
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LG:.0f} {AL:.0f}" '
         f'width="{LG:.0f}" height="{AL:.0f}" role="img" aria-label="Planta da '
         f'ideia 2: as 28 mesas receptoras encostadas nas paredes do Hall 2">',
         f'<rect x="0" y="0" width="{LG}" height="{AL}" fill="#fbfaf7"/>']

    # ---------- zonas de atendimento
    o.append(rect(0, 0, esp["x0"], H, fill=AZUL, opacity=".045"))
    o.append(rect(esp["x1"], 0, W, H, fill=AMBAR, opacity=".04"))
    o.append(rect(0, 0, 7.8, 7.0, fill="#fbfaf7"))

    poly = [(7.8, 0), (W, 0), (W, H), (0, H), (0, 7.0), (7.8, 7.0)]
    pts = " ".join(f"{px(x, y)[0]:.1f},{px(x, y)[1]:.1f}" for x, y in poly)
    o.append(f'<polygon points="{pts}" fill="none" stroke="#1c2733" stroke-width="3.4"/>')

    # ---------- envelopes de recuo das saidas de emergencia
    for lado, lista in d["portas"].items():
        r = d["recuo"].get(lado, 0.6)
        for nome, a, b in lista:
            if "carga" in nome or "Hall 1" in nome:
                continue
            if lado == "norte":
                z = (a - r, H - r, b + r, H)
            elif lado == "sul":
                z = (a - r, 0, b + r, r)
            elif lado == "oeste":
                z = (0, a - r, r, b + r)
            else:
                z = (W - r, a - r, W, b + r)
            o.append(rect(*z, fill=VERDE, opacity=".07", stroke=VERDE,
                          stroke_width="0.9", stroke_dasharray="3 3"))

    # ---------- baias e modulos
    for m in d["mrvs"]:
        o.append(rect(*m["baia"], fill=COR[m["classe"]], opacity=".85",
                      stroke="#6b7480", stroke_width="1", stroke_dasharray="4 3"))
        o.append(modulo(m))
        o.append(rotulo_da_baia(m))

    # ---------- circulacao
    # Avenida de entrada e corredor de retorno correm em faixas paralelas e
    # adjacentes entre a boca das baias e o miolo; so se encontram na espinha.
    def meio(parede, faixa):
        a, b = faixas[parede][faixa]
        d_ = (a + b) / 2
        return H - d_ if parede == "norte" else (d_ if parede == "oeste" else W - d_)

    av_o, rt_o = meio("oeste", "avenida"), meio("oeste", "retorno")
    av_l, rt_l = meio("leste", "avenida"), meio("leste", "retorno")
    av_n, rt_n = meio("norte", "avenida"), meio("norte", "retorno")
    ea, eb = d["entradas"]["A"][0], d["entradas"]["B"][0]
    exo = (esp["x0"] + esp["x1"]) / 2

    o.append(rota([(ea, 1.8), (ea, 8.0), (av_o, 9.5), (av_o, av_n),
                   (esp["x0"] - 1.5, av_n)], AZUL, 3.0))
    o.append(rota([(eb, 1.8), (eb, 4.0), (av_l, 6.0), (av_l, av_n),
                   (esp["x1"] + 1.5, av_n)], AZUL, 3.0))
    o.append(rota([(10.0, rt_n), (esp["x0"] - 0.6, rt_n)], AMBAR, 2.4, ".15"))
    o.append(rota([(44.0, rt_n), (esp["x1"] + 0.6, rt_n)], AMBAR, 2.4, ".15"))
    o.append(rota([(rt_o, rt_n - 1.5), (rt_o, 8.0), (12.0, 4.5),
                   (esp["x0"] - 0.4, 4.5)], AMBAR, 2.4, ".15"))
    o.append(rota([(rt_l, rt_n - 1.5), (rt_l, 4.5),
                   (esp["x1"] + 0.4, 4.5)], AMBAR, 2.4, ".15"))
    o.append(rota([(exo, esp["y1"] - 0.5), (exo, 1.6)], AMBAR, 5.0, ".18"))

    o.append(txt(av_o, 21.0, "AVENIDA A", "via", rot=-90))
    o.append(txt(av_l, 21.0, "AVENIDA B", "via", rot=-90))
    o.append(txt(exo, 18.0, "ESPINHA DE SAÍDA", "via", rot=-90))
    o.append(txt(14.5, rt_n - 0.9, "retorno da parede norte", "via"))
    # Nos vaos das portas laterais, onde nao ha baia para atrapalhar.
    o.append(txt(rt_o, 20.9, "RETORNO A", "via", rot=-90))
    o.append(txt(rt_l, 28.0, "RETORNO B", "via", rot=-90))
    o.append(txt(14.5, av_n + 1.1, "avenida da parede norte", "via"))

    # ---------- portas da fachada sul
    for nome, a, b in d["portas"]["sul"]:
        papel = ("ENTRADA A" if a == d["portas"]["sul"][0][1] else
                 "ENTRADA B" if "carga" in nome else
                 "SAÍDA" if nome == "2.4" else nome)
        o.append(txt((a + b) / 2, -1.5, papel, "prt" if papel.isupper() else "sub"))
    o.append(txt(W / 2, -3.2, "FACHADA SUL — duas entradas nas pontas, saída no meio",
                 "via"))

    # ---------- setor reforcado
    setor = [m for m in d["mrvs"] if m["zona"] == "setor"]
    if setor:
        x0 = min(m["baia"][0] for m in setor) - 0.4
        x1 = max(m["baia"][2] for m in setor) + 0.4
        y0 = min(m["baia"][1] for m in setor) - 0.4
        o.append(rect(x0, y0, x1, H, fill="none", stroke=VERM, stroke_width="2",
                      stroke_dasharray="6 4"))
        o.append(txt((x0 + x1) / 2, y0 - 2.6,
                     "SETOR REFORÇADO · 4 mesários · 45 s", "prt"))

    o.append(txt(0.0, H + 3.0, "IDEIA 2 — as 28 MRVs nas paredes", "tit",
                 anchor="start"))

    # ---------- legenda
    ly, cx = MT + H * S + 96, ML
    itens = [(COR["leve"], "urna leve", False), (COR["media"], "média", False),
             (COR["alta"], "alta", False), (COR["critica"], "crítica", True),
             (AZUL, "avenida de entrada", False),
             (AMBAR, "corredor de retorno e espinha de saída", False),
             (VERDE, "recuo de 3 m das saídas 2.16–2.23", False),
             (MODULO, "módulo em linha (1,80 × 2,60 m)", True),
             (VERM, "face bloqueada: a tela da urna aponta para a parede", True)]
    for i, (c, lab, cheio) in enumerate(itens):
        if i in (4, 7):
            cx, ly = ML, ly + 20
        o.append(f'<rect x="{cx}" y="{ly - 8}" width="11" height="11" fill="{c}" '
                 f'opacity="{1 if cheio else .45}" stroke="{c}"/>')
        o.append(f'<text x="{cx + 16}" y="{ly + 1}" {EST["lbl"]}>{esc(lab)}</text>')
        cx += 24 + len(lab) * 5.3
    for i, linha in enumerate((
            "Em cada baia: código da urna (acima) e eleitores esperados (abaixo). "
            "O módulo tem o fundo na parede e a tela voltada para ela.",
            "O eleitor chega pela avenida, entra na baia, vota de costas para o "
            "salão e volta pelo corredor de retorno, que corre colado à boca das",
            "baias até a espinha central. As baias mais rasas são as das urnas "
            "sem fila; a profundidade de cada uma sai da fila de pico da sua urna.")):
        o.append(f'<text x="{ML}" y="{ly + 26 + i * 14}" {EST["sub"]}>'
                 f'{esc(linha)}</text>')
    o.append("</svg>")

    cam = os.path.join(RAIZ, "saidas", "ideia2_planta.svg")
    open(cam, "w", encoding="utf-8").write("\n".join(o))
    print("gravado", cam, os.path.getsize(cam), "bytes")


if __name__ == "__main__":
    main()
