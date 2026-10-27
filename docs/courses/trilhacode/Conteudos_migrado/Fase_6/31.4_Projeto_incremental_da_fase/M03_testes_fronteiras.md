---
arquivo_id: "f6-31-4-m03-testes-fronteiras-md"
parent_key: "31.4"
tipo_arquivo: "milestone"
ordem: 3
itens_origem: ["M03"]
titulo_marco: "Marco 3 — Cubra comportamento e fronteiras com testes"
---

### Marco 3 — Cubra comportamento e fronteiras com testes
**Objetivo:** aumentar confiança no fluxo sem confundir testes mockados com validação do backend.

**Tarefas:**
1. Escreva testes de componente por comportamento observável para a ação principal e os estados relevantes.
2. Use MSW ou ferramenta equivalente para controlar respostas HTTP, incluindo ao menos sucesso, vazio e falha.
3. Acrescente um fluxo Playwright curto para o caminho central; declare se usa API de teste real ou se intercepta a rede.
4. Quando usar API real, prepare conta e dados isolados e descreva limpeza; nunca use produção.
5. Mostre que uma regressão visível plausível faz ao menos um teste falhar e restaure o comportamento correto.

**Evidências:** comandos e saída de testes, handlers ou fixtures, fluxo de navegador e tabela que enumera o que cada cenário simulou ou alcançou de verdade.

**Verificação:** execute os testes em isolamento e na ordem da suíte; confira que não dependem da rede pública, de dados de outro teste ou de uma conta pessoal.


