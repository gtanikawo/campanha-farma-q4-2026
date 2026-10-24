"""Gera Farma_Cards_Q4_Legends_RPG_v2.html a partir do protótipo original (origem_v1, não é alterado).

O que a v2 muda em relação ao v1:
- tema claro Reckitt (src/v2.css), logos oficiais SPOT e Reckitt embutidos;
- o pct passa a se chamar "% lojas executadas" (não é a nota NP) e a regra fica isolada em getNPScore();
- Forja só leitura: faixas e requisitos vêm do CONFIG deste arquivo, iguais para todo mundo;
- regras propostas (Mítica trimestral, amostra mínima) aparecem desligadas;
- dado importado guardado com o carimbo da base: uma versão nova do arquivo descarta importações antigas;
- importação valida a estrutura antes de trocar os dados;
- barras do Confronto corrigidas (faltava o %).
Rodar:  python build_v2.py   (a partir desta pasta src)
"""
import base64, json, re, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
ORIGEM = RAIZ / 'origem_v1' / 'Farma_Cards_Q4_Legends_RPG.html'
PLACAR = RAIZ.parent / '03_HTML' / 'Placar_Farma_Q4_2026_Ajustado.html'
SAIDA = RAIZ / 'Farma_Cards_Q4_Legends_RPG_v2.html'
LOGO_SPOT = AQUI / 'spot_logo.png'
LOGO_RK = AQUI / 'reckitt_logo.svg'

h = ORIGEM.read_text(encoding='utf-8')
falhas = []

def troca(velho, novo, minimo=1, todas=True):
    global h
    n = h.count(velho)
    if n < minimo:
        falhas.append(f'não achei ({n}x): {velho[:90]}')
        return
    h = h.replace(velho, novo) if todas else h.replace(velho, novo, 1)

# 1. Dados oficiais: MESES do placar validado
placar = PLACAR.read_text(encoding='utf-8-sig')
meses = json.loads(re.search(r'const MESES = (\{.*?\});\s*\n\s*const ORDEM_MESES', placar, re.S).group(1))
ini = h.index('const BASE_DATA = ')
fim = h.index('\nlet MESES = clone(BASE_DATA);')
h = h[:ini] + 'const BASE_DATA = ' + json.dumps(meses, ensure_ascii=False) + ';' + h[fim:]

# 2. CSS claro
css = (AQUI / 'v2.css').read_text(encoding='utf-8')
h = re.sub(r'<style>.*?</style>', lambda m: css.strip(), h, count=1, flags=re.S)
troca('<meta name="theme-color" content="#090b16">', '<meta name="theme-color" content="#FF1B83">')
troca('<title>Farma Cards — Q4 Legends RPG</title>', '<title>Farma Cards Q4</title>')

# 3. Logos oficiais
spot = 'data:image/png;base64,' + base64.b64encode(LOGO_SPOT.read_bytes()).decode()
rk = 'data:image/svg+xml;base64,' + base64.b64encode(LOGO_RK.read_bytes()).decode()
UNIAO = ('<span class="uniao" aria-label="em parceria com" role="img"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true">'
         '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
         '<path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>')
LOGOS = f'<span class="logo-chip"><img src="{spot}" alt="SPOT"></span>{UNIAO}<span class="logo-chip"><img src="{rk}" alt="Reckitt"></span>'
troca('<div class="brand"><div class="brand-mark">✦</div><div class="brand-copy">',
      f'<div class="brand"><div class="brand-logos">{LOGOS}</div><div class="brand-copy">')
troca('<div class="hero"><div class="hero-content">',
      f'<div class="hero"><div class="hero-content"><div class="hero-logos">{LOGOS}</div>')
troca('<meta name="theme-color" content="#FF1B83">', f'<meta name="theme-color" content="#FF1B83">\n<link rel="icon" type="image/svg+xml" href="{rk}">')

