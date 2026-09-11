"""Modelo de fila por urna para a votacao de Dublin em 04/10/2026.

Configuracao fixada pelo TRE (negociacao encerrada): 28 urnas, 28 mesas
receptoras (1:1), 51 secoes, 16.794 aptos, janela 8h-17h no RDS Hall 2.

O modelo responde a duas perguntas distintas, que tem solucoes diferentes:

  - HORARIO DE FECHAMENTO: e problema de vazao pura. Depende so do ciclo por
    eleitor. Nenhuma gestao de fila o altera.
  - TAMANHO DA FILA: e problema de curva de chegada. Depende do perfil horario
    e da organizacao fisica, e e o que dimensiona o Ring 3.

Premissas explicitas (todas ajustaveis no topo do arquivo):
  - comparecimento esperado pela base B, taxa de 2022 por domicilio de origem
    (scripts/comparecimento.py; decisao do Posto de 06/09/2026);
  - perfil horario de chegada com pico de manha (premissa, nao medida);
  - eleitor no exterior vota SO para Presidente, entao o ato de votar e curto e
    a identificacao no caderno domina o ciclo.

Uso:  python3 scripts/simula_fluxo.py
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import comparecimento as CP                                   # noqa: E402

# --- premissas -------------------------------------------------------------

# Fracao das chegadas em cada hora, das 8h as 17h.
PERFIL_CENTRAL = [.12, .15, .16, .15, .12, .09, .08, .07, .06]
PERFIL_AGUDO = [.14, .18, .20, .16, .11, .07, .06, .05, .03]

JANELA_MIN = 9 * 60


def carrega_urnas():
    """Devolve [(urna, comparecimento_esperado, qtd_secoes)] ordenado por carga."""
    dados = CP.carrega_dados()
    esperados = {e["urna"]: e["esperado"] for e in CP.por_urna(dados)}
    urnas = [(u["Urna"], float(esperados[u["Urna"]]), u["Qtd_secoes"])
             for u in dados["urnas"]]
    return sorted(urnas, key=lambda x: -x[1])


def ciclo(arranjo, t_id, t_voto, qtd_secoes):
    """Segundos por eleitor conforme o arranjo fisico da mesa receptora.

    t_id   busca no caderno + conferencia do documento + assinatura
    t_voto liberacao no terminal + deslocamento + voto (so Presidente)

    serial    fila unica; identificacao e voto acontecem em sequencia
    pipeline  identifica o proximo enquanto o anterior esta na urna
    paralelo  um caderno por secao, dois mesarios identificando ao mesmo tempo
              (so possivel nas 23 urnas que acumulam duas secoes)
    """
    if arranjo == "serial":
        return t_id + t_voto
    if arranjo == "pipeline":
        return max(t_id, t_voto)
    if arranjo == "paralelo":
        postos = 2 if qtd_secoes == 2 else 1
        return max(t_id / postos, t_voto)
    raise ValueError(f"arranjo desconhecido: {arranjo}")


def simula(arranjo, t_id, t_voto, perfil=PERFIL_CENTRAL, escala=1.0):
    """Fila hora a hora por urna. Devolve resumo agregado do sistema."""
    urnas = carrega_urnas()
    fila_total_por_hora = [0.0] * len(perfil)
    atrasadas, pior_espera, maior_fila_urna = 0, 0.0, 0.0

    for _, esperado, qtd_secoes in urnas:
        esperado *= escala
        cap_hora = 3600.0 / ciclo(arranjo, t_id, t_voto, qtd_secoes)
        fila = 0.0
        for h, fatia in enumerate(perfil):
            fila += esperado * fatia
            fila -= min(fila, cap_hora)
            fila_total_por_hora[h] += fila
            maior_fila_urna = max(maior_fila_urna, fila)
        if fila > 0.5:
            atrasadas += 1
        pior_espera = max(pior_espera, fila / cap_hora)

    return {
        "arranjo": arranjo,
        "ciclo_t1": ciclo(arranjo, t_id, t_voto, 2),
        "urnas_atrasadas": atrasadas,
        "maior_fila_urna": maior_fila_urna,
        "fila_total_pico": max(fila_total_por_hora),
        "hora_pico": 8 + fila_total_por_hora.index(max(fila_total_por_hora)),
        "fila_total_por_hora": fila_total_por_hora,
        "fecha_as": 17 + pior_espera,
    }


def _hhmm(hora_decimal):
    h = int(hora_decimal)
    m = int(round((hora_decimal - h) * 60))
    if m == 60:
        h, m = h + 1, 0
    return f"{h}h{m:02d}"


def main():
    urnas = carrega_urnas()
    total = sum(e for _, e, _ in urnas)
    print(f"28 urnas | comparecimento esperado {total:,.0f} "
          f"| pico {urnas[0][1]:.0f} (urna {urnas[0][0]}) "
          f"| teto de ciclo na urna critica {JANELA_MIN * 60 / urnas[0][1]:.0f}s\n")

    cabecalho = (f"{'ARRANJO':<12} {'t_id':>5} {'t_voto':>7} {'ciclo':>6} "
                 f"{'atrasadas':>10} {'fila/urna':>10} {'FILA TOTAL':>11} "
                 f"{'pico as':>8} {'fecha':>7}")
    print(cabecalho)
    print("-" * len(cabecalho))
    for arranjo in ("serial", "pipeline", "paralelo"):
        for t_id, t_voto in ((45, 22), (55, 22), (65, 22), (75, 25)):
            r = simula(arranjo, t_id, t_voto)
            print(f"{r['arranjo']:<12} {t_id:>4}s {t_voto:>6}s {r['ciclo_t1']:>5.0f}s "
                  f"{r['urnas_atrasadas']:>7}/28 {r['maior_fila_urna']:>10.0f} "
                  f"{r['fila_total_pico']:>11.0f} {r['hora_pico']:>6}h "
                  f"{_hhmm(r['fecha_as']):>7}")
        print()

    print("Dimensionamento do Ring 3 = coluna FILA TOTAL (pessoas simultaneas "
          "em espera no conjunto das 28 urnas).")


if __name__ == "__main__":
    main()


# --------------------------------------------------------------------------
# Atribuicao das urnas as entradas A/B/C do Ring 3
#
# Mora em scripts/decisoes.py (fonte unica): as quotas vem da capacidade de
# cada serpenteado calculada em layout_ring3.py, e as tres mesas de classe
# alta vao para entradas diferentes. Aqui so se imprime o relatorio.


def atribui_entradas():
    """{entrada: [mrv...]}, {entrada: esperado}, {entrada: alvo} -- de decisoes."""
    import decisoes as DC
    d = DC.montar()
    grupos = {e["id"]: e["mrvs"] for e in d["entradas"]}
    carga = {e["id"]: float(e["esperado"]) for e in d["entradas"]}
    alvo = {e["id"]: float(e["alvo"]) for e in d["entradas"]}
    return grupos, carga, alvo


def tabela_ciclos(ciclos=(45, 50, 55, 60, 75, 90)):
    """Urnas ainda com fila as 17h e ultima a fechar, por ciclo puro por eleitor."""
    out = []
    for c in ciclos:
        r = simula("serial", c, 0)
        out.append((c, r["urnas_atrasadas"], _hhmm(r["fecha_as"])))
    return out


def _relatorio_entradas():
    import decisoes as DC
    d = DC.montar()
    secao = {m["mrv"]: m["principal"] for m in d["mesas"]}
    total = sum(e["esperado"] for e in d["entradas"])
    print("\nATRIBUICAO DAS URNAS AS ENTRADAS DO RING 3 (scripts/decisoes.py)")
    cab = f"{'entrada':<8} {'porta':<6} {'urnas':>6} {'esperado':>9} {'quota':>7} {'alvo':>8} {'desvio':>8}"
    print(cab); print("-" * len(cab))
    for e in d["entradas"]:
        print(f"{e['id']:<8} {e['porta']:<6} {len(e['mrvs']):>6} {e['esperado']:>9} "
              f"{e['esperado']/total:>6.1%} {e['alvo']:>8} {e['esperado']-e['alvo']:>+8}")
    print("-" * len(cab))
    print(f"{'TOTAL':<8} {'':<6} {sum(len(e['mrvs']) for e in d['entradas']):>6} {total:>9}")
    for e in d["entradas"]:
        print(f"\n  {e['id']} ({e['porta']}): " + ", ".join(f"MRV {m} ({secao[m]})" for m in e["mrvs"]))
