# Campanha de Incentivo CR Farma · Q4 2026

Site da campanha (SPOT × Reckitt), publicado no Vercel a partir da pasta `site/`: **só o Farma Cards** (o jogo da campanha).
O placar oficial é gerado e testado aqui (`03_HTML`), mas é de uso interno e **não** vai para o site; `/placar` redireciona para o início.

| Página | Arquivo publicado | Gerado por |
|---|---|---|
| Início = Farma Cards | `site/index.html` (e `site/cards/index.html`) | `05_Farma_Cards_RPG/src/build_v2.py` |
| Placar oficial (interno) | não publicado | `03_HTML/src/build_placar.py` |

## Atualização semanal

1. Gerar o pacote do mês a partir do Tracking: `python 03_HTML/src/extrai_mes_tracking.py "<Tracking .xlsb>" 2026-11`
2. Montar e testar tudo: `python publicar.py` (para se algum teste falhar)
3. Versionar e publicar: `git add -A` → `git commit -m "Versão AAAA-MM-DD"` → `git push` (o Vercel publica sozinho)

Formato dos dados e regras de cálculo: [`03_HTML/FORMATO_DADOS.md`](03_HTML/FORMATO_DADOS.md).

## Regras oficiais (não mudam com o jogo)

- % lojas executadas = lojas com ≥ 1 pesquisa NewsPage ÷ lojas do roteiro do mês. O Q4 soma os totais dos meses apurados.
- Desempate: % de visitas cumpridas.
- Fora da conta: vaga em aberto, loja abonada e loja repetida na mesma rota (conta 1 vez).
- Elegibilidade à premiação: roteiro nos 3 meses.

Bases de origem, conferências e scripts com acesso ao banco **não** entram neste repositório (`.gitignore`).
