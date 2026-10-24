/* ===== Missões & selos em 3 atos (um por mês) =====
   Cada ato abre quando o mês tem dados. As missões ficam mais difíceis e valem mais XP a cada ato.
   O XP das missões soma no nível da carta e sobe a pessoa na trilha de recompensas.
   Tudo é camada de jogo: não muda posição, desempate nem premiação oficial. */
const ATOS=[
 {num:1,key:'out',nome:'Ato I',mes:'Outubro',tema:'Despertar',desc:'Primeiro mês: mostrar a que veio na rota.'},
 {num:2,key:'nov',nome:'Ato II',mes:'Novembro',tema:'Ascensão',desc:'Segundo mês: evoluir e manter o ritmo.'},
 {num:3,key:'dez',nome:'Ato III',mes:'Dezembro',tema:'Lenda',desc:'Mês final: fechar o trimestre em alta.'}
];
const TIERS={bronze:{nome:'Bronze',cor:'#B0652F'},prata:{nome:'Prata',cor:'#6F7C96'},ouro:{nome:'Ouro',cor:'#C08A12'},mitico:{nome:'Mítico',cor:'#FF1B83'},lendario:{nome:'Lendário',cor:'#7B4FD6'}};
/* p = jornada da pessoa: {out,nov,dez,q4} com o registro de cada mês (ou null) */
const sc=r=>r?getNPScore(r):null, vis=r=>r?Number(r.pctv):null;
const MISSOES=[
 {id:'a1_passo',ato:1,tier:'bronze',xp:100,icon:'⬟',titulo:'Primeiros passos',desc:'50% ou mais das lojas executadas em outubro.',test:p=>sc(p.out)>=50},
 {id:'a1_firme',ato:1,tier:'prata',xp:150,icon:'✧',titulo:'Rota firme',desc:'75% ou mais das lojas executadas em outubro.',test:p=>sc(p.out)>=75},
 {id:'a1_disc',ato:1,tier:'prata',xp:150,icon:'⛨',titulo:'Passo disciplinado',desc:'50% ou mais das visitas cumpridas em outubro.',test:p=>vis(p.out)>=50},
 {id:'a1_over',ato:1,tier:'ouro',xp:250,icon:'✦',titulo:'Overdrive',desc:'85% ou mais das lojas executadas em outubro.',test:p=>sc(p.out)>=85},
 {id:'a1_perf',ato:1,tier:'mitico',xp:400,icon:'✺',titulo:'Rota perfeita',desc:'100% das lojas do roteiro executadas em outubro.',test:p=>sc(p.out)>=99.95},
 {id:'a2_evolui',ato:2,tier:'prata',xp:250,icon:'↗',titulo:'Evolução',desc:'% de lojas executadas em novembro maior que em outubro (ou 95%+ nos dois).',test:p=>p.out&&p.nov&&(sc(p.nov)>sc(p.out)||(sc(p.nov)>=95&&sc(p.out)>=95))},
 {id:'a2_const',ato:2,tier:'ouro',xp:350,icon:'❖',titulo:'Constância',desc:'75% ou mais em outubro e em novembro.',test:p=>sc(p.out)>=75&&sc(p.nov)>=75},
 {id:'a2_disc',ato:2,tier:'prata',xp:250,icon:'⛨',titulo:'Disciplina II',desc:'60% ou mais das visitas cumpridas em novembro.',test:p=>vis(p.nov)>=60},
 {id:'a2_salto',ato:2,tier:'ouro',xp:350,icon:'⚡',titulo:'Salto de nível',desc:'Subir 10 pontos percentuais ou mais de outubro para novembro.',test:p=>p.out&&p.nov&&sc(p.nov)-sc(p.out)>=10},
 {id:'a2_duplo',ato:2,tier:'mitico',xp:500,icon:'✺',titulo:'Overdrive duplo',desc:'85% ou mais em outubro e em novembro.',test:p=>sc(p.out)>=85&&sc(p.nov)>=85},
 {id:'a3_luas',ato:3,tier:'prata',xp:300,icon:'☾',titulo:'Três luas',desc:'Roteiro nos três meses (outubro, novembro e dezembro).',test:p=>!!(p.out&&p.nov&&p.dez)},
 {id:'a3_escalada',ato:3,tier:'ouro',xp:450,icon:'⛰',titulo:'Escalada',desc:'Nunca cair: dezembro ≥ novembro ≥ outubro.',test:p=>p.out&&p.nov&&p.dez&&sc(p.dez)>=sc(p.nov)&&sc(p.nov)>=sc(p.out)},
 {id:'a3_trilogia',ato:3,tier:'ouro',xp:500,icon:'♜',titulo:'Trilogia',desc:'75% ou mais nos três meses.',test:p=>sc(p.out)>=75&&sc(p.nov)>=75&&sc(p.dez)>=75},
 {id:'a3_lenda',ato:3,tier:'lendario',xp:800,icon:'♛',titulo:'Lenda do Q4',desc:'90% ou mais das lojas executadas no acumulado do trimestre e 60% ou mais das visitas cumpridas.',test:p=>sc(p.q4)>=90&&vis(p.q4)>=60},
 {id:'a3_podio',ato:3,tier:'lendario',xp:800,icon:'🏆',titulo:'Pódio final',desc:'Terminar o trimestre no pódio do placar oficial (top 3 promotores ou 1º supervisor).',test:p=>p.q4&&(p.kind==='sup'?Number(p.q4.pos)===1:Number(p.q4.pos)<=3)}
];
const TRILHA=[
 {xp:0,nome:'Recruta',premio:'Carta base da coleção',cls:''},
 {xp:250,nome:'Aprendiz',premio:'Selo de bronze na carta',cls:'rw-1'},
 {xp:700,nome:'Veterano',premio:'Moldura cintilante',cls:'rw-2'},
 {xp:1400,nome:'Campeão',premio:'Título dourado e brilho na moldura',cls:'rw-3'},
 {xp:2500,nome:'Lenda',premio:'Coroa e aura lendária animada',cls:'rw-4'}
];
const XP_NIVEL=250, NIVEL_MAX=30;
function atoAberto(n){const a=ATOS[n-1];if(n===3)return hasMonth('dez');return hasMonth(a.key)}
function jornada(r){const id=identity(r),kind=r.kind||'prom',get=k=>hasMonth(k)?(allRows(k).find(x=>identity(x)===id)||null):null;
 const out=get('out'),nov=get('nov'),dez=get('dez');const q4=monthCompleteSet()?get('q4'):null;return {kind,out,nov,dez,q4}}
