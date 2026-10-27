---
arquivo_id: "f5-21-1-90-integracao-p03-pratica-compartilhada"
parent_key: "21.1"
tipo_arquivo: "practice"
assuntos: ["02_acoplamento_custo_mudanca", "03_di_ponto_de_composicao", "04_refatoracao_comportamento_evidencia"]
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Revisão crítica da abstração
**Objetivo:** decidir se uma interface/camada existente deve permanecer, mudar ou ser removida.

**Passos:**
1. Escolha uma abstração existente no projeto, como interface de repositório, gateway, serviço genérico ou container.
2. Identifique quem a usa, que contrato promete e quais implementações ou variações realmente existem.
3. Descreva uma mudança que a abstração facilita e uma que ela dificulta; considere quantidade de indireções e duplicação.
4. Verifique se testes usam dublê necessário ou mockam detalhe interno sem proteger contrato.
5. Decida manter, simplificar ou ajustar a fronteira; registre sinais para revisar essa decisão no futuro.

**Dica:** uma única implementação concreta não invalida automaticamente uma interface se ela protege uma fronteira importante; várias implementações também não garantem que o contrato está bem desenhado.

