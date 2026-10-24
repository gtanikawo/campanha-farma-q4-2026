/* ===== Farma Cards v3: oficial × jogo, missões com evidência, ficha, confronto, crônica, importação com prévia =====
   Este bloco vem depois do resto do script: as funções com o mesmo nome substituem as anteriores.
   Regra de ouro: nada aqui altera posição, desempate, elegibilidade ou premiação. O XP é CALCULADO das regras
   (não é acumulado), então abrir carta, importar de novo ou recarregar nunca soma XP repetido. */

/* --- rótulos de origem da informação --- */
const LB = {of:['OFICIAL','Resultado validado no placar'], rpg:['RPG','Atributo de jogo calculado'], sim:['SIMULAÇÃO','Resultado hipotético; não muda nada oficial'], pend:['PENDENTE','Informação ainda não validada']};
const lb = k => `<span class="lb lb-${k}" title="${LB[k][1]}">${LB[k][0]}</span>`;
const MESES_Q4 = ['out','nov','dez'];

/* --- meses: corte e fechado (vêm do placar) --- */
function mesFechado(k){ return !!(MESES[k] && MESES[k].disponivel && MESES[k].fechado) }
function corteBR(k){ const c = MESES[k] && MESES[k].corte; return c ? c.slice(8,10)+'/'+c.slice(5,7) : '' }

/* --- estado e evidência de cada missão --- */
const fmtP = v => v==null ? '—' : pct(v);
function evidencia(m, p){
  const o = p.out, n = p.nov, d = p.dez, q = p.q4, s = r => r ? getNPScore(r) : null, v = r => r ? Number(r.pctv) : null;
  switch (m.id){
    case 'a1_passo': case 'a1_firme': case 'a1_over': case 'a1_perf': return `Outubro: ${fmtP(s(o))} das lojas executadas`;
    case 'a1_disc': return `Outubro: ${fmtP(v(o))} das visitas cumpridas`;
    case 'a2_evolui': case 'a2_salto': return n && o ? `Out ${fmtP(s(o))} → Nov ${fmtP(s(n))} (${(s(n)-s(o)>=0?'+':'')}${(s(n)-s(o)).toFixed(1).replace('.',',')} p.p.)` : 'Precisa de outubro e novembro';
    case 'a2_const': case 'a2_duplo': return `Out ${fmtP(s(o))} · Nov ${fmtP(s(n))}`;
    case 'a2_disc': return `Novembro: ${fmtP(v(n))} das visitas cumpridas`;
    case 'a3_luas': return `Roteiro em: ${['out','nov','dez'].filter(k => p[k]).map(monthLabel).join(', ') || 'nenhum mês'}`;
    case 'a3_escalada': case 'a3_trilogia': return `Out ${fmtP(s(o))} · Nov ${fmtP(s(n))} · Dez ${fmtP(s(d))}`;
    case 'a3_lenda': return q ? `Q4: ${fmtP(s(q))} das lojas · ${fmtP(v(q))} das visitas` : 'Precisa do trimestre completo';
    case 'a3_podio': return q ? `Posição oficial no Q4: ${q.pos}º` : 'Precisa do trimestre completo';
  }
  return '';
}
function estadoMissao(m, aberto, feito){
  const k = ATOS[m.ato-1].key, fechado = mesFechado(k);
  if (!aberto) return {st:'bloq', txt:'Bloqueada', det:`Abre quando ${ATOS[m.ato-1].mes.toLowerCase()} entrar no placar`};
  if (feito) return fechado ? {st:'ok', txt:'Concluída', det:'Mês fechado'} : {st:'ok-parcial', txt:'Atingida até agora', det:`Mês parcial (até ${corteBR(k)}): confirma no fechamento`};
  return fechado ? {st:'nao', txt:'Não atingida', det:'Mês fechado'} : {st:'and', txt:'Em andamento', det:`Mês parcial (até ${corteBR(k)})`};
}
function missoesDe(r){
  const p = jornada(r);
  return MISSOES.map(m => { const aberto = atoAberto(m.ato); let feito = false;
    if (aberto){ try { feito = !!m.test(p) } catch { feito = false } }
    return {...m, aberto, feito, estado: estadoMissao(m, aberto, feito), evid: aberto ? evidencia(m, p) : ''} });
}

/* --- elegibilidade (mesma regra do placar oficial) --- */
function elegibilidade(r){
  const com = [], sem = [], aguard = [];
  MESES_Q4.forEach(k => { if (!hasMonth(k)) aguard.push(monthLabel(k).toLowerCase()); else (allRows(k).some(x => identity(x) === identity(r)) ? com : sem).push(monthLabel(k).toLowerCase()); });
  const j = a => a.join(', ').replace(/, ([^,]*)$/, ' e $1');
  if (sem.length) return {st:'inelegivel', txt:'Inelegível', just:`Sem ${r.kind==='sup'?'time':'roteiro'} em ${j(sem)} (mês apurado).`};
  if (!aguard.length) return {st:'elegivel', txt:'Elegível', just:'Com roteiro nos três meses.'};
  return {st:'pendente', txt:'Pendente', just:`Com ${r.kind==='sup'?'time':'roteiro'} em ${j(com)}; aguardando ${j(aguard)}.`};
}

