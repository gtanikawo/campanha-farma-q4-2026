"""Leva a nota oficial (50% lojas + 50% frequência, visitas cobradas por janela) para o cálculo em Python do build_placar.py."""
from pathlib import Path
AQUI = Path(__file__).resolve().parent
p = AQUI / 'build_placar.py'
s = p.read_text(encoding='utf-8')
falhas = []
def troca(velho, novo):
    global s
    if velho not in s: falhas.append(velho[:80]); return
    s = s.replace(velho, novo)

troca("""Rodar: python build_placar.py
      python build_placar.py --nota  -> Placar_Farma_Q4_2026_Nota_VALIDACAO.html (promotores pela nota lojas + frequência;
                                         não mexe no placar oficial nem no artifact)
""", """- Regra oficial desde 26/10/2026: nota = 50% % lojas executadas + 50% % frequência (visitas cobradas por janela);
  desempate % lojas → % frequência → % NewsPage → nome. A conferência com o placar original passa a checar
  lojas e executadas de cada pessoa e os totais (a ordem mudou de propósito com a regra nova).
Rodar: python build_placar.py
""")
troca("NOTA = '--nota' in sys.argv\nSAIDA = HTML_DIR / ('Placar_Farma_Q4_2026_Nota_VALIDACAO.html' if NOTA else 'Placar_Farma_Q4_2026_Ajustado.html')",
      "SAIDA = HTML_DIR / 'Placar_Farma_Q4_2026_Ajustado.html'")
troca("""def calcular(meses):
    P, S, lojas, execs = {}, {}, 0, 0
    for m in meses:
        vistos = set()""", """import calendar, math
def vencidas(plan, dias_mes, dia_corte):
    # a visita k (de plan) vence no dia ceil(k × dias do mês ÷ plan); no mês fechado, dia_corte = último dia
    return sum(1 for k in range(1, plan + 1) if math.ceil(k * dias_mes / plan) <= dia_corte)

def calcular(meses):
    P, S, lojas, execs = {}, {}, 0, 0
    for m in meses:
        dm = calendar.monthrange(int(m[:4]), int(m[5:]))[1]
        corte = pacotes[m]['corte']
        dc = dm if int(corte[8:10]) >= dm else int(corte[8:10])
        vistos = set()""")
troca("""            e, c, k = (1 if pesq > 0 else 0), min(pesq, plan), norm(colab)
            lojas += 1; execs += e
            p = P.setdefault(k, {'raw': colab, 'lojas': 0, 'exec': 0, 'plan': 0, 'cump': 0, 'uf': Counter(), 'sup': defaultdict(Counter)})
            p['lojas'] += 1; p['exec'] += e; p['plan'] += plan; p['cump'] += c; p['uf'][uf] += 1; p['sup'][m][sup] += 1
            ks = norm(sup)
            s = S.setdefault(ks, {'raw': sup, 'lojas': 0, 'exec': 0, 'plan': 0, 'cump': 0, 'pessoas': set()})
            s['lojas'] += 1; s['exec'] += e; s['plan'] += plan; s['cump'] += c; s['pessoas'].add(k)
    ordem = lambda r: (-r['px'], -r['pvx'], r['nome'])""", """            e, c, k = (1 if pesq > 0 else 0), min(pesq, plan), norm(colab)
            den = max(vencidas(plan, dm, dc), c)
            lojas += 1; execs += e
            p = P.setdefault(k, {'raw': colab, 'lojas': 0, 'exec': 0, 'plan': 0, 'cump': 0, 'den': 0, 'pesq': 0, 'uf': Counter(), 'sup': defaultdict(Counter)})
            p['lojas'] += 1; p['exec'] += e; p['plan'] += plan; p['cump'] += c; p['den'] += den; p['pesq'] += pesq; p['uf'][uf] += 1; p['sup'][m][sup] += 1
            ks = norm(sup)
            s = S.setdefault(ks, {'raw': sup, 'lojas': 0, 'exec': 0, 'plan': 0, 'cump': 0, 'den': 0, 'pesq': 0, 'pessoas': set()})
            s['lojas'] += 1; s['exec'] += e; s['plan'] += plan; s['cump'] += c; s['den'] += den; s['pesq'] += pesq; s['pessoas'].add(k)
    def notas(x):
        px = x['exec'] / x['lojas']; pfx = x['cump'] / x['den'] if x['den'] else px
        return {'px': px, 'pvx': pfx, 'pnp': x['pesq'] / x['plan'] if x['plan'] else 0, 'nota': (px + pfx) / 2}
    ordem = lambda r: (-r['nota'], -r['px'], -r['pvx'], -r['pnp'], r['nome'])""")
