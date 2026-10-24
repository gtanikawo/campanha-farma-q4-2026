"""Gera o pacote de dados de um mês do placar (formato placar-farma-q4/v1) a partir do
Tracking Pesquisas NewsPage Farma (.xlsb), aba Lojas Roteiro.

Uso:  python extrai_mes_tracking.py <caminho_do_tracking.xlsb> <AAAA-MM>
Saída: dados/<AAAA-MM>.json   (ver FORMATO_DADOS.md)

Regras aplicadas aqui (as mesmas do placar desde o Q3):
- só linhas com COUNT_LOJA = 1 (loja prevista no mês; loja abonada, com Planejado Real 0, fica fora);
- 1 linha por mês + rota + loja (a aba repete a loja quando só muda a "Próxima Visita");
- pesquisas = Realizado Newspage; a loja é executada quando pesquisas > 0;
- vaga em aberto vai no pacote com o nome "VAGA EM ABERTO" (o placar a deixa fora do ranking);
- corte = maior data diária da aba CALC (a "Data Ultima Visita" é do mês anterior).
"""
import json, sys, hashlib, datetime as dt
from pathlib import Path
import pandas as pd
from pyxlsb import open_workbook

xlsb, mes = Path(sys.argv[1]), sys.argv[2]
assert len(mes) == 7 and mes[4] == '-', 'mês no formato AAAA-MM'
BASE = pd.Timestamp('1899-12-30')

rows = []
with open_workbook(str(xlsb)) as wb:
    with wb.get_sheet('Lojas Roteiro') as sh:
        for i, row in enumerate(sh.rows()):
            v = [c.v for c in row]
            if i == 6: hdr = [str(x) for x in v[:52]]; continue
            if i > 6 and len(v) > 50 and v[10]: rows.append(v[:52])
    datas = []
    with wb.get_sheet('CALC') as sh:
        for row in sh.rows():
            v = [c.v for c in row]
            for j, x in enumerate(v):
                if isinstance(x, float) and 40000 < x < 60000 and j + 1 < len(v) and isinstance(v[j + 1], (int, float)):
                    d = BASE + pd.Timedelta(days=int(x))
                    if d.strftime('%Y-%m') == mes: datas.append(d)
df = pd.DataFrame(rows, columns=hdr)
df = df[pd.to_numeric(df['COUNT_LOJA'], errors='coerce') == 1]
antes = len(df)
df = df.drop_duplicates(['COD_ROTA', 'CUSTOMER CODE'])
repetidas = antes - len(df)
corte = max(datas).strftime('%Y-%m-%d') if datas else None

def num(x):
    try: return int(float(x))
    except Exception: return None
lojas = []
for _, r in df.iterrows():
    lojas.append([num(r['COD_ROTA']), str(r['CUSTOMER CODE']).strip(), num(r['COD_COLABORADOR_SPOT']), str(r['COLABORADOR']).strip(),
                  str(r['SUPERVISOR SPOT']).strip(), str(r['UF']).strip(), num(r['Planejado Real']) or 0, num(r['Realizado Newspage']) or 0])
pacote = {
    'formato': 'placar-farma-q4/v1',
    'mes': mes,
    'corte': corte,
    'atualizado_em': dt.datetime.fromtimestamp(xlsb.stat().st_mtime).strftime('%Y-%m-%d %H:%M'),
    'fonte': f'{xlsb.name} · aba Lojas Roteiro (COUNT_LOJA = 1)',
    'colunas': ['cod_rota', 'loja_id', 'cod_colaborador', 'colaborador', 'supervisor', 'uf', 'planejado', 'pesquisas'],
    'lojas': lojas,
}
pacote['hash'] = hashlib.sha1(json.dumps(pacote['lojas'], ensure_ascii=False).encode()).hexdigest()[:12]
out = Path(__file__).resolve().parent / 'dados' / f'{mes}.json'
out.write_text(json.dumps(pacote, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print(f'{out.name}: {len(lojas)} lojas (repetidas removidas: {repetidas}), corte {corte}, hash {pacote["hash"]}')
