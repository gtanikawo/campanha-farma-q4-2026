# Guia de implementação — FARMA CARDS · Q4 LEGENDS RPG

## Objetivo deste material

Este documento é a especificação para o Claude dar continuidade ao protótipo `Farma_Cards_Q4_Legends_RPG.html`, usando como fonte operacional o placar oficial `Placar_Farma_Q4_2026_Parcial_Outubro.html`.

A meta é manter uma aplicação HTML autocontida com aparência de card game/RPG, transformando cada promotor e supervisor em uma carta evolutiva, com raridades configuráveis, atributos, missões, selos, confronto, coleção, cronologia e animações. O produto final deve continuar funcional sem servidor e sem enviar dados operacionais para serviços externos.

> **Regra de ouro:** o RPG é uma camada de apresentação e gamificação. Não pode alterar a posição oficial, os critérios de desempate, a premiação, os dados importados ou a interpretação operacional.

---

## 1. Arquivos que devem ser entregues ao Claude

Anexe os dois arquivos abaixo à mesma conversa com Claude:

1. **`Placar_Farma_Q4_2026_Parcial_Outubro.html`** — fonte original. Contém o placar e o objeto `MESES`, que deve ser tratado como fonte dos dados oficiais.
2. **`Farma_Cards_Q4_Legends_RPG.html`** — protótipo atual. Contém a identidade visual escura de RPG, telas, cartas, estilos, interações e a camada de gamificação já implementada.
3. **`Guia_Completo_Claude_Farma_Cards_Q4_Legends.md`** — este guia, para explicar requisitos, fórmulas e testes.

Se Claude estiver trabalhando em uma pasta local pelo Claude Code, coloque os três arquivos na mesma pasta do projeto. Caso esteja usando a interface web do Claude, anexe os arquivos e cole o prompt mestre da seção 12.

### Ordem recomendada no Claude

1. Peça para ele ler por inteiro o HTML original e o HTML do protótipo.
2. Peça para ele comparar a estrutura de dados, não apenas resumir o visual.
3. Peça para ele implementar as melhorias em uma cópia nova, sem sobrescrever a fonte original.
4. Peça validação de sintaxe JavaScript, integridade dos dados, navegação, importação de novos placares e comportamento responsivo.
5. Peça que devolva o HTML final e um resumo das mudanças, limitações e testes realmente executados.

---

## 2. Arquitetura técnica

### Formato

- Um único arquivo `.html` para abrir diretamente no Edge ou Chrome.
- HTML semântico, CSS no `<style>` e JavaScript no `<script>` do mesmo arquivo.
- Idioma `pt-BR`.
- Layout adaptável a desktop, tablet e celular.
- Não exigir npm, build, servidor, banco de dados, instalação de bibliotecas ou conexão com API.
- Não incluir `fetch`, analytics, trackers, uploads remotos nem envio de dados para terceiros.
- Usar fontes de sistema; não depender de Google Fonts ou imagens externas para renderizar a aplicação.
- Pode usar CSS, SVG inline, emojis/símbolos e canvas para efeitos visuais.
- Tratar erros de `localStorage` e de carregamento de arquivos sem quebrar a aplicação.

### Organização do código

Mesmo que a entrega final seja um único HTML, manter o JavaScript internamente organizado por responsabilidades:

1. **Dados e configuração:** dados base, meses disponíveis, limiares e requisitos de raridade.
2. **Funções utilitárias:** formatação, normalização de nomes, escape de HTML, identidade do participante.
3. **Motor de regras:** raridade, poder RPG, XP, nível, classes e selos.
4. **Renderização:** Santuário, coleção, ficha da carta, confronto, missões, crônica e forja.
5. **Interações:** navegação, filtros, modais, abertura de pacote, importação e salvamento.
6. **Acessibilidade e animações:** teclado, foco, redução de movimento, canvas de partículas.
7. **Inicialização:** ligar eventos e renderizar as telas na ordem correta.

Evitar duplicação de funções e listeners em cada atualização de tela. Preferir funções curtas e nomes claros.

---

## 3. Dados oficiais: esquema esperado

O HTML oficial contém um objeto JavaScript chamado `MESES`. O protótipo inicial contém uma cópia local chamada `BASE_DATA` e uma variável ativa `MESES`.