/* --- acumulado até cada mês, posição nesse acumulado e nível ao fim do mês --- */
function acumuladoAte(k){
  const lim = MESES_Q4.indexOf(k), meses = MESES_Q4.slice(0, lim+1).filter(hasMonth), M = new Map();
  meses.forEach(mk => allRows(mk).forEach(r => { const id = identity(r); const a = M.get(id) || {...r, lojas:0, exec:0, plan:0, cump:0, _m:0};
    a.lojas += Number(r.lojas)||0; a.exec += Number(r.exec)||0; a.plan += Number(r.plan)||0; a.cump += Number(r.cump)||0; a._m++; M.set(id, a); }));
  const rows = [...M.values()].map(a => ({...a, px:a.exec/a.lojas, pvx:a.plan ? a.cump/a.plan : 0, pct:Math.round(a.exec/a.lojas*1000)/10, pctv:a.plan ? Math.round(a.cump/a.plan*1000)/10 : 0}));
  ['prom','sup'].forEach(kind => rows.filter(r => r.kind===kind).sort((a,b) => b.px-a.px || b.pvx-a.pvx || (a.nome<b.nome?-1:1)).forEach((r,i) => r.pos = i+1));
  return new Map(rows.map(r => [identity(r), r]));
}
function historico(r){
  const id = identity(r);
  return MESES_Q4.map((k, i) => {
    if (!hasMonth(k)) return {k, carregado:false};
    const mes = allRows(k).find(x => identity(x) === id) || null, acum = acumuladoAte(k).get(id) || null;
    let nivel = null, xpT = null;
    if (acum){ const base = xpBase(acum), ms = missoesDe(r).filter(m => m.ato <= i+1 && m.feito); xpT = base + ms.reduce((s,m)=>s+m.xp,0); nivel = Math.max(1, Math.min(NIVEL_MAX, 1 + Math.floor(xpT/XP_NIVEL))); }
    return {k, carregado:true, parcial:!mesFechado(k), mes, acum, nivel, xp:xpT};
  });
}

/* --- extrato de XP: de onde vem cada ponto (calculado, sem duplicar) --- */
function extratoXP(r){
  const linhas = [{origem:`XP base do PWR (${Math.round(power(r))} de 100)`, xp:xpBase(r), evid:'recalculado a cada atualização do placar'}];
  missoesDe(r).filter(m => m.feito).forEach(m => linhas.push({origem:`Missão ${m.titulo} (${ATOS[m.ato-1].nome})`, xp:m.xp, evid:m.evid}));
  return linhas;
}

/* --- raridade explicada --- */
function raridadeExplicada(r){
  const v = getNPScore(r), t = tier(r), idx = RARITIES.findIndex(x => x.id === t.id), prox = RARITIES[idx+1];
  const req = [
    [`${thresholds.mythic}%+ das lojas executadas`, v >= thresholds.mythic, fmtP(v)],
    [`${gates.mythicVisit}%+ das visitas cumpridas`, Number(r.pctv) >= gates.mythicVisit, fmtP(Number(r.pctv))],
    [`${gates.mythicExec}+ lojas executadas`, Number(r.exec) >= gates.mythicExec, number(r.exec)]];
  return {t, v, falta: prox ? Math.max(0, prox.min() - v) : 0, prox, req, foil:isFoil(r)};
}

