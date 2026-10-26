"""Promove a regra da nota (validada pelo Gustavo em 26/10) a regra oficial do placar.
Roda uma vez sobre corpo_ajustado.html e build_placar.py; cada troca confere se o trecho existe."""
from pathlib import Path
AQUI = Path(__file__).resolve().parent
falhas = []

def troca(txt, velho, novo):
    if velho not in txt:
        falhas.append(velho[:90]); return txt
    return txt.replace(velho, novo)

c = (AQUI / 'corpo_ajustado.html').read_text(encoding='utf-8')
c = troca(c, """/* REGRA_NOTA (build --nota, versão de validação): promotores ordenados pela nota = (% lojas + % frequência) ÷ 2.
   % frequência = Σ mín(pesquisas, planejado) ÷ Σ máx(visitas vencidas, visitas feitas). As visitas planejadas dividem
   o mês em janelas iguais; uma visita só é cobrada quando a janela dela fecha (no mês fechado, o planejado inteiro). */
const REGRA_NOTA = __REGRA_NOTA__;""", """/* REGRA OFICIAL (validada pelo Gustavo em 26/10/2026): nota = 50% × % lojas executadas + 50% × % frequência.
   % frequência = Σ mín(pesquisas, planejado) ÷ Σ máx(visitas vencidas, visitas feitas). As visitas planejadas dividem
   o mês em janelas iguais; uma visita só é cobrada quando a janela dela fecha (no mês fechado, o planejado inteiro).
   Desempate: % lojas executadas → % frequência → % NewsPage realizado (pesquisas ÷ planejado) → nome. Vale para promotores e supervisores. */
const REGRA_NOTA = true;""")
# acumula pesquisas (para o % NewsPage) em promotores e supervisores; supervisores também com visitas vencidas
c = troca(c, "let p = P.get(k); if (!p){ p = {nomeRaw:colab, lojas:0, exec:0, plan:0, cump:0, venc:0, den:0, pend:[], uf:{}, supM:{}, meses:new Set()}; P.set(k, p); }",
             "let p = P.get(k); if (!p){ p = {nomeRaw:colab, lojas:0, exec:0, plan:0, cump:0, venc:0, den:0, pesq:0, pend:[], uf:{}, supM:{}, meses:new Set()}; P.set(k, p); }")
c = troca(c, "p.lojas++; p.exec += e; p.plan += plan; p.cump += c; p.venc += v; p.den += Math.max(v, c); if (!e) p.pend.push(v);",
             "p.lojas++; p.exec += e; p.plan += plan; p.cump += c; p.venc += v; p.den += Math.max(v, c); p.pesq += pesq; if (!e) p.pend.push(v);")
c = troca(c, "const ks = norm(sup); let s = S.get(ks); if (!s){ s = {nomeRaw:sup, lojas:0, exec:0, plan:0, cump:0, pessoas:new Set(), meses:new Set()}; S.set(ks, s); }\n      s.lojas++; s.exec += e; s.plan += plan; s.cump += c; s.pessoas.add(k); s.meses.add(m);",
             "const ks = norm(sup); let s = S.get(ks); if (!s){ s = {nomeRaw:sup, lojas:0, exec:0, plan:0, cump:0, den:0, pesq:0, pessoas:new Set(), meses:new Set()}; S.set(ks, s); }\n      s.lojas++; s.exec += e; s.plan += plan; s.cump += c; s.den += Math.max(v, c); s.pesq += pesq; s.pessoas.add(k); s.meses.add(m);")
c = troca(c, """  const ord = (a,b) => b.px - a.px || b.pvx - a.pvx || nm(a,b);
  const ordProm = REGRA_NOTA ? (a,b) => b.nota - a.nota || b.px - a.px || nm(a,b) : ord;""",
"""  // ordem oficial: nota → % lojas → % frequência → % NewsPage → nome
  const ord = (a,b) => b.nota - a.nota || b.px - a.px || b.pfx - a.pfx || b.pnp - a.pnp || nm(a,b);
  const ordProm = ord;""")