### Chaves esperadas

- `out`: outubro.
- `nov`: novembro.
- `dez`: dezembro.
- `q4`: acumulado oficial do trimestre, quando a origem o disponibiliza.

Os meses ainda sem dados podem existir como objetos-placeholder com `disponivel: false`. Não os converter em valores zero.

### Estrutura de cada mês

```js
{
  prom: [],       // registros de promotores
  sup: [],        // registros de supervisores
  tot: {
    lojas: 0,     // universo de lojas do placar
    exec: 0       // lojas executadas
  },
  rodape: "...",
  label: "Outubro",
  sub: "...",
  disponivel: true,
  titulo: "...",
  periodo: "..."
}
```

Os exemplos acima mostram o formato e não substituem os valores reais do arquivo fonte.

### Campos dos promotores

- `pos`: posição oficial do ranking importado.
- `nome`: nome do promotor.
- `sup`: nome curto do supervisor.
- `supFull`: nome completo do supervisor.
- `uf`: estado associado ao participante.
- `lojas`: quantidade de lojas consideradas no roteiro.
- `exec`: quantidade de lojas executadas.
- `pct`: percentual fornecido pelo placar de origem.
- `pctv`: percentual de visitas cumpridas fornecido pelo placar de origem.

### Campos dos supervisores

- `pos`: posição oficial.
- `nome`: nome completo.
- `prom`: quantidade de promotores associada ao supervisor.
- `lojas`: total de lojas do universo do supervisor.
- `exec`: total de lojas executadas.
- `pct`: percentual do placar de origem.
- `pctv`: percentual de visitas cumpridas.

### Cuidados semânticos importantes

1. O campo `pct` é o percentual publicado pelo placar original. A interface atual o rotula visualmente como `NP SCORE`, mas o arquivo de origem apresenta a relação de lojas de roteiro e executadas. Claude deve confirmar o significado operacional com o usuário antes de renomear ou substituir essa métrica.
2. Não inventar um campo de pontuação NP independente se ele não existir no arquivo recebido.
3. Criar uma função central, por exemplo `getNPScore(registro)`, para isolar qual campo alimenta a raridade. Por padrão, ela pode usar `pct`, conforme o protótipo atual, deixando claro que é uma regra configurável a validar.
4. Usar `pos` e os dados do ranking oficial para mostrar a classificação. Não reordenar o ranking oficial com `PWR`, XP, nível ou raridade de carta.
5. O HTML atual foi apurado parcialmente em outubro, até 22/10/2026. A presença de uma chave `q4` não significa que o trimestre terminou: deve-se olhar `disponivel`, o período e os dados efetivamente carregados.
6. No momento do protótipo, a base contém 89 promotores e 5 supervisores, com 7.072 lojas no universo e 4.815 executadas no recorte informado. Validar esses números novamente após qualquer importação; não fixá-los no código de renderização.
7. O rodapé da fonte informa que vagas em aberto ficam fora do ranking e que loja repetida na mesma rota conta uma vez. Preservar essas observações ao exibir a origem/regra.

---

## 4. Regras de raridade

### 4.1 Raridade-base por pontuação

A raridade básica é definida pelo percentual usado como pontuação NP, centralizado na função `getNPScore(registro)`.

| Raridade | Limiar padrão |
|---|---:|
| Comum | abaixo de Bronze |
| Bronze | 50% |
| Prata | 65% |
| Ouro | 75% |
| Épica | 85% |
| Mítica | 95% |

Interpretação: selecionar a raridade mais alta cujo limiar foi atingido. Exemplo: se o NP for 88%, a carta é Épica, desde que a função de pontuação use o percentual certo.

Esses limiares são **padrões iniciais de gamificação**, não regras aprovadas de remuneração ou premiação. Devem ser ajustáveis na tela **Forja de raridade**.

### 4.2 Requisitos extras para a raridade Mítica Holográfica

O protótipo separa a raridade textual de sua versão especial com efeito holográfico. Para habilitar a holografia, os requisitos padrão são simultaneamente:

- Pontuação NP igual ou superior ao limiar Mítico (95% por padrão).
- `pctv` igual ou superior a 50%.
- Pelo menos 15 lojas executadas (`exec >= 15`).

