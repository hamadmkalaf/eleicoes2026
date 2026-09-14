"""Dimensionamento e alocacao da equipe de voluntarios (apoio logistico) do
posto de votacao de Dublin, Eleicoes 2026.

Le saidas/dados.json (produzido por mapa_agregacoes.py) e converte eleitorado
apto em fluxo esperado por hora; de cada hora deriva a equipe simultanea
necessaria por funcao; das horas deriva a escala de turnos e o total de
pessoas a recrutar.

Produz saidas/dimensionamento_voluntarios.json e .md. O plano narrativo
que consome esses numeros e o plano_voluntarios.md na raiz do repositorio.

Premissas explicitas ficam todas em PREMISSAS -- nenhuma delas e dado do TSE.
Mudar um numero la e recalcular e o modo de testar sensibilidade.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SAIDAS = BASE / "saidas"

# Variacoes de premissa testadas para mostrar a que o numero e sensivel.
CENARIOS = {
    "Enxuto": {
        "frac_precisa_triagem": 0.40, "seg_por_triagem": 15,
        "urnas_por_orientador_corredor": 6, "urnas_por_runner": 14,
        "frac_precisa_consulta": 0.05,
    },
    "Base": {},
    "Reforcado": {
        "frac_precisa_triagem": 0.75, "seg_por_triagem": 25,
        "urnas_por_orientador_corredor": 3, "urnas_por_runner": 5,
        "frac_precisa_consulta": 0.12,
    },
}

PREMISSAS = {
    # Taxas de comparecimento de 2022 por domicilio do eleitor (contexto_*.md).
    "taxa_comparecimento_dublin": 0.74,
    "taxa_comparecimento_interior": 0.50,
    # Curva de chegada ao longo das 9h de votacao. Assumida: nao ha serie
    # historica hora a hora do posto. Pico no meio da manha, cauda a tarde.
    "curva_chegada": {
        "08-09": 0.08, "09-10": 0.12, "10-11": 0.15, "11-12": 0.15,
        "12-13": 0.13, "13-14": 0.11, "14-15": 0.10, "15-16": 0.09,
        "16-17": 0.07,
    },
    # Triagem na entrada: fracao que precisa de interacao falada (o resto
    # segue sinalizacao por conta propria) e duracao dessa interacao.
    "frac_precisa_triagem": 0.60,
    "seg_por_triagem": 20,
    # Balcao de consulta: eleitor sem seção identificada, titulo, duvida.
    "frac_precisa_consulta": 0.08,
    "seg_por_consulta": 90,
    # Utilizacao alvo de um posto de atendimento. Acima disso a fila explode.
    "utilizacao_alvo": 0.80,
    # Cobertura de fila: 1 orientador por N eleitores em fila visivel.
    "eleitores_por_orientador_fila": 60,
    # Fila acumulada antes da abertura: fracao do fluxo da 1a hora que ja
    # esta na calcada as 08h00 (comportamento observado em posto no exterior:
    # eleitor chega cedo para "resolver" o voto). Assumida.
    "frac_fila_na_abertura": 0.45,
    # Corredor interno: 1 orientador por N urnas.
    "urnas_por_orientador_corredor": 3.5,
    # Prioritarios (idoso, PcD, gestante, crianca de colo) sobre o fluxo.
    "frac_prioritarios": 0.10,
    "prioritarios_por_apoio_hora": 60,
    # Runner de apoio aos mesarios: 1 por N urnas.
    "urnas_por_runner": 7,
    # Postos fixos independentes de fluxo.
    "fixos_saida": 2,
    "fixos_coordenacao": 3,
    # Reserva para pausas, atrasos e substituicao.
    "margem_reserva": 0.15,
    # Absenteismo de voluntario entre confirmacao e comparecimento.
    "absenteismo_recrutamento": 0.25,
}

# Dois turnos longos que cobrem o dia inteiro, mais um bloco curto de reforco
# so no pico. Turnos que se sobrepoem somam cobertura na hora sobreposta.
TURNOS = {
    "T1 Manha (07h00-13h30)": ["08-09", "09-10", "10-11", "11-12", "12-13"],
    "T2 Tarde (12h30-encerramento)": ["12-13", "13-14", "14-15", "15-16", "16-17"],
    "T3 Reforco de pico (09h30-14h00)": ["10-11", "11-12", "12-13", "13-14"],
}

def teto(x: float) -> int:
    return int(-(-x // 1))


def comparecimento_por_urna(dados: dict, p: dict = None) -> list[dict]:
    """Converte aptos por urna em comparecimento esperado, ponderado pelo
    domicilio do eleitor (Dublin vs. interior)."""
    p = p or PREMISSAS
    td = p["taxa_comparecimento_dublin"]
    ti = p["taxa_comparecimento_interior"]
    linhas = []
    for reg in dados["residencia_urna"]:
        esperado = 0.0
        for local, qtd in reg.items():
            if local in ("Urna", "TOTAL"):
                continue
            esperado += qtd * (td if local == "DUBLIN" else ti)
        linhas.append({
            "Urna": reg["Urna"],
            "Aptos": reg["TOTAL"],
            "Comparecimento_esperado": round(esperado),
        })
    linhas.sort(key=lambda r: -r["Comparecimento_esperado"])
    return linhas


def equipe_da_hora(fluxo_hora: float, n_urnas: int, fila_inicial: float = 0.0,
                   p: dict = None) -> dict:
    """Equipe simultanea necessaria numa hora com o fluxo dado."""
    p = p or PREMISSAS
    por_min = fluxo_hora / 60

    triagem = (por_min * p["frac_precisa_triagem"]) / (
        (60 / p["seg_por_triagem"]) * p["utilizacao_alvo"])
    consulta = (fluxo_hora * p["frac_precisa_consulta"] * p["seg_por_consulta"]) / (
        3600 * p["utilizacao_alvo"])
    # Fila externa: acumulo de ~4 min de chegadas, mais a fila que ja existe
    # na calcada quando a hora comeca (relevante so na abertura).
    fila = (por_min * 4 + fila_inicial) / p["eleitores_por_orientador_fila"]
    corredor = n_urnas / p["urnas_por_orientador_corredor"]
    prioritarios = (fluxo_hora * p["frac_prioritarios"]) / p["prioritarios_por_apoio_hora"]
    runners = n_urnas / p["urnas_por_runner"]

    linha = {
        "Fila externa e recepcao": max(2, teto(fila)),
        "Triagem nas entradas A e B": max(2, teto(triagem)),
        "Balcao de consulta e casos": max(2, teto(consulta)),
        "Orientacao de corredor": teto(corredor),
        "Atendimento prioritario": max(2, teto(prioritarios)),
        "Apoio as mesas (runner)": teto(runners),
        "Saida e pos-voto": p["fixos_saida"],
        "Coordenacao": p["fixos_coordenacao"],
    }
    linha["Subtotal"] = sum(linha.values())
    linha["Reserva"] = teto(linha["Subtotal"] * p["margem_reserva"])
    linha["Total"] = linha["Subtotal"] + linha["Reserva"]
    return linha


def clusters_de_corredor(urnas: list[dict], n_clusters: int) -> list[dict]:
    """Divide as urnas em clusters de corredor equilibrados por comparecimento
    (distribuicao em serpentina sobre a lista ordenada) e reparte os clusters
    entre as entradas A e B minimizando a diferenca de carga."""
    grupos = [[] for _ in range(n_clusters)]
    for i, u in enumerate(urnas):  # urnas ja vem ordenada por comparecimento
        volta = i // n_clusters
        idx = i % n_clusters if volta % 2 == 0 else n_clusters - 1 - (i % n_clusters)
        grupos[idx].append(u)

    carga = [sum(u["Comparecimento_esperado"] for u in g) for g in grupos]
    # Reparticao A/B: testa todas as combinacoes e fica com a mais equilibrada.
    melhor, dif_min = None, None
    total = sum(carga)
    for mascara in range(1 << n_clusters):
        a = sum(carga[i] for i in range(n_clusters) if mascara >> i & 1)
        n_a = sum(1 for i in range(n_clusters) if mascara >> i & 1)
        # Entradas simetricas: metade dos clusters em cada uma.
        if n_a != n_clusters // 2:
            continue
        dif = abs(2 * a - total)
        if dif_min is None or dif < dif_min:
            melhor, dif_min = mascara, dif

    return [{
        "Cluster": f"C{i + 1}",
        "Entrada": "A" if melhor >> i & 1 else "B",
        "Urnas": [u["Urna"] for u in g],
        "Comparecimento_esperado": carga[i],
    } for i, g in enumerate(grupos)]


def roda(dados: dict, override: dict | None = None) -> dict:
    """Roda o modelo inteiro com as premissas, aplicando override por cima."""
    p = dict(PREMISSAS)
    p.update(override or {})
    n_urnas = dados["total_urnas"]

    urnas = comparecimento_por_urna(dados, p)
    aptos = sum(u["Aptos"] for u in urnas)
    esperado = sum(u["Comparecimento_esperado"] for u in urnas)

    horas = {}
    for faixa, peso in p["curva_chegada"].items():
        fluxo = esperado * peso
        fila_inicial = fluxo * p["frac_fila_na_abertura"] if faixa == "08-09" else 0.0
        horas[faixa] = {
            "Fluxo_esperado": round(fluxo),
            "Eleitores_por_minuto": round(fluxo / 60, 1),
            "Fila_na_abertura": round(fila_inicial),
            "Equipe": equipe_da_hora(fluxo, n_urnas, fila_inicial, p),
        }

    funcoes = list(next(iter(horas.values()))["Equipe"].keys())
    pico = {f: max(h["Equipe"][f] for h in horas.values()) for f in funcoes}

    exigencia = {f: horas[f]["Equipe"]["Total"] for f in horas}
    nomes = list(TURNOS)
    limite = max(exigencia.values()) + 1
    melhor = None
    for a in range(limite):
        for b in range(limite):
            for c in range(limite):
                alocacao = dict(zip(nomes, (a, b, c)))
                if any(
                    sum(n for t, n in alocacao.items() if faixa in TURNOS[t]) < preciso
                    for faixa, preciso in exigencia.items()
                ):
                    continue
                if melhor is None or a + b + c < sum(melhor.values()):
                    melhor = alocacao
    pessoas = sum(melhor.values())
    clusters = clusters_de_corredor(urnas, pico["Orientacao de corredor"])

    return {
        "clusters": clusters,
        "premissas": p,
        "aptos": aptos,
        "comparecimento_esperado": esperado,
        "urnas": n_urnas,
        "urnas_detalhe": urnas,
        "horas": horas,
        "pico_por_funcao": pico,
        "equipe_simultanea_pico": max(exigencia.values()),
        "exigencia_por_hora": exigencia,
        "escala_turnos": melhor,
        "pessoas_distintas_dia": pessoas,
        "voluntarios_a_recrutar": teto(pessoas / (1 - p["absenteismo_recrutamento"])),
    }


def markdown(base: dict, cenarios: dict[str, dict]) -> str:
    """Tabelas do dimensionamento, para anexar ao plano."""
    L = ["# Dimensionamento de voluntarios — anexo quantitativo",
         "",
         "Gerado por `scripts/voluntarios.py`. Todas as premissas estao no",
         "dicionario `PREMISSAS` do script; mudar um valor e rodar de novo",
         "refaz este anexo.",
         "",
         f"Base: **{base['aptos']} aptos**, **{base['urnas']} urnas**, "
         f"comparecimento esperado **{base['comparecimento_esperado']}** "
         f"({base['comparecimento_esperado'] / base['aptos']:.0%}).",
         "",
         "## Fluxo e equipe necessaria, hora a hora",
         "",
         "| Hora | Eleitores | Por minuto | Fila ext. | Triagem | Consulta | "
         "Corredor | Prioritario | Runner | Saida | Coord. | Reserva | **Total** |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    ordem = ["Fila externa e recepcao", "Triagem nas entradas A e B",
             "Balcao de consulta e casos", "Orientacao de corredor",
             "Atendimento prioritario", "Apoio as mesas (runner)",
             "Saida e pos-voto", "Coordenacao", "Reserva"]
    for faixa, h in base["horas"].items():
        e = h["Equipe"]
        cels = " | ".join(str(e[f]) for f in ordem)
        L.append(f"| {faixa} | {h['Fluxo_esperado']} | "
                 f"{h['Eleitores_por_minuto']} | {cels} | **{e['Total']}** |")
    L += ["",
          f"Pico de equipe simultanea: **{base['equipe_simultanea_pico']} pessoas** "
          f"(entre 10h e 12h).",
          "",
          "## Escala de turnos",
          "",
          "| Turno | Pessoas |", "|---|---|"]
    for t, n in base["escala_turnos"].items():
        L.append(f"| {t} | {n} |")
    L += [f"| **Pessoas distintas no dia** | **{base['pessoas_distintas_dia']}** |",
          f"| **A recrutar** (absenteismo de "
          f"{base['premissas']['absenteismo_recrutamento']:.0%}) | "
          f"**{base['voluntarios_a_recrutar']}** |",
          "",
          "## Sensibilidade",
          "",
          "| Cenario | Pico simultaneo | Pessoas no dia | A recrutar |",
          "|---|---|---|---|"]
    for nome, r in cenarios.items():
        L.append(f"| {nome} | {r['equipe_simultanea_pico']} | "
                 f"{r['pessoas_distintas_dia']} | {r['voluntarios_a_recrutar']} |")
    L += ["",
          "## Alocacao fisica: clusters de corredor e entradas",
          "",
          "Um orientador de corredor por cluster. A reparticao entre as",
          "entradas A e B equilibra o comparecimento esperado, nao a",
          "contagem de urnas.",
          "",
          "| Cluster | Entrada | Urnas | Comparecimento esperado |",
          "|---|---|---|---|"]
    for c in base["clusters"]:
        L.append(f"| {c['Cluster']} | {c['Entrada']} | "
                 f"{', '.join(str(u) for u in c['Urnas'])} | "
                 f"{c['Comparecimento_esperado']} |")
    for entrada in ("A", "B"):
        sel = [c for c in base["clusters"] if c["Entrada"] == entrada]
        L.append(f"| **Entrada {entrada}** | | "
                 f"**{sum(len(c['Urnas']) for c in sel)} urnas** | "
                 f"**{sum(c['Comparecimento_esperado'] for c in sel)}** |")
    L += ["",
          "## Comparecimento esperado por urna",
          "",
          "| Urna | Aptos | Comparecimento esperado |", "|---|---|---|"]
    for u in base["urnas_detalhe"]:
        L.append(f"| {u['Urna']} | {u['Aptos']} | {u['Comparecimento_esperado']} |")
    return "\n".join(L) + "\n"


def main() -> None:
    dados = json.loads((SAIDAS / "dados.json").read_text(encoding="utf-8"))
    cenarios = {nome: roda(dados, ov) for nome, ov in CENARIOS.items()}
    base = cenarios["Base"]

    (SAIDAS / "dimensionamento_voluntarios.json").write_text(
        json.dumps({"base": base,
                    "cenarios": {n: {k: v for k, v in r.items()
                                     if k not in ("urnas_detalhe", "horas",
                                                  "clusters")}
                                 for n, r in cenarios.items()}},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    (SAIDAS / "dimensionamento_voluntarios.md").write_text(
        markdown(base, cenarios), encoding="utf-8")

    print(f"Aptos {base['aptos']} | comparecimento esperado "
          f"{base['comparecimento_esperado']} | urnas {base['urnas']}")
    print(f"Pico de fluxo: {max(h['Fluxo_esperado'] for h in base['horas'].values())}/h")
    for nome, r in cenarios.items():
        print(f"  {nome:11s} pico {r['equipe_simultanea_pico']:3d} | "
              f"dia {r['pessoas_distintas_dia']:3d} | "
              f"recrutar {r['voluntarios_a_recrutar']:3d}")
    print("Escala (cenario base):")
    for t, n in base["escala_turnos"].items():
        print(f"  {t}: {n}")
    print("Pico por funcao (cenario base):")
    for f, n in base["pico_por_funcao"].items():
        if f not in ("Subtotal", "Total"):
            print(f"  {f}: {n}")


if __name__ == "__main__":
    main()
