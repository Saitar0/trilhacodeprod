---
arquivo_id: "f6-27-2-90-integracao-p01-pratica-md"
parent_key: "27.2"
tipo_arquivo: "practice"
assuntos: ["01_estado_operacao_comunicacao_acessivel", "02_vazio_resultados_falhas"]
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Construa a matriz de estados da listagem
**Objetivo:** transformar respostas da API em estados claros e sem combinações contraditórias.

**Passos:**
1. Escolha uma listagem já criada ou use uma coleção de projetos com campos `id`, `name` e `status`.
2. Escreva cenários para primeira carga, itens encontrados, coleção vazia no primeiro acesso, filtro sem resultados, falha inicial, atualização em segundo plano e falha de atualização com dados anteriores.
3. Para cada cenário, registre disponibilidade dos dados, atividade da rede, mensagem, ação disponível e resultado esperado ao acionar essa ação.
4. Implemente o mapeamento da resposta e da atividade de rede para a interface. Garanta que cada cenário tenha uma apresentação definida.
5. Demonstre que os dados anteriores permanecem identificados como anteriores durante uma atualização e após uma falha de atualização.

**Dica:** use uma tabela antes de criar componentes. Trate o conteúdo da coleção e o estado da requisição como informações separadas.

**Entrega:** matriz de estados e uma listagem funcional que cobre os sete cenários.

**Critérios de conclusão:** nenhum erro aparece como estado vazio; cada cenário tem uma próxima ação coerente; dados anteriores não são apresentados como resposta atual sem indicação.

