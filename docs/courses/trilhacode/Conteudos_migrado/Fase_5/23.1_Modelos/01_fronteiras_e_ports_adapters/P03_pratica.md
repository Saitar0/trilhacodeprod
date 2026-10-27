---
arquivo_id: "f5-23-1-01-fronteiras-e-ports-adapters-p03-pratica"
parent_key: "23.1"
tipo_arquivo: "practice"
assunto: "01_fronteiras_e_ports_adapters"
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Injete uma porta e prove a troca

**Desafio:** em NestJS, conecte um caso de uso de reserva a uma porta de persistência sem depender diretamente do provider PostgreSQL e demonstre a substituição em teste.

**Passos:**
1. Defina um contrato pequeno, por exemplo, consultar conflito e salvar uma reserva.
2. Registre um token de injeção em runtime para o contrato, já que interfaces TypeScript não existem após a compilação.
3. Implemente o contrato com um adapter PostgreSQL e faça o módulo fornecer esse adapter pelo token.
4. Crie um fake compatível para o teste do caso de uso.
5. Teste uma reserva válida e outra que conflita; verifique também o comportamento quando a persistência falha.
6. Explique qual tipo de mudança a fronteira facilita e qual complexidade ela adiciona.

**Dica:** em Nest, contratos expressos como interface podem ser usados pelo TypeScript, mas a injeção precisa de um token que exista em runtime e de @Inject() quando necessário.