c = troca(c, """    const px = p.exec/p.lojas, pfx = p.den ? p.cump/p.den : px;   // sem visita vencida nem feita: a frequência acompanha o % de lojas
    return {key:k, nome:titulo(p.nomeRaw), sup:titulo(supRaw).split(' ')[0], supFull:titulo(supRaw), uf:moda(p.uf), lojas:p.lojas, exec:p.exec, plan:p.plan, cump:p.cump,
      venc:p.venc, den:p.den, pend:p.pend, px, pvx:p.plan ? p.cump/p.plan : 0, pfx, nota:(px + pfx) / 2}; })
    .sort(ordProm).map((r,i) => ({...r, pos:i+1, pct:Math.round(r.px*1000)/10, pctv:Math.round(r.pvx*1000)/10, pctf:Math.round(r.pfx*1000)/10, notaPct:Math.round(r.nota*1000)/10}));
  const sup = [...S.entries()].map(([k,s]) => ({key:k, nome:titulo(s.nomeRaw), prom:s.pessoas.size, lojas:s.lojas, exec:s.exec, plan:s.plan, cump:s.cump, px:s.exec/s.lojas, pvx:s.plan ? s.cump/s.plan : 0}))
    .sort(ord).map((r,i) => ({...r, pos:i+1, pct:Math.round(r.px*1000)/10, pctv:Math.round(r.pvx*1000)/10}));""",
"""    const px = p.exec/p.lojas, pfx = p.den ? p.cump/p.den : px;   // sem visita vencida nem feita: a frequência acompanha o % de lojas
    return {key:k, nome:titulo(p.nomeRaw), sup:titulo(supRaw).split(' ')[0], supFull:titulo(supRaw), uf:moda(p.uf), lojas:p.lojas, exec:p.exec, plan:p.plan, cump:p.cump,
      venc:p.venc, den:p.den, pesq:p.pesq, pend:p.pend, px, pvx:pfx, pfx, pnp:p.plan ? p.pesq/p.plan : 0, nota:(px + pfx) / 2}; })
    .sort(ordProm).map((r,i) => ({...r, pos:i+1, pct:Math.round(r.px*1000)/10, pctv:Math.round(r.pfx*1000)/10, pctf:Math.round(r.pfx*1000)/10, pctnp:Math.round(r.pnp*1000)/10, notaPct:Math.round(r.nota*1000)/10}));
  const sup = [...S.entries()].map(([k,s]) => { const px = s.exec/s.lojas, pfx = s.den ? s.cump/s.den : px;
      return {key:k, nome:titulo(s.nomeRaw), prom:s.pessoas.size, lojas:s.lojas, exec:s.exec, plan:s.plan, cump:s.cump, den:s.den, pesq:s.pesq, px, pvx:pfx, pfx, pnp:s.plan ? s.pesq/s.plan : 0, nota:(px + pfx) / 2}; })
    .sort(ord).map((r,i) => ({...r, pos:i+1, pct:Math.round(r.px*1000)/10, pctv:Math.round(r.pfx*1000)/10, pctf:Math.round(r.pfx*1000)/10, pctnp:Math.round(r.pnp*1000)/10, notaPct:Math.round(r.nota*1000)/10}));""")
c = troca(c, "+ (REGRA_NOTA ? ' · promotores: nota = (% lojas + % frequência) ÷ 2; visita cobrada só depois que a janela dela fecha' : ''); });",
             "+ ' · nota = 50% lojas + 50% frequência; visita cobrada só depois que a janela dela fecha'; });")
c = troca(c, """  document.title = 'Placar Farma Q4 · Nota (validação)';
  document.querySelector('.rules').innerHTML = `
    <div class="rule"><b>Versão para validação</b><p>Promotores pela nova nota (lojas + frequência). Supervisores seguem na regra atual (% de lojas). Não é o placar oficial.</p></div>
    <div class="rule"><b>Nota do promotor</b><p>(% lojas executadas + % frequência) ÷ 2. No Q4, cada parte soma os totais dos meses apurados (não é média dos %).</p></div>""",
"""  document.querySelector('.rules').innerHTML = `
    <div class="rule"><b>Loja executada</b><p>Loja do roteiro do mês com pelo menos 1 pesquisa NewsPage no mês.</p></div>
    <div class="rule"><b>Nota</b><p>50% × % lojas executadas + 50% × % frequência. Vale para promotores e supervisores. No Q4, cada parte soma os totais dos meses apurados (não é média dos %).</p></div>""")
c = troca(c, """    <div class="rule"><b>Desempate</b><p>% de lojas executadas; depois ordem alfabética.</p></div>`;""",
"""    <div class="rule"><b>Desempate</b><p>1º % de lojas executadas · 2º % frequência · 3º % NewsPage realizado (pesquisas ÷ planejado). Premiação: 3 promotores e 1 supervisor, com roteiro nos 3 meses.</p></div>`;""")
c = troca(c, "/* valor que ordena o grupo: promotores usam a nota na versão REGRA_NOTA; supervisores seguem no % de lojas */\nconst vg = (r, g) => g==='prom' ? vp(r) : r.pct;",
             "/* valor que ordena o grupo: a nota oficial, para promotores e supervisores */\nconst vg = (r, g) => vp(r);")