A lógica é: a pontuação determina a faixa base; critérios adicionais liberam a variante holográfica. Se a carta atingir a faixa Mítica, mas falhar em um requisito adicional, ela continua Mítica, porém aparece como “Mítica · Selada”, sem o efeito holográfico.

### 4.3 Selos complementares padrão

Os selos são independentes da posição oficial e não somam pontos ao placar:

- **NP Overdrive:** pontuação NP igual ou superior a 85%.
- **Disciplina:** `pctv` igual ou superior a 65% por padrão.
- **Impacto:** `exec` igual ou superior a 40 por padrão.
- **Perfeição:** pontuação percentual igual ou superior a 99,95%, para representar praticamente 100% no dado de origem.
- **Top 3 Parcial:** posição oficial `pos <= 3` no recorte exibido.
- **Três Luas:** elegível quando os três meses outubro, novembro e dezembro estão presentes e o mesmo participante existe nos três.

Os limiares dos selos devem ser configuráveis sempre que forem numéricos.

### 4.4 Como elevar a confiança da raridade — novas regras recomendadas

Além dos limiares atuais, implementar suporte a requisitos extras configuráveis. Não ativar novas regras escondidas ou arbitrárias; exibir a descrição de cada uma na Forja.

**Regras sugeridas para avaliação com o usuário:**

1. **Mítica Consistente:** para a variante final, exigir NP acima do limite em todos os meses válidos, e não somente em um retrato isolado.
2. **Mítica Trimestral:** exigir os três meses carregados, presença do participante em todos eles e pontuação acumulada oficial acima do limiar final.
3. **Mínimo de amostra:** exigir quantidade mínima de lojas no roteiro antes de entregar uma variante máxima, a fim de evitar classificar uma amostra muito pequena como se fosse equivalente a uma amostra grande.
4. **Disciplina de visitas:** exigir limite mínimo configurável para `pctv`.
5. **Volume real:** exigir um mínimo configurável de lojas executadas.
6. **Sem dados insuficientes:** se um campo necessário estiver ausente ou não numérico, não conceder o efeito premium por suposição; mostrar “dados insuficientes”.

As regras novas precisam ser identificadas como propostas/configurações, não como regras atuais confirmadas. Permitir ao usuário ativá-las ou desativá-las.

### 4.5 Validação dos limiares

- Os limiares devem ficar ordenados: Bronze < Prata < Ouro < Épica < Mítica.
- Impedir valores fora de intervalo ou configuração inválida.
- Se os limites forem incoerentes, mostrar mensagem compreensível e não salvar a configuração incorreta.
- Oferecer botão para restaurar padrões.
- Mostrar por que uma carta recebeu a raridade e o que falta para desbloquear o próximo efeito.

---

## 5. Fórmulas da camada RPG já usadas no protótipo

Essas fórmulas são indicadores lúdicos. Não substituem os percentuais oficiais nem recalculam o ranking.

### 5.1 Índice de volume

```js
volumeIndex = Math.min(100, (exec / 50) * 100)
```

O índice chega a 100 quando há 50 ou mais lojas executadas. Este corte é uma configuração de jogo, e não um KPI de negócio. Torná-lo ajustável se o usuário solicitar.

### 5.2 Poder de jogo (PWR)

```js
PWR = 0.70 * NP + 0.20 * percentualVisitas + 0.10 * volumeIndex
```

No protótipo: `NP` usa `pct`; `percentualVisitas` usa `pctv`; `volumeIndex` deriva de `exec`.

### 5.3 XP e nível

```js
XP = Math.round((PWR * PWR / 100) * 25)
level = Math.max(1, Math.min(20, 1 + Math.floor(XP / 150)))
```

Observação: no protótipo atual, XP e nível são derivados da situação atual, não são um histórico persistente de experiência ganha a cada mês. Se a evolução de outubro para novembro para dezembro precisar ser cumulativa, Claude deve definir essa lógica explicitamente, usando snapshots mensais disponíveis e sem inventar progresso em meses não carregados.

### 5.4 Classe temática

A ordem atual de decisão é:

