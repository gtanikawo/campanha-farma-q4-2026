"""Frequência = regra do Tracking NP Farma (% Realizado Newspage): Σ Realizado Newspage ÷ Σ Planejado Real do mês,
sem proporcionalidade e sem limite por loja (pedido do Gustavo, 26/10, depois do caso Anderson 99,1).
Substitui a cobrança por janela/proporcional. Roda uma vez sobre o placar (JS e Python), o jogo e os documentos."""
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent.parent
falhas = []
def edita(caminho, pares):
    p = RAIZ / caminho; s = p.read_text(encoding='utf-8')
    for velho, novo in pares:
        if velho not in s: falhas.append(f'{caminho}: {velho[:70]}'); continue
        s = s.replace(velho, novo)
    p.write_text(s, encoding='utf-8')

edita('03_HTML/src/corpo_ajustado.html', [
    ("""   % frequência = Σ mín(pesquisas, planejado) ÷ Σ máx(visitas vencidas, visitas feitas). As visitas planejadas dividem
   o mês em janelas iguais; uma visita só é cobrada quando a janela dela fecha (no mês fechado, o planejado inteiro).""",
     """   % frequência = regra do Tracking NP Farma (% Realizado Newspage): Σ pesquisas NewsPage ÷ Σ visitas planejadas do mês,
   sem proporcionalidade e sem limite por loja (desde 26/10, depois da validação do caso Anderson)."""),
    ("const e = pesq > 0 ? 1 : 0, c = Math.min(pesq, plan), k = norm(colab), v = vencidas(plan, dm, dc);",
     "const e = pesq > 0 ? 1 : 0, c = pesq, k = norm(colab), v = plan;   // frequência como no Tracking: pesquisas ÷ planejado do mês"),
    ("p.den += Math.max(v, c); p.pesq += pesq;", "p.den += plan; p.pesq += pesq;"),
    ("s.den += Math.max(v, c); s.pesq += pesq;", "s.den += plan; s.pesq += pesq;"),
    ("+ ' · nota = 50% lojas + 50% frequência; visita cobrada só depois que a janela dela fecha'; });",
     "+ ' · nota = 50% lojas + 50% frequência (pesquisas NewsPage ÷ visitas planejadas do mês, como no Tracking)'; });"),
    ("['visitas','Visitas feitas / cobradas','r']", "['visitas','Pesquisas / planejadas','r']"),
    ('title="cobradas = visitas vencidas até o corte, ou feitas se for maior"', 'title="pesquisas NewsPage ÷ visitas planejadas no mês (como no Tracking)"'),
])
p = RAIZ / '03_HTML/src/corpo_ajustado.html'; s = p.read_text(encoding='utf-8')
i = s.find('<div class="rule"><b>% Frequência</b>')
if i < 0: falhas.append('corpo: quadro % Frequência')
else:
    j = s.index('</div>', i) + len('</div>')
    s = s[:i] + '<div class="rule"><b>% Frequência</b><p>Como no Tracking NP Farma (% Realizado Newspage): pesquisas NewsPage feitas ÷ visitas planejadas no mês para as lojas do roteiro. Loja quinzenal com 1 pesquisa conta 1 de 2.</p></div>' + s[j:]
    p.write_text(s, encoding='utf-8')

edita('03_HTML/src/build_placar.py', [
    ("""            e, c, k = (1 if pesq > 0 else 0), min(pesq, plan), norm(colab)
            den = max(vencidas(plan, dm, dc), c)""",
     """            # frequência como no Tracking (% Realizado Newspage): pesquisas ÷ planejado do mês, sem limite por loja
            e, c, k = (1 if pesq > 0 else 0), pesq, norm(colab)
            den = plan"""),
    ("- Regra oficial desde 26/10/2026: nota = 50% % lojas executadas + 50% % frequência (visitas cobradas por janela);",
     "- Regra oficial desde 26/10/2026: nota = 50% % lojas executadas + 50% % frequência (Σ pesquisas ÷ Σ planejado do mês, como no Tracking);"),
])
edita('03_HTML/FORMATO_DADOS.md', [
    ("| % frequência | Σ mín(pesquisas, planejado) ÷ Σ máx(visitas cobradas, visitas feitas). As visitas planejadas da loja dividem o mês em janelas iguais, e a visita k vence no dia ⌈k × dias do mês ÷ planejado⌉. **Mês aberto:** só cobra a visita cuja janela já fechou até o corte (mensal e bimestral: no fim do mês; quinzenal: na metade e no fim; semanal: uma por semana). A visita feita antes do prazo já conta. **Mês fechado:** cobra todo o planejado. |",
     "| % frequência | **Regra do Tracking NP Farma (% Realizado Newspage):** Σ pesquisas NewsPage (Realizado Newspage) ÷ Σ visitas planejadas no mês (Planejado Real), sem proporcionalidade e sem limite por loja. Loja quinzenal com 1 pesquisa conta 1 de 2. Pesquisa a mais numa loja também conta, como no Tracking. |"),
    ("| Desempate | 1º % lojas executadas · 2º % frequência · 3º % NewsPage realizado (Σ pesquisas ÷ Σ planejado, sem limite) · por último o nome. |",
     "| Desempate | 1º % lojas executadas · 2º % frequência · 3º % NewsPage realizado (hoje é a mesma conta da frequência) · por último o nome. |"),
])
edita('05_Farma_Cards_RPG/src/rpg_v3.js', [
    ("${number(r.cump)} de ${number(r.plan)} visitas cobradas até o corte", "${number(r.cump)} pesquisas de ${number(r.plan)} visitas planejadas no mês"),
])
edita('05_Farma_Cards_RPG/src/missoes.js', [
    ("nota = 50% × % lojas executadas + 50% × % frequência (visitas feitas ÷ visitas já cobradas até o corte)",
     "nota = 50% × % lojas executadas + 50% × % frequência (pesquisas NewsPage ÷ visitas planejadas no mês, como no Tracking)"),
])
edita('05_Farma_Cards_RPG/src/build_v2.py', [
    ("50% lojas executadas + 50% frequência (visitas feitas ÷ visitas já cobradas até o corte).", "50% lojas executadas + 50% frequência (pesquisas NewsPage ÷ visitas planejadas no mês, como no Tracking)."),
])
edita('03_HTML/src/teste_placar.py', [
    ("    ok('Frequência só cobra visitas vencidas: geral entre 85% e 92% em 22/10', 85 <= sum(r['cump'] for r in V['q4']['prom']) / sum(r['den'] for r in V['q4']['prom']) * 100 <= 92)",
     """    ok('Frequência = Σ pesquisas ÷ Σ planejado (regra do Tracking): geral 55,0%', round(sum(r['cump'] for r in V['q4']['prom']) / sum(r['den'] for r in V['q4']['prom']) * 100, 1) == 55.0)
    an = next(x for x in V['q4']['prom'] if x['nome'].startswith('Anderson'))
    ok('Anderson: 59 pesquisas de 104 planejadas = 56,7% de frequência', (an['cump'], an['den'], an['pctf']) == (59, 104, 56.7), str((an['cump'], an['den'], an['pctf'])))
    ok('Ninguém com 100% de frequência sem ter feito todas as pesquisas', all(r['pctf'] < 100 or r['cump'] >= r['den'] for r in V['q4']['prom']))"""),
])
print('FALHAS: ' + ' | '.join(falhas) if falhas else 'ok: regra do Tracking aplicada')
