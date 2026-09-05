"""Modelo de fila por urna para a votacao de Dublin em 04/10/2026.

Configuracao fixada pelo TRE (negociacao encerrada): 28 urnas, 28 mesas
receptoras (1:1), 51 secoes, 16.794 aptos, janela 8h-17h no RDS Hall 2.

O modelo responde a duas perguntas distintas, que tem solucoes diferentes:

  - HORARIO DE FECHAMENTO: e problema de vazao pura. Depende so do ciclo por
    eleitor. Nenhuma gestao de fila o altera.
  - TAMANHO DA FILA: e problema de curva de chegada. Depende do perfil horario
    e da organizacao fisica, e e o que dimensiona o Ring 3.

Premissas explicitas (todas ajustaveis no topo do arquivo):
  - taxas de comparecimento de 2022: 74% para residentes em Dublin, 50% para
    residentes no interior (fonte: secao 2 de contexto_eleicoes_dublin_2026.md);
  - perfil horario de chegada com pico de manha (premissa, nao medida);
  - eleitor no exterior vota SO para Presidente, entao o ato de votar e curto e
    a identificacao no caderno domina o ciclo.

Uso:  python3 scripts/simula_fluxo.py
"""

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "saidas" / "dados.json"

# --- premissas -------------------------------------------------------------

TAXA_DUBLIN = 0.74
TAXA_INTERIOR = 0.50

# Fracao das chegadas em cada hora, das 8h as 17h.
PERFIL_CENTRAL = [.12, .15, .16, .15, .12, .09, .08, .07, .06]
PERFIL_AGUDO = [.14, .18, .20, .16, .11, .07, .06, .05, .03]

JANELA_MIN = 9 * 60


def carrega_urnas():
    """Devolve [(urna, comparecimento_esperado, qtd_secoes)] ordenado por carga."""
    dados = json.loads(DADOS.read_text(encoding="utf-8"))
    residencia = {r["Urna"]: r for r in dados["residencia_urna"]}
    urnas = []
    for u in dados["urnas"]:
        r = residencia[u["Urna"]]
        dublin = r.get("DUBLIN", 0)
        interior = r["TOTAL"] - dublin
        esperado = dublin * TAXA_DUBLIN + interior * TAXA_INTERIOR
        urnas.append((u["Urna"], esperado, u["Qtd_secoes"]))
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