function missoesDe(r){const p=jornada(r);return MISSOES.map(m=>{const aberto=atoAberto(m.ato);let feito=false;if(aberto){try{feito=!!m.test(p)}catch{feito=false}}return {...m,aberto,feito}})}
function missionXP(r){return missoesDe(r).filter(m=>m.feito).reduce((s,m)=>s+m.xp,0)}
function trilhaDe(r){const x=missionXP(r);let atual=TRILHA[0],prox=null;for(const t of TRILHA){if(x>=t.xp)atual=t;else{prox=t;break}}return {xp:x,atual,prox}}
function xpMax(){return MISSOES.filter(m=>atoAberto(m.ato)).reduce((s,m)=>s+m.xp,0)}
/* ---- telas ---- */
function contaTrilha(rows){const c=TRILHA.map(()=>0);rows.forEach(r=>{const t=trilhaDe(r).atual;c[TRILHA.indexOf(t)]++});return c}
function trilhaMini(r){const t=trilhaDe(r);const max=xpMax();const falta=t.prox?t.prox.xp-t.xp:0;
 return `<div style="display:flex;justify-content:space-between;gap:8px;font-size:12px"><b>${esc(t.atual.nome)} · ${number(t.xp)} XP de missões</b><span style="color:var(--muted)">${number(max)} XP possíveis até agora</span></div>`+
 `<div class="card-progress" style="height:7px;margin-top:8px"><span style="width:${max?Math.min(100,t.xp/max*100):0}%"></span></div>`+
 `<div style="color:var(--muted);font-size:11px;margin-top:7px">${t.prox?`Faltam ${number(falta)} XP para <b>${esc(t.prox.nome)}</b> (${esc(t.prox.premio.toLowerCase())}).`:'Topo da trilha alcançado.'}</div>`}
function renderJourney(){const id=$('journeyPick').value;const r=findRowById(id);if(!r){$('journeyBox').innerHTML='<div class="empty-state">Escolha um nome para ver a jornada.</div>';return}
 const ms=missoesDe(r),t=trilhaDe(r);
 const lista=ATOS.map(a=>`<div class="jl-act">${a.nome} · ${a.mes}${atoAberto(a.num)?'':' · selado'}</div>`+ms.filter(m=>m.ato===a.num).map(m=>`<div class="jl-row ${m.feito?'ok':''} ${m.aberto?'':'lock'}"><span class="st">${m.feito?'✓':m.aberto?'·':'🔒'}</span><div><b>${m.icon} ${esc(m.titulo)}</b><small>${esc(m.desc)}</small></div><span class="xp">${m.feito?'+':''}${m.xp} XP</span></div>`).join('')).join('');
 $('journeyBox').innerHTML=`<div class="journey"><div class="journey-card"><div class="eyebrow">${r.kind==='sup'?'Supervisor':'Promotor'}</div><h3>${esc(r.nome)}</h3><div style="font-size:12px;color:var(--muted)">${ms.filter(m=>m.feito).length} de ${ms.filter(m=>m.aberto).length} missões abertas conquistadas</div><div class="jc-tier">${esc(t.atual.nome)}</div><div style="margin-top:10px">${trilhaMini(r)}</div><div class="jc-next">Posição oficial no placar: ${r.pos}º · ${pct(r.pct)} das lojas executadas.</div></div><div class="journey-list">${lista}</div></div>`}