/* --- ficha do personagem (frente com dados, verso com raridade) --- */
function openCard(id){
  const r = findRowById(id); if (!r) return; activeDetail = id;
  const t = tier(r), kind = r.kind || 'prom', el = elegibilidade(r), rx = raridadeExplicada(r), hist = historico(r), ms = missoesDe(r);
  const xpV = xp(r), lvl = level(r), falta = lvl >= NIVEL_MAX ? 0 : XP_NIVEL - (xpV % XP_NIVEL), tr = trilhaDe(r);
  const E = getNPScore(r)||0, D = Number(r.pctv)||0, V = volumeIndex(r);
  const comp = [['Execução', E, .70, '% lojas executadas'], ['Disciplina', D, .20, '% visitas cumpridas'], ['Volume', V, .10, `lojas executadas ÷ 50 (máx. 100)`]];
  const periodo = activeKey==='q4' ? 'Q4 acumulado · ' + (data().fechado ? 'trimestre fechado' : 'parcial até ' + corteBR('q4')) : monthLabel(activeKey) + ' · ' + (mesFechado(activeKey) ? 'mês fechado' : 'parcial até ' + corteBR(activeKey));
  const ultimo = hist.filter(h => h.carregado && h.nivel != null), subiu = ultimo.length > 1 && ultimo[ultimo.length-1].nivel > ultimo[ultimo.length-2].nivel;
  const novas = ms.filter(m => m.feito && m.ato === Math.max(...ATOS.filter(a => atoAberto(a.num)).map(a => a.num), 0));
  const verso = `<div class="detail-back"><div class="seal">${t.icon} ${esc(t.name.toUpperCase())} ${t.icon}</div><div class="back-sigil">${glyph(r)}</div>
    <div><p><b>Por que ${esc(t.name)}?</b> ${fmtP(rx.v)} das lojas executadas ${lb('of')}. ${rx.prox ? `Faltam ${rx.falta.toFixed(1).replace('.',',')} p.p. para ${esc(rx.prox.name)}.` : 'Faixa máxima.'}</p>
    <p style="margin-top:6px"><b>Holográfica</b> ${lb('rpg')}<br>${rx.req.map(([l,ok,val]) => `${ok?'✓':'✗'} ${l} <small>(${val})</small>`).join('<br>')}</p></div>
    <div class="seal">FARMA CARDS · Q4 2026</div></div>`;
  $('modalTitle').textContent = 'Ficha do personagem';
  $('modalBody').innerHTML = `<div class="detail-layout"><div><div class="detail-card-wrap" style="--rc:${t.color}"><div class="detail-card-3d" id="detailCard3D"><div class="detail-side">${cardHTML(r, kind, false)}</div>${verso}</div></div>
      <button class="btn" style="width:100%;margin-top:9px" id="flipCard">↻ Virar carta (raridade)</button><button class="btn" style="width:100%;margin-top:7px" id="copyCardInfo">⧉ Copiar ficha</button></div>
    <div class="detail-stats">
      <div class="eyebrow">${kind==='sup'?'Carta de comandante':'Carta de campo'} · ${esc(t.name)}${rx.foil?' · Holográfica':''}</div>
      <h3>${esc(r.nome)}</h3>
      <div class="sup-line">${kind==='prom'?`Supervisor ${esc(r.supFull||r.sup||'—')} · ${esc(r.uf||'UF não informada')}`:`${number(r.prom)} promotores no time`} · posição oficial <b>${r.pos}º</b> ${lb('of')} · ${esc(periodo)}</div>
      ${subiu ? `<div class="levelup">✦ Subiu para o nível ${ultimo[ultimo.length-1].nivel} em ${monthLabel(ultimo[ultimo.length-1].k).toLowerCase()}</div>` : ''}
      <div class="casa-line">⌛ ${(() => { const pt = patente(r); return pt ? `<b>${esc(pt.nome)}</b> · ${textoCasa(pt.meses)}` : '<b>Tempo de casa pendente</b> (não encontrado no cadastro)'; })()} ${lb(patente(r)?'of':'pend')} <small>patente pelo tempo de casa; não entra no PWR nem no ranking</small></div>
      <div class="detail-section-title">Desempenho ${lb('of')}</div>
      <div class="detail-attributes"><div class="attribute"><span>% LOJAS EXECUTADAS</span><b style="color:${t.color}">${pct(r.pct)}</b></div><div class="attribute"><span>LOJAS EXECUTADAS / PREVISTAS</span><b>${number(r.exec)} / ${number(r.lojas)}</b></div>
        <div class="attribute"><span>% VISITAS CUMPRIDAS (desempate)</span><b>${pct(r.pctv)}</b></div><div class="attribute"><span>ELEGIBILIDADE Q4</span><b><span class="eleg ${el.st}">${el.txt}</span></b><small>${esc(el.just)}</small></div></div>
      <div class="detail-section-title">Poder de jogo (PWR) ${lb('rpg')}</div>
      <div class="pwr-break">${comp.map(([n,val,w,desc]) => `<div class="pwr-row"><span>${n} <small>${desc}</small></span><div class="duel-track"><div class="duel-fill" style="width:${Math.min(100,val)}%;background:${t.color}"></div></div><b>${Math.round(val)} × ${String(w).replace('.',',')} = ${(val*w).toFixed(1).replace('.',',')}</b></div>`).join('')}
        <div class="pwr-total">PWR = ${Math.round(power(r))} de 100</div></div>
      <div class="detail-section-title">Nível e XP ${lb('rpg')}</div>
      <div class="lvl-line"><div class="lvl-badge" style="border-color:${t.color};color:${t.color}">${lvl}</div><div style="flex:1"><b>Nível ${lvl} · ${number(xpV)} XP · ${esc(tr.atual.nome)}</b><div class="card-progress" style="height:7px;margin-top:8px"><span style="width:${(xpV%XP_NIVEL)/XP_NIVEL*100}%;background:${t.color}"></span></div><small>${lvl>=NIVEL_MAX?'Nível máximo.':`Faltam ${number(falta)} XP para o nível ${lvl+1}.`} O XP é calculado das regras a cada atualização: abrir a carta ou importar de novo não soma XP.</small></div></div>
      <div class="xp-ledger">${extratoXP(r).map(l => `<div><span>${esc(l.origem)}<small>${esc(l.evid)}</small></span><b>+${number(l.xp)}</b></div>`).join('')}<div class="tot"><span>Total</span><b>${number(xpV)} XP</b></div></div>
      ${novas.length ? `<div class="detail-section-title">Conquistas do ato atual ${lb('rpg')}</div><div class="card-badges">${novas.map(m => `<span class="mini-badge new">${m.icon} ${esc(m.titulo)}</span>`).join('')}</div>` : ''}
      <div class="detail-section-title">Crônica mensal ${lb('of')}</div>
      <div class="hist">${hist.map((h,i) => { if (!h.carregado) return `<div class="hist-row pend"><b>${monthLabel(h.k)}</b><span>${lb('pend')} aguardando apuração</span></div>`;
        const ant = hist[i-1] && hist[i-1].carregado ? hist[i-1] : null;
        const dpp = h.mes && ant && ant.mes ? (getNPScore(h.mes) - getNPScore(ant.mes)) : null, dpos = h.acum && ant && ant.acum ? ant.acum.pos - h.acum.pos : null;
        return `<div class="hist-row"><b>${monthLabel(h.k)}${h.parcial?` <small>até ${corteBR(h.k)}</small>`:''}</b>
          <span>Mês: ${h.mes ? `${pct(h.mes.pct)} (${h.mes.exec}/${h.mes.lojas})` : 'sem roteiro'}${dpp!=null?` · ${dpp>=0?'+':''}${dpp.toFixed(1).replace('.',',')} p.p.`:''}</span>
          <span>Acumulado: ${h.acum ? `${pct(h.acum.pct)} · ${h.acum.pos}º${dpos?` (${dpos>0?'↑':'↓'}${Math.abs(dpos)})`:''}` : '—'}</span><span>Nível ${h.nivel ?? '—'} ${lb('rpg')}</span></div>`; }).join('')}</div>
      <div class="detail-actions"><button class="btn primary" id="compareThis">⚔ Comparar esta carta</button><button class="btn" id="copyRank">Copiar posição</button></div>
    </div></div>`;
  $('cardModal').hidden = false;
  const det = $('detailCard3D'); det.querySelector('.detail-side .player-card')?.removeAttribute('data-open-card');
  $('flipCard').onclick = () => det.classList.toggle('flipped');
  $('copyCardInfo').onclick = () => copyText(`${r.nome}\n${kind==='sup'?'Supervisor':'Promotor'} · posição oficial ${r.pos}º (${periodo})\n% lojas executadas (OFICIAL): ${pct(r.pct)} (${r.exec} de ${r.lojas})\n% visitas cumpridas (OFICIAL): ${pct(r.pctv)}\nElegibilidade Q4: ${el.txt}\nRaridade (RPG): ${t.name} · PWR ${Math.round(power(r))} · nível ${lvl} · ${number(xpV)} XP`);
  $('copyRank').onclick = () => copyText(`${r.nome} — posição oficial ${r.pos}º · ${pct(r.pct)} das lojas executadas (${periodo})`);
  $('compareThis').onclick = () => { closeModal('cardModal'); gotoPage('duel'); fillDuelSelects(); $('fighterA').value = identity(r); const nx = allRows().find(x => identity(x)!==identity(r) && x.kind===r.kind); if (nx) $('fighterB').value = identity(nx); renderDuel(); };
}

