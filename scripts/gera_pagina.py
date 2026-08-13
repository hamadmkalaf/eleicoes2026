"""Gera a pagina visual a partir de saidas/dados.json.

A pagina e um documento de briefing operacional: entrega os totais por urna
ordenados e a origem dos eleitores, sem aplicar criterio de gargalo -- o corte
e do usuario.
"""

import html
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SAIDAS = BASE / "saidas"


def fmt(n) -> str:
    """Formata inteiro no padrao brasileiro."""
    return f"{int(n):,}".replace(",", ".")


def barra(principal: int, agregada: int, maximo: int) -> str:
    """Barra empilhada: fatia da secao principal + fatia da agregada."""
    p = principal / maximo * 100
    a = agregada / maximo * 100
    partes = [f'<span class="seg seg-p" style="width:{p:.3f}%"></span>']
    if agregada:
        partes.append(f'<span class="seg seg-a" style="width:{a:.3f}%"></span>')
    return f'<span class="bar">{"".join(partes)}</span>'


def main():
    d = json.loads((SAIDAS / "dados.json").read_text(encoding="utf-8"))
    urnas = d["urnas"]
    secoes = d["secoes"]
    residencia_total = d["residencia_total"]

    por_secao = {int(s["Secao"]): s for s in secoes}
    maximo = max(u["Total_combinado"] for u in urnas)
    max_local = max(residencia_total.values())

    duplas = [u for u in urnas if u["Qtd_secoes"] == 2]
    sozinhas = [u for u in urnas if u["Qtd_secoes"] == 1]
    total_principais = sum(
        s["Eleitores"] for s in secoes if s["Papel"] == "Principal")
    fora_dublin = sum(v for k, v in residencia_total.items() if k != "DUBLIN")

    # ---- linhas da tabela de urnas -------------------------------------
    linhas_urnas = []
    for u in urnas:
        agregada = u["Secao_agregada"]
        if agregada is not None and str(agregada) != "nan":
            n_agregada = int(float(agregada))
            origem = por_secao[n_agregada]["Residencia_predominante"]
            cel_agregada = (f'<span class="sec">{n_agregada:04d}</span>'
                            f'<span class="qt">{fmt(u["Eleitores_agregada"])}</span>')
            cel_origem = f'<span class="local">{html.escape(origem)}</span>'
        else:
            cel_agregada = '<span class="vazio">sem agregada</span>'
            cel_origem = '<span class="vazio">&mdash;</span>'

        linhas_urnas.append(f"""        <tr>
          <td class="rank">{u['Posicao']}</td>
          <td class="col-sec"><span class="urna">{u['Secao_principal']:04d}</span><span class="qt">{fmt(u['Eleitores_principal'])}</span></td>
          <td class="col-sec">{cel_agregada}</td>
          <td class="col-origem">{cel_origem}</td>
          <td class="col-bar">{barra(u['Eleitores_principal'], u['Eleitores_agregada'], maximo)}</td>
          <td class="total">{fmt(u['Total_combinado'])}</td>
        </tr>""")

    # ---- linhas da tabela de residencia --------------------------------
    linhas_residencia = []
    for local, qt in residencia_total.items():
        largura = qt / max_local * 100
        classe = "seg-p" if local == "DUBLIN" else "seg-a"
        linhas_residencia.append(f"""        <tr>
          <td class="col-local">{html.escape(local)}</td>
          <td class="col-bar"><span class="bar"><span class="seg {classe}" style="width:{largura:.3f}%"></span></span></td>
          <td class="total">{fmt(qt)}</td>
          <td class="pct">{qt / d['total_eleitores'] * 100:.1f}%</td>
        </tr>""")

    # ---- apendice: as 51 secoes ----------------------------------------
    linhas_secoes = []
    for s in sorted(secoes, key=lambda x: int(x["Secao"])):
        papel = s["Papel"]
        chip = ("principal" if papel == "Principal" else "agregada")
        linhas_secoes.append(f"""        <tr>
          <td class="urna">{int(s['Secao']):04d}</td>
          <td><span class="chip chip-{chip}">{papel}</span></td>
          <td class="urna dim">{int(s['Urna']):04d}</td>
          <td class="col-local">{html.escape(s['Residencia_predominante'])}</td>
          <td class="total">{fmt(s['Eleitores'])}</td>
          <td class="total dim">{fmt(s['Total_urna_TSE']) if s['Papel'] == 'Principal' else '&mdash;'}</td>
        </tr>""")

    # A reconciliacao ja tem bullet proprio na secao de metodo; evita repetir.
    notas = "".join(
        f"<li><strong>{html.escape(i['Referencia'])}.</strong> "
        f"{html.escape(i['Descricao'])}</li>"
        for i in d["inconsistencias"] if i["Tipo"] != "Reconciliação")

    pagina = f"""<title>Urnas de Dublin</title>
<style>
  :root {{
    color-scheme: light;
    --ground:      #f4f6f9;
    --surface:     #ffffff;
    --surface-2:   #eef1f6;
    --ink:         #11151c;
    --ink-2:       #515b6b;
    --ink-3:       #7a8494;
    --rule:        #dde3ea;
    --rule-forte:  #c3ccd8;
    --s1:          #2a78d6;
    --s2:          #eb6834;
    --s1-fraco:    #dce9f9;
    --s2-fraco:    #fbe3d8;

    --serif: Georgia, "Iowan Old Style", "Times New Roman", serif;
    --sans: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    --mono: ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, monospace;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      color-scheme: dark;
      --ground:     #0e1116;
      --surface:    #171b22;
      --surface-2:  #1f242d;
      --ink:        #eef1f5;
      --ink-2:      #a0aab8;
      --ink-3:      #76808e;
      --rule:       #282e38;
      --rule-forte: #3a4250;
      --s1:         #3987e5;
      --s2:         #d95926;
      --s1-fraco:   #1b2f47;
      --s2-fraco:   #3a2318;
    }}
  }}
  :root[data-theme="dark"] {{
    color-scheme: dark;
    --ground:     #0e1116;
    --surface:    #171b22;
    --surface-2:  #1f242d;
    --ink:        #eef1f5;
    --ink-2:      #a0aab8;
    --ink-3:      #76808e;
    --rule:       #282e38;
    --rule-forte: #3a4250;
    --s1:         #3987e5;
    --s2:         #d95926;
    --s1-fraco:   #1b2f47;
    --s2-fraco:   #3a2318;
  }}

  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--ground);
    color: var(--ink);
    font-family: var(--sans);
    font-size: 15px;
    line-height: 1.55;
    -webkit-font-smoothing: antialiased;
  }}
  .wrap {{
    max-width: 1120px;
    margin: 0 auto;
    padding: 40px 24px 72px;
    display: flex;
    flex-direction: column;
    gap: 44px;
  }}

  /* ---------- cabecalho ---------- */
  header {{ display: flex; flex-direction: column; gap: 22px; }}
  .eyebrow {{
    font-family: var(--mono);
    font-size: 11.5px;
    letter-spacing: .13em;
    text-transform: uppercase;
    color: var(--ink-3);
  }}
  h1 {{
    font-family: var(--serif);
    font-size: clamp(30px, 4.6vw, 46px);
    line-height: 1.1;
    font-weight: 600;
    letter-spacing: -.015em;
    margin: 0;
    text-wrap: balance;
  }}
  .sub {{
    margin: 0;
    max-width: 64ch;
    color: var(--ink-2);
    font-size: 16px;
  }}
  .local-band {{
    display: flex;
    flex-wrap: wrap;
    gap: 4px 18px;
    padding: 14px 18px;
    background: var(--surface);
    border: 1px solid var(--rule);
    border-left: 3px solid var(--s1);
    border-radius: 3px;
  }}
  .local-band .nome {{ font-family: var(--serif); font-size: 17px; font-weight: 600; }}
  .local-band .end {{ color: var(--ink-2); font-size: 14px; }}

  .tiles {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1px;
    background: var(--rule);
    border: 1px solid var(--rule);
    border-radius: 3px;
    overflow: hidden;
  }}
  .tile {{ background: var(--surface); padding: 18px 20px; display: flex; flex-direction: column; gap: 3px; }}
  .tile .n {{ font-family: var(--mono); font-size: 30px; font-weight: 600; letter-spacing: -.02em; font-variant-numeric: tabular-nums; }}
  .tile .k {{ font-size: 12.5px; color: var(--ink-2); }}

  /* ---------- secoes ---------- */
  section {{ display: flex; flex-direction: column; gap: 16px; }}
  h2 {{
    font-family: var(--serif);
    font-size: 25px;
    font-weight: 600;
    margin: 0;
    letter-spacing: -.01em;
    padding-bottom: 9px;
    border-bottom: 2px solid var(--rule-forte);
  }}
  .nota {{ margin: 0; color: var(--ink-2); max-width: 74ch; font-size: 14.5px; }}
  .nota strong {{ color: var(--ink); font-weight: 600; }}

  /* ---------- legenda ---------- */
  .legenda {{ display: flex; flex-wrap: wrap; gap: 18px; font-size: 13px; color: var(--ink-2); }}
  .legenda span {{ display: inline-flex; align-items: center; gap: 7px; }}
  .swatch {{ width: 11px; height: 11px; border-radius: 2px; flex: none; }}
  .sw-p {{ background: var(--s1); }}
  .sw-a {{ background: var(--s2); }}

  /* ---------- tabelas ---------- */
  .scroll {{ overflow-x: auto; border: 1px solid var(--rule); border-radius: 3px; background: var(--surface); }}
  table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
  thead th {{
    position: sticky; top: 0;
    background: var(--surface-2);
    font-family: var(--mono);
    font-size: 10.5px;
    letter-spacing: .09em;
    text-transform: uppercase;
    color: var(--ink-2);
    font-weight: 600;
    text-align: left;
    padding: 11px 12px;
    border-bottom: 1px solid var(--rule-forte);
    white-space: nowrap;
  }}
  tbody td {{ padding: 9px 12px; border-bottom: 1px solid var(--rule); vertical-align: middle; }}
  tbody tr:last-child td {{ border-bottom: 0; }}
  tbody tr:hover td {{ background: var(--surface-2); }}

  .rank {{ font-family: var(--mono); font-size: 12px; color: var(--ink-3); width: 34px; font-variant-numeric: tabular-nums; }}
  .urna {{ font-family: var(--mono); font-weight: 600; font-variant-numeric: tabular-nums; white-space: nowrap; }}
  .urna.dim {{ font-weight: 400; color: var(--ink-2); }}
  .col-sec {{ white-space: nowrap; }}
  .col-sec .sec {{ font-family: var(--mono); font-variant-numeric: tabular-nums; }}
  .col-sec .qt {{ font-family: var(--mono); font-size: 12px; color: var(--ink-2); margin-left: 9px; font-variant-numeric: tabular-nums; }}
  .col-sec .vazio, .col-origem .vazio {{ color: var(--ink-3); font-size: 13px; font-style: italic; }}
  .col-origem .local, .col-local {{ font-size: 13px; color: var(--ink-2); white-space: nowrap; }}
  .total {{ font-family: var(--mono); font-weight: 600; text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }}
  .total.dim {{ font-weight: 400; color: var(--ink-2); }}
  .pct {{ font-family: var(--mono); font-size: 12px; color: var(--ink-2); text-align: right; font-variant-numeric: tabular-nums; }}

  .col-bar {{ width: 40%; min-width: 190px; }}
  .bar {{ display: flex; gap: 2px; align-items: center; height: 14px; }}
  .seg {{ height: 100%; border-radius: 0 3px 3px 0; }}
  .seg:first-child {{ border-radius: 3px; }}
  .seg-p {{ background: var(--s1); }}
  .seg-a {{ background: var(--s2); }}

  .chip {{
    display: inline-block; padding: 2px 8px; border-radius: 2px;
    font-size: 11px; font-weight: 600; letter-spacing: .02em;
  }}
  .chip-principal {{ background: var(--s1-fraco); color: var(--s1); }}
  .chip-agregada {{ background: var(--s2-fraco); color: var(--s2); }}

  /* ---------- destaques ---------- */
  .achados {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(255px, 1fr)); gap: 14px; }}
  .achado {{
    background: var(--surface); border: 1px solid var(--rule);
    border-top: 2px solid var(--s2); border-radius: 3px;
    padding: 16px 18px; display: flex; flex-direction: column; gap: 6px;
  }}
  .achado .t {{ font-family: var(--serif); font-size: 16.5px; font-weight: 600; }}
  .achado .d {{ font-size: 13.5px; color: var(--ink-2); }}

  .metodo {{ background: var(--surface); border: 1px solid var(--rule); border-radius: 3px; padding: 20px 24px; }}
  .metodo ul {{ margin: 0; padding-left: 20px; display: flex; flex-direction: column; gap: 9px; }}
  .metodo li {{ font-size: 13.5px; color: var(--ink-2); }}
  .metodo strong {{ color: var(--ink); font-weight: 600; }}

  footer {{ color: var(--ink-3); font-size: 12.5px; border-top: 1px solid var(--rule); padding-top: 16px; }}

  @media (max-width: 720px) {{
    .col-bar {{ display: none; }}
    .wrap {{ padding: 28px 16px 56px; gap: 34px; }}
  }}
</style>

<div class="wrap">
  <header>
    <div class="eyebrow">Elei&ccedil;&otilde;es 2026 &middot; 1&ordm; turno &middot; 04/10/2026 &middot; Zona 1 &middot; ZZ</div>
    <h1>Eleitorado por se&ccedil;&atilde;o e por urna em Dublin</h1>
    <p class="sub">O mapa de agrega&ccedil;&otilde;es do TSE concentra as 51 se&ccedil;&otilde;es da Irlanda em 28 urnas,
    todas num &uacute;nico local. Abaixo, quantos eleitores cada se&ccedil;&atilde;o traz e onde eles residem.</p>
    <div class="local-band">
      <span class="nome">{html.escape(d['local'])}</span>
      <span class="end">{html.escape(d['endereco'])}</span>
    </div>
    <div class="tiles">
      <div class="tile"><span class="n">{fmt(d['total_eleitores'])}</span><span class="k">eleitores na zona de Dublin</span></div>
      <div class="tile"><span class="n">{d['total_secoes']}</span><span class="k">se&ccedil;&otilde;es (28 principais + 23 agregadas)</span></div>
      <div class="tile"><span class="n">{d['total_urnas']}</span><span class="k">urnas no Royal Dublin Society</span></div>
      <div class="tile"><span class="n">{fmt(maximo)}</span><span class="k">eleitores na urna mais carregada</span></div>
    </div>
  </header>

  <section>
    <h2>As 28 urnas, da mais carregada &agrave; menos</h2>
    <p class="nota">Cada urna &eacute; identificada pela sua se&ccedil;&atilde;o principal e re&uacute;ne, em 23 casos,
    uma se&ccedil;&atilde;o agregada. A coluna <strong>origem</strong> indica onde residem os eleitores da
    se&ccedil;&atilde;o agregada &mdash; todas as se&ccedil;&otilde;es principais s&atilde;o de residentes em Dublin.</p>
    <div class="legenda">
      <span><i class="swatch sw-p"></i>Se&ccedil;&atilde;o principal</span>
      <span><i class="swatch sw-a"></i>Se&ccedil;&atilde;o agregada</span>
    </div>
    <div class="scroll">
      <table>
        <thead><tr>
          <th>#</th><th>Se&ccedil;&atilde;o principal</th><th>Se&ccedil;&atilde;o agregada</th>
          <th>Origem da agregada</th><th>Composi&ccedil;&atilde;o</th><th style="text-align:right">Total na urna</th>
        </tr></thead>
        <tbody>
{chr(10).join(linhas_urnas)}
        </tbody>
      </table>
    </div>
  </section>

  <section>
    <h2>O que os n&uacute;meros mostram</h2>
    <div class="achados">
      <div class="achado">
        <span class="t">{len(duplas)} urnas com duas se&ccedil;&otilde;es</span>
        <span class="d">V&atilde;o de {fmt(min(u['Total_combinado'] for u in duplas))} a {fmt(maximo)} eleitores.
        As {len(sozinhas)} urnas restantes operam com uma se&ccedil;&atilde;o s&oacute;, entre {fmt(min(u['Total_combinado'] for u in sozinhas))} e {fmt(max(u['Total_combinado'] for u in sozinhas))}.</span>
      </div>
      <div class="achado">
        <span class="t">Duas naturezas de urna cheia</span>
        <span class="d">No topo convivem urnas que somam duas se&ccedil;&otilde;es de Dublin (3313, 3322, 3315)
        e urnas que somam uma se&ccedil;&atilde;o de Dublin com uma se&ccedil;&atilde;o inteira do interior
        (3142 com Limerick, 3161 e 3245 com Cork, 3305 e 3108 com Galway).</span>
      </div>
      <div class="achado">
        <span class="t">Cada se&ccedil;&atilde;o &eacute; de uma s&oacute; localidade</span>
        <span class="d">Nas 51 se&ccedil;&otilde;es, 100% dos eleitores v&ecirc;m de um &uacute;nico local de origem.
        As 28 principais somam {fmt(total_principais)} eleitores, todos de Dublin.</span>
      </div>
      <div class="achado">
        <span class="t">{fmt(fora_dublin)} eleitores fora de Dublin</span>
        <span class="d">{fora_dublin / d['total_eleitores'] * 100:.0f}% do eleitorado da zona reside em outros condados e
        passa a votar em Dublin. Em sete urnas essa parcela chega perto da metade.</span>
      </div>
    </div>
  </section>

  <section>
    <h2>De onde v&ecirc;m os eleitores</h2>
    <p class="nota">Local de vota&ccedil;&atilde;o de origem de cada eleitor, usado aqui como refer&ecirc;ncia de resid&ecirc;ncia.
    Com a agrega&ccedil;&atilde;o, todos passam a votar no Royal Dublin Society.</p>
    <div class="scroll">
      <table>
        <thead><tr>
          <th>Localidade</th><th>Distribui&ccedil;&atilde;o</th>
          <th style="text-align:right">Eleitores</th><th style="text-align:right">Share</th>
        </tr></thead>
        <tbody>
{chr(10).join(linhas_residencia)}
        </tbody>
      </table>
    </div>
  </section>

  <section>
    <h2>As 51 se&ccedil;&otilde;es, uma a uma</h2>
    <p class="nota">A &uacute;ltima coluna reproduz o campo <code>QT_ELEITOR_ELEICAO_FEDERAL</code> do TSE, que
    j&aacute; traz o total agregado da urna na se&ccedil;&atilde;o principal e vem zerado nas agregadas.
    Ele confere com o total calculado aqui nas 28 urnas.</p>
    <div class="scroll">
      <table>
        <thead><tr>
          <th>Se&ccedil;&atilde;o</th><th>Papel</th><th>Urna</th><th>Resid&ecirc;ncia</th>
          <th style="text-align:right">Eleitores</th><th style="text-align:right">Total na urna (TSE)</th>
        </tr></thead>
        <tbody>
{chr(10).join(linhas_secoes)}
        </tbody>
      </table>
    </div>
  </section>

  <section>
    <h2>Como estes n&uacute;meros foram apurados</h2>
    <div class="metodo">
      <ul>
        <li><strong>Fontes.</strong> <code>eleitorado_local_votacao_2026_ZZ.csv</code> (TSE, gerado em 13/08/2026)
        para se&ccedil;&otilde;es, papel e eleitorado; <code>Filtrado_Dublin.csv</code> (TSE, 14/07/2026) para a
        origem dos eleitores; e o PNG do mapa de agrega&ccedil;&otilde;es do TSE.</li>
        <li><strong>Reconcilia&ccedil;&atilde;o.</strong> As duas bases batem se&ccedil;&atilde;o a se&ccedil;&atilde;o,
        somando {fmt(d['total_eleitores'])} eleitores em ambas.</li>
        <li><strong>Confer&ecirc;ncia independente.</strong> O total somado aqui para cada uma das 28 urnas
        coincide com o campo <code>QT_ELEITOR_ELEICAO_FEDERAL</code>, que o TSE j&aacute; publica agregado
        na se&ccedil;&atilde;o principal. Os dois caminhos de c&aacute;lculo chegam ao mesmo n&uacute;mero.</li>
        {notas}
        <li><strong>Sem crit&eacute;rio de gargalo.</strong> A pedido, nenhum modelo de tempo de vota&ccedil;&atilde;o
        foi aplicado: a p&aacute;gina entrega os totais ordenados e o corte fica a cargo de quem analisa.</li>
      </ul>
    </div>
  </section>

  <footer>Elaborado a partir dos dados abertos do TSE para as Elei&ccedil;&otilde;es 2026, 1&ordm; turno.</footer>
</div>
"""

    destino = SAIDAS / "dublin_agregacoes.html"
    destino.write_text(pagina, encoding="utf-8")
    print(f"Pagina: {destino} ({len(pagina):,} bytes)")


if __name__ == "__main__":
    main()
