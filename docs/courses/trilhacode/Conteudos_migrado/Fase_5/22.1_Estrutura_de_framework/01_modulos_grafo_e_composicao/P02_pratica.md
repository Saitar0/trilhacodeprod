---
arquivo_id: "f5-22-1-01-modulos-grafo-e-composicao-p02-pratica"
parent_key: "22.1"
tipo_arquivo: "practice"
assunto: "01_modulos_grafo_e_composicao"
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Importe e exponha uma dependência de feature
**Objetivo:** tornar o contrato entre dois módulos explícito sem globalização ou cópia de provider.

**Passos:**
1. Modele duas features relacionadas, como OrdersModule e BillingModule.
2. Decida qual capacidade OrdersModule oferece aos consumidores e qual provider deve ser público.
3. Exporte somente esse provider e importe OrdersModule em BillingModule.
4. Associe um token de repositório a uma implementação concreta no módulo que compõe a aplicação.
5. Desenhe o grafo e explique por que não registrou o mesmo provider em BillingModule nem tornou o módulo global.

**Dica:** a interface TypeScript pode descrever o contrato, mas registre/injete um token existente em runtime.