/* --- missões: estado, objetivo, progresso, recompensa --- */
const STC = {ok:'Concluída', 'ok-parcial':'Atingida até agora', and:'Em andamento', nao:'Não atingida', bloq:'Bloqueada'};
function renderJourney(){
  const r = findRowById($('journeyPick').value);
  if (!r){ $('journeyBox').innerHTML = '<div class="empty-state">Escolha um nome para ver a jornada.</div>'; return; }
  const ms = missoesDe(r), t = trilhaDe(r);
  const lista = ATOS.map(a => `<div class="jl-act">${a.nome} · ${a.mes}${atoAberto(a.num)?(mesFechado(a.key)?' · mês fechado':` · parcial até ${corteBR(a.key)}`):' · selado'}</div>` +
    ms.filter(m => m.ato===a.num).map(m => `<div class="jl-row st-${m.estado.st}"><span class="st">${m.estado.st.startsWith('ok')?'✓':m.estado.st==='bloq'?'🔒':m.estado.st==='nao'?'✗':'…'}</span>
      <div><b>${m.icon} ${esc(m.titulo)}</b> <span class="mstate ${m.estado.st}">${m.estado.txt}</span><small>Objetivo: ${esc(m.desc)}</small>${m.evid?`<small>Progresso ${lb('of')}: ${esc(m.evid)}</small>`:''}<small>${esc(m.estado.det)}</small></div>
      <span class="xp">${m.feito?'+':''}${m.xp} XP</span></div>`).join('')).join('');
  $('journeyBox').innerHTML = `<div class="journey"><div class="journey-card"><div class="eyebrow">${r.kind==='sup'?'Supervisor':'Promotor'}</div><h3>${esc(r.nome)}</h3>
    <div style="font-size:12px;color:var(--muted)">${ms.filter(m=>m.feito).length} de ${ms.filter(m=>m.aberto).length} missões abertas atingidas</div><div class="jc-tier">${esc(t.atual.nome)}</div>
    <div style="margin-top:10px">${trilhaMini(r)}</div><div class="jc-next">Posição oficial: ${r.pos}º · ${pct(r.pct)} das lojas executadas ${lb('of')}<br>Elegibilidade Q4: ${elegibilidade(r).txt}</div></div><div class="journey-list">${lista}</div></div>`;
}

