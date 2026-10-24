"""Testes do Placar_Farma_Q4_2026_Ajustado.html (Playwright + Chromium).
Parte A: base real (números, interface, celular).
Parte B: dados ARTIFICIAIS num HTML temporário separado (nomes "TESTE"), sem tocar a base oficial:
acumulado entre meses, mês ausente, importação repetida/atualizada/antiga/inválida, CSV,
lojas repetidas, elegibilidade e resultado final.
Rodar: python teste_placar.py"""
import json, re, sys, tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

AQUI = Path(__file__).resolve().parent
HTML = AQUI.parent / 'Placar_Farma_Q4_2026_Ajustado.html'
PRINTS = AQUI / 'prints'; PRINTS.mkdir(exist_ok=True)
TMP = Path(tempfile.mkdtemp())
res = []
def ok(nome, cond, det=''):
    res.append(bool(cond)); print(('OK     ' if cond else 'FALHA  ') + nome + (f' | {det}' if det else ''))

h = HTML.read_text(encoding='utf-8')
snap = json.loads(re.search(r'const MESES = (\{.*?\});\s*\n\s*const ORDEM_MESES', h, re.S).group(1))

# ---------- dados artificiais ----------
def pac(mes, corte, lojas, hash_=None):
    p = {'formato': 'placar-farma-q4/v1', 'mes': mes, 'corte': corte, 'atualizado_em': corte + ' 10:00', 'fonte': 'TESTE ARTIFICIAL', 'lojas': lojas}
    if hash_: p['hash'] = hash_
    return p
def lojas_de(pessoa, sup, uf, n, n_exec, rota, prefixo):
    return [[rota, f'{prefixo}-{i:04d}', 1, pessoa, sup, uf, 2, (1 if i < n_exec else 0)] for i in range(n)]
OUT = lojas_de('ANA TESTE', 'SUP TESTE UM', 'SP', 100, 80, 1, 'OUT') + lojas_de('BRUNO TESTE', 'SUP TESTE UM', 'RJ', 50, 20, 2, 'OUTB') + lojas_de('CARLA TESTE', 'SUP TESTE DOIS', 'MG', 40, 39, 3, 'OUTC') + lojas_de('VAGA EM ABERTO', 'SUP TESTE DOIS', 'MG', 30, 0, 4, 'OUTV')
NOV = lojas_de('ANA TESTE', 'SUP TESTE UM', 'SP', 120, 108, 1, 'NOV') + lojas_de('BRUNO TESTE', 'SUP TESTE UM', 'RJ', 50, 50, 2, 'NOVB') + lojas_de('CARLA TESTE', 'SUP TESTE DOIS', 'MG', 40, 40, 3, 'NOVC')
NOV_DUP = NOV + [NOV[0], NOV[1]]  # 2 lojas repetidas na mesma rota
DEZ = lojas_de('ANA TESTE', 'SUP TESTE UM', 'SP', 110, 99, 1, 'DEZ') + lojas_de('CARLA TESTE', 'SUP TESTE DOIS', 'MG', 40, 40, 3, 'DEZC')  # Bruno sem roteiro em dez
base_teste = {'2026-10': pac('2026-10', '2026-10-31', OUT)}
ht = re.sub(r'const PACOTES_BASE = \{.*?\};\n', lambda m: 'const PACOTES_BASE = ' + json.dumps(base_teste) + ';\n', h, count=1, flags=re.S)
HT = TMP / 'placar_TESTE_artificial.html'; HT.write_text(ht, encoding='utf-8')
def arq(nome, obj):
    f = TMP / nome; f.write_text(json.dumps(obj) if not isinstance(obj, str) else obj, encoding='utf-8'); return str(f)