# 3b. Ajustes de 23/10 (Gustavo): sem ARCHIVE · OF · LEGENDS, sem "· RPG", sem a trilha FARMA CARDS / página no topo
troca('<div class="hero-rune">ARCHIVE · OF · LEGENDS</div>', '')
troca('<span>Q4 LEGENDS · RPG</span>', '<span>Q4 LEGENDS</span>')
troca('<small>PWR · RPG</small>', '<small>PWR</small>')
troca('<div class="crumb"><span>FARMA CARDS</span><span>／</span><strong id="crumbCurrent">Santuário</strong></div>', '<div class="crumb"></div>')
troca("$('crumbCurrent').textContent=", "document.title='Farma Cards Q4 · '+")

# 4. Rótulos: pct = % de lojas executadas (não é a nota NP)
for velho, novo in [
    ('NP SCORE', '% LOJAS EXEC.'),
    ('<small>NP · PWR ${', '<small>lojas exec. · PWR ${'),
    ('\\nNP: ${pct(r.pct)}', '\\n% lojas executadas: ${pct(r.pct)}'),
    ('\\nLojas executadas: ${r.exec}/${r.lojas}', '\\nLojas: ${r.exec} de ${r.lojas}'),
    ('Ranking oficial: ${r.pos}º · NP ${pct(r.pct)}', 'Ranking oficial: ${r.pos}º · ${pct(r.pct)} das lojas executadas'),
    ('posição ${r.pos} · NP ${pct(r.pct)}', 'posição ${r.pos} · ${pct(r.pct)} das lojas executadas'),
    ('NP · LOJAS EXECUTADAS', '% LOJAS EXECUTADAS'),
    ('percentual de lojas executadas do placar (NP).<br>• Poder de jogo (PWR) = 70% NP + 20%', 'percentual de lojas executadas do placar oficial.<br>• Poder de jogo (PWR) = 70% lojas executadas + 20%'),
    ('`${myth} cartas na faixa mítica de NP`', "`${myth} ${myth===1?'carta':'cartas'} na faixa Mítica`"),
    ("${esc(d.periodo?stripHTML(d.periodo):'')} ${loaded<3", "${esc(d.periodo?stripHTML(d.periodo):'')}. ${loaded<3"),
    ('Configure as faixas de NP que definem as raridades e as condições adicionais necessárias para liberar o efeito máximo. As configurações ficam salvas neste navegador.',
     'Estas são as regras de raridade da campanha. Valem igual para todo mundo e só mudam numa nova versão do arquivo.'),
    ('✦ Raridade guiada por NP', '✦ Raridade pelo % de lojas executadas'),
    ('Compare NP, disciplina', 'Compare execução, disciplina'),
    ('lojas executadas no recorte de NP.', 'lojas executadas no recorte atual.'),
    ('⚒ Limiares de NP</h3><span>Pontuação-base (%)', '⚒ Faixas de raridade</h3><span>% de lojas executadas'),
    ('(${thresholds.epic}% NP)', '(${thresholds.epic}% das lojas executadas)'),
    ('O NP define a faixa base.', 'O % de lojas executadas define a faixa base.'),
    ('Ordenar: NP maior', 'Ordenar: % lojas executadas'),
    ('${pct(leader.pct)} <small>NP</small>', '${pct(leader.pct)} <small>DAS LOJAS EXECUTADAS</small>'),
    ('NP ${pct(r.pct)} · VISITAS ${pct(r.pctv)}', 'LOJAS ${pct(r.pct)} · VISITAS ${pct(r.pctv)}'),
    ("label:'NP OVERDRIVE',icon:'✦',desc:'Pontuação NP de 85% ou mais'", "label:'OVERDRIVE',icon:'✦',desc:'85% ou mais das lojas executadas'"),
    ('Efeito holográfico habilitado: NP acima do limiar', 'Efeito holográfico habilitado: % de lojas executadas acima do limiar'),
    ('A moldura reflete a pontuação NP.', 'A moldura reflete o % de lojas executadas.'),
    ("'Arcanista de NP'", "'Arcanista da Execução'"),
    ('execução NP, consistência', 'lojas executadas, consistência'),
    ('o nível base usa a pontuação NP', 'o nível base usa o % de lojas executadas'),
    ('Maior NP no recorte atual', '1º lugar do placar oficial'),
    ('desc:`NP ≥ ${thresholds.mythic}%', 'desc:`Lojas executadas ≥ ${thresholds.mythic}%'),
    ("[['NP',a.pct,b.pct]", "[['Lojas exec.',a.pct,b.pct]"),
    ("[['NP',r.pct,'Percentual NP']", "[['NP',r.pct,'% lojas executadas']"),
    ('Editar regras ↗', 'Ver regras ↗'),
    ('<div class="eyebrow">Personalização da coleção</div>', '<div class="eyebrow">Regras da coleção</div>'),
]:
    troca(velho, novo)