1. NP >= 90% → **Arcanista de NP**.
2. Senão, percentual de visitas >= limite de Disciplina → **Guardião da Disciplina**.
3. Senão, lojas executadas >= limite de Impacto → **Cavaleiro do Volume**.
4. Senão, NP >= limiar de Ouro → **Sentinela de Execução**.
5. Caso contrário → **Viajante da Rota**.

Deixar os critérios legíveis e ajustar apenas se a mudança for solicitada. A classe é descritiva, não um nível hierárquico da empresa.

---

## 6. Telas e funcionalidades

### 6.1 Santuário (página inicial)

- Hero com nome FARMA CARDS · Q4 LEGENDS RPG.
- Orbe mágico com animação e partículas de fundo.
- Situação da temporada: parcial, acumulado de dois meses ou trimestre completo, com base nos meses efetivamente carregados.
- Aviso claro sobre a data da apuração e sobre meses ainda indisponíveis.
- KPIs resumidos que sejam calculados a partir dos dados importados.
- Uma carta em destaque baseada no dado real, não em sorteio.
- Cartas em destaque seguindo a posição oficial do placar.
- Legenda das raridades e atalho para a Forja.

### 6.2 Coleção de cartas

- Grade responsiva de cartas com moldura e acabamento conforme raridade.
- Alternância entre grade de cartas e visual de lista.
- Busca por nome de promotor ou supervisor.
- Filtros por categoria (promotor/supervisor), raridade, supervisor e UF, quando a UF existir no registro.
- Ordenação por posição oficial, NP, PWR, lojas executadas e nome.
- Ao selecionar uma carta, abrir ficha detalhada com dados oficiais, XP, nível, classe, selos e explicações das regras.
- A coleção deve usar um identificador estável por tipo e nome normalizado, mas não pode usar posição do ranking como identificador, porque a posição muda mês a mês.

### 6.3 Ficha detalhada / modal de carta

- Carta ampliada, virável para frente/verso.
- Frente: nome, categoria, posição oficial, raridade, nível, XP, pontuação NP, PWR e quantidade de lojas.
- Verso: explicação de atributos, origem dos números, critério da raridade, requisitos cumpridos/faltantes e selos.
- Exibir supervisor/UF quando disponível.
- Fechar com botão, clique na área externa do modal e tecla Escape.
- Oferecer foco visível e acionamento por teclado.

### 6.4 Invocação / abertura de pacote

- Efeito visual de pacote selado e revelação de até três cartas.
- Pode selecionar aleatoriamente três participantes apenas para a experiência de descoberta visual.
- O efeito não deve sugerir dinheiro, aposta, prêmio real ou distribuição de performance.
- A raridade exibida continua calculada a partir dos dados e das regras configuradas; não sortear raridade.
- Não criar resultados, não alterar ranking, não criar cartas inexistentes nem gravar “propriedade” de uma carta como se fosse sistema de contas.
- Permitir abrir a ficha de cada carta revelada e invocar outro pacote.

### 6.5 Confronto

- Seletor de personagem A e B.
- Botão para sortear dois participantes distintos para um confronto visual.
- Comparar NP, percentual de visitas, lojas executadas, volume, PWR, raridade, nível e posição oficial.
- Destacar qual participante tem o maior valor em cada atributo.
- Exibir resultado como “simulação RPG”, nunca como classificação oficial ou definição de campeão.
- Impedir o confronto de uma pessoa contra ela mesma.

### 6.6 Missões & selos

- Catálogo de missões com requisito, descrição, progresso e participantes que o atingiram.
- Missões atuais: NP >= 80%; Disciplina (pctv configurável); Impacto (exec configurável); Ascensão Épica; desbloqueio Mítico.
- Missões trimestrais ficam bloqueadas até haver outubro, novembro e dezembro válidos.
- Cada selo explica a regra que o liberou.
- Nenhuma missão deve alterar pontos, posições ou elegibilidade oficial para premiação.

### 6.7 Crônica Q4

- Linha do tempo de Outubro, Novembro e Dezembro.
- Cada mês aparece como disponível apenas quando `disponivel === true` e arrays necessários estão presentes.
- Meses futuros ou não importados ficam visualmente selados/desabilitados, com instrução de importar a nova versão do placar.
- Mostrar mês selecionado, total de lojas, executadas, percentual total e Top 5 daquele mês quando os dados existirem.
- Não substituir ausência de dado por zero.
- Mostrar o período e rodapé da fonte, sem remover observações importantes.