function renderQuests(){const pessoas=allRows();const n=pessoas.length;
 const abertos=ATOS.filter(a=>atoAberto(a.num)).length;
 const todas=pessoas.map(r=>missoesDe(r));
 const selos=todas.reduce((s,ms)=>s+ms.filter(m=>m.feito).length,0);
 const xpTot=todas.reduce((s,ms)=>s+ms.filter(m=>m.feito).reduce((a,m)=>a+m.xp,0),0);
 const cont=contaTrilha(pessoas);
 $('questSummary').innerHTML=[['ATOS ABERTOS',`${abertos} de 3`,abertos<3?`Próximo: ${ATOS[abertos].nome} · ${ATOS[abertos].mes}`:'Trimestre completo','☾'],['MISSÕES ABERTAS',number(MISSOES.filter(m=>atoAberto(m.ato)).length),`de ${MISSOES.length} na temporada`,'✧'],['SELOS CONQUISTADOS',number(selos),'somando todas as cartas','✦'],['VETERANO OU ACIMA',number(cont.slice(2).reduce((a,b)=>a+b,0)),`de ${n} cartas`,'♛']].map(([l,v,s,i])=>`<div class="stat"><div class="label">${l}</div><strong>${v}</strong><small>${s}</small><span class="icon">${i}</span></div>`).join('');
 const cores=['#8A8F9E','#B0652F','#6F7C96','#C08A12','#FF1B83'],icones=['◇','⬟','✧','✦','♛'];
 $('rewardTrack').innerHTML=TRILHA.map((t,i)=>`<div class="reward-step ${cont[i]?'on':''}" style="--rs:${cores[i]}"><span class="rs-icon">${icones[i]}</span><span class="rs-xp">${number(t.xp)} XP</span><b>${t.nome}</b><p>${esc(t.premio)}</p><span class="rs-count">${cont[i]} ${cont[i]===1?'carta':'cartas'}</span></div>`).join('');
 const sel=$('journeyPick');const old=sel.value;sel.innerHTML=pessoas.slice().sort((a,b)=>a.nome.localeCompare(b.nome,'pt-BR')).map(r=>`<option value="${esc(identity(r))}">${esc(r.nome)}${r.kind==='sup'?' · SUP':''}</option>`).join('');
 sel.value=[...sel.options].some(o=>o.value===old)?old:identity({...(data().prom||[])[0],kind:'prom'});sel.onchange=renderJourney;renderJourney();
 $('actsBox').innerHTML=ATOS.map(a=>{const aberto=atoAberto(a.num);const ms=MISSOES.filter(m=>m.ato===a.num);const xpAto=ms.reduce((s,m)=>s+m.xp,0);
  return `<div class="act ${aberto?'':'sealed'}"><div class="act-head"><div><div class="act-num">${a.nome} · ${a.mes} · ${a.tema}</div><h3>${esc(a.desc)}</h3><p>${ms.length} missões · até ${number(xpAto)} XP neste ato</p></div><span class="act-state">${aberto?'Aberto':'Selado até '+a.mes.toLowerCase()+' entrar no placar'}</span></div>`+
  `<div class="quest-grid">${ms.map(m=>{const T=TIERS[m.tier];const feitos=aberto?todas.filter(x=>x.find(y=>y.id===m.id).feito).length:0;const st=n?Math.round(feitos/n*100):0;
   return `<div class="quest ${aberto?'':'locked'}" style="--quest:${T.cor}"><div class="quest-top"><div class="quest-symbol">${aberto?m.icon:'🔒'}</div><span class="quest-xp">+${m.xp} XP</span></div><h3>${esc(m.titulo)}</h3><span class="tier-chip">${T.nome}</span><p style="margin-top:8px">${esc(m.desc)}</p><div class="quest-progress"><span style="width:${st}%"></span></div><div class="quest-bottom"><span>${aberto?`${feitos} de ${n} conquistaram`:'AGUARDANDO O MÊS'}</span><span>${aberto?st+'%':'SELADA'}</span></div></div>`}).join('')}</div></div>`}).join('')}