troca("'% NP']", "'% lojas']", minimo=5)

# 5. Regra central da pontuação + carimbo dos dados + validação + propostas
troca('function clone(v){return JSON.parse(JSON.stringify(v))}',
      'function clone(v){return JSON.parse(JSON.stringify(v))}\n'
      '/* Pontuação que define a raridade. Hoje = pct do placar (% de lojas executadas). Mudar só aqui. */\n'
      'function getNPScore(r){const v=Number(r&&r.pct);return Number.isFinite(v)?v:null}\n'
      'function dataStamp(m){try{const q=m.q4||m.out||{};return [q.periodo||"",q.tot&&q.tot.lojas,q.tot&&q.tot.exec,(q.prom||[]).length,["out","nov","dez"].map(k=>m[k]&&m[k].disponivel?1:0).join("")].join("|")}catch{return ""}}\n'
      'function validMeses(m){if(!m||typeof m!=="object")return "Arquivo sem o objeto MESES.";if(!m.out||!m.q4)return "Arquivo sem os meses out e q4 do placar oficial.";'
      'for(const k of ["out","nov","dez","q4"]){const d=m[k];if(!d||!d.disponivel)continue;if(!Array.isArray(d.prom)||!d.prom.length||!Array.isArray(d.sup))return `Mês ${k} marcado como disponível, mas sem promotores/supervisores.`;'
      'for(const r of d.prom){if(typeof r.nome!=="string"||!["pos","lojas","exec","pct","pctv"].every(c=>Number.isFinite(Number(r[c]))))return `Registro inválido em ${k}: ${r&&r.nome||"sem nome"}.`}'
      'if(!d.tot||!Number.isFinite(Number(d.tot.lojas))||!Number.isFinite(Number(d.tot.exec)))return `Totais ausentes em ${k}.`}return true}\n'
      '/* Regras propostas (NÃO oficiais). Ligar só com decisão da coordenação. */\n'
      'const PROPOSALS={trimestral:{on:false},amostra:{on:false,min:30}};\n'
      'function proposalsOk(r){if(PROPOSALS.amostra.on&&!(Number(r.lojas)>=PROPOSALS.amostra.min))return false;if(PROPOSALS.trimestral.on&&!(monthCompleteSet()&&eligibleAllMonths(r)&&["out","nov","dez"].every(k=>{const x=allRows(k).find(y=>identity(y)===identity(r));return x&&getNPScore(x)>=thresholds.mythic})))return false;return true}')

# regras passam a usar getNPScore
h_js_ini = h.index('let MESES = clone(BASE_DATA);')
js = h[h_js_ini:]
js = js.replace('Number(r.pct||0)*.7', '(getNPScore(r)??0)*.7')
js = js.replace('let v=Number(r.pct)||0;', 'let v=getNPScore(r)??0;')
js = js.replace('Number(r.pct)>=', 'getNPScore(r)>=')
js = js.replace('r=>r.pct>=', 'r=>getNPScore(r)>=')
js = js.replace("sort==='np'?b.pct-a.pct", "sort==='np'?(getNPScore(b)??0)-(getNPScore(a)??0)")
js = js.replace('mythicUnlocked(r){return getNPScore(r)>=thresholds.mythic&&Number(r.pctv)>=gates.mythicVisit&&Number(r.exec)>=gates.mythicExec}',
                'mythicUnlocked(r){return getNPScore(r)>=thresholds.mythic&&Number(r.pctv)>=gates.mythicVisit&&Number(r.exec)>=gates.mythicExec&&proposalsOk(r)}')