troca("""                     'lojas': p['lojas'], 'exec': p['exec'], 'plan': p['plan'], 'cump': p['cump'], 'px': p['exec'] / p['lojas'], 'pvx': p['cump'] / p['plan'] if p['plan'] else 0})""",
      """                     'lojas': p['lojas'], 'exec': p['exec'], 'plan': p['den'], 'cump': p['cump'], 'pesq': p['pesq'], **notas(p)})""")
troca("""    sup = [{'nome': titulo(s['raw']), 'prom': len(s['pessoas']), 'lojas': s['lojas'], 'exec': s['exec'], 'plan': s['plan'], 'cump': s['cump'],
            'px': s['exec'] / s['lojas'], 'pvx': s['cump'] / s['plan'] if s['plan'] else 0} for s in S.values()]""",
      """    sup = [{'nome': titulo(s['raw']), 'prom': len(s['pessoas']), 'lojas': s['lojas'], 'exec': s['exec'], 'plan': s['den'], 'cump': s['cump'], 'pesq': s['pesq'], **notas(s)}
           for s in S.values()]""")
troca("""        return [dict({c: r[c] for c in campos}, pos=i + 1, pct=round(r['px'] * 100, 1), pctv=round(r['pvx'] * 100, 1)) for i, r in enumerate(rows)]
    return (fim(prom, ['nome', 'sup', 'supFull', 'uf', 'lojas', 'exec', 'plan', 'cump']), fim(sup, ['nome', 'prom', 'lojas', 'exec', 'plan', 'cump']), {'lojas': lojas, 'exec': execs})""",
      """        # pct = % lojas · pctv = % frequência · nota = nota oficial · pnp = % NewsPage (pesquisas ÷ planejado)
        # plan = visitas cobradas (vencidas até o corte, ou feitas se maior) · cump = visitas feitas até o planejado
        return [dict({c: r[c] for c in campos}, pos=i + 1, pct=round(r['px'] * 100, 1), pctv=round(r['pvx'] * 100, 1),
                     nota=round(r['nota'] * 100, 1), pnp=round(r['pnp'] * 100, 1)) for i, r in enumerate(rows)]
    return (fim(prom, ['nome', 'sup', 'supFull', 'uf', 'lojas', 'exec', 'plan', 'cump', 'pesq']), fim(sup, ['nome', 'prom', 'lojas', 'exec', 'plan', 'cump', 'pesq']), {'lojas': lojas, 'exec': execs})""")
troca("""# conferência com o placar original (outubro): ranking, totais e campos têm que ser idênticos
orig = json.loads(re.search(r'const MESES = (\\{.*?\\});\\s*\\n\\s*const ORDEM_MESES', ORIGINAL.read_text(encoding='utf-8-sig'), re.S).group(1))
falhas = []
for k in ['out', 'q4']:
    for parte in ['prom', 'sup', 'tot']:
        a = MESES[k][parte]; b = orig[k][parte]
        if parte != 'tot':
            campos = [c for c in a[0] if c in b[0]]
            a = [{c: r[c] for c in campos} for r in a]; b = [{c: r[c] for c in campos} for r in b]
        if a != b: falhas.append(f'{k}.{parte} diferente do placar original')
if falhas:
    print('PARA: ' + '; '.join(falhas)); sys.exit(1)
print('conferência: out e q4 idênticos ao placar original (prom, sup, tot)')""",
"""# conferência com o placar original (outubro): mesmas pessoas, mesmas lojas e executadas e mesmos totais.
# A ordem e os % mudam de propósito com a nota oficial (26/10); o resto não pode mudar.
orig = json.loads(re.search(r'const MESES = (\\{.*?\\});\\s*\\n\\s*const ORDEM_MESES', ORIGINAL.read_text(encoding='utf-8-sig'), re.S).group(1))
falhas = []
for k in ['out', 'q4']:
    if MESES[k]['tot'] != orig[k]['tot']: falhas.append(f'{k}.tot diferente do placar original')
    for parte in ['prom', 'sup']:
        chave = lambda r: (r['nome'], r['lojas'], r['exec'])
        if sorted(map(chave, MESES[k][parte])) != sorted(map(chave, orig[k][parte])): falhas.append(f'{k}.{parte}: lojas/executadas diferentes do placar original')
        if any(round(r['exec'] / r['lojas'] * 100, 1) != r['pct'] for r in MESES[k][parte]): falhas.append(f'{k}.{parte}: % lojas incoerente')
if falhas:
    print('PARA: ' + '; '.join(falhas)); sys.exit(1)
print('conferência: out e q4 com as mesmas pessoas, lojas, executadas e totais do placar original; ordem pela nota oficial')""")
p.write_text(s, encoding='utf-8')
print('FALHAS: ' + ' | '.join(falhas) if falhas else 'ok: build_placar.py com a nota oficial')
