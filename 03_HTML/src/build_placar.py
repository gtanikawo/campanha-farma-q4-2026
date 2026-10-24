"""Gera Placar_Farma_Q4_2026_Ajustado.html (pasta 03_HTML) a partir dos pacotes mensais em src/dados.

- Embute os pacotes (1 linha por mês + rota + loja) e o motor de cálculo em JS.
- Calcula em Python, com a mesma regra, o retrato de cada mês e do Q4 (const MESES),
  mantido para compatibilidade com o Farma Cards e para conferência.
- Confere esse retrato com o placar original de outubro (Placar_Farma_Q4_2026_Parcial_Outubro.html):
  se algum número mudar, o build para.
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

def calcular(meses):
    P, S, lojas, execs = {}, {}, 0, 0
    for m in meses:
        vistos = set()
        for cod_rota, loja, cod, colab, sup, uf, plan, pesq in pacotes[m]['lojas']:
            if (cod_rota, loja) in vistos: continue
            vistos.add((cod_rota, loja))
            if vaga(colab): continue
            e, c, k = (1 if pesq > 0 else 0), min(pesq, plan), norm(colab)
            lojas += 1; execs += e
            p = P.setdefault(k, {'raw': colab, 'lojas': 0, 'exec': 0, 'plan': 0, 'cump': 0, 'uf': Counter(), 'sup': defaultdict(Counter)})
            p['lojas'] += 1; p['exec'] += e; p['plan'] += plan; p['cump'] += c; p['uf'][uf] += 1; p['sup'][m][sup] += 1
            ks = norm(sup)
            s = S.setdefault(ks, {'raw': sup, 'lojas': 0, 'exec': 0, 'plan': 0, 'cump': 0, 'pessoas': set()})
            s['lojas'] += 1; s['exec'] += e; s['plan'] += plan; s['cump'] += c; s['pessoas'].add(k)
    ordem = lambda r: (-r['px'], -r['pvx'], r['nome'])
    prom = []
    for k, p in P.items():
        ult = [m for m in meses if p['sup'].get(m)][-1]
        supraw = moda(p['sup'][ult])
        prom.append({'nome': titulo(p['raw']), 'sup': titulo(supraw).split()[0], 'supFull': titulo(supraw), 'uf': moda(p['uf']),
                     'lojas': p['lojas'], 'exec': p['exec'], 'px': p['exec'] / p['lojas'], 'pvx': p['cump'] / p['plan'] if p['plan'] else 0})
    prom.sort(key=ordem)
    sup = [{'nome': titulo(s['raw']), 'prom': len(s['pessoas']), 'lojas': s['lojas'], 'exec': s['exec'],
            'px': s['exec'] / s['lojas'], 'pvx': s['cump'] / s['plan'] if s['plan'] else 0} for s in S.values()]
    sup.sort(key=ordem)
    def fim(rows, campos):
        return [dict({c: r[c] for c in campos}, pos=i + 1, pct=round(r['px'] * 100, 1), pctv=round(r['pvx'] * 100, 1)) for i, r in enumerate(rows)]
    return (fim(prom, ['nome', 'sup', 'supFull', 'uf', 'lojas', 'exec']), fim(sup, ['nome', 'prom', 'lojas', 'exec']), {'lojas': lojas, 'exec': execs})

def dbr(iso): return f'{iso[8:10]}/{iso[5:7]}/{iso[:4]}'
MESES = {}
disp = [m for m in Q4 if m in pacotes]
for m in Q4:
    if m not in pacotes:
        MESES[CHAVE[m]] = {'label': NOME[m], 'sub': 'aguardando apuração', 'disponivel': False}; continue
    prom, sup, tot = calcular([m]); c = pacotes[m]['corte']
    MESES[CHAVE[m]] = {'prom': prom, 'sup': sup, 'tot': tot, 'label': NOME[m], 'sub': f'até {dbr(c)[:5]}', 'disponivel': True,
                       'titulo': f'de {NOME[m].lower()}', 'periodo': f'Apuração de <b>01/{m[5:]}</b> a <b>{dbr(c)[:5]}</b> · {NOME[m]}'}
if disp:
    prom, sup, tot = calcular(disp); c = pacotes[disp[-1]]['corte']
    MESES['q4'] = {'prom': prom, 'sup': sup, 'tot': tot, 'label': 'Q4 acumulado', 'sub': '+'.join(NOME[m][:3].lower() for m in disp), 'disponivel': True,
                   'titulo': 'parcial do Q4', 'periodo': f'Q4 2026 — acumulado parcial até {dbr(c)}'}

# conferência com o placar original (outubro): ranking, totais e campos têm que ser idênticos
orig = json.loads(re.search(r'const MESES = (\{.*?\});\s*\n\s*const ORDEM_MESES', ORIGINAL.read_text(encoding='utf-8-sig'), re.S).group(1))
falhas = []
for k in ['out', 'q4']:
    for parte in ['prom', 'sup', 'tot']:
        a = MESES[k][parte]; b = orig[k][parte]
        if parte != 'tot':
            b = [{c: r[c] for c in a[0]} for r in b]
        if a != b: falhas.append(f'{k}.{parte} diferente do placar original')
if falhas:
    print('PARA: ' + '; '.join(falhas)); sys.exit(1)
print('conferência: out e q4 idênticos ao placar original (prom, sup, tot)')

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