if 'proposalsOk(r)}' not in js:
    falhas.append('mythicUnlocked não recebeu proposalsOk')
h = h[:h_js_ini] + js

# 6. Forja só leitura: config fixa no arquivo, sem localStorage
troca("try{const saved=getStored('farmaCards.thresholds');if(saved)thresholds={...DEFAULT_THRESHOLDS,...JSON.parse(saved)}}catch{}", "removeStored('farmaCards.thresholds');")
troca("try{const saved=getStored('farmaCards.gates');if(saved)gates={...DEFAULT_GATES,...JSON.parse(saved)}}catch{}", "removeStored('farmaCards.gates');")
troca("try{const saved=getStored('farmaCards.data');if(saved){const parsed=JSON.parse(saved);if(parsed&&parsed.out&&parsed.q4)MESES=parsed}}catch{}",
      "removeStored('farmaCards.data');const BASE_STAMP=dataStamp(BASE_DATA);try{const saved=JSON.parse(getStored('farmaCards.data.v2')||'null');if(saved&&saved.base===BASE_STAMP&&validMeses(saved.meses)===true)MESES=saved.meses;else removeStored('farmaCards.data.v2')}catch{}")
troca('<form id="rarityForm"><div id="rarityInputs"></div><div style="display:flex;gap:9px;flex-wrap:wrap;margin-top:17px"><button type="submit" class="btn primary">Guardar regras</button><button type="button" id="resetRarity" class="btn">Restaurar padrões</button></div></form>',
      '<div id="rarityInputs"></div>')
troca('<div style="display:flex;gap:9px;flex-wrap:wrap;margin-top:17px"><button type="button" id="saveGates" class="btn primary">Salvar requisitos</button><button type="button" id="resetGates" class="btn">Restaurar</button></div>', '')
troca("$('rarityForm').addEventListener('submit',saveThresholds);$('saveGates').addEventListener('click',saveGateValues);$('resetRarity').addEventListener('click',()=>{thresholds={...DEFAULT_THRESHOLDS};setStored('farmaCards.thresholds',JSON.stringify(thresholds));renderForge();refreshApp();showToast('Faixas de raridade restauradas.')});$('resetGates').addEventListener('click',()=>{gates={...DEFAULT_GATES};setStored('farmaCards.gates',JSON.stringify(gates));renderForge();refreshApp();showToast('Requisitos adicionais restaurados.')});", '')
ini = h.index('function renderForge(){')
fim = h.index('\nfunction saveThresholds(')
h = h[:ini] + (
    "function renderForge(){const row=(l,s,v,off)=>`<div class=\"setting-row\"><div><strong>${l}</strong><small>${s}</small></div><span class=\"val${off?' off':''}\">${v}</span></div>`;"
    "$('rarityInputs').innerHTML=[['bronze','Bronze'],['silver','Prata'],['gold','Ouro'],['epic','Épica'],['mythic','Mítica']].map(([k,n])=>row(`${n} a partir de`,'% de lojas executadas no recorte',thresholds[k]+'%')).join('')+row('Comum',`abaixo de ${thresholds.bronze}%`,'&lt; '+thresholds.bronze+'%');"
    "$('gatingInputs').innerHTML=[row('Holográfica: visitas mínimas','% de visitas cumpridas, além da faixa Mítica',gates.mythicVisit+'%'),row('Holográfica: volume mínimo','lojas executadas no recorte',gates.mythicExec),row('Classe Guardião da Disciplina','% de visitas cumpridas',gates.disciplineVisit+'%'),row('Classe Cavaleiro do Volume','lojas executadas no recorte',gates.volumeExec),"
    "row('Proposta: Mítica trimestral','Exigir os 3 meses e a faixa Mítica em todos. Não é regra oficial.',PROPOSALS.trimestral.on?'ligada':'desligada',!PROPOSALS.trimestral.on),"
    "row('Proposta: amostra mínima',`Exigir ao menos ${PROPOSALS.amostra.min} lojas no roteiro para a holográfica. Não é regra oficial.`,PROPOSALS.amostra.on?'ligada':'desligada',!PROPOSALS.amostra.on)].join('')}"
) + h[fim:]

