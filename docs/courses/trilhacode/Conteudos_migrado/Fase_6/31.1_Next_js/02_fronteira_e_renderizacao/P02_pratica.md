---
arquivo_id: "f6-31-1-02-fronteira-e-renderizacao-p02-pratica-md"
parent_key: "31.1"
tipo_arquivo: "practice"
assunto: "02_fronteira_e_renderizacao"
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Separe servidor e interação cliente
**Objetivo:** buscar dados protegidos no servidor e limitar o bundle cliente ao que precisa de interação.

**Passos:**
1. Implemente uma página de detalhe que leia um registro usando uma função de servidor ou API de teste.
2. Mantenha credenciais e acesso à fonte de dados fora do grafo cliente; identifique cada variável que atravessa a renderização.
3. Extraia uma interação real, como favoritar ou alternar um painel, para um Client Component pequeno.
4. Passe pela fronteira apenas valores necessários e serializáveis; documente o que acontece com sessão inválida e recurso não autorizado.
5. Examine o bundle ou a saída de build para confirmar que nenhum segredo foi exposto e confira a experiência com JavaScript habilitado e carregamento progressivo esperado.

**Dica:** `'use client'` define uma fronteira de módulos, não uma anotação isolada que deixa todos os imports no servidor.

**Entrega:** página com leitura no servidor e uma interação cliente, acompanhada de diagrama da fronteira e revisão das variáveis.

**Critérios de conclusão:** segredo permanece no servidor; a parte cliente é limitada à interação; estado não autorizado é tratado no servidor e na interface.

