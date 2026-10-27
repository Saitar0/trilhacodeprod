---
arquivo_id: "f6-31-5-m03-jornada-teste-regra-md"
parent_key: "31.5"
tipo_arquivo: "milestone"
ordem: 3
itens_origem: ["M03"]
titulo_marco: "Marco 3 — Teste a jornada e tente quebrar a regra"
---

### Marco 3 — Teste a jornada e tente quebrar a regra
**Objetivo:** comprovar o comportamento observável e detectar uma regressão plausível da regra específica.

**Tarefas:**
1. Escreva testes de comportamento para a ação principal e estados relevantes; use MSW ou ferramenta equivalente na fronteira HTTP para cenários determinísticos.
2. Inclua sucesso, vazio e falha nos cenários simulados e identifique-os claramente como simulados.
3. Percorra o fluxo central no navegador; registre se a rede foi interceptada ou se alcançou API de teste real. Use dados/conta isolados se houver escrita.
4. Acrescente um teste que falharia se a regra central fosse violada: duplo envio no T1; controle de rota/experiência por papel no T2; colisão de cache ao trocar filtro/página no T4; confusão entre job processando e relatório vazio no T5.
5. No T2, vincule evidência própria do backend que valide isolamento por empresa. Teste apenas de frontend não satisfaz esse requisito.
6. Se uma falha for não determinística ou depender de serviço externo, registre a limitação e não a apresente como teste isolado.

**Evidências:** comandos/resultados dos testes, handlers ou fixtures, fluxo de navegador, caso de regressão detectada e tabela que separa simulação de integração real. Para T2, inclua também referência verificável ao teste de autorização/isolation na API.

**Verificação:** repita os testes em isolamento e na suíte; confirme independência de dados de outros testes e que a regressão planejada realmente é detectada.


