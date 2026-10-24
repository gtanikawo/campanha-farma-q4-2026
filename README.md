# Campanha de Incentivo CR Farma · Q4 2026

Site da campanha (SPOT × Reckitt): **Placar Q4** e **Farma Cards**, publicado no Vercel a partir da pasta `site/`.

| Página | Arquivo publicado | Gerado por |
|---|---|---|
| Início | `site/index.html` | `site_template/index.html` + `publicar.py` |
| Placar Q4 | `site/placar/index.html` | `03_HTML/src/build_placar.py` |
| Farma Cards | `site/cards/index.html` | `05_Farma_Cards_RPG/src/build_v2.py` |

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