# 7. Importação: validar antes de trocar; guardar com carimbo da base
troca("if(!imported.out||!imported.q4)throw new Error('Arquivo sem estrutura compatível do placar oficial (meses out e q4).');",
      "const prob=validMeses(imported);if(prob!==true)throw new Error(prob);")
troca("setStored('farmaCards.data',JSON.stringify(MESES))", "setStored('farmaCards.data.v2',JSON.stringify({base:BASE_STAMP,meses:MESES}))")
troca("removeStored('farmaCards.data');refreshApp()", "removeStored('farmaCards.data.v2');refreshApp()")

# 8. Confronto: barras com %
troca("Math.min(100,Number(val))};background:${t.color}", "Math.min(100,Number(val))}%;background:${t.color}")
troca('background:linear-gradient(90deg,#69e6e0,#a9fff4)', 'background:#8C1D5A')

# 8b. Filtros da coleção: UF esconde supervisores (não têm UF); supervisor mostra o time + a carta dele
troca("if(sup!=='all'&&r.kind==='prom'&&(r.supFull||r.sup)!==sup)return false;", "if(sup!=='all'&&(r.kind==='prom'?(r.supFull||r.sup)!==sup:r.nome!==sup))return false;")
troca("if(uf!=='all'&&r.kind==='prom'&&r.uf!==uf)return false;", "if(uf!=='all'&&(r.kind!=='prom'||r.uf!==uf))return false;")

# 9. Cores legíveis no claro
for velho, novo in [
    ("color:'#b4b9ca'", "color:'#8A8F9E'"), ("color:'#c98556'", "color:'#B0652F'"), ("color:'#d1dbf3'", "color:'#6F7C96'"),
    ("name:'Ouro',min:()=>thresholds.gold,color:'#ffcf70'", "name:'Ouro',min:()=>thresholds.gold,color:'#C08A12'"),
    ("name:'Épica',min:()=>thresholds.epic,color:'#c0a0ff'", "name:'Épica',min:()=>thresholds.epic,color:'#7B4FD6'"),
    ("name:'Mítica',min:()=>thresholds.mythic,color:'#ff71b5'", "name:'Mítica',min:()=>thresholds.mythic,color:'#FF1B83'"),
    ("'⌁','#ff4f9c'", "'⌁','#FF1B83'"), ("'◉','#8d77ff'", "'◉','#7B4FD6'"), ("'▧','#ffcf70'", "'▧','#C08A12'"), ("'✺','#70e6d8'", "'✺','#0F8F86'"),
    ("color:'#ff77b8'", "color:'#FF1B83'"), ("color:'#72e9df'", "color:'#0F8F86'"), ("color:'#ffcb70'", "color:'#C08A12'"),
    ("title:'Ascensão épica',color:'#c0a0ff'", "title:'Ascensão épica',color:'#7B4FD6'"),
    ("title:'A porta Mítica',color:'#ff71b5'", "title:'A porta Mítica',color:'#D3006A'"), ("color:'#7f92ff'", "color:'#5B6BD6'"),
    ("'255,130,190':'185,170,255'", "'255,27,131':'140,29,90'"), ('opacity:.48', 'opacity:.3'),
]:
    troca(velho, novo)

