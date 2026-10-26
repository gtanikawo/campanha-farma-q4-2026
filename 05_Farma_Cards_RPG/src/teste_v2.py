"""Teste de navegador do Farma Cards v2 (Playwright + Chromium).
Abre o HTML de verdade, percorre as telas, confere os números contra o placar oficial,
testa raridades nos limites, filtros, modal, pacote, confronto, Forja, importação e celular.
Rodar: python teste_v2.py   -> imprime OK/FALHA por item e salva prints em src/prints/"""
import json, re, sys, tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
V2 = RAIZ / 'Farma_Cards_Q4_Legends_RPG_v2.html'
PLACAR = RAIZ.parent / '03_HTML' / 'Placar_Farma_Q4_2026_Ajustado.html'
PRINTS = AQUI / 'prints'; PRINTS.mkdir(exist_ok=True)
oficial = json.loads(re.search(r'const MESES = (\{.*?\});\s*\n\s*const ORDEM_MESES', PLACAR.read_text(encoding='utf-8-sig'), re.S).group(1))
res = []
def ok(nome, cond, det=''):
    res.append((bool(cond), nome, det)); print(('OK     ' if cond else 'FALHA  ') + nome + (f' | {det}' if det else ''))

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 1366, 'height': 900})
    pg = ctx.new_page(); erros = []
    pg.on('console', lambda m: erros.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.goto(V2.as_uri()); pg.wait_for_timeout(800)
    pg.screenshot(path=str(PRINTS / '01_santuario_desktop.png'), full_page=True)

    # dados = placar oficial
    m = pg.evaluate('MESES')
    ok('Dados iguais ao placar oficial (out e q4)', m['out'] == oficial['out'] and m['q4'] == oficial['q4'], f"{len(m['q4']['prom'])} promotores, {len(m['q4']['sup'])} supervisores")
    ok('Nov e dez indisponíveis', not m['nov'].get('disponivel') and not m['dez'].get('disponivel'))
    ok('Santuário: líder = 1º do placar', oficial['q4']['prom'][0]['nome'] in pg.inner_text('#leaderFeature'))
    ok('Santuário: total executado', f"{oficial['q4']['tot']['exec']:,}".replace(',', '.') in pg.inner_text('#homeStats'))
    ok('Sem "NP SCORE" na tela', 'NP SCORE' not in pg.inner_text('body'))

    # raridade nos limites
    lim = pg.evaluate("""()=>{const t=v=>tier({pct:v}).id;return [t(49.9),t(50),t(64.9),t(65),t(74.9),t(75),t(84.9),t(85),t(94.9),t(95),t(null)]}""")
    ok('Raridade nos limites', lim == ['common','bronze','bronze','silver','silver','gold','gold','epic','epic','mythic','common'], str(lim))
    holo = pg.evaluate("""()=>[mythicUnlocked({pct:95,pctv:50,exec:15}),mythicUnlocked({pct:95,pctv:49.9,exec:15}),mythicUnlocked({pct:95,pctv:50,exec:14}),mythicUnlocked({pct:94.9,pctv:90,exec:90}),isFoil({pct:96,pctv:40,exec:40})]""")
    ok('Mítica holográfica x selada', holo == [True, False, False, False, False], str(holo))
    ok('Campo sem número não ganha premium', pg.evaluate("()=>mythicUnlocked({pct:'x',pctv:90,exec:90})") is False)
    pos_antes = pg.evaluate("()=>MESES.q4.prom.map(r=>r.pos).join()")
    pg.evaluate("()=>{thresholds.mythic=50;refreshApp()}")
    ok('Mudar raridade não mexe na posição', pg.evaluate("()=>MESES.q4.prom.map(r=>r.pos).join()") == pos_antes)
    pg.evaluate("()=>{thresholds={...DEFAULT_THRESHOLDS};refreshApp()}")

    # navegação
    for page in ['collection', 'duel', 'quests', 'chronicle', 'forge', 'home']:
        pg.click(f'.sidebar .nav-btn[data-page="{page}"]'); pg.wait_for_timeout(250)
        ok(f'Navegação: {page}', pg.is_visible(f'#page-{page}'))

    # coleção
    pg.click('.sidebar .nav-btn[data-page="collection"]'); pg.wait_for_timeout(300)
    n_cards = pg.locator('#collectionCards .player-card').count()
    ok('Coleção: todas as cartas', n_cards == len(oficial['q4']['prom']) + len(oficial['q4']['sup']), str(n_cards))
    pg.screenshot(path=str(PRINTS / '02_colecao_desktop.png'))
    ordem = pg.evaluate("()=>[...document.querySelectorAll('#collectionCards .player-card .card-rank')].filter(e=>e.textContent.includes('PROMOTOR')).map(e=>parseInt(e.textContent.replace('#','')))")
    ok('Coleção na ordem oficial', ordem == sorted(ordem) and len(ordem) == len(oficial['q4']['prom']))
    pg.fill('#searchCards', 'edna'); pg.wait_for_timeout(200)
    ok('Busca', pg.locator('#collectionCards .player-card').count() == 1)
    pg.fill('#searchCards', ''); pg.select_option('#roleFilter', 'sup'); pg.wait_for_timeout(200)
    ok('Filtro supervisores', pg.locator('#collectionCards .player-card').count() == len(oficial['q4']['sup']))
    pg.select_option('#roleFilter', 'all'); pg.select_option('#rarityFilter', 'mythic'); pg.wait_for_timeout(200)
    n_myth = sum(1 for r in oficial['q4']['prom'] + oficial['q4']['sup'] if r.get('nota', r['pct']) >= 95)
    ok('Filtro raridade Mítica', pg.locator('#collectionCards .player-card').count() == n_myth, str(n_myth))
    pg.select_option('#rarityFilter', 'all'); pg.select_option('#ufFilter', 'RS'); pg.wait_for_timeout(200)
    ok('Filtro UF', pg.locator('#collectionCards .player-card').count() == sum(1 for r in oficial['q4']['prom'] if r['uf'] == 'RS'))
    pg.select_option('#ufFilter', 'all')
    s1 = oficial['q4']['sup'][0]['nome']
    pg.select_option('#supervisorFilter', s1); pg.wait_for_timeout(200)
    ok('Filtro supervisor = time + carta do supervisor', pg.locator('#collectionCards .player-card').count() == sum(1 for r in oficial['q4']['prom'] if r['supFull'] == s1) + 1)
    pg.select_option('#supervisorFilter', 'all'); pg.select_option('#sortCards', 'np'); pg.wait_for_timeout(200)
    pg.click('[data-layout="list"]'); pg.wait_for_timeout(200)
    ok('Modo lista', pg.is_visible('#collectionList') and pg.locator('#collectionList .list-row').count() == n_cards)
    pg.click('[data-layout="cards"]'); pg.select_option('#sortCards', 'pos')

    # ficha
    pg.locator('#collectionCards .player-card').first.click(); pg.wait_for_timeout(400)
    ok('Ficha abre', pg.is_visible('#cardModal'))
    txt = pg.inner_text('#modalBody'); l1 = oficial['q4']['prom'][0]
    ok('Ficha com dados oficiais', l1['nome'] in txt and f"{l1['pct']:.1f}".replace('.', ',') in txt)
    pg.screenshot(path=str(PRINTS / '03_ficha.png'))
    pg.click('#flipCard'); pg.wait_for_timeout(700)
    ok('Carta vira', 'flipped' in (pg.get_attribute('#detailCard3D', 'class') or ''))
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    ok('Escape fecha a ficha', not pg.is_visible('#cardModal'))

    # pacote
    pg.click('#openPackTop'); pg.wait_for_timeout(300)
    ok('Pacote abre com 3 cartas seladas', pg.locator('#packCards .pack-cover').count() == 3)
    pg.click('#revealPack'); pg.wait_for_timeout(800)
    ok('Pacote revela 3 cartas', pg.locator('#packCards .player-card').count() == 3)
    pg.screenshot(path=str(PRINTS / '04_pacote.png'))
    pg.click('#packModal .xbtn'); pg.wait_for_timeout(200)

    # confronto
    pg.click('.sidebar .nav-btn[data-page="duel"]'); pg.wait_for_timeout(300)
    pg.click('#startDuel'); pg.wait_for_timeout(700)
    larg = pg.evaluate("()=>[...document.querySelectorAll('.fighter .duel-fill')].map(e=>e.getBoundingClientRect().width)")
    ok('Confronto: barras preenchidas', len(larg) >= 6 and all(w > 0 for w in larg), str([round(w) for w in larg]))
    pg.screenshot(path=str(PRINTS / '05_confronto.png'), full_page=True)
    pg.click('#randomDuel'); pg.wait_for_timeout(300)
    ok('Confronto sorteado: duas pessoas diferentes', pg.input_value('#fighterA') != pg.input_value('#fighterB'))

    # missões, crônica, forja
    pg.click('.sidebar .nav-btn[data-page="quests"]'); pg.wait_for_timeout(300)
    ok('Missões: 15 missões, 10 seladas (atos II e III)', pg.locator('#actsBox .quest').count() == 15 and pg.locator('#actsBox .quest.locked').count() == 10)
    ok('Missões: trilha com 5 recompensas', pg.locator('#rewardTrack .reward-step').count() == 5)
    ok('Missões: jornada do líder abre', oficial['q4']['prom'][0]['nome'] in pg.inner_text('#journeyBox'))
    ato1 = pg.evaluate("()=>{const r={...MESES.out.prom[0],kind:'prom'};return missoesDe(r).filter(m=>m.feito).map(m=>m.id)}")
    ok('Líder conquista as missões do Ato I que bate', set(ato1) == {'a1_passo','a1_firme','a1_disc','a1_over'}, str(ato1))
    pg.screenshot(path=str(PRINTS / '13_missoes.png'), full_page=True)
    # simulação de nov/dez só na memória (não vai para o arquivo)
    sim = pg.evaluate('''()=>{const base=MESES.out;const mk=(f,lab)=>{const c=clone(base);c.label=lab;c.prom.forEach((r,i)=>{r.pct=Math.min(100,+(r.pct*f).toFixed(1))});return c};
      MESES.nov=mk(1.05,'Novembro');MESES.dez=mk(1.10,'Dezembro');MESES.q4=clone(MESES.dez);refreshApp();
      const r={...MESES.q4.prom[0],kind:'prom'};const ms=missoesDe(r);
      return {abertos:[1,2,3].map(atoAberto),feitos:ms.filter(m=>m.feito).map(m=>m.id),trilha:trilhaDe(r).atual.nome,xp:missionXP(r),selados:document.querySelectorAll('#actsBox .quest.locked').length}}''')
    ok('Simulação: com nov e dez os 3 atos abrem', sim['abertos'] == [True, True, True] and sim['selados'] == 0, str(sim['abertos']))
    ok('Simulação: missões de evolução e trilogia contam', {'a2_evolui','a2_duplo','a3_luas','a3_escalada','a3_trilogia'} <= set(sim['feitos']), f"{sim['trilha']} · {sim['xp']} XP")
    ok('Simulação: recompensa sobe até Lenda', sim['trilha'] == 'Lenda')
    pg.reload(); pg.wait_for_timeout(500)
    pg.click('.sidebar .nav-btn[data-page="chronicle"]'); pg.wait_for_timeout(300)
    ok('Crônica: nov e dez selados', pg.locator('.month-node.future[disabled]').count() == 2)
    pg.click('.sidebar .nav-btn[data-page="forge"]'); pg.wait_for_timeout(300)
    ok('Forja só leitura (sem campos)', pg.locator('#page-forge input').count() == 0 and pg.locator('#page-forge .setting-row').count() >= 12)
    ok('Forja: 6 blocos de regras (raridade, classes, missões, trilha, fórmulas, patente)', pg.locator('#forgeRules .forge-block').count() == 6)
    ok('Forja: 15 missões e 5 níveis da trilha listados', pg.locator('#forgeRules .forge-block').nth(2).locator('tbody tr').count() == 15 and pg.locator('#forgeRules .forge-block').nth(3).locator('tbody tr').count() == 5)
    ok('Forja: Mítica selada x holográfica e fórmulas de XP/nível', 'Mítica selada' in pg.inner_text('#forgeRules') and 'a cada 250 XP' in pg.inner_text('#forgeRules'))
    ok('Forja mostra propostas desligadas', pg.inner_text('#gatingInputs').count('desligada') == 2)
    pg.screenshot(path=str(PRINTS / '06_forja.png'), full_page=True)

    # ---------- v3: oficial × RPG (base real) ----------
    pg.click('.sidebar .nav-btn[data-page="collection"]'); pg.wait_for_timeout(300)
    pg.locator('#collectionCards .player-card').first.click(); pg.wait_for_timeout(400)
    ficha = pg.inner_text('#modalBody')
    ok('Ficha: rótulos OFICIAL e RPG, elegibilidade pendente', 'OFICIAL' in ficha and 'RPG' in ficha and 'Pendente' in ficha)
    ok('Ficha: faltam X XP e extrato de XP', 'Faltam' in ficha and 'XP base do PWR' in ficha)
    tot = pg.evaluate("()=>{const r=findRowById(activeDetail);return [extratoXP(r).reduce((s,l)=>s+l.xp,0), xp(r)]}")
    ok('Extrato de XP soma o XP total', tot[0] == tot[1], str(tot))
    xp1 = pg.evaluate("()=>MESES.q4.prom.map(r=>xp({...r,kind:'prom'})).join()")
    pg.keyboard.press('Escape')
    for _ in range(3):
        pg.locator('#collectionCards .player-card').first.click(); pg.wait_for_timeout(150); pg.keyboard.press('Escape')
    ok('Abrir a mesma carta várias vezes não muda XP', pg.evaluate("()=>MESES.q4.prom.map(r=>xp({...r,kind:'prom'})).join()") == xp1)
    rar = pg.evaluate("()=>MESES.q4.prom.map(r=>tier(r).id).join()")
    pg.reload(); pg.wait_for_timeout(500)
    ok('Mesmos dados = mesma raridade (após recarregar)', pg.evaluate("()=>MESES.q4.prom.map(r=>tier(r).id).join()") == rar)
    pos0 = pg.evaluate("()=>MESES.q4.prom.map(r=>r.pos).join()")
    pg.click('.sidebar .nav-btn[data-page="duel"]'); pg.wait_for_timeout(200)
    for modo in ['rapido', 'tatico', 'equipe']:
        pg.click(f'#duelModes button[data-mode="{modo}"]'); pg.wait_for_timeout(500)
    txt = pg.inner_text('#duelResult')
    ok('Confronto de equipe compara supervisores (SIMULAÇÃO)', 'SIMULAÇÃO' in txt and 'Confronto de equipe' in txt and pg.evaluate("()=>findRowById($('fighterA').value).kind") == 'sup')
    pg.click('#duelModes button[data-mode="tatico"]'); pg.wait_for_timeout(2200)
    ok('Análise tática mostra a contribuição de cada atributo no PWR', 'pontos de PWR' in pg.inner_text('#duelResult'))
    pg.screenshot(path=str(PRINTS / '16_confronto_tatico.png'), full_page=True)
    ok('Confronto não altera o ranking oficial', pg.evaluate("()=>MESES.q4.prom.map(r=>r.pos).join()") == pos0)
    pg.click('.sidebar .nav-btn[data-page="quests"]'); pg.wait_for_timeout(300)
    jt = pg.inner_text('#journeyBox')
    ok('Missões: "Atingida até agora" (outubro parcial) e progresso com evidência', 'Atingida até agora' in jt and 'Progresso' in jt and 'Outubro: 98,2%' in jt)
    ok('Missões de novembro e dezembro: Bloqueada', jt.count('Bloqueada') == 10)
    pg.screenshot(path=str(PRINTS / '17_jornada.png'), full_page=True)
    pg.click('.sidebar .nav-btn[data-page="chronicle"]'); pg.wait_for_timeout(300)
    ok('Crônica: outubro parcial, nov/dez aguardando', 'Parcial até 22/10' in pg.inner_text('#monthTrack') and pg.inner_text('#monthTrack').count('Aguardando apuração') == 2)

    # importação com prévia (base real)
    tmp = Path(tempfile.mkdtemp())
    def espera_toast(trecho):
        try: pg.wait_for_function("t=>document.getElementById('toast').textContent.includes(t)", arg=trecho, timeout=4000); return True
        except Exception: return False
    ruim = tmp / 'corrompido.html'; ruim.write_text('<html>sem dados</html>', encoding='utf-8')
    pg.evaluate("()=>{$('toast').textContent=''}"); pg.set_input_files('#importFile', str(ruim))
    ok('Arquivo sem dados: erro e dados intactos', espera_toast('Não foi possível ler') and pg.evaluate('MESES.q4.prom.length') == len(oficial['q4']['prom']))
    pg.set_input_files('#importFile', str(PLACAR)); pg.wait_for_selector('#importModal:not([hidden])', timeout=4000)
    ok('Importar outubro de novo: prévia diz que nada muda e não deixa confirmar', 'nada muda' in pg.inner_text('#importBody') and pg.is_disabled('#importConfirm'))
    pg.click('#importCancel')
    ok('XP igual depois de reimportar outubro', pg.evaluate("()=>MESES.q4.prom.map(r=>xp({...r,kind:'prom'})).join()") == xp1)

    # ---------- v3: dados ARTIFICIAIS (cópia separada do HTML, nomes TESTE) ----------
    def linha(nome, sup, uf, lojas, ex, plan, cump):
        return {'nome': nome, 'sup': sup.split()[0], 'supFull': sup, 'uf': uf, 'lojas': lojas, 'exec': ex, 'plan': plan, 'cump': cump}
    def mes(rows, label, corte, fechado):
        def rank(rs):
            rs = sorted(rs, key=lambda r: (-r['exec'] / r['lojas'], -(r['cump'] / r['plan']), r['nome']))
            return [dict(r, pos=i + 1, pct=round(r['exec'] / r['lojas'] * 100, 1), pctv=round(r['cump'] / r['plan'] * 100, 1)) for i, r in enumerate(rs)]
        prom = rank(rows); sups = {}
        for r in rows:
            s = sups.setdefault(r['supFull'], {'nome': r['supFull'], 'prom': 0, 'lojas': 0, 'exec': 0, 'plan': 0, 'cump': 0})
            s['prom'] += 1; s['lojas'] += r['lojas']; s['exec'] += r['exec']; s['plan'] += r['plan']; s['cump'] += r['cump']
        return {'prom': prom, 'sup': rank(list(sups.values())), 'tot': {'lojas': sum(r['lojas'] for r in rows), 'exec': sum(r['exec'] for r in rows)},
                'label': label, 'sub': 'mês fechado' if fechado else 'parcial', 'disponivel': True, 'corte': corte, 'fechado': fechado, 'titulo': label, 'periodo': label}
    def soma(*meses_):
        acc = {}
        for m in meses_:
            for r in m['prom']:
                a = acc.setdefault(r['nome'], dict(linha(r['nome'], r['supFull'], r['uf'], 0, 0, 0, 0)))
                for c in ['lojas', 'exec', 'plan', 'cump']: a[c] += r[c]
        return mes(list(acc.values()), 'Q4 acumulado', meses_[-1]['corte'], False)
    OUT = [linha('ANA TESTE', 'SUP TESTE UM', 'SP', 100, 80, 200, 150), linha('BRUNO TESTE', 'SUP TESTE UM', 'RJ', 50, 20, 100, 30), linha('CARLA TESTE', 'SUP TESTE DOIS', 'MG', 40, 39, 80, 70)]
    NOV = [linha('ANA TESTE', 'SUP TESTE UM', 'SP', 120, 108, 240, 200), linha('BRUNO TESTE', 'SUP TESTE UM', 'RJ', 50, 50, 100, 90), linha('CARLA TESTE', 'SUP TESTE DOIS', 'MG', 40, 40, 80, 80)]
    mo = mes(OUT, 'Outubro', '2026-10-31', True); mn = mes(NOV, 'Novembro', '2026-11-20', False)
    DEZ_AUS = {'label': 'Dezembro', 'sub': 'aguardando', 'disponivel': False}
    base_t = {'out': mo, 'nov': {'label': 'Novembro', 'sub': 'aguardando', 'disponivel': False}, 'dez': DEZ_AUS, 'q4': soma(mo)}
    h2 = V2.read_text(encoding='utf-8')
    i0 = h2.index('const BASE_DATA = '); i1 = h2.index('\nlet MESES = clone(BASE_DATA);')
    HT = tmp / 'cards_TESTE_artificial.html'; HT.write_text(h2[:i0] + 'const BASE_DATA = ' + json.dumps(base_t) + ';' + h2[i1:], encoding='utf-8')
    tc = b.new_context(viewport={'width': 1366, 'height': 900}); tp = tc.new_page(); errt = []
    tp.on('pageerror', lambda e: errt.append(str(e)))
    tp.goto(HT.as_uri()); tp.wait_for_timeout(500)
    ok('[TESTE] Outubro fechado: missão "Concluída"', 'Concluída' in tp.evaluate("()=>missoesDe(findRowById('prom::ana teste')).filter(m=>m.feito).map(m=>m.estado.txt).join()"))
    novo = {'out': mo, 'nov': mn, 'dez': DEZ_AUS, 'q4': soma(mo, mn)}
    f = tmp / 'com_nov.json'; f.write_text(json.dumps(novo), encoding='utf-8')
    tp.set_input_files('#importFile', str(f)); tp.wait_for_selector('#importModal:not([hidden])', timeout=4000)
    pv = tp.inner_text('#importBody')
    ok('[TESTE] Prévia mostra meses e totais antes de confirmar', 'Outubro (fechado)' in pv and 'Novembro (até 20/11)' in pv and not tp.is_disabled('#importConfirm'))
    tp.click('#importConfirm'); tp.wait_for_timeout(400)
    ac = tp.evaluate("()=>{const r=acumuladoAte('nov').get('prom::ana teste');return [r.lojas,r.exec,r.plan,r.cump]}")
    ok('[TESTE] Acumulado out+nov conta cada mês uma vez (Ana 220/188)', ac == [220, 188, 440, 350], str(ac))
    ok('[TESTE] Dezembro ausente não vira zero nem mês concluído', tp.evaluate("()=>hasMonth('dez')") is False and tp.evaluate("()=>elegibilidade(findRowById('prom::ana teste')).st") == 'pendente')
    ok('[TESTE] Missão do Ato II "Atingida até agora" (novembro parcial)', 'Atingida até agora' in tp.evaluate("()=>missoesDe(findRowById('prom::ana teste')).filter(m=>m.ato===2&&m.feito).map(m=>m.estado.txt).join()"))
    xpA = tp.evaluate("()=>xp(findRowById('prom::ana teste'))")
    tp.set_input_files('#importFile', str(f)); tp.wait_for_selector('#importModal:not([hidden])', timeout=4000)
    ok('[TESTE] Reimportar o mesmo arquivo: nada muda e não soma XP', 'nada muda' in tp.inner_text('#importBody') and tp.is_disabled('#importConfirm') and tp.evaluate("()=>xp(findRowById('prom::ana teste'))") == xpA)
    tp.click('#importCancel')
    hist = tp.evaluate("()=>historico(findRowById('prom::bruno teste')).filter(h=>h.carregado).map(h=>h.acum.pos)")
    ok('[TESTE] Crônica: posição no acumulado mês a mês (Bruno)', len(hist) == 2, str(hist))
    mo2 = mes([OUT[0], OUT[1], linha('CARLA TESTE', 'SUP TESTE DOIS', 'MG', 40, 20, 80, 30)], 'Outubro', '2026-10-31', True)
    corr = {'out': mo2, 'nov': mn, 'dez': DEZ_AUS, 'q4': soma(mo2, mn)}
    f2 = tmp / 'correcao.json'; f2.write_text(json.dumps(corr), encoding='utf-8')
    antes = tp.evaluate("()=>missoesDe(findRowById('prom::carla teste')).filter(m=>m.feito).map(m=>m.id).join()")
    tp.set_input_files('#importFile', str(f2)); tp.wait_for_selector('#importModal:not([hidden])', timeout=4000); tp.click('#importConfirm'); tp.wait_for_timeout(400)
    depois = tp.evaluate("()=>missoesDe(findRowById('prom::carla teste')).filter(m=>m.feito).map(m=>m.id).join()")
    ok('[TESTE] Correção no dado oficial recalcula as missões (sem XP fantasma)', 'a1_over' in antes and 'a1_over' not in depois, f'{antes} -> {depois}')
    ruim2 = json.loads(json.dumps(novo)); ruim2['out']['prom'][0]['pct'] = 150
    f3 = tmp / 'ruim.json'; f3.write_text(json.dumps(ruim2), encoding='utf-8')
    tp.set_input_files('#importFile', str(f3)); tp.wait_for_selector('#importModal:not([hidden])', timeout=4000)
    ok('[TESTE] Percentual fora de 0–100 bloqueia a importação', 'Importação bloqueada' in tp.inner_text('#importBody') and tp.is_disabled('#importConfirm'))
    tp.click('#importCancel')
    tp.click('.sidebar .nav-btn[data-page="collection"]'); tp.wait_for_timeout(200); tp.select_option('#periodFilter', 'nov'); tp.wait_for_timeout(300)
    ok('[TESTE] Coleção por período (novembro)', tp.evaluate('activeKey') == 'nov' and tp.locator('#collectionCards .player-card').count() == 5)
    tp.click('#openPackTop'); tp.wait_for_timeout(200); tp.click('#revealPack'); tp.wait_for_timeout(1500)
    ids = tp.evaluate("()=>packDraw.map(identity)")
    ok('[TESTE] Pacote com cartas distintas', len(ids) == len(set(ids)) == 3)
    ok('[TESTE] Console sem erros', not errt, '; '.join(errt[:2]))


    # ---------- tempo de casa e supervisor Top 1 no Santuário (24/10) ----------
    tcasa = json.loads((AQUI / 'dados' / 'tempo_casa.json').read_text(encoding='utf-8'))['pessoas']
    pg.goto(V2.as_uri()); pg.wait_for_timeout(600)
    sup1 = oficial['q4']['sup'][0]
    supf = pg.inner_text('#supFeature')
    ok('Santuário: supervisor Top 1 em destaque', sup1['nome'] in supf and '1º SUPERVISOR' in supf and f"{sup1['pct']:.1f}".replace('.', ',') in supf, sup1['nome'])
    ok('Santuário: promotor líder continua em destaque', oficial['q4']['prom'][0]['nome'] in pg.inner_text('#leaderFeature'))
    pg.locator('#page-home .split').screenshot(path=str(PRINTS / '18_santuario_destaques.png'))
    pg.click('.sidebar .nav-btn[data-page="collection"]'); pg.wait_for_timeout(300)
    ok('Carta mostra a patente e os meses de casa', 'de casa' in pg.inner_text('#collectionCards .player-card >> nth=0'))
    for nome, faixa in [('Novato', (0, 3)), ('Escudeiro', (3, 6)), ('Desbravador', (6, 9)), ('Mestre', (9, 12))]:
        pg.select_option('#casaFilter', nome); pg.wait_for_timeout(150)
        esperado = sum(1 for k, v in tcasa.items() if faixa[0] <= v['meses'] < faixa[1])
        ok(f'Filtro tempo de casa: {nome}', pg.locator('#collectionCards .player-card').count() == esperado, str(esperado))
    pg.select_option('#casaFilter', 'pend'); pg.wait_for_timeout(150)
    ok('Sem tempo de casa no banco: pendente (Willian Molulo)', pg.locator('#collectionCards .player-card').count() == 1 and 'Molulo' in pg.inner_text('#collectionCards'))
    pg.locator('#collectionCards .player-card').first.click(); pg.wait_for_timeout(300)
    ok('Ficha sem tempo de casa mostra PENDENTE', 'Tempo de casa pendente' in pg.inner_text('#modalBody') and 'PENDENTE' in pg.inner_text('#modalBody'))
    pg.keyboard.press('Escape'); pg.select_option('#casaFilter', 'all'); pg.wait_for_timeout(150)
    pos_casa = pg.evaluate("()=>MESES.q4.prom.map(r=>r.pos+':'+power({...r,kind:'prom'})).join()")
    pg.select_option('#sortCards', 'casa'); pg.wait_for_timeout(200)
    ok('Ordenar por tempo de casa não muda posição nem PWR', pg.evaluate("()=>MESES.q4.prom.map(r=>r.pos+':'+power({...r,kind:'prom'})).join()") == pos_casa)
    pg.select_option('#sortCards', 'pos')


    # ---------- modo escuro e fundo animado (24/10) ----------
    pg.goto(V2.as_uri()); pg.wait_for_timeout(500)
    ok('Tema padrão = claro', pg.evaluate('document.documentElement.dataset.tema') == 'claro' and 'Modo escuro' in pg.inner_text('#temaBtn'))
    pg.click('#temaBtn'); pg.wait_for_timeout(200)
    fundo = pg.evaluate("getComputedStyle(document.querySelector('.panel')).backgroundColor")
    ok('Botão liga o modo escuro (painéis escuros)', pg.evaluate('document.documentElement.dataset.tema') == 'escuro' and fundo == 'rgb(30, 26, 40)', fundo)
    pg.reload(); pg.wait_for_timeout(500)
    ok('Modo escuro fica salvo ao recarregar', pg.evaluate('document.documentElement.dataset.tema') == 'escuro' and 'Modo claro' in pg.inner_text('#temaBtn'))
    pg.click('#temaBtn'); pg.wait_for_timeout(200)
    ok('Botão volta ao modo claro', pg.evaluate('document.documentElement.dataset.tema') == 'claro')
    ok('Fundo animado ativo (estrelas e partículas)', pg.evaluate("getComputedStyle(document.querySelector('.ambient')).display") != 'none' and pg.evaluate("parseFloat(document.getElementById('particles').style.opacity)") >= .5)
    lg = pg.evaluate("()=>{const [a,b]=[...document.querySelectorAll('.hero-logos .logo-chip')].map(c=>c.getBoundingClientRect());return [a.width,a.height,b.width,b.height]}")
    ok('Logos SPOT e Reckitt com o mesmo selo', lg[0] == lg[2] and lg[1] == lg[3], str(lg))


    # ---------- nota oficial (26/10): 50% lojas + 50% frequência ----------
    pg.goto(V2.as_uri()); pg.wait_for_timeout(500)
    l1 = oficial['q4']['prom'][0]
    ok('Santuário: líder pela nota oficial', 'NOTA OFICIAL' in pg.inner_text('#leaderFeature') and f"{l1['nota']:.1f}".replace('.', ',') in pg.inner_text('#leaderFeature'), f"{l1['nome']} {l1['nota']}")
    ok('Santuário: supervisor Top 1 pela nota do time', 'NOTA DO TIME' in pg.inner_text('#supFeature') and oficial['q4']['sup'][0]['nome'] in pg.inner_text('#supFeature'))
    pg.click('.sidebar .nav-btn[data-page="collection"]'); pg.wait_for_timeout(300)
    ok('Carta mostra NOTA', 'NOTA' in pg.inner_text('#collectionCards .player-card >> nth=0'))
    pg.locator('#collectionCards .player-card').first.click(); pg.wait_for_timeout(300)
    fx = pg.inner_text('#modalBody')
    ok('Ficha: nota oficial, % lojas, % frequência e % NewsPage', 'NOTA OFICIAL' in fx and '% FREQUÊNCIA' in fx and '% NEWSPAGE' in fx and 'visitas cumpridas' not in fx.lower())
    pg.keyboard.press('Escape')
    ok('Raridade segue a nota oficial', pg.evaluate("()=>MESES.q4.prom.every(r=>tier(r).id===tier({pct:r.nota}).id)"))


    # celular
    mob = b.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce', is_mobile=True)
    mp = mob.new_page(); mp.on('pageerror', lambda e: erros.append('mobile: ' + str(e)))
    mp.goto(V2.as_uri()); mp.wait_for_timeout(600)
    ok('Celular: sem rolagem lateral', mp.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'), str(mp.evaluate('[document.documentElement.scrollWidth, innerWidth]')))
    ok('Celular: menu inferior visível', mp.is_visible('.mobile-nav'))
    mp.screenshot(path=str(PRINTS / '07_santuario_celular.png'), full_page=True)
    mp.click('.mobile-nav button[data-page="collection"]'); mp.wait_for_timeout(300)
    ok('Celular: coleção sem rolagem lateral', mp.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'))
    mp.screenshot(path=str(PRINTS / '08_colecao_celular.png'))

    ok('Sem legenda de rodapé', pg.locator('#footerNote').count() == 0 and 'Interface de gamificação' not in pg.content())
    ok('Sem ARCHIVE · OF · LEGENDS e sem "· RPG"', 'ARCHIVE' not in pg.content() and '· RPG' not in pg.inner_text('body'))
    ok('Aviso parcial discreto no fim do Santuário', pg.locator('#page-home .data-note').count() == 1)
    tam = pg.evaluate("()=>[...document.querySelectorAll('.hero-logos .logo-chip')].map(c=>c.getBoundingClientRect().width+'x'+c.getBoundingClientRect().height)")
    ok('Logos SPOT e Reckitt no mesmo tamanho', len(tam) == 2 and tam[0] == tam[1], str(tam))
    ok('Console sem erros', not erros, '; '.join(erros[:3]))
    b.close()

falhas = [r for r in res if not r[0]]
print(f'\n{len(res) - len(falhas)} de {len(res)} OK')
sys.exit(1 if falhas else 0)
