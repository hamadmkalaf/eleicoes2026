"""Postos de voluntario do posto de votacao de Dublin, Eleicoes 2026.

Conta POSTOS (funcoes a cobrir), nao pessoas. Quantas pessoas ocupam cada
posto e por quantos turnos e decisao de quem recruta.

Le saidas/dados.json, converte eleitorado apto em fluxo esperado por hora e
usa o pico desse fluxo para dimensionar os postos que dependem de vazao
(triagem movel na fila, balcao de casos, orientacao de corredor). Os demais
sao posicionais: existem porque ha um lugar a cobrir.

Tres zonas, na ordem em que o eleitor as atravessa:
  1. Rota   — calcada da Merrion Road, portao unico e caminho interno.
  2. Ring 3 — area de espera a ceu aberto, onde a fila se acumula.
  3. Hall 2 — dentro do salao de votacao.

Os codigos (R1, G2-G5, H5-H13...) sao gerados a partir da ordem e das
quantidades desta lista; os dois desenhos conferem os codigos contra o JSON
gerado aqui, entao modelo, mapa e texto nao podem divergir.

Saida: saidas/postos_voluntarios.json e saidas/postos_voluntarios.md
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SAIDAS = BASE / "saidas"

PREMISSAS = {
    # Taxas de comparecimento de 2022 por domicilio do eleitor.
    "taxa_comparecimento_dublin": 0.74,
    "taxa_comparecimento_interior": 0.50,
    # Curva de chegada ao longo das 9h de votacao. Assumida: nao ha serie
    # historica hora a hora do posto.
    "curva_chegada": {
        "08-09": 0.08, "09-10": 0.12, "10-11": 0.15, "11-12": 0.15,
        "12-13": 0.13, "13-14": 0.11, "14-15": 0.10, "15-16": 0.09,
        "16-17": 0.07,
    },
    # Triagem movel: o voluntario percorre a fila do Ring 3 e resolve o
    # destino do eleitor enquanto ele ja esta esperando.
    "frac_precisa_triagem": 0.60,
    "seg_por_triagem": 20,
    # Eleitores por interacao: gente chega em dupla e em familia, e uma
    # pergunta respondida em voz alta serve ao grupo todo.
    "eleitores_por_interacao": 1.5,
    # Balcao de casos: so o que a triagem movel nao resolve de pe.
    "frac_caso_dificil": 0.03,
    "seg_por_caso_dificil": 120,
    "utilizacao_alvo_balcao": 0.80,
    # Corredor: o desenho do Hall 2 tem 30 posicoes de mesa em 9 blocos
    # geograficos (4+4+2+2+4+4+4+3+3), um posto por bloco.
    "mesas_por_bloco_corredor": 3.5,
    "mesas_no_desenho": 30,
}

# (zona, nome, o que faz, quantidade | "vazao:<chave>")
POSTOS = [
    ("1. Rota", "Cabeca de fila na calcada",
     "Mantem a calcada da Merrion Road transitavel e encaminha quem chega a "
     "pe do DART e do onibus para o portao.", 1),
    ("1. Rota", "Fim de fila movel",
     "Carrega a placa de fim de fila e caminha com ela. Sem esse posto "
     "ninguem sabe onde a fila comeca.", 1),
    ("1. Rota", "Portao da Merrion Road",
     "Primeiro contato: confirma que o eleitor esta no lugar certo e manda "
     "preparar o documento. Dobra de efetivo na abertura.", 1),
    ("1. Rota", "Desvio prioritario no portao",
     "Identifica idoso, PcD, gestante e crianca de colo ja no portao e os "
     "poe na rota curta, antes da fila geral.", 1),
    ("1. Rota", "Balizamento da rota interna",
     "Fica na curva entre o portao e o Ring 3, onde o eleitor tem duvida de "
     "para onde ir. Um posto por bifurcacao do tracado real.", 1),
    ("1. Rota", "Rota de saida",
     "Separa quem sai de quem entra. Contrafluxo num caminho estreito custa "
     "mais fila que qualquer gargalo de mesa.", 1),

    ("2. Ring 3", "Boca da serpentina",
     "Entrada da area de espera: organiza a entrada na primeira baia e "
     "impede que a fila unica se parta em varias.", 1),
    ("2. Ring 3", "Triagem movel na fila",
     "Percorre a serpentina perguntando a secao, entrega o cartao de cor A "
     "ou B e resolve a duvida enquanto o eleitor ja espera. E o posto que "
     "decide se a porta do Hall 2 vira gargalo.", "vazao:triagem"),
    ("2. Ring 3", "Balcao de casos",
     "Mesa fixa fora da fila, com listagem impressa e consulta eletronica, "
     "para o que nao se resolve de pe: titulo, eleitor nao localizado, "
     "transferencia.", "vazao:balcao"),
    ("2. Ring 3", "Bifurcacao A / B",
     "Onde a fila unica vira duas. Le o cartao de cor entregue pela triagem "
     "movel e manda o eleitor para a porta certa.", 1),
    ("2. Ring 3", "Fila prioritaria",
     "Conduz a fila paralela de prioritarios ate a porta, sem passar pela "
     "serpentina.", 1),
    ("2. Ring 3", "Apoio geral da espera",
     "Agua, abrigo de chuva, mal-estar, crianca perdida, WC. O Ring 3 e a "
     "ceu aberto: este e o posto que mais depende do tempo no dia.", 1),
    ("2. Ring 3", "Enlace com seguranca e RDS",
     "Ponto unico de contato com os 20 segurancas contratados e com o staff "
     "do RDS. Requer ingles funcional.", 1),

    ("3. Hall 2", "Porta A — dosagem de entrada",
     "Admite eleitores enquanto houver fila util dentro. Se o salao encher, "
     "a espera fica no Ring 3, que tem espaco.", 1),
    ("3. Hall 2", "Porta B — dosagem de entrada", "Idem, na porta B.", 1),
    ("3. Hall 2", "No de despacho A",
     "No ponto onde as filas se abrem em leque: confirma o destino e "
     "recupera quem chegou sem triagem ou na porta errada.", 1),
    ("3. Hall 2", "No de despacho B", "Idem, no leque da porta B.", 1),
    ("3. Hall 2", "Orientacao de corredor",
     "Um posto por bloco de mesas: organiza a fila curta de cada bloco e "
     "mantem livres os corredores de circulacao.", "vazao:corredor"),
    ("3. Hall 2", "Acessibilidade e fila prioritaria",
     "Recebe a fila prioritaria dentro do salao e acompanha ate a mesa.", 1),
    ("3. Hall 2", "WC — orientacao de ida e volta",
     "Os WC ficam fora do salao, num corredor lateral: sem orientacao, quem "
     "sai para o WC perde o lugar e volta pela porta errada.", 1),
    ("3. Hall 2", "Sala de transmissao",
     "Controle de acesso a area restrita de transmissao de resultados.", 1),
    ("3. Hall 2", "Saida — pos-voto e contrafluxo",
     "Conduz quem votou para fora pela saida central e impede o retorno "
     "contra o fluxo de entrada.", 1),
    ("3. Hall 2", "Posto de comando",
     "Coordenacao do salao, em ponto fixo e visivel. E para ca que o "
     "problema sobe quando o voluntario nao resolve.", 1),
]

PREFIXO = {"1. Rota": "R", "2. Ring 3": "G", "3. Hall 2": "H"}


def teto(x: float) -> int:
    return int(-(-x // 1))


def fluxo_de_pico(dados: dict, p: dict) -> tuple[int, int, float]:
    """Aptos, comparecimento esperado e pico de chegadas por minuto."""
    aptos = esperado = 0
    for reg in dados["residencia_urna"]:
        aptos += reg["TOTAL"]
        for local, qtd in reg.items():
            if local in ("Urna", "TOTAL"):
                continue
            esperado += qtd * (p["taxa_comparecimento_dublin"] if local == "DUBLIN"
                               else p["taxa_comparecimento_interior"])
    pico_hora = esperado * max(p["curva_chegada"].values())
    return aptos, round(esperado), pico_hora / 60


def quantidades_por_vazao(por_min: float, p: dict) -> dict[str, int]:
    """Postos cujo numero sai do fluxo de eleitores, nao da planta."""
    return {
        # A fila anda de qualquer jeito, entao nao se reserva folga de
        # utilizacao: quem escapa da triagem e recuperado no despacho.
        "triagem": teto(
            (por_min * p["frac_precisa_triagem"] / p["eleitores_por_interacao"])
            / (60 / p["seg_por_triagem"])),
        # O balcao tem fila propria, sem valvula de escape: a folga de
        # utilizacao aqui e obrigatoria.
        "balcao": teto(
            (por_min * 60 * p["frac_caso_dificil"] * p["seg_por_caso_dificil"])
            / (3600 * p["utilizacao_alvo_balcao"])),
        "corredor": teto(p["mesas_no_desenho"] / p["mesas_por_bloco_corredor"]),
    }


def numera(postos: list, vazao: dict[str, int]) -> list[dict]:
    """Atribui codigo sequencial por zona, respeitando a ordem da lista."""
    contador: dict[str, int] = {}
    saida = []
    for zona, nome, funcao, qtd in postos:
        if isinstance(qtd, str):
            qtd = vazao[qtd.split(":", 1)[1]]
        pref = PREFIXO[zona]
        inicio = contador.get(pref, 0) + 1
        contador[pref] = inicio + qtd - 1
        codigo = f"{pref}{inicio}" if qtd == 1 else f"{pref}{inicio}-{pref}{inicio + qtd - 1}"
        saida.append({"Codigo": codigo, "Zona": zona, "Posto": nome,
                      "Funcao": funcao, "Postos": qtd})
    return saida


def main() -> None:
    dados = json.loads((SAIDAS / "dados.json").read_text(encoding="utf-8"))
    p = PREMISSAS
    aptos, esperado, por_min = fluxo_de_pico(dados, p)
    vazao = quantidades_por_vazao(por_min, p)
    postos = numera(POSTOS, vazao)

    zonas: dict[str, int] = {}
    for r in postos:
        zonas[r["Zona"]] = zonas.get(r["Zona"], 0) + r["Postos"]
    total = sum(zonas.values())

    (SAIDAS / "postos_voluntarios.json").write_text(json.dumps({
        "premissas": p,
        "aptos": aptos,
        "comparecimento_esperado": esperado,
        "pico_eleitores_por_minuto": round(por_min, 1),
        "quantidades_por_vazao": vazao,
        "postos": postos,
        "postos_por_zona": zonas,
        "total_postos": total,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    L = ["# Postos de voluntario — anexo quantitativo", "",
         "Gerado por `scripts/voluntarios.py`. Conta **postos**, nao pessoas:",
         "um posto pode ser ocupado por uma ou duas pessoas e trocar de",
         "ocupante a cada turno.", "",
         f"Base: {aptos} aptos, comparecimento esperado {esperado}, pico de "
         f"{round(por_min, 1)} eleitores por minuto (10h-12h).", "",
         "| Codigo | Zona | Posto | Postos no pico | O que faz |",
         "|---|---|---|---|---|"]
    for r in postos:
        L.append(f"| {r['Codigo']} | {r['Zona']} | {r['Posto']} | "
                 f"{r['Postos']} | {r['Funcao']} |")
    L += ["", "| Zona | Postos |", "|---|---|"]
    for z, q in sorted(zonas.items()):
        L.append(f"| {z} | {q} |")
    L.append(f"| **Total** | **{total}** |")
    (SAIDAS / "postos_voluntarios.md").write_text("\n".join(L) + "\n",
                                                  encoding="utf-8")

    print(f"Aptos {aptos} | esperado {esperado} | pico {por_min:.1f}/min")
    for r in postos:
        print(f"  {r['Codigo']:9s} {r['Zona']:10s} {r['Posto']}")
    for z, q in sorted(zonas.items()):
        print(f"  {z}: {q} postos")
    print(f"  TOTAL: {total} postos")


if __name__ == "__main__":
    main()