# 10. Missões & selos em 3 atos (src/missoes.js) + trilha de recompensas
missoes_js = (AQUI / 'missoes.js').read_text(encoding='utf-8')
troca("function xp(r){return Math.round(power(r)*power(r)/100*25)}",
      "function xpBase(r){return Math.round(power(r)*power(r)/100*25)}\nfunction xp(r){return xpBase(r)+missionXP(r)}")
troca("function level(r){return Math.max(1,Math.min(20,1+Math.floor(xp(r)/150)))}",
      "function level(r){return Math.max(1,Math.min(NIVEL_MAX,1+Math.floor(xp(r)/XP_NIVEL)))}")
troca("xpV%150", "xpV%XP_NIVEL")
troca("xp(r)%150}/150 XP", "xp(r)%XP_NIVEL}/${XP_NIVEL} XP")
troca("(xp(r)%150)/1.5", "(xp(r)%XP_NIVEL)/XP_NIVEL*100")
troca("XP ${number(xpV)}", "${esc(trilhaDe(r).atual.nome)} · XP ${number(xpV)}")
troca("class=\"player-card ${cssTier(r)} ${compact?'compact':''} ${foil?'foil':''}\"", "class=\"player-card ${cssTier(r)} ${trilhaDe(r).atual.cls} ${compact?'compact':''} ${foil?'foil':''}\"")
troca('<div class="detail-section-title">Crônica mensal</div>', '<div class="detail-section-title">Trilha de recompensas</div>${trilhaMini(r)}<div class="detail-section-title">Crônica mensal</div>')
ini = h.index('function extraBadges(r){'); fim = h.index('\nfunction eligibleAllMonths(')
h = h[:ini] + "function extraBadges(r){return missoesDe(r).filter(m=>m.feito).sort((a,b)=>b.xp-a.xp).map(m=>({label:m.titulo.toUpperCase(),icon:m.icon,desc:m.desc}))}" + h[fim:]
ini = h.index('function renderQuests(){'); fim = h.index('\nfunction renderChronicle(')
h = h[:ini] + missoes_js.strip() + h[fim:]
ini = h.index('<section id="page-quests" class="page">'); fim = h.index('</section>', ini) + len('</section>')
h = h[:ini] + ('<section id="page-quests" class="page">'
 '<div class="page-title"><div><div class="eyebrow">Jornada Q4 · 3 atos</div><h1>Missões & selos</h1><p>Cada mês abre um ato novo, com missões mais difíceis e recompensas maiores. O XP das missões sobe o nível da carta e avança na trilha de recompensas. Nada disso muda o ranking oficial nem a premiação.</p></div></div>'
 '<div id="questSummary" class="stat-grid"></div>'
 '<div class="section-head"><div><h2>Trilha de recompensas</h2><p>Quanto mais XP de missões, mais a carta ganha: selo, moldura cintilante, título dourado e, no topo, a aura de Lenda.</p></div></div><div id="rewardTrack" class="reward-track"></div>'
 '<div class="section-head"><div><h2>Minha jornada</h2><p>Escolha um nome para ver as missões conquistadas, as que faltam e quanto falta para a próxima recompensa.</p></div><select id="journeyPick" class="control" aria-label="Escolher pessoa"></select></div><div class="panel" id="journeyBox"></div>'
 '<div id="actsBox"></div>'
 '<div class="notice"><strong>Como funciona:</strong> as missões são conferidas no placar oficial de cada mês. O Ato II abre quando novembro entrar no placar, e o Ato III quando dezembro entrar (com o acumulado do trimestre). As missões de um ato já aberto continuam valendo nos meses seguintes.</div>'
 '</section>') + h[fim:]
troca("• PWR, nível, XP, selos e raridade nunca alteram o ranking oficial.", "• XP = XP base do PWR + XP das missões conquistadas; nível sobe a cada 250 XP (até 30).<br>• PWR, nível, XP, selos e raridade nunca alteram o ranking oficial.")