/* --- confronto: rápido, tático e equipe --- */
let duelMode = 'rapido';
function fillDuelSelects(){
  const kind = duelMode==='equipe' ? 'sup' : 'prom';
  const people = allRows().filter(r => r.kind===kind).sort((a,b) => a.nome.localeCompare(b.nome,'pt-BR'));
  optionsFill($('fighterA'), people, kind==='sup'?'Escolha o supervisor A':'Escolha o personagem A');
  optionsFill($('fighterB'), people, kind==='sup'?'Escolha o supervisor B':'Escolha o personagem B');
  const top = (data()[kind]||[]);
  if (!people.some(p => identity(p)===$('fighterA').value) && top[0]) $('fighterA').value = identity({...top[0], kind});
  if (!people.some(p => identity(p)===$('fighterB').value) && top[1]) $('fighterB').value = identity({...top[1], kind});
}
function renderDuel(){
  const a = findRowById($('fighterA').value), b = findRowById($('fighterB').value);
  if (!a || !b){ $('duelResult').innerHTML = '<div class="empty-state">Escolha dois participantes para iniciar o confronto.</div>'; return; }
  if (identity(a)===identity(b)){ $('duelResult').innerHTML = '<div class="empty-state">Escolha dois participantes diferentes.</div>'; return; }
  const at = r => [['Execução', getNPScore(r)||0, .70], ['Disciplina', Number(r.pctv)||0, .20], ['Volume', volumeIndex(r), .10]];
  const A = at(a), B = at(b), pa = power(a), pb = power(b);
  const vant = A.map((x,i) => ({n:x[0], a:x[1], b:B[i][1], w:x[2], cont:(x[1]-B[i][1])*x[2]}));
  const venc = pa===pb ? null : pa>pb ? a : b, perd = venc===a ? b : a;
  const resumo = venc ? `${esc(venc.nome)} tem maior PWR neste comparativo (${Math.round(Math.max(pa,pb))} × ${Math.round(Math.min(pa,pb))}).` : 'PWR empatado.';
  const contra = vant.filter(v => (venc===a ? v.b>v.a : v.a>v.b)).map(v => v.n);
  const linhas = vant.map((v,i) => { const max = Math.max(v.a, v.b, 1), w = v.a>v.b?'A':v.b>v.a?'B':'=';
    return `<div class="metric-row duel-anim" style="animation-delay:${duelMode==='rapido'?0:i*.45}s"><span style="color:var(--muted)">${v.n}</span><div><div style="display:flex;justify-content:space-between;margin-bottom:5px"><span>${Math.round(v.a)}</span><span>${Math.round(v.b)}</span></div><div class="duel-track" style="display:flex"><div class="duel-fill" style="width:${v.a/max*50}%;border-radius:8px 0 0 8px"></div><div style="flex:1"></div><div class="duel-fill" style="width:${v.b/max*50}%;background:#8C1D5A;border-radius:0 8px 8px 0"></div></div>${duelMode!=='rapido'?`<small class="tat">Peso ${String(v.w).replace('.',',')} → ${v.cont>=0?'A':'B'} +${Math.abs(v.cont).toFixed(1).replace('.',',')} pontos de PWR</small>`:''}</div><span class="value">${w==='='?'EMPATE':w+' VENCE'}</span></div>`; }).join('');
  const oficial = `Posição oficial: A ${a.pos}º · B ${b.pos}º ${lb('of')}`;
  $('duelResult').innerHTML = `<div class="duel-result">${fighterPanel(a)}${fighterPanel(b)}</div>
    <div class="panel" style="margin-top:14px"><div class="panel-head"><h3>⚔ ${duelMode==='equipe'?'Confronto de equipe':duelMode==='tatico'?'Análise tática':'Duelo rápido'} ${lb('sim')}</h3><span>${oficial}</span></div>
    <div class="metric-compare">${linhas}<div class="metric-row duel-anim" style="animation-delay:${duelMode==='rapido'?0:1.35}s"><span style="color:var(--muted)">PWR</span><div><div style="display:flex;justify-content:space-between"><b>${Math.round(pa)}</b><b>${Math.round(pb)}</b></div></div><span class="value">${pa===pb?'EMPATE':pa>pb?'A VENCE':'B VENCE'}</span></div></div>
    <div class="battle-outcome duel-anim" style="animation-delay:${duelMode==='rapido'?0:1.6}s">✧ Confronto concluído. ${resumo}${venc && contra.length ? ` ${esc(perd.nome)} tem vantagem em ${contra.join(' e ').toLowerCase()}.` : ''}${duelMode==='equipe'?' Os números do time somam as lojas de todos os promotores (executadas ÷ previstas), não a média dos %.':''}<br><small style="color:var(--muted)">Simulação de atributos de jogo. Não altera o ranking oficial, a raridade nem a premiação.</small></div></div>`;
}

