---
arquivo_id: "f5-22-2-01-validacao-entrada-runtime-p01-pratica"
parent_key: "22.2"
tipo_arquivo: "practice"
assunto: "01_validacao_entrada_runtime"
ordem: 1
itens_origem: ["P1"]
---

## Atividades práticas

### Atividade 1 — DTO e pipe de entrada
**Objetivo:** validar e restringir um payload antes de executar uma operação.

**Passos:**
1. Escolha um endpoint de criação ou atualização e liste campos aceitos, formato e limites.
2. Implemente DTO com class-validator e ValidationPipe ou schema runtime com StandardSchemaValidationPipe.
3. Configure rejeição ou remoção de propriedades não declaradas de forma consciente.
4. Verifique requisição válida, campo obrigatório ausente, tipo/formato inválido e campo administrativo extra.
5. Separe no caso de uso uma regra que depende do estado do domínio, não só da forma do payload.

**Dica:** se usar ValidationPipe com class-validator, uma propriedade precisa dos metadados de validação esperados para entrar na whitelist. Se usar schema, consulte a política de unknown keys da biblioteca.

