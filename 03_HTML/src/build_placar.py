"""Gera Placar_Farma_Q4_2026_Ajustado.html (pasta 03_HTML) a partir dos pacotes mensais em src/dados.

- Embute os pacotes (1 linha por mês + rota + loja) e o motor de cálculo em JS.
- Calcula em Python, com a mesma regra, o retrato de cada mês e do Q4 (const MESES),
  mantido para compatibilidade com o Farma Cards e para conferência.
- Confere esse retrato com o placar original de outubro (Placar_Farma_Q4_2026_Parcial_Outubro.html):
  se algum número mudar, o build para.
- Regra oficial desde 26/10/2026: nota = 50% % lojas executadas + 50% % frequência (Σ pesquisas ÷ Σ planejado do mês, como no Tracking);
  desempate % lojas → % frequência → % NewsPage → nome. A conferência com o placar original passa a checar
  lojas e executadas de cada pessoa e os totais (a ordem mudou de propósito com a regra nova).
Rodar: python build_placar.py
"""
import json, re, sys, unicodedata
from pathlib import Path
from collections import Counter, defaultdict

AQUI = Path(__file__).resolve().parent
HTML_DIR = AQUI.parent
ORIGINAL = HTML_DIR / 'Placar_Farma_Q4_2026_Parcial_Outubro.html'
SAIDA = HTML_DIR / 'Placar_Farma_Q4_2026_Ajustado.html'
Q4 = ['2026-10', '2026-11', '2026-12']
NOME = {'2026-10': 'Outubro', '2026-11': 'Novembro', '2026-12': 'Dezembro'}
CHAVE = {'2026-10': 'out', '2026-11': 'nov', '2026-12': 'dez'}
LIGA = {'DE', 'DA', 'DOS', 'DAS', 'E', 'DO'}

def norm(s): return ' '.join(unicodedata.normalize('NFD', str(s)).encode('ascii', 'ignore').decode().lower().split())
def titulo(s): return ' '.join(w.lower() if w in LIGA else w[:1].upper() + w[1:].lower() for w in str(s).split())
def vaga(n): return 'VAGA' in str(n).upper()
def moda(c): return sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

pacotes = {}
for m in Q4:
    f = AQUI / 'dados' / f'{m}.json'
    if f.exists():
        pacotes[m] = json.loads(f.read_text(encoding='utf-8'))

import calendar, math
def vencidas(plan, dias_mes, dia_corte):
    # a visita k (de plan) vence no dia ceil(k × dias do mês ÷ plan); no mês fechado, dia_corte = último dia
    return sum(1 for k in range(1, plan + 1) if math.ceil(k * dias_mes / plan) <= dia_corte)

def calcular(meses):
    P, S, lojas, execs = {}, {}, 0, 0
    for m in meses:
        dm = calendar.monthrange(int(m[:4]), int(m[5:]))[1]
        corte = pacotes[m]['corte']
        dc = dm if int(corte[8:10]) >= dm else int(corte[8:10])
        vistos = set()
        for cod_rota, loja, cod, colab, sup, uf, plan, pesq in pacotes[m]['lojas']:
            if (cod_rota, loja) in vistos: continue
            vistos.add((cod_rota, loja))
            if vaga(colab): continue
            # frequência como no Tracking (% Realizado Newspage): pesquisas ÷ planejado do mês, sem limite por loja
            e, c, k = (1 if pesq > 0 else 0), pesq, norm(colab)
            den = plan
            lojas += 1; execs += e
            p = P.setdefault(k, {'raw': colab, 'lojas': 0, 'exec': 0, 'plan': 0, 'cump': 0, 'den': 0, 'pesq': 0, 'uf': Counter(), 'sup': defaultdict(Counter)})
            p['lojas'] += 1; p['exec'] += e; p['plan'] += plan; p['cump'] += c; p['den'] += den; p['pesq'] += pesq; p['uf'][uf] += 1; p['sup'][m][sup] += 1
            ks = norm(sup)
            s = S.setdefault(ks, {'raw': sup, 'lojas': 0, 'exec': 0, 'plan': 0, 'cump': 0, 'den': 0, 'pesq': 0, 'pessoas': set()})
            s['lojas'] += 1; s['exec'] += e; s['plan'] += plan; s['cump'] += c; s['den'] += den; s['pesq'] += pesq; s['pessoas'].add(k)
    def notas(x):
        px = x['exec'] / x['lojas']; pfx = x['cump'] / x['den'] if x['den'] else px
        return {'px': px, 'pvx': pfx, 'pnp': x['pesq'] / x['plan'] if x['plan'] else 0, 'nota': (px + pfx) / 2}
    ordem = lambda r: (-r['nota'], -r['px'], -r['pvx'], -r['pnp'], r['nome'])
    prom = []
    for k, p in P.items():
        ult = [m for m in meses if p['sup'].get(m)][-1]
        supraw = moda(p['sup'][ult])
        prom.append({'nome': titulo(p['raw']), 'sup': titulo(supraw).split()[0], 'supFull': titulo(supraw), 'uf': moda(p['uf']),
                     'lojas': p['lojas'], 'exec': p['exec'], 'plan': p['den'], 'cump': p['cump'], 'pesq': p['pesq'], **notas(p)})
    prom.sort(key=ordem)
    sup = [{'nome': titulo(s['raw']), 'prom': len(s['pessoas']), 'lojas': s['lojas'], 'exec': s['exec'], 'plan': s['den'], 'cump': s['cump'], 'pesq': s['pesq'], **notas(s)}
           for s in S.values()]
    sup.sort(key=ordem)
    def fim(rows, campos):
        # pct = % lojas · pctv = % frequência · nota = nota oficial · pnp = % NewsPage (pesquisas ÷ planejado)
        # plan = visitas cobradas (vencidas até o corte, ou feitas se maior) · cump = visitas feitas até o planejado
        r1 = lambda v: math.floor(v * 1000 + 0.5) / 10   # arredonda o meio para cima, igual ao placar (JS) e ao Excel
        return [dict({c: r[c] for c in campos}, pos=i + 1, pct=r1(r['px']), pctv=r1(r['pvx']), nota=r1(r['nota']), pnp=r1(r['pnp'])) for i, r in enumerate(rows)]
    return (fim(prom, ['nome', 'sup', 'supFull', 'uf', 'lojas', 'exec', 'plan', 'cump', 'pesq']), fim(sup, ['nome', 'prom', 'lojas', 'exec', 'plan', 'cump', 'pesq']), {'lojas': lojas, 'exec': execs})