/* --- crônica: mês a mês, com acumulado, variação e mudança de posição --- */
let cronVista = 'acum';
function renderChronicle(selected){
  const carregados = MESES_Q4.filter(hasMonth);
  selected = selected && hasMonth(selected) ? selected : (carregados[carregados.length-1] || 'out');
  $('monthTrack').innerHTML = MESES_Q4.map((k,i) => { const ready = hasMonth(k), d = MESES[k] || {};
    return `<button class="month-node ${ready?'available':'future'} ${k===selected?'sel':''}" data-month="${k}" ${ready?'':'disabled'}><span class="node-orb">${ready?(mesFechado(k)?'✓':'◐'):'⌁'}</span><div class="month-name">${ATOS[i].nome} · ${monthLabel(k)}</div><div class="month-state">${ready?(mesFechado(k)?'Mês fechado':`Parcial até ${corteBR(k)}`):'Aguardando apuração'}</div></button>`; }).join('');
  document.querySelectorAll('[data-month]').forEach(b => b.addEventListener('click', () => renderChronicle(b.dataset.month)));
  if (!hasMonth(selected)){ $('monthResults').innerHTML = `<h3>✧ Este capítulo ainda está selado</h3><p>Ele abre quando o placar oficial trouxer ${monthLabel(selected).toLowerCase()}. Mês sem dado nunca vira zero.</p>`; return; }
  const idx = MESES_Q4.indexOf(selected), ant = MESES_Q4.slice(0, idx).filter(hasMonth).pop();
  const acum = acumuladoAte(selected), acumAnt = ant ? acumuladoAte(ant) : null, mes = MESES[selected];
  const linhas = (cronVista==='mes' ? mes.prom.map(r => ({...r, kind:'prom'})) : [...acum.values()].filter(r => r.kind==='prom').sort((a,b) => a.pos-b.pos)).slice(0, 10);
  const totL = cronVista==='mes' ? mes.tot : [...acum.values()].filter(r=>r.kind==='prom').reduce((s,r)=>({lojas:s.lojas+r.lojas, exec:s.exec+r.exec}),{lojas:0,exec:0});
  $('monthResults').innerHTML = `<div class="panel-head"><div><h3>${ATOS[idx].nome} · ${monthLabel(selected)} ${lb('of')}</h3><span>${mesFechado(selected)?'Mês fechado':`Parcial até ${corteBR(selected)}`} · ${cronVista==='mes'?'só o mês':'acumulado do Q4 até este mês'}</span></div>
      <div class="view-segment"><button class="${cronVista==='acum'?'active':''}" data-cv="acum">Acumulado</button><button class="${cronVista==='mes'?'active':''}" data-cv="mes">Só o mês</button></div></div>
    <div class="stat-grid" style="margin:0 0 15px"><div class="stat"><div class="label">Lojas no roteiro</div><strong>${number(totL.lojas)}</strong></div><div class="stat"><div class="label">Lojas executadas</div><strong>${number(totL.exec)}</strong></div><div class="stat"><div class="label">Execução</div><strong>${pct(totL.lojas?totL.exec/totL.lojas*100:0)}</strong></div><div class="stat"><div class="label">Meses no acumulado</div><strong>${MESES_Q4.slice(0,idx+1).filter(hasMonth).length}</strong></div></div>
    <h3 style="margin:12px 0 8px">Top 10 · ${cronVista==='mes'?monthLabel(selected):'acumulado até '+monthLabel(selected).toLowerCase()}</h3>
    ${linhas.map(r => { const pa = acumAnt && acumAnt.get(identity(r)); const dpos = cronVista==='acum' && pa ? pa.pos - r.pos : null; const dpp = cronVista==='acum' && pa ? r.pct - pa.pct : null;
      return `<div class="rank-line"><span class="rank-pos">#${r.pos}</span><div><div class="rank-name">${esc(r.nome)} ${dpos?`<small class="${dpos>0?'up':'down'}">${dpos>0?'↑':'↓'}${Math.abs(dpos)}</small>`:''}</div><div class="rank-bar"><span style="width:${Math.min(100,r.pct)}%"></span></div></div><span class="rank-percent">${pct(r.pct)}${dpp!=null?`<small> ${dpp>=0?'+':''}${dpp.toFixed(1).replace('.',',')} p.p.</small>`:''}</span></div>`; }).join('')}
    <p style="margin-top:13px">${ant ? `Setas e p.p. comparam com o acumulado até ${monthLabel(ant).toLowerCase()}.` : 'Primeiro capítulo: ainda não há mês anterior para comparar.'} O retrato publicado de cada semana fica guardado no histórico de versões do site.</p>`;
  document.querySelectorAll('[data-cv]').forEach(b => b.addEventListener('click', () => { cronVista = b.dataset.cv; renderChronicle(selected); }));
}

/* --- coleção: período e estado --- */
function setupPeriodo(){
  const s = $('periodFilter'); if (!s) return;
  s.innerHTML = ['out','nov','dez','q4'].map(k => `<option value="${k}" ${hasMonth(k)?'':'disabled'} ${k===activeKey?'selected':''}>${monthLabel(k)}${hasMonth(k)?(k==='q4'?'':(mesFechado(k)?' (fechado)':` (até ${corteBR(k)})`)):' (aguardando)'}</option>`).join('');
  s.onchange = () => { activeKey = s.value; refreshApp(); };
}

/* --- pacote: revelação carta a carta, efeito pela raridade calculada --- */
function renderPack(){
  if (!packDraw.length){ $('packCards').innerHTML = ''; return; }
  $('packCards').innerHTML = packDraw.map((r,i) => `<div class="pack-slot ${packRevealed?'revealed reveal-'+tier(r).id:''}" style="animation-delay:${i*.45}s">${packRevealed?cardHTML(r, r.kind, true):`<button class="pack-cover" data-reveal-one="${i}"><span class="seal">✧</span><strong>CARTA SELADA</strong><span style="font-size:9px">TOQUE PARA REVELAR</span></button>`}</div>`).join('');
  if (packRevealed) $('packCards').querySelectorAll('[data-open-card]').forEach(el => el.addEventListener('click', () => { closeModal('packModal'); openCard(el.dataset.openCard); }));
}

/* --- importação com prévia e validação reforçada --- */
let importPend = null;
function checarDados(m){
  const prob = validMeses(m); if (prob !== true) return {erros:[prob], avisos:[]};
  const erros = [], avisos = [];
  ['out','nov','dez','q4'].forEach(k => { const d = m[k]; if (!d || !d.disponivel) return;
    const nomes = new Set();
    d.prom.forEach(r => { const pc = Number(r.pct), pv = Number(r.pctv);
      if (pc < 0 || pc > 100 || pv < 0 || pv > 100) erros.push(`${monthLabel(k)}: percentual fora de 0–100 em ${r.nome}`);
      if (Number(r.exec) > Number(r.lojas)) erros.push(`${monthLabel(k)}: ${r.nome} com mais executadas que previstas`);
      const n = norm(r.nome); if (nomes.has(n)) erros.push(`${monthLabel(k)}: ${r.nome} aparece 2 vezes`); nomes.add(n); });
    const sl = d.prom.reduce((s,r)=>s+Number(r.lojas),0), se = d.prom.reduce((s,r)=>s+Number(r.exec),0);
    if (d.tot && (sl !== Number(d.tot.lojas) || se !== Number(d.tot.exec))) erros.push(`${monthLabel(k)}: soma dos promotores (${sl}/${se}) diferente do total (${d.tot.lojas}/${d.tot.exec})`);
    const pos = d.prom.map(r => Number(r.pos)).sort((a,b)=>a-b); if (pos.some((p,i) => p !== i+1)) erros.push(`${monthLabel(k)}: posições fora de sequência`);
    if (!('plan' in (d.prom[0]||{}))) avisos.push(`${monthLabel(k)}: arquivo sem visitas planejadas; a crônica acumulada fica limitada`);
  });
  if (m.nov && m.nov.disponivel && !(m.out && m.out.disponivel)) erros.push('Novembro sem outubro: o acumulado ficaria incompleto');
  return {erros, avisos};
}
function importOfficialFile(file){
  if (!file) return;
  const rd = new FileReader();
  rd.onload = () => { try {
      let imp; if (/\.json$/i.test(file.name)){ const raw = JSON.parse(rd.result); imp = raw.MESES || raw; }
      else { const mt = String(rd.result).match(/const\s+MESES\s*=\s*(\{[\s\S]*?\})\s*;\s*const\s+ORDEM_MESES/); if (!mt) throw new Error('não encontramos o bloco de dados do placar. Escolha o HTML oficial do placar'); imp = JSON.parse(mt[1]); }
      const c = checarDados(imp); importPend = {dados:imp, nome:file.name, ...c};
      const meses = ['out','nov','dez'].filter(k => imp[k] && imp[k].disponivel), q = imp.q4 || {};
      const igual = dataStamp(imp) === dataStamp(MESES);
      $('importBody').innerHTML = `<p><b>Arquivo:</b> ${esc(file.name)}</p><p><b>Meses encontrados:</b> ${meses.map(k => `${monthLabel(k)}${imp[k].fechado?' (fechado)':imp[k].corte?` (até ${imp[k].corte.slice(8,10)}/${imp[k].corte.slice(5,7)})`:''}`).join(', ') || 'nenhum'}</p>
        <p><b>Acumulado:</b> ${number((q.prom||[]).length)} promotores · ${number((q.sup||[]).length)} supervisores · ${number(q.tot?.exec||0)} de ${number(q.tot?.lojas||0)} lojas executadas</p>
        ${igual ? '<p class="imp-ok">Mesmos dados que já estão carregados: nada muda (e nenhum XP é somado).</p>' : ''}
        ${c.erros.length ? `<div class="imp-err"><b>Importação bloqueada:</b><br>${c.erros.slice(0,8).map(esc).join('<br>')}</div>` : ''}
        ${c.avisos.length ? `<div class="imp-warn">${c.avisos.map(esc).join('<br>')}</div>` : ''}
        <p class="pack-footnote">Ao confirmar, ranking, raridade, PWR, níveis, missões e crônica são recalculados com estes dados. A importação fica só neste navegador; o site oficial é atualizado pela versão semanal.</p>`;
      $('importConfirm').disabled = c.erros.length > 0 || igual;
      $('importModal').hidden = false;
    } catch (err) { showToast('Não foi possível ler o arquivo: ' + err.message + '. Os dados atuais continuam.'); }
    $('importFile').value = ''; };
  rd.onerror = () => showToast('Erro ao ler o arquivo selecionado.');
  rd.readAsText(file);
}
function confirmarImport(){
  if (!importPend || importPend.erros.length) return;
  MESES = clone(importPend.dados); activeKey = hasMonth('q4') ? 'q4' : 'out';
  setStored('farmaCards.data.v2', JSON.stringify({base:BASE_STAMP, meses:MESES}));
  $('importModal').hidden = true; importPend = null; setupPeriodo(); refreshApp();
  showToast(`Placar importado. Meses disponíveis: ${MESES_Q4.filter(hasMonth).map(monthLabel).join(', ')}.`);
}

/* --- ligação dos controles novos --- */
function initV3(){
  initTema();
  setupPeriodo();
  document.querySelectorAll('#duelModes button').forEach(b => b.addEventListener('click', () => { duelMode = b.dataset.mode; document.querySelectorAll('#duelModes button').forEach(x => x.classList.toggle('active', x===b)); fillDuelSelects(); renderDuel(); }));
  $('importConfirm').addEventListener('click', confirmarImport);
  $('importCancel').addEventListener('click', () => { $('importModal').hidden = true; importPend = null; });
  refreshApp();
}

/* --- tempo de casa (patente na guilda): dado do banco, NÃO entra no PWR nem no ranking --- */
const PATENTES = [[0,'Novato'],[3,'Escudeiro'],[6,'Desbravador'],[9,'Mestre'],[12,'Ancião']];
function mesesCasa(r){ const t = (typeof TEMPO_CASA !== 'undefined' && TEMPO_CASA.pessoas) ? TEMPO_CASA.pessoas[identity(r)] : null; return t ? t.meses : null }
function patente(r){ const m = mesesCasa(r); if (m == null) return null; let p = PATENTES[0]; for (const x of PATENTES) if (m >= x[0]) p = x; return {nome:p[1], min:p[0], meses:m} }
function textoCasa(m){ if (m == null) return 'tempo de casa pendente'; if (m < 1) return 'menos de 1 mês de casa'; const a = Math.floor(m/12), r = m % 12; return (a ? `${a} ano${a>1?'s':''}${r?' e ':''}` : '') + (r ? `${r} ${r>1?'meses':'mês'}` : '') + ' de casa' }
function casaLinha(r){ const p = patente(r); return `<div class="card-casa">⌛ ${p ? `${esc(p.nome)} · ${p.meses}m de casa` : 'tempo de casa pendente'}</div>` }
function casaOk(r){ const f = $('casaFilter'); if (!f || f.value === 'all') return true; const p = patente(r); return f.value === 'pend' ? !p : (p && p.nome === f.value) }

/* --- Santuário: comandante (supervisor Top 1) em destaque --- */
function renderSupFeature(){
  const el = $('supFeature'); if (!el) return;
  const s = (data().sup || [])[0];
  if (!s){ el.innerHTML = '<div class="empty-state">Sem supervisores no período.</div>'; return; }
  const r = {...s, kind:'sup'}, p = patente(r), time = (data().prom || []).filter(x => x.supFull === s.nome);
  el.innerHTML = `<div class="leader-zone"><div class="leader-card-mini">${cardHTML(r, 'sup', true)}</div><div class="leader-copy">
    <div class="rank">♛ 1º SUPERVISOR · ${esc(data().label)} ${lb('of')}</div><h3>${esc(s.nome)}</h3>
    <p>${number(s.prom)} promotores no time · ${p ? `${esc(p.nome)} · ${textoCasa(p.meses)}` : 'tempo de casa pendente'}</p>
    <div class="big-score">${pct(s.pct)} <small>DAS LOJAS DO TIME EXECUTADAS</small></div>
    <p style="margin-top:6px">${number(s.exec)} de ${number(s.lojas)} lojas do time (soma das lojas de todos os promotores, não média dos %).${time[0] ? ` Melhor do time: ${esc(time[0].nome)} (${pct(time[0].pct)}).` : ''}</p>
    <button class="btn" style="margin-top:12px" data-open-card="${esc(identity(r))}">Inspecionar carta ↗</button></div></div>`;
}

/* --- modo escuro: botão no topo; a escolha fica só neste navegador; padrão = claro --- */
function aplicarTema(t){
  document.documentElement.dataset.tema = t;
  const b = $('temaBtn'); if (b){ b.textContent = t === 'escuro' ? '☀ Modo claro' : '☾ Modo escuro'; b.setAttribute('aria-pressed', String(t === 'escuro')); }
}
function initTema(){
  let t = 'claro'; try { t = localStorage.getItem('farmaCards.tema') || 'claro' } catch {}
  aplicarTema(t);
  $('temaBtn').addEventListener('click', () => { const novo = document.documentElement.dataset.tema === 'escuro' ? 'claro' : 'escuro'; aplicarTema(novo); try { localStorage.setItem('farmaCards.tema', novo) } catch {} });
}