c = troca(c, "    const det = g==='prom' && REGRA_NOTA ? `<div class=\"meta\">lojas ${pct(r.pct)} · frequência ${pct(r.pctf)}</div>` : '';",
             "    const det = `<div class=\"meta\">lojas ${pct(r.pct)} · frequência ${pct(r.pctf)}</div>`;")
c = troca(c, "    ? [['pos','Posição',''],['nome','Promotor',''],['sup','Supervisor',''],['uf','UF','c'],['exec','Lojas exec.','r'],['pct','% Lojas exec.','r'],['visitas','Visitas feitas / cobradas','r'],['pctf','% Frequência','r'],['notaPct','Nota','r'],['eleg','Elegibilidade Q4','c']]",
             "    ? [['pos','Posição',''],['nome','Promotor',''],['sup','Supervisor',''],['uf','UF','c'],['exec','Lojas exec.','r'],['pct','% Lojas exec.','r'],['visitas','Visitas feitas / cobradas','r'],['pctf','% Frequência','r'],['notaPct','Nota','r'],['pctnp','% NewsPage','r'],['eleg','Elegibilidade Q4','c']]")
c = troca(c, "  sup:[['pos','Posição',''],['nome','Supervisor',''],['prom','Promotores','r'],['exec','Lojas exec.','r'],['pct','% Lojas exec.','r'],['pctv','% Visitas','r'],['eleg','Elegibilidade Q4','c']]",
             "  sup:[['pos','Posição',''],['nome','Supervisor',''],['prom','Promotores','r'],['exec','Lojas exec.','r'],['pct','% Lojas exec.','r'],['pctf','% Frequência','r'],['notaPct','Nota','r'],['pctnp','% NewsPage','r'],['eleg','Elegibilidade Q4','c']]")
c = troca(c, "<td class=\"r mono\" title=\"cobradas = visitas vencidas até o corte, ou feitas se for maior\">${r.cump}/${r.den}</td><td class=\"r mono\">${pct(r.pctf)}</td><td class=\"r pct\">${pct(r.notaPct)}</td><td class=\"c\">${chip(r.eleg)}</td></tr>`",
             "<td class=\"r mono\" title=\"cobradas = visitas vencidas até o corte, ou feitas se for maior\">${r.cump}/${r.den}</td><td class=\"r mono\">${pct(r.pctf)}</td><td class=\"r pct\">${pct(r.notaPct)}</td><td class=\"r mono\">${pct(r.pctnp)}</td><td class=\"c\">${chip(r.eleg)}</td></tr>`")
c = troca(c, "      : `<tr class=\"${cls}\"><td class=\"pos\">${r.pos}º</td><td>${esc(r.nome)}</td><td class=\"r mono\">${r.prom}</td><td class=\"r mono\">${int(r.exec)}/${int(r.lojas)}</td><td class=\"r pct\">${pct(r.pct)}</td><td class=\"r mono\">${pct(r.pctv)}</td><td class=\"c\">${chip(r.eleg)}</td></tr>`; }).join('');",
             "      : `<tr class=\"${cls}\"><td class=\"pos\">${r.pos}º</td><td>${esc(r.nome)}</td><td class=\"r mono\">${r.prom}</td><td class=\"r mono\">${int(r.exec)}/${int(r.lojas)}</td><td class=\"r mono\">${pct(r.pct)}</td><td class=\"r mono\">${pct(r.pctf)}</td><td class=\"r pct\">${pct(r.notaPct)}</td><td class=\"r mono\">${pct(r.pctnp)}</td><td class=\"c\">${chip(r.eleg)}</td></tr>`; }).join('');")
c = troca(c, "<span class=\"num\">time ${pct(s.pct)} · ${rows.length} promotores</span>", "<span class=\"num\">time nota ${pct(s.notaPct)} · ${rows.length} promotores</span>")
(AQUI / 'corpo_ajustado.html').write_text(c, encoding='utf-8')

b = (AQUI / 'build_placar.py').read_text(encoding='utf-8')
b = troca(b, "pagina = pagina.replace('__MESES__', json.dumps(MESES, ensure_ascii=False)).replace('__REGRA_NOTA__', 'true' if NOTA else 'false')",
             "pagina = pagina.replace('__MESES__', json.dumps(MESES, ensure_ascii=False))")
b = troca(b, "for ph in ['__PACOTES__', '__MESES__', '__SPOT_LOGO__', '__RK_LOGO__', '__REGRA_NOTA__']:", "for ph in ['__PACOTES__', '__MESES__', '__SPOT_LOGO__', '__RK_LOGO__']:")
(AQUI / 'build_placar.py').write_text(b, encoding='utf-8')
print('FALHAS: ' + ' | '.join(falhas) if falhas else 'ok: todas as trocas aplicadas')