# 11. Sem a legenda de rodapé em todas as páginas (pedido do Gustavo, 23/10)
troca('<div class="footer-note" id="footerNote"></div>', '')
troca("$('footerNote').textContent=(d.rodape||'').replace(/·/g,' · ')+'  |  Interface de gamificação FARMA CARDS — dados processados localmente no navegador.';", '')

# 12. Aviso de versão parcial num canto discreto: fim da página inicial, texto pequeno
ini = h.index('<div class="notice" id="dataNotice">'); fim = h.index('</div>', ini) + len('</div>')
h = h[:ini] + h[fim:]
troca('</div>\n  </section>\n\n  <section id="page-collection"', '</div>\n    <p class="data-note" id="dataNotice"></p>\n  </section>\n\n  <section id="page-collection"')
troca("$('dataNotice').innerHTML=`<strong>⚠ ${loaded===3?'Dados trimestrais carregados:':'Versão parcial:'}</strong>", "$('dataNotice').innerHTML=`<strong>${loaded===3?'Dados trimestrais carregados:':'Versão parcial:'}</strong>")

# 13. Forja com todas as regras (pedido do Gustavo, 23/10): classes, raridade completa, missões, trilha e fórmulas
troca('<div class="notice"><strong>Importante:</strong> no arquivo parcial de outubro', '<div id="forgeRules" class="forge-rules"></div><div class="notice"><strong>Importante:</strong> no arquivo parcial de outubro')
h = h.replace("function refreshApp(){", "function refreshApp(){try{renderForgeRules()}catch(e){console.error(e)};", 1)
troca("if(page==='forge')renderForge()", "if(page==='forge'){renderForge();renderForgeRules()}")

# 14. v3 (plano de refinamento): oficial × RPG, missões com estado e evidência, ficha completa, extrato de XP,
#     confronto em 3 modos, crônica com acumulado e variação, período na coleção, importação com prévia
rpg_js = (AQUI / 'rpg_v3.js').read_text(encoding='utf-8')
troca('\ninit();\n', '\n' + rpg_js.strip() + '\ninit();\ninitV3();\n')
troca('<select id="roleFilter" class="control">', '<select id="periodFilter" class="control" aria-label="Período"></select><select id="roleFilter" class="control">')
troca('<div class="duel-selects">', '<div class="view-segment duel-modes" id="duelModes" role="tablist" aria-label="Modo do confronto"><button type="button" class="active" data-mode="rapido">Duelo rápido</button><button type="button" data-mode="tatico">Análise tática</button><button type="button" data-mode="equipe">Confronto de equipe</button></div><div class="duel-selects">')
troca('<div id="toast" class="toast" role="status" aria-live="polite">',
      '<div id="importModal" class="modal" hidden><div class="modal-box"><div class="modal-head"><h2>Prévia da importação</h2><button class="xbtn" data-close="importModal" aria-label="Fechar">×</button></div><div id="importBody"></div>'
      '<div class="detail-actions"><button class="btn primary" id="importConfirm">Confirmar importação</button><button class="btn" id="importCancel">Cancelar</button></div></div></div>'
      '<div id="toast" class="toast" role="status" aria-live="polite">')

if falhas:
    print('FALHAS:'); [print(' -', f) for f in falhas]; sys.exit(1)
SAIDA.write_text(h, encoding='utf-8')
print('ok ->', SAIDA.name, len(h), 'bytes;', len(meses['q4']['prom']), 'promotores')
# cópia para a página online (claude.ai): sem doctype/html/head/body, que o publicador coloca
a = re.sub(r'<!doctype html>\s*', '', h, flags=re.I)
for t in [r'<html[^>]*>', r'</html>', r'<head>', r'</head>', r'<body>', r'</body>', r'<meta charset="utf-8">', r'<meta name="viewport"[^>]*>']:
    a = re.sub(t, '', a, count=1, flags=re.I)
(AQUI / 'artifact_farma_cards_q4.html').write_text(a.strip() + chr(10), encoding='utf-8')