/* ---- Forja: todas as regras do jogo, geradas das mesmas constantes ---- */
function renderForgeRules(){
 const tab=(cab,linhas)=>`<div class="rules-table"><table><thead><tr>${cab.map(c=>`<th>${c}</th>`).join('')}</tr></thead><tbody>${linhas.map(l=>`<tr>${l.map(c=>`<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
 const bloco=(t,s,html)=>`<div class="panel forge-block"><div class="panel-head"><h3>${t}</h3><span>${s}</span></div>${html}</div>`;
 const classes=tab(['Ordem','Classe','Quando a carta recebe'],[
  ['1º','Arcanista da Execução','90% ou mais das lojas executadas'],
  ['2º','Guardião da Disciplina',`${gates.disciplineVisit}% ou mais das visitas cumpridas`],
  ['3º','Cavaleiro do Volume',`${gates.volumeExec} lojas executadas ou mais`],
  ['4º','Sentinela de Execução',`${thresholds.gold}% ou mais das lojas executadas (faixa Ouro)`],
  ['5º','Viajante da Rota','nenhuma das anteriores']]);
 const raridade=tab(['Raridade','Faixa de lojas executadas','Observação'],[
  ['Comum',`abaixo de ${thresholds.bronze}%`,''],['Bronze',`${thresholds.bronze}% a ${thresholds.silver-0.1}%`,''],['Prata',`${thresholds.silver}% a ${thresholds.gold-0.1}%`,''],
  ['Ouro',`${thresholds.gold}% a ${thresholds.epic-0.1}%`,''],['Épica',`${thresholds.epic}% a ${thresholds.mythic-0.1}%`,''],
  ['Mítica selada',`${thresholds.mythic}% ou mais`,'sem os requisitos extras: moldura Mítica, sem holografia'],
  ['Mítica holográfica',`${thresholds.mythic}% ou mais`,`e ${gates.mythicVisit}%+ de visitas cumpridas e ${gates.mythicExec}+ lojas executadas`]]);
 const missoes=tab(['Ato','Missão','Selo','Regra','XP'],MISSOES.map(m=>{const a=ATOS[m.ato-1];return [`${a.nome} · ${a.mes}`,`${m.icon} ${esc(m.titulo)}`,TIERS[m.tier].nome,esc(m.desc),`+${m.xp}`]}));
 const trilha=tab(['Nível da trilha','XP de missões','Recompensa na carta'],TRILHA.map(t=>[t.nome,`${number(t.xp)}+`,esc(t.premio)]));
 const somaAto=n=>number(MISSOES.filter(m=>m.ato===n).reduce((s,m)=>s+m.xp,0));
 const formulas=`<div class="formula">
  <b>Índice de volume</b> = mín(100; lojas executadas ÷ 50 × 100).<br>
  <b>PWR (poder de jogo)</b> = 70% × % lojas executadas + 20% × % visitas cumpridas + 10% × índice de volume.<br>
  <b>XP base</b> = arredondar(PWR × PWR ÷ 100 × 25).<br>
  <b>XP total</b> = XP base + XP das missões conquistadas (Ato I até ${somaAto(1)} · Ato II até ${somaAto(2)} · Ato III até ${somaAto(3)}).<br>
  <b>Nível</b> = 1 + a cada ${XP_NIVEL} XP, até o nível ${NIVEL_MAX}.<br>
  <b>Atos:</b> cada ato abre quando o mês entra no placar (Ato III com dezembro e o acumulado do trimestre). Missão de ato aberto continua valendo nos meses seguintes.<br>
  <b>Ranking oficial:</b> lojas executadas ÷ lojas do roteiro, desempate pelo % de visitas cumpridas. Raridade, classe, PWR, XP, nível, missões, selos, trilha e confronto <b>não</b> mudam posição, desempate nem premiação.</div>`;
 $('forgeRules').innerHTML=bloco('◇ Raridade completa','% de lojas executadas',raridade)+bloco('♜ Classes da carta','decididas nesta ordem',classes)+bloco('✧ Missões e selos','15 missões em 3 atos',missoes)+bloco('♛ Trilha de recompensas','XP das missões',trilha)+bloco('⚙ Fórmulas do jogo','como cada número é calculado',formulas)+(typeof PATENTES!=='undefined'?bloco('⌛ Patente na guilda','tempo de casa (cadastro)',tab(['Patente','Tempo de casa','Efeito'],PATENTES.map((p,i)=>[p[1],PATENTES[i+1]?`${p[0]} a ${PATENTES[i+1][0]-1} meses`:`${p[0]} meses ou mais`,'Título na carta e filtro da coleção. Não entra no PWR, no XP nem no ranking.']))):'');
}