### 6.8 Forja de raridade

- Formulário com os limiares de Bronze, Prata, Ouro, Épica e Mítica.
- Entradas para requisitos de holografia, Disciplina e Impacto.
- Permitir ativar/desativar novos requisitos propostos, como consistência trimestral ou amostra mínima.
- Botão de salvar e botão de restaurar padrões.
- Persistir preferências localmente e recalcular imediatamente todas as cartas/telas.
- Exibir fórmula de PWR e deixar claro que a camada de jogo não altera o ranking.

---

## 7. Direção visual e animações

### Direção de arte

- Misturar card game colecionável, fantasia/RPG e acabamento premium.
- Não copiar integralmente identidade, logos, personagens ou ilustrações protegidas de EA SPORTS FC, Yu-Gi-Oh! ou outro jogo. Usar linguagem visual original.
- Fundo grafite quase preto com profundidade em roxo, magenta e azul-violeta.
- Ouro para nível Ouro e destaques de campeões; prata e bronze para suas raridades; magenta/violeta para Épica/Mítica; ciano/verde para estados de apoio.
- Cartas com bordas especiais, sigilo central, barra de atributos e brilho conforme a raridade.
- Tipografia de sistema e contraste adequado; não depender de imagens externas.
- Evitar excesso de painéis corporativos. A coleção de cartas deve ser a protagonista.

### Animações já presentes no protótipo

- Estrelas/partículas deslocando-se em canvas.
- Orbe que flutua e anéis que orbitam.
- Entrada suave ao trocar de página.
- Efeito de brilho/holografia conforme raridade.
- Efeito de sigilo flutuante.
- Modal com entrada animada.
- Revelação de carta e animação da invocação.
- Transições curtas em botões e cartas.

### Regras de desempenho/acessibilidade

- Respeitar `prefers-reduced-motion: reduce`; reduzir ou desativar animações quando o sistema operacional solicitar.
- Não manter animação pesada em todas as cartas fora da tela.
- O canvas deve redimensionar sem distorcer e limitar quantidade de partículas.
- Não usar flashes rápidos, tremores intensos ou movimentos que dificultem ler o conteúdo.
- Permitir navegação por teclado, foco visível, botões com nomes acessíveis e Escape para fechar modal.
- Garantir que cards e filtros sejam utilizáveis em celular; a sidebar deve se adaptar para navegação móvel.

---

## 8. Importar atualizações futuras do placar

### Fluxo esperado

1. Usuário clica em “Importar placar atualizado”.
2. Seleciona o HTML oficial novo ou um JSON compatível.
3. A aplicação lê o arquivo localmente com `FileReader`.
4. No JSON, aceitar objeto direto ou propriedade `MESES`.
5. No HTML, extrair com segurança a declaração `const MESES = {...};` antes de `const ORDEM_MESES` e aplicar `JSON.parse` no fragmento válido.
6. Validar estrutura, meses e campos essenciais antes de trocar os dados que estão em tela.
7. Se falhar, manter a base atual intacta e mostrar erro amigável.
8. Se funcionar, substituir os dados em memória, salvar o último conjunto válido no `localStorage` e atualizar todas as telas.
9. Informar quais meses ficaram disponíveis após a importação.

### Robustez necessária

- Não executar o arquivo HTML importado com `eval` ou `new Function`.
- A extração não deve aceitar silenciosamente um bloco inválido.
- Verificar que existem registros `prom` e `sup` para meses disponíveis e que os campos usados pelas fórmulas são numéricos ou podem ser convertidos de forma segura.
- Evitar perder os dados atuais se o arquivo novo estiver corrompido.
- Mostrar o nome do arquivo importado, se prático, a data/período declarado na origem e o status dos meses.
- Se o formato do HTML oficial mudar, explicar o que não foi reconhecido e não fabricar dados.
- Aceitar uma exportação JSON bem documentada como alternativa de longo prazo.

### Acumulado Q4