with sync_playwright() as p:
    b = p.chromium.launch()
    # ================= PARTE A: base real =================
    ctx = b.new_context(viewport={'width': 1366, 'height': 900}); pg = ctx.new_page(); erros = []
    pg.on('pageerror', lambda e: erros.append(str(e))); pg.on('console', lambda m: erros.append(m.text) if m.type == 'error' else None)
    pg.goto(HTML.as_uri()); pg.wait_for_timeout(700)
    pg.screenshot(path=str(PRINTS / 'A1_placar_desktop.png'), full_page=True)
    V = pg.evaluate('VIEWS')
    for k in ['out', 'q4']:
        cp = lambda rows, cs: [{c: r[c] for c in cs} for r in rows]
        pc = ['pos', 'nome', 'sup', 'supFull', 'uf', 'lojas', 'exec', 'pct', 'pctv']; sc = ['pos', 'nome', 'prom', 'lojas', 'exec', 'pct', 'pctv']
        ok(f'JS = retrato do build ({k}): promotores, supervisores e totais', cp(V[k]['prom'], pc) == cp(snap[k]['prom'], pc) and cp(V[k]['sup'], sc) == cp(snap[k]['sup'], sc) and V[k]['tot'] == snap[k]['tot'])
    t = V['q4']['tot']
    ok('Totais: 89 promotores, 5 supervisores, 7.072 lojas, 4.815 executadas, 68,1%', len(V['q4']['prom']) == 89 and len(V['q4']['sup']) == 5 and t == {'lojas': 7072, 'exec': 4815} and round(t['exec'] / t['lojas'] * 100, 1) == 68.1)
    ok('Soma dos promotores = total geral', sum(r['lojas'] for r in V['q4']['prom']) == t['lojas'] and sum(r['exec'] for r in V['q4']['prom']) == t['exec'])
    ok('Soma dos supervisores = total geral', sum(r['lojas'] for r in V['q4']['sup']) == t['lojas'] and sum(r['exec'] for r in V['q4']['sup']) == t['exec'])
    ok('% = exec ÷ lojas em todas as linhas', all(abs(r['pct'] - round(r['exec'] / r['lojas'] * 100, 1)) < 1e-9 for r in V['q4']['prom'] + V['q4']['sup']))
    ok('Ordem: % lojas e depois % visitas', all((a['px'], a['pvx']) >= (b_['px'], b_['pvx']) for a, b_ in zip(V['q4']['prom'], V['q4']['prom'][1:])))
    ok('Status: Q4 2026 — ACUMULADO PARCIAL ATÉ 22/10/2026', pg.inner_text('#statusQ4') == 'Q4 2026 — ACUMULADO PARCIAL ATÉ 22/10/2026')
    ok('Novembro e dezembro aguardando apuração (desabilitados)', pg.locator('#mesPills .pill[disabled]').count() == 2 and 'aguardando apuração' in pg.inner_text('#mesPills'))
    ok('Aviso de trimestre em andamento visível', pg.is_visible('#avisoDados'))
    ok('Elegibilidade: todos pendentes, com justificativa', all(r['eleg']['st'] == 'pendente' and 'aguardando novembro e dezembro' in r['eleg']['just'] for r in V['q4']['prom'] + V['q4']['sup']))
    ok('Base: data de atualização visível', '22/10/2026' in pg.inner_text('#baseInfo') and '2026-10-23' in pg.inner_text('#baseInfo'))
    pg.click('#mesPills .pill[data-mes="out"]'); pg.wait_for_timeout(200)
    ok('Período Outubro: status e pódio do mês', pg.inner_text('#statusQ4') == 'OUTUBRO 2026 — PARCIAL ATÉ 22/10/2026' and 'pódio de outubro' in pg.inner_text('#panel-prom').lower())
    pg.click('#mesPills .pill[data-mes="q4"]'); pg.wait_for_timeout(200)
    pg.fill('#busca-prom', 'edna'); pg.wait_for_timeout(150)
    me = pg.inner_text('#me')
    ok('Busca + simulação com aviso', pg.locator('#tbody-prom tr').count() == 1 and 'Simulação com a classificação atual' in me and 'Elegibilidade Q4: Pendente' in me)
    r = next(x for x in V['q4']['prom'] if x['nome'].startswith('Edna')); c = V['q4']['prom'][2]
    n = next(i for i in range(1, 999) if (r['exec'] + i) * c['lojas'] > c['exec'] * r['lojas'])
    ok('Simulação: nº de lojas = menor inteiro que passa o 3º (conta em inteiros)', f'mais {n} loja' in me, f'{n} lojas')
    pg.fill('#busca-prom', ''); pg.select_option('#uf-prom', 'RS'); pg.wait_for_timeout(150)
    ok('Filtro UF', pg.locator('#tbody-prom tr').count() == sum(1 for x in V['q4']['prom'] if x['uf'] == 'RS'))
    pg.select_option('#uf-prom', ''); pg.click('#panel-prom th[data-key="pct"]'); pg.wait_for_timeout(150)
    ok('Ordenação por coluna', pg.locator('#panel-prom th.sorted').count() == 1)
    pg.click('.tab[data-group="sup"]'); pg.wait_for_timeout(150)
    ok('Aba supervisores (ranking separado)', pg.is_visible('#panel-sup') and pg.locator('#tbody-sup tr').count() == 5)
    pg.click('.view-switch .pill[data-view="times"]'); pg.wait_for_timeout(150)
    ok('Pódio por supervisor', pg.locator('#teamGrid .team').count() == 5 and 'ACUMULADO PARCIAL' in pg.inner_text('#statusTimes'))
    ok('Base real: console sem erros', not erros, '; '.join(erros[:2]))
    mob = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True); mp = mob.new_page(); mp.goto(HTML.as_uri()); mp.wait_for_timeout(500)
    ok('Celular sem rolagem lateral', mp.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'))
    mp.screenshot(path=str(PRINTS / 'A2_placar_celular.png'), full_page=True)

    # ================= PARTE B: dados artificiais (arquivo separado) =================
    tc = b.new_context(viewport={'width': 1366, 'height': 900}); tp = tc.new_page(); errt = []
    tp.on('pageerror', lambda e: errt.append(str(e)))
    tp.goto(HT.as_uri()); tp.wait_for_timeout(400)
    def importa(caminho, espera):
        tp.evaluate("()=>{document.getElementById('impMsg').textContent=''}")
        tp.set_input_files('#importFile', caminho)
        try: tp.wait_for_function("t=>document.getElementById('impMsg').textContent.includes(t)", arg=espera, timeout=4000); return True
        except Exception: return False
    q = lambda: tp.evaluate("()=>VIEWS.q4")
    ok('[TESTE] Só outubro: vaga em aberto fora (190 lojas)', q()['tot'] == {'lojas': 190, 'exec': 139})
    ok('[TESTE] Antes de dezembro: elegibilidade pendente', all(r['eleg']['st'] == 'pendente' for r in q()['prom']))
    ok('[TESTE] Importa novembro com 2 lojas repetidas: inclui e avisa', importa(arq('nov.json', pac('2026-11', '2026-11-20', NOV_DUP)), 'Novembro incluído') and 'repetida' in tp.inner_text('#impMsg'))
    ok('[TESTE] Nov: repetidas contadas 1 vez (210 lojas)', tp.evaluate("()=>VIEWS.nov.tot") == {'lojas': 210, 'exec': 198})
    ok('[TESTE] Q4 = out + nov sem somar out duas vezes', q()['tot'] == {'lojas': 400, 'exec': 337})
    ok('[TESTE] Dezembro ausente: aguardando, não zerado', tp.evaluate("()=>VIEWS.dez.disponivel") is False and 'aguardando' in tp.inner_text('#mesPills'))
    ok('[TESTE] Importar o mesmo arquivo de novo não muda nada', importa(arq('nov2.json', pac('2026-11', '2026-11-20', NOV_DUP)), 'Nada mudou') and q()['tot'] == {'lojas': 400, 'exec': 337})
    ok('[TESTE] Arquivo inválido: erro e dados intactos', importa(arq('ruim.json', {'formato': 'x'}), 'Não foi possível importar') and q()['tot'] == {'lojas': 400, 'exec': 337})
    ok('[TESTE] Arquivo mais antigo que o carregado é recusado', importa(arq('nov_velho.json', pac('2026-11', '2026-11-10', NOV[:10])), 'mais antigo'))
    ok('[TESTE] Novembro atualizado (corte mais novo) substitui', importa(arq('nov_novo.json', pac('2026-11', '2026-11-30', NOV)), 'Novembro atualizado') and q()['tot'] == {'lojas': 400, 'exec': 337})
    cab = 'mes;corte;cod_rota;loja_id;cod_colaborador;colaborador;supervisor;uf;planejado;pesquisas\n'
    csv = cab + ''.join(f'2026-12;2026-12-31;{l[0]};{l[1]};{l[2]};{l[3]};{l[4]};{l[5]};{l[6]};{l[7]}\n' for l in DEZ)
    ok('[TESTE] Importa dezembro por CSV', importa(arq('dez.csv', csv), 'Dezembro incluído'))
    ana = next(r for r in q()['prom'] if r['nome'] == 'Ana Teste')
    ok('[TESTE] Exemplo do prompt: Ana 287/330 = 86,97%', ana['exec'] == 287 and ana['lojas'] == 330 and abs(ana['px'] * 100 - 86.9697) < 0.001, f"{ana['exec']}/{ana['lojas']} = {ana['px']*100:.2f}%")
    medias = (80 / 100 + 108 / 120 + 99 / 110) / 3 * 100
    ok('[TESTE] Acumulado não é média simples dos % mensais', abs(ana['px'] * 100 - medias) > 0.01, f'média simples seria {medias:.2f}%')
    el = {r['nome']: r['eleg']['st'] for r in q()['prom']}
    ok('[TESTE] Elegibilidade: Ana e Carla elegíveis; Bruno inelegível (sem roteiro em dez)', el == {'Ana Teste': 'elegivel', 'Carla Teste': 'elegivel', 'Bruno Teste': 'inelegivel'}, str(el))
    ok('[TESTE] Justificativa da inelegibilidade', 'Sem roteiro em dezembro' in next(r for r in q()['prom'] if r['nome'] == 'Bruno Teste')['eleg']['just'])
    ok('[TESTE] Supervisores com ranking separado', [s['nome'] for s in q()['sup']] == ['Sup Teste Dois', 'Sup Teste Um'])
    ok('[TESTE] 3 meses fechados: RESULTADO FINAL', tp.inner_text('#statusQ4') == 'Q4 2026 — RESULTADO FINAL')
    tp.reload(); tp.wait_for_timeout(400)
    ok('[TESTE] Importações continuam após recarregar (só neste navegador)', q()['tot']['lojas'] == 400 + 150)
    tp.click('#resetBase'); tp.wait_for_timeout(300)
    ok('[TESTE] Voltar à base do arquivo', q()['tot'] == {'lojas': 190, 'exec': 139})
    ok('[TESTE] Console sem erros', not errt, '; '.join(errt[:2]))
    b.close()

print(f'\n{sum(res)} de {len(res)} OK')
sys.exit(0 if all(res) else 1)
