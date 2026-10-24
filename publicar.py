"""Monta a versão semanal do site (pasta site/) publicada no Vercel.

1. Gera e testa o placar (03_HTML/src) e o Farma Cards (05_Farma_Cards_RPG/src). Para se algum teste falhar.
2. Publica SÓ o Farma Cards: site/index.html (endereço principal) e site/cards/index.html (link antigo).
   O placar oficial NÃO vai para o site (decisão do Gustavo, 23/10): fica só em 03_HTML para uso interno.
3. Gera site/versao.json.
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

shutil.rmtree(SITE / 'placar', ignore_errors=True)
(SITE / 'cards').mkdir(parents=True, exist_ok=True)
cards = RAIZ / '05_Farma_Cards_RPG' / 'Farma_Cards_Q4_Legends_RPG_v2.html'
shutil.copyfile(cards, SITE / 'index.html')
shutil.copyfile(cards, SITE / 'cards' / 'index.html')

meses = {'2026-10': 'Outubro', '2026-11': 'Novembro', '2026-12': 'Dezembro'}
dados = sorted((P_SRC / 'dados').glob('2026-1*.json'))
pacotes = [json.loads(f.read_text(encoding='utf-8')) for f in dados]
ult = pacotes[-1]
corte = f"{ult['corte'][8:10]}/{ult['corte'][5:7]}/{ult['corte'][:4]}"
fechados = len(pacotes) == 3 and ult['corte'][8:10] == '31'
status = 'Q4 2026 — RESULTADO FINAL' if fechados else f'Q4 2026 — ACUMULADO PARCIAL ATÉ {corte}'
versao = dt.date.today().isoformat()
(SITE / 'versao.json').write_text(json.dumps({'versao': versao, 'status': status, 'corte': ult['corte'],
    'meses': [{'mes': p['mes'], 'nome': meses[p['mes']], 'corte': p['corte'], 'atualizado_em': p.get('atualizado_em')} for p in pacotes]},
    ensure_ascii=False, indent=2), encoding='utf-8')
print(f'site pronto: versão {versao} · {status}')
