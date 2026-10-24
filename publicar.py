"""Monta a versão semanal do site (pasta site/) publicada no Vercel.

1. Gera e testa o placar (03_HTML/src) e o Farma Cards (05_Farma_Cards_RPG/src). Para se algum teste falhar.
2. Copia: placar ajustado -> site/placar/index.html ; Farma Cards -> site/cards/index.html
3. Gera a página inicial (site_template/index.html) e site/versao.json.
Depois: git add -A && git commit -m "Versão AAAA-MM-DD" && git push  (o Vercel publica sozinho).

Rodar:  python publicar.py            (versão = data de hoje)
        python publicar.py --sem-teste (só se os testes já rodaram)
"""
import json, shutil, subprocess, sys, datetime as dt
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
P_SRC = RAIZ / '03_HTML' / 'src'
C_SRC = RAIZ / '05_Farma_Cards_RPG' / 'src'
SITE = RAIZ / 'site'

def roda(pasta, script):
    print(f'> {script}')
    r = subprocess.run([sys.executable, '-I', '-X', 'utf8', script], cwd=pasta)
    if r.returncode:
        sys.exit(f'PAROU: {script} falhou. Nada foi publicado.')

passos = [(P_SRC, 'build_placar.py'), (C_SRC, 'build_v2.py')]
if '--sem-teste' not in sys.argv:
    passos = [(P_SRC, 'build_placar.py'), (P_SRC, 'teste_placar.py'), (C_SRC, 'build_v2.py'), (C_SRC, 'teste_v2.py')]
for pasta, script in passos:
    roda(pasta, script)

(SITE / 'placar').mkdir(parents=True, exist_ok=True)
(SITE / 'cards').mkdir(parents=True, exist_ok=True)
shutil.copyfile(RAIZ / '03_HTML' / 'Placar_Farma_Q4_2026_Ajustado.html', SITE / 'placar' / 'index.html')
shutil.copyfile(RAIZ / '05_Farma_Cards_RPG' / 'Farma_Cards_Q4_Legends_RPG_v2.html', SITE / 'cards' / 'index.html')

meses = {'2026-10': 'Outubro', '2026-11': 'Novembro', '2026-12': 'Dezembro'}
dados = sorted((P_SRC / 'dados').glob('2026-1*.json'))
pacotes = [json.loads(f.read_text(encoding='utf-8')) for f in dados]
ult = pacotes[-1]
corte = f"{ult['corte'][8:10]}/{ult['corte'][5:7]}/{ult['corte'][:4]}"
fechados = len(pacotes) == 3 and ult['corte'][8:10] == '31'
status = 'Q4 2026 — RESULTADO FINAL' if fechados else f'Q4 2026 — ACUMULADO PARCIAL ATÉ {corte}'
versao = dt.date.today().isoformat()
logo_spot = (P_SRC / 'spot_logo.txt').read_text().strip()
logo_rk = (P_SRC / 'rk_logo.txt').read_text().strip()
idx = (RAIZ / 'site_template' / 'index.html').read_text(encoding='utf-8')
for k, v in {'__SPOT_LOGO__': logo_spot, '__RK_LOGO__': logo_rk, '__STATUS__': status, '__VERSAO__': versao, '__CORTE__': corte}.items():
    idx = idx.replace(k, v)
(SITE / 'index.html').write_text(idx, encoding='utf-8')
(SITE / 'versao.json').write_text(json.dumps({'versao': versao, 'status': status, 'corte': ult['corte'],
    'meses': [{'mes': p['mes'], 'nome': meses[p['mes']], 'corte': p['corte'], 'atualizado_em': p.get('atualizado_em')} for p in pacotes]},
    ensure_ascii=False, indent=2), encoding='utf-8')
print(f'site pronto: versão {versao} · {status}')
