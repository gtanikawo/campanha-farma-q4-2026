# Placar Farma Q4 2026 — formato dos dados e como atualizar

O placar `Placar_Farma_Q4_2026_Ajustado.html` guarda, para cada mês, **uma linha por loja do roteiro** (mês + rota + loja). A partir dessas linhas ele calcula outubro, novembro, dezembro e o acumulado do Q4, os rankings, o pódio, o top 10, os supervisores e a elegibilidade.

## Regras de cálculo (as mesmas do placar original)

| Item | Regra |
|---|---|
| Loja prevista | Loja do roteiro do mês com `COUNT_LOJA = 1` no Tracking. Loja abonada (Planejado Real = 0) fica fora. |
| Loja executada | Loja prevista com pelo menos 1 pesquisa NewsPage no mês (`pesquisas > 0`). |
| % lojas executadas | executadas ÷ previstas. **Q4 = soma das executadas ÷ soma das previstas dos meses apurados**, nunca média dos % mensais. |
| Desempate | % visitas cumpridas = Σ mín(pesquisas, planejado) ÷ Σ planejado. |
| Empate total | Não existe na base atual. Se acontecer, a ordem é alfabética. |
| Lojas repetidas | Mesma rota + mesma loja no mesmo mês conta 1 vez. A mesma loja conta de novo em outro mês. |
| Vaga em aberto | Linha com "VAGA" no nome do colaborador fica fora dos rankings e dos totais. |
| Supervisores | Ranking próprio, somando as lojas dos promotores do time em cada mês. Não se mistura com o de promotores. |
| Mês sem dados | Aparece como "aguardando apuração", não entra no Q4 e nunca vira zero. |
| Elegibilidade Q4 | **Elegível:** com roteiro (supervisor: à frente de time) em out, nov e dez. **Inelegível:** sem roteiro num mês já apurado. **Pendente:** algum mês ainda não apurado. A elegibilidade não muda o ranking; vale para a premiação final. |

## Formato JSON (preferido)

Arquivo `AAAA-MM.json`, um por mês:

```json
{
  "formato": "placar-farma-q4/v1",
  "mes": "2026-11",
  "corte": "2026-11-21",
  "atualizado_em": "2026-11-22 09:30",
  "fonte": "Tracking Pesquisas News Page Farma.xlsb · aba Lojas Roteiro (COUNT_LOJA = 1)",
  "colunas": ["cod_rota","loja_id","cod_colaborador","colaborador","supervisor","uf","planejado","pesquisas"],
  "lojas": [
    [1700, "RH-0002876", 57, "AILTON CESAR DOS SANTOS", "CATARINA FIDELIS DA SILVA", "SP", 2, 1]
  ]
}
```

| Campo | Obrigatório | De onde vem no Tracking (aba Lojas Roteiro) |
|---|---|---|
| `mes` | sim | 2026-10, 2026-11 ou 2026-12 |
| `corte` | sim | Último dia com dado (maior data diária da aba CALC). Se for o último dia do mês, o mês aparece como **fechado**. |
| `atualizado_em` | não | Data/hora do arquivo de origem (aparece no quadro "Base de dados") |
| `cod_rota` | sim (pode ser vazio) | COD_ROTA |
| `loja_id` | sim | CUSTOMER CODE (RH-…) |
| `cod_colaborador` | não | COD_COLABORADOR_SPOT |
| `colaborador` | sim | COLABORADOR (ou "VAGA EM ABERTO") |
| `supervisor` | sim | SUPERVISOR SPOT |
| `uf` | sim | UF |
| `planejado` | sim, ≥ 1 | Planejado Real |
| `pesquisas` | sim, ≥ 0 | Realizado Newspage |

**Gerar automaticamente:** `python src\extrai_mes_tracking.py "<caminho do Tracking .xlsb>" 2026-11` cria `src\dados\2026-11.json` com essas regras.

## Formato CSV (alternativa)

Separador `;` (ou `,`), com cabeçalho e um único mês/corte por arquivo:

```
mes;corte;cod_rota;loja_id;cod_colaborador;colaborador;supervisor;uf;planejado;pesquisas;atualizado_em
2026-11;2026-11-21;1700;RH-0002876;57;AILTON CESAR DOS SANTOS;CATARINA FIDELIS DA SILVA;SP;2;1;2026-11-22 09:30
```

## Duas formas de atualizar

1. **Para todo mundo (recomendado):** gerar o JSON do mês em `src\dados`, rodar `python src\build_placar.py` e depois `python src\teste_placar.py`, e enviar o novo `Placar_Farma_Q4_2026_Ajustado.html`. O build para se o cálculo de outubro deixar de bater com o placar original.
2. **Só no seu navegador:** no placar, "Importar mês (JSON ou CSV)".
   - **Mês novo:** é incluído.
   - **Mês já carregado, com corte mais novo:** substitui o anterior, sem somar de novo.
   - **Mesmo arquivo:** "nada mudou".
   - **Arquivo mais antigo, inválido ou incompleto:** é recusado, com o motivo, e os dados atuais continuam.
   - A importação fica salva **só neste navegador e neste computador**, não é compartilhada. "Voltar à base do arquivo" desfaz.
