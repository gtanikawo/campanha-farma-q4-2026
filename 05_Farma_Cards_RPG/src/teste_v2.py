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
    n_myth = sum(1 for r in oficial['q4']['prom'] + oficial['q4']['sup'] if r['pct'] >= 95)
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
    ok('Forja: 5 blocos de regras (raridade, classes, missões, trilha, fórmulas)', pg.locator('#forgeRules .forge-block').count() == 5)
    ok('Forja: 15 missões e 5 níveis da trilha listados', pg.locator('#forgeRules .forge-block').nth(2).locator('tbody tr').count() == 15 and pg.locator('#forgeRules .forge-block').nth(3).locator('tbody tr').count() == 5)
    ok('Forja: Mítica selada x holográfica e fórmulas de XP/nível', 'Mítica selada' in pg.inner_text('#forgeRules') and 'a cada 250 XP' in pg.inner_text('#forgeRules'))
    ok('Forja mostra propostas desligadas', pg.inner_text('#gatingInputs').count('desligada') == 2)
    pg.screenshot(path=str(PRINTS / '06_forja.png'), full_page=True)

    # importação
    tmp = Path(tempfile.mkdtemp())
    ruim = tmp / 'corrompido.html'; ruim.write_text('<html>sem dados</html>', encoding='utf-8')
    def espera_toast(trecho):
        try: pg.wait_for_function("t=>document.getElementById('toast').textContent.includes(t)", arg=trecho, timeout=4000); return True
        except Exception: return False
    pg.evaluate("()=>{$('toast').textContent=''}")
    pg.set_input_files('#importFile', str(ruim))
    ok('Importar arquivo ruim: erro e dados intactos', espera_toast('Não foi possível importar') and pg.evaluate('MESES.q4.prom.length') == len(oficial['q4']['prom']))
    pg.evaluate("()=>{$('toast').textContent=''}"); pg.set_input_files('#importFile', str(PLACAR))
    ok('Importar HTML oficial', espera_toast('importado com sucesso'))
    js = tmp / 'placar.json'; js.write_text(json.dumps({'MESES': oficial}, ensure_ascii=False), encoding='utf-8')
    pg.evaluate("()=>{$('toast').textContent=''}"); pg.set_input_files('#importFile', str(js))
    ok('Importar JSON compatível', espera_toast('importado com sucesso'))
    salvo = pg.evaluate("()=>JSON.parse(localStorage.getItem('farmaCards.data.v2')||'null')")
    ok('Importação guardada com carimbo da base', salvo and salvo['base'] == pg.evaluate('BASE_STAMP'))
    pg.evaluate("()=>localStorage.setItem('farmaCards.data.v2',JSON.stringify({base:'versao-antiga',meses:MESES}))")
    pg.reload(); pg.wait_for_timeout(600)
    ok('Dado de versão antiga é descartado ao abrir', pg.evaluate("()=>localStorage.getItem('farmaCards.data.v2')") is None)

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
