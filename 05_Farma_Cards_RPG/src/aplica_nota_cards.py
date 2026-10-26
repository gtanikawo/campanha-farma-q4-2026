"""Farma Cards com a nota oficial (26/10): raridade e carta pela nota; ficha e Santuário com nota, lojas, frequência e NewsPage;
"visitas cumpridas" passa a "frequência"; regras do ranking atualizadas. Roda uma vez; cada troca confere o trecho."""
from pathlib import Path
AQUI = Path(__file__).resolve().parent
falhas = []
def troca(txt, velho, novo, nome):
    if velho not in txt: falhas.append(f'{nome}: {velho[:70]}'); return txt
    return txt.replace(velho, novo)

# --- rpg_v3.js ---
p = AQUI / 'rpg_v3.js'; s = p.read_text(encoding='utf-8')
s = troca(s, "const MESES_Q4 = ['out','nov','dez'];", """const MESES_Q4 = ['out','nov','dez'];

/* --- nota oficial (26/10): 50% lojas + 50% frequência; raridade e carta usam a nota --- */
function getNota(r){ const v = Number(r && r.nota); return Number.isFinite(v) ? v : getNPScore(r) }
function tier(r){ const v = getNota(r) ?? 0; let sel = RARITIES[0]; for (const it of RARITIES.slice(1)) if (v >= it.min()) sel = it; return sel }
function mythicUnlocked(r){ return getNota(r) >= thresholds.mythic && Number(r.pctv) >= gates.mythicVisit && Number(r.exec) >= gates.mythicExec && proposalsOk(r) }""", 'rpg nota')
s = troca(s, "  const v = getNPScore(r), t = tier(r), idx = RARITIES.findIndex(x => x.id === t.id), prox = RARITIES[idx+1];",
             "  const v = getNota(r), t = tier(r), idx = RARITIES.findIndex(x => x.id === t.id), prox = RARITIES[idx+1];", 'rpg raridade')
s = troca(s, "    [`${thresholds.mythic}%+ das lojas executadas`, v >= thresholds.mythic, fmtP(v)],", "    [`nota ${thresholds.mythic}+`, v >= thresholds.mythic, fmtP(v)],", 'rpg req')
s = troca(s, "<p><b>Por que ${esc(t.name)}?</b> ${fmtP(rx.v)} das lojas executadas ${lb('of')}.", "<p><b>Por que ${esc(t.name)}?</b> Nota oficial ${fmtP(rx.v)} ${lb('of')}.", 'rpg verso')
s = troca(s, """      <div class="detail-attributes"><div class="attribute"><span>% LOJAS EXECUTADAS</span><b style="color:${t.color}">${pct(r.pct)}</b></div><div class="attribute"><span>LOJAS EXECUTADAS / PREVISTAS</span><b>${number(r.exec)} / ${number(r.lojas)}</b></div>""",
"""      <div class="detail-attributes"><div class="attribute nota-attr"><span>NOTA OFICIAL (50% lojas + 50% frequência)</span><b style="color:${t.color}">${pct(getNota(r))}</b></div><div class="attribute"><span>% LOJAS EXECUTADAS</span><b>${pct(r.pct)}</b><small>${number(r.exec)} de ${number(r.lojas)} lojas</small></div>""", 'rpg ficha')
s = troca(s, """<div class="attribute"><span>% VISITAS CUMPRIDAS (desempate)</span><b>${pct(r.pctv)}</b></div>""",
             """<div class="attribute"><span>% FREQUÊNCIA</span><b>${pct(r.pctv)}</b><small>${r.cump!=null&&r.plan!=null?`${number(r.cump)} de ${number(r.plan)} visitas cobradas até o corte`:''}</small></div><div class="attribute"><span>% NEWSPAGE REALIZADO (3º desempate)</span><b>${r.pnp!=null?pct(r.pnp):'—'}</b></div>""", 'rpg freq')
s = troca(s, """    <div class="big-score">${pct(s.pct)} <small>DAS LOJAS DO TIME EXECUTADAS</small></div>
    <p style="margin-top:6px">${number(s.exec)} de ${number(s.lojas)} lojas do time (soma das lojas de todos os promotores, não média dos %).""",
"""    <div class="big-score">${pct(getNota(s))} <small>NOTA DO TIME</small></div>
    <p style="margin-top:6px">Lojas ${pct(s.pct)} · frequência ${pct(s.pctv)} · ${number(s.exec)} de ${number(s.lojas)} lojas do time (soma das lojas de todos os promotores, não média dos %).""", 'rpg sup')