def dbr(iso): return f'{iso[8:10]}/{iso[5:7]}/{iso[:4]}'
MESES = {}
disp = [m for m in Q4 if m in pacotes]
for m in Q4:
    if m not in pacotes:
        MESES[CHAVE[m]] = {'label': NOME[m], 'sub': 'aguardando apuração', 'disponivel': False}; continue
    prom, sup, tot = calcular([m]); c = pacotes[m]['corte']
    fech = int(c[8:10]) >= __import__('calendar').monthrange(int(m[:4]), int(m[5:]))[1]
    MESES[CHAVE[m]] = {'prom': prom, 'sup': sup, 'tot': tot, 'label': NOME[m], 'sub': 'mês fechado' if fech else f'até {dbr(c)[:5]}', 'disponivel': True, 'corte': c, 'fechado': fech,
                       'titulo': f'de {NOME[m].lower()}', 'periodo': f'Apuração de <b>01/{m[5:]}</b> a <b>{dbr(c)[:5]}</b> · {NOME[m]}'}
if disp:
    prom, sup, tot = calcular(disp); c = pacotes[disp[-1]]['corte']
    MESES['q4'] = {'prom': prom, 'sup': sup, 'tot': tot, 'label': 'Q4 acumulado', 'sub': '+'.join(NOME[m][:3].lower() for m in disp), 'disponivel': True,
                   'titulo': 'parcial do Q4', 'periodo': f'Q4 2026 — acumulado parcial até {dbr(c)}', 'corte': c,
                   'fechado': len(disp) == 3 and all(MESES[CHAVE[m]]['fechado'] for m in disp), 'meses': [CHAVE[m] for m in disp]}

# conferência com o placar original (outubro): mesmas pessoas, mesmas lojas e executadas e mesmos totais.
# A ordem e os % mudam de propósito com a nota oficial (26/10); o resto não pode mudar.
orig = json.loads(re.search(r'const MESES = (\{.*?\});\s*\n\s*const ORDEM_MESES', ORIGINAL.read_text(encoding='utf-8-sig'), re.S).group(1))
falhas = []
for k in ['out', 'q4']:
    if MESES[k]['tot'] != orig[k]['tot']: falhas.append(f'{k}.tot diferente do placar original')
    for parte in ['prom', 'sup']:
        chave = lambda r: (r['nome'], r['lojas'], r['exec'])
        if sorted(map(chave, MESES[k][parte])) != sorted(map(chave, orig[k][parte])): falhas.append(f'{k}.{parte}: lojas/executadas diferentes do placar original')
        if any(math.floor(r['exec'] / r['lojas'] * 1000 + 0.5) / 10 != r['pct'] for r in MESES[k][parte]): falhas.append(f'{k}.{parte}: % lojas incoerente')
if falhas:
    print('PARA: ' + '; '.join(falhas)); sys.exit(1)
print('conferência: out e q4 com as mesmas pessoas, lojas, executadas e totais do placar original; ordem pela nota oficial')

ref = (AQUI / 'template_v1_referencia.html').read_text(encoding='utf-8')
corpo = (AQUI / 'corpo_ajustado.html').read_text(encoding='utf-8')
css_extra = (AQUI / 'extra.css').read_text(encoding='utf-8')
cabeca = ref[:ref.index('</style>')] + css_extra + '</style>\n'
topo = ref[ref.index('<div class="wrap">'):ref.index('  <!-- VISÃO COMPLETA -->')]
pagina = (cabeca + topo + corpo).replace('<title>Destaques Farma Q4</title>', '<title>Placar Farma Q4</title>')
pagina = pagina.replace('__PACOTES__', json.dumps(pacotes, ensure_ascii=False, separators=(',', ':')))
pagina = pagina.replace('__MESES__', json.dumps(MESES, ensure_ascii=False))
pagina = pagina.replace('__SPOT_LOGO__', (AQUI / 'spot_logo.txt').read_text().strip()).replace('__RK_LOGO__', (AQUI / 'rk_logo.txt').read_text().strip())
for ph in ['__PACOTES__', '__MESES__', '__SPOT_LOGO__', '__RK_LOGO__']:
    assert ph not in pagina, ph
(AQUI / 'artifact_placar_q4.html').write_text(pagina, encoding='utf-8')
i = pagina.index('<div class="wrap">')
completo = ('<!doctype html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + pagina[:i] + '</head>\n<body>\n' + pagina[i:] + '\n</body>\n</html>\n')
SAIDA.write_text(completo, encoding='utf-8')
print(f'ok -> {SAIDA.name} ({len(completo)//1024} KB); meses: {", ".join(NOME[m] + " até " + dbr(pacotes[m]["corte"]) for m in disp)}')