- Priorizar o acumulado `q4` calculado pelo placar oficial quando disponível e validado.
- Não somar cegamente outubro + novembro + dezembro se o arquivo já traz `q4` calculado.
- Se for necessário construir o acumulado a partir de meses, agrupar a mesma pessoa por identidade estável e calcular percentuais sobre totais compatíveis (`exec total / lojas total * 100`), não tirar média simples dos percentuais mensais quando o denominador varia.
- Não tratar um mês ausente como mês com zero execução.
- Confirmar a regra oficial para as lojas recorrentes a cada mês e para participantes que mudam de supervisor/UF.
- A elegibilidade trimestral “Três Luas” exige a presença em todos os três meses; explicar o que acontece se o participante tiver sido transferido entre supervisores.

---

## 9. Persistência local e privacidade

O protótipo usa `localStorage` para preservar localmente:

- `farmaCards.thresholds`: limiares de raridade.
- `farmaCards.gates`: requisitos adicionais de raridade/selos.
- `farmaCards.data`: último objeto `MESES` importado com sucesso.

Requisitos:

- Proteger acessos ao `localStorage` com `try/catch`.
- Explicar que dados ficam no navegador daquele computador/perfil e não são sincronizados automaticamente com outros usuários.
- Não armazenar senhas nem informações pessoais além dos nomes presentes na fonte oficial.
- Não transmitir nomes ou resultados para serviços remotos.
- Incluir forma de restaurar configuração e dados-base do protótipo.

---

## 10. Erros comuns que Claude deve evitar

1. Alterar as pontuações oficiais ao calcular PWR, XP ou raridade.
2. Confundir `pct` com outra métrica de NP sem validar seu significado.
3. Mostrar “Q4 completo” porque existe a chave `q4`; a disponibilidade deve refletir o período real.
4. Transformar novembro/dezembro não carregados em 0%, fazendo parecer que participantes não executaram nada.
5. Calcular raridade por posição do ranking, exceto nos selos específicos de posição (ex.: Top 3 Parcial).
6. Sortear a raridade no pacote. O sorteio escolhe participantes para a animação; atributos e raridade são determinísticos com base nos dados e limiares.
7. Misturar os percentuais de supervisor com os do promotor sem identificar o tipo de carta.
8. Criar duplicados da mesma pessoa entre meses por causa de acentos, caixa ou espaços extras no nome.
9. Usar posição `pos` como identidade, porque muda no ranking mensal.
10. Sobrescrever o HTML original ou perder a versão funcional antes de validar o novo arquivo.
11. Incluir dependências externas que impeçam o HTML de funcionar offline.
12. Afirmar que a renderização visual foi validada sem ter aberto/testado o arquivo em um navegador.

---

## 11. Checklist de validação antes de entregar

### Dados e ranking

- [ ] Comparar totais, nomes, `pos`, `lojas`, `exec`, `pct` e `pctv` com o HTML original após importação.
- [ ] Confirmar que 89 promotores e 5 supervisores aparecem para a versão atual, sem fixar esse total para versões futuras.
- [ ] Confirmar que a posição oficial exibida não muda ao alterar limiares ou PWR.
- [ ] Confirmar que os meses ausentes estão selados, não zerados.
- [ ] Confirmar que Q4 parcial aparece com texto explícito de parcial e período da fonte.

### Raridade e RPG

- [ ] Testar percentuais imediatamente abaixo, exatamente no limiar e acima de cada raridade.
- [ ] Testar que Mítica sem os requisitos extras permanece selada.
- [ ] Testar que Mítica com todos os requisitos extras mostra a versão holográfica.
- [ ] Testar ausência de campo: não conceder bônus premium por suposição.
- [ ] Confirmar que missão/raridade/XP não afetam o ranking ou premiações.
- [ ] Confirmar que o confronto não permite o mesmo participante nos dois lados.

### Interação e interface

- [ ] Todos os itens da navegação levam à tela correta.
- [ ] Busca, filtros, ordenação e modo lista/cartas funcionam.
- [ ] Clique na carta abre os detalhes e modal fecha por botão, fundo ou Escape.
- [ ] Invocação abre pacote, revela até três cartas e abre a ficha delas.
- [ ] As configurações da Forja são salvas e continuam após atualizar/reabrir o navegador.
- [ ] Restaurar padrões realmente restaura os valores de origem.
- [ ] A aplicação funciona em largura desktop e celular.
- [ ] `prefers-reduced-motion` reduz as animações.
- [ ] Não aparecem erros no console do navegador.

