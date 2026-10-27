---
arquivo_id: "f6-26-2-02-custom-hooks-p02-pratica-md"
parent_key: "26.2"
tipo_arquivo: "practice"
assunto: "02_custom_hooks"
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Extraia lógica em custom Hook sem compartilhar estado por engano

**Desafio:** dois formulários repetem estado de texto, alteração, limpeza e validação obrigatória. Extraia uma lógica comum chamada useRequiredField.

**Passos:**
1. Identifique o comportamento realmente igual nos dois campos e diferenças que devem ser parâmetros.
2. Escreva Hook que use state para valor e exponha value, onChange, reset e erro/validade.
3. Use o Hook uma vez para nome e outra para e-mail.
4. Mostre que limpar ou digitar em um campo não altera o outro.
5. Mantenha validação específica de formato de e-mail fora do Hook genérico, a menos que a interface aceite estratégia explícita para ela.

**Dica:** repetir o Hook cria duas instâncias independentes; o Hook organiza lógica, não funciona como store compartilhada.