s = troca(s, "copyText(`${r.nome}\\n${kind==='sup'?'Supervisor':'Promotor'} · posição oficial ${r.pos}º (${periodo})\\n% lojas executadas (OFICIAL)",
             "copyText(`${r.nome}\\n${kind==='sup'?'Supervisor':'Promotor'} · posição oficial ${r.pos}º (${periodo})\\nNota oficial: ${pct(getNota(r))}\\n% lojas executadas (OFICIAL)", 'rpg copiar')
p.write_text(s, encoding='utf-8')

# --- missoes.js (Forja) ---
p = AQUI / 'missoes.js'; s = p.read_text(encoding='utf-8')
s = troca(s, "const raridade=tab(['Raridade','Faixa de lojas executadas','Observação'],[", "const raridade=tab(['Raridade','Faixa da nota oficial','Observação'],[", 'forja raridade')
s = troca(s, "  <b>Ranking oficial:</b> lojas executadas ÷ lojas do roteiro, desempate pelo % de visitas cumpridas.",
             "  <b>Ranking oficial:</b> nota = 50% × % lojas executadas + 50% × % frequência (visitas feitas ÷ visitas já cobradas até o corte); desempate % lojas → % frequência → % NewsPage realizado.", 'forja ranking')
s = troca(s, "$('forgeRules').innerHTML=bloco('◇ Raridade completa','% de lojas executadas',raridade)", "$('forgeRules').innerHTML=bloco('◇ Raridade completa','nota oficial',raridade)", 'forja titulo')
p.write_text(s, encoding='utf-8')

# --- build_v2.py: trocas no protótipo + passada final de textos ---
p = AQUI / 'build_v2.py'; s = p.read_text(encoding='utf-8')
s = troca(s, "\nif falhas:", r'''
# 18. Nota oficial (26/10): carta, Santuário e regras pela nota; "visitas cumpridas" passa a "frequência"
troca("row(`${n} a partir de`,'% de lojas executadas no recorte',thresholds[k]+'%')", "row(`${n} a partir de`,'nota oficial no recorte',thresholds[k]+'%')")
troca('✦ Raridade pelo % de lojas executadas', '✦ Raridade pela nota oficial')
troca('O % de lojas executadas define a faixa base.', 'A nota oficial define a faixa base.')
troca('<small>% LOJAS EXEC.</small><strong>${pct(r.pct)}</strong>', '<small>NOTA</small><strong>${pct(getNota(r))}</strong>')
troca('${pct(leader.pct)} <small>DAS LOJAS EXECUTADAS</small>', '${pct(getNota(leader))} <small>NOTA OFICIAL</small>')
troca('lojas executadas de ${number(leader.lojas)} previstas no recorte atual.', 'lojas executadas de ${number(leader.lojas)} previstas · lojas ${pct(leader.pct)} · frequência ${pct(leader.pctv)}.')
troca('O ranking oficial continua definido por lojas executadas ÷ lojas de roteiro, com % de visitas cumpridas como desempate.', 'O ranking oficial usa a nota = 50% lojas executadas + 50% frequência, com desempate por % lojas, % frequência e % NewsPage.')
troca('<strong>Desempate:</strong> percentual de visitas cumpridas conforme o placar oficial.', '<strong>Nota:</strong> 50% lojas executadas + 50% frequência (visitas feitas ÷ visitas já cobradas até o corte). <strong>Desempate:</strong> % lojas, depois % frequência, depois % NewsPage realizado.')
for velho, novo in [('% VISITAS CUMPRIDAS', '% FREQUÊNCIA'), ('VISITAS CUMPRIDAS', 'FREQUÊNCIA'), ('das visitas cumpridas', 'de frequência'), ('de visitas cumpridas', 'de frequência'),
                    ('% visitas cumpridas', '% frequência'), ('visitas cumpridas', 'frequência'), ('Visitas cumpridas', 'Frequência')]:
    h = h.replace(velho, novo)
''' + "\nif falhas:", 'build')
p.write_text(s, encoding='utf-8')
print('FALHAS: ' + ' | '.join(falhas) if falhas else 'ok: todas as trocas aplicadas')