### Importação

- [ ] Importar o HTML original funciona.
- [ ] Importar JSON compatível funciona.
- [ ] Um arquivo corrompido mostra erro sem apagar os dados válidos atuais.
- [ ] A importação não executa scripts de terceiros do arquivo escolhido.
- [ ] Depois de importar, todas as telas e opções são recalculadas.

### Entrega

- [ ] Salvar com nome novo, por exemplo `Farma_Cards_Q4_Legends_RPG_v2.html`.
- [ ] Manter intactos os dois arquivos de entrada.
- [ ] Declarar o que foi testado de verdade e o que não pôde ser validado visualmente.
- [ ] Entregar um resumo de mudanças e instruções de uso em português.

---

## 12. Prompt mestre pronto para colar no Claude

Copie o texto a seguir depois de anexar os arquivos e este guia:

> Você é um engenheiro front-end sênior com experiência em visualização de dados, gamificação, UX, HTML/CSS/JavaScript e validação de indicadores operacionais.
>
> Leia integralmente os arquivos anexados:
> 1. `Placar_Farma_Q4_2026_Parcial_Outubro.html` — fonte original dos dados e do ranking;
> 2. `Farma_Cards_Q4_Legends_RPG.html` — protótipo atual da aplicação;
> 3. `Guia_Completo_Claude_Farma_Cards_Q4_Legends.md` — especificação obrigatória.
>
> Desenvolva uma nova versão funcional, mantendo o arquivo original intacto. Salve como `Farma_Cards_Q4_Legends_RPG_v2.html`.
>
> O objetivo é criar um card game corporativo de fantasia/RPG: cada promotor e supervisor tem uma carta colecionável; cada carta tem atributos derivados dos dados reais, nível, XP, raridade e selos; há coleção, ficha detalhada, invocação visual de pacote, confronto de atributos, missões, crônica dos três meses e uma Forja para configurar os limiares de raridade.
>
> **Antes de codificar:** inspecione a estrutura da declaração `MESES` no HTML fonte e compare-a com `BASE_DATA` no protótipo. Verifique campos e semântica. O campo `pct` é o percentual que o placar de origem fornece e, no protótipo atual, é usado como base visual chamada `NP SCORE`; não presuma que existe uma coluna independente de pontuação NP sem conferir os arquivos. Isole essa regra em `getNPScore(registro)` para que possa ser ajustada de forma central.
>
> **Não altere a regra oficial de classificação.** Use a posição `pos` e os dados oficiais para exibir ranking. PWR, XP, nível, selos, raridade e resultados de confronto são apenas elementos RPG e jamais podem afetar posição, desempate ou premiação.
>
> **Raridade-base inicial:** Comum abaixo de 50%; Bronze a partir de 50%; Prata a partir de 65%; Ouro a partir de 75%; Épica a partir de 85%; Mítica a partir de 95%. Esses limiares precisam ser configuráveis na tela Forja. O nível Mítico Holográfico exige adicionalmente `pctv >= 50` e `exec >= 15`, além do limiar Mítico. Permita configurar esses requisitos. Inclua os selos NP Overdrive (`NP >= 85`), Disciplina (`pctv >= 65`), Impacto (`exec >= 40`), Perfeição (`pct >= 99.95`), Top 3 Parcial (`pos <= 3`) e Três Luas (participante presente em outubro, novembro e dezembro válidos). Mantenha os critérios numéricos configuráveis. Adicione opção explícita de ativar requisitos propostos de consistência trimestral e amostra mínima; não os ative silenciosamente nem os apresente como regras oficiais confirmadas.
>
> **Fórmulas RPG atuais:** `volumeIndex = min(100, exec / 50 * 100)`; `PWR = 0.70 * NP + 0.20 * pctv + 0.10 * volumeIndex`; `XP = round((PWR * PWR / 100) * 25)`; `level = max(1, min(20, 1 + floor(XP / 150)))`. Documente-as na interface. Se você alterar alguma fórmula, explique o motivo e mantenha a camada RPG separada da classificação oficial.
>
> **Telas obrigatórias:**
> 1. Santuário — status real da temporada, KPIs calculados, carta em destaque e atalhos;
> 2. Coleção — cartas em grade ou lista, filtros por tipo, raridade, supervisor, UF, busca e ordenação;
> 3. Ficha do personagem — frente/verso, atributos, origem dos valores, requisitos cumpridos e selos;
> 4. Invocação de cartas — revelar até três participantes com animação, sem sortear raridade, desempenho ou prêmio;
> 5. Confronto — comparar dois participantes e seus atributos, deixando claro que é um duelo simulado de RPG;
> 6. Missões & selos — objetivos transparentes e progresso com base nos dados disponíveis;
> 7. Crônica Q4 — linha do tempo outubro/novembro/dezembro, meses ausentes selados;
> 8. Forja de raridade — editar limiares e requisitos, salvar e restaurar padrões.
>
> **Importação de dados:** aceitar HTML oficial e JSON compatível. Para HTML, localizar `const MESES = {...};` antes de `const ORDEM_MESES` e validar o fragmento com `JSON.parse`. Nunca usar `eval` ou `new Function`. Para JSON, aceitar o objeto `MESES` ou o objeto diretamente. Validar os dados antes de substituir o estado atual. Em erro, manter os dados anteriores e explicar o problema. Após importação bem-sucedida, atualizar todas as telas e salvar localmente. Não substituir ausência por zero. Se o objeto `q4` for disponibilizado pelo placar oficial, não somar de novo os meses cegamente; priorizar o acumulado oficial validado.
>
> **Visual/UX:** criar arte original inspirada em colecionáveis premium e RPG, sem copiar logos, personagens ou layout integral de jogos comerciais. Manter tema escuro com tons de roxo, magenta, ouro e ciano; molduras por raridade; animações de brilho, cartas, orbe, modais e partículas; navegação responsiva. Respeitar `prefers-reduced-motion`; garantir foco por teclado, Escape nos modais, acessibilidade básica e legibilidade.
>
> **Privacidade/arquitetura:** entregar um único HTML offline, com HTML/CSS/JS embutidos, sem dependências externas obrigatórias, sem API, analytics, fetch ou upload de dados. Usar `localStorage` com `try/catch` para configuração e último conjunto de dados, e informar que o armazenamento é local ao navegador.
>
> **Validação obrigatória:** confira números oficiais contra a origem; teste limiares exatamente abaixo/no/acima de cada faixa; teste Mítica selada e holográfica; teste filtros, busca, ordenação, modal, teclado, pacote, confronto, Forja, armazenamento local, importação de HTML e JSON e arquivo corrompido. Verifique sintaxe JavaScript e console. Não afirme ter feito um teste visual no navegador se não tiver realmente executado a aplicação em um navegador. Preserve os arquivos originais.
>
> Ao terminar, entregue o caminho do HTML final, descreva as alterações feitas, explique como abrir/importar uma nova versão do placar e liste qualquer comportamento que não tenha sido possível validar. Não invente dados de novembro/dezembro nem regras operacionais ausentes dos arquivos.

---

## 13. Como testar o resultado de forma prática

1. Abra `Farma_Cards_Q4_Legends_RPG_v2.html` no Edge/Chrome.
2. Na tela **Coleção**, busque pelo nome de um promotor conhecido e confirme supervisor, UF, lojas e valores com o placar original.
3. Abra uma carta de NP alto, outra na faixa Épica, uma Mítica não holográfica e uma carta de menor pontuação. Confirme que a aparência segue os limiares e requisitos.
4. Na **Forja**, mude temporariamente um limiar, salve, confira as cartas e atualize o navegador para verificar persistência. Depois use **Restaurar padrões**.
5. Na tela **Confronto**, escolha duas pessoas distintas e confirme que as estatísticas não mudam o ranking.
6. Na **Crônica**, confirme que novembro e dezembro continuam bloqueados até que o placar oficial os disponibilize.
7. Use **Importar placar atualizado** e selecione uma cópia do HTML oficial. Confira a mensagem de sucesso e compare o total de participantes/valores com a origem.
8. Teste em janela estreita e com movimento reduzido ativado no sistema operacional.
9. Se algo falhar, mande ao Claude o erro exato do console e o nome da tela/ação; solicite correção pontual, sem reconstruir a aplicação do zero.
