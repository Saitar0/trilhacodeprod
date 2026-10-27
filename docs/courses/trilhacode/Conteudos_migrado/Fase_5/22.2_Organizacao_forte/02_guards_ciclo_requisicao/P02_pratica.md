---
arquivo_id: "f5-22-2-02-guards-ciclo-requisicao-p02-pratica"
parent_key: "22.2"
tipo_arquivo: "practice"
assunto: "02_guards_ciclo_requisicao"
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Guard de autenticação e papel
**Objetivo:** proteger uma rota com contexto de autenticação e metadados declarativos.

**Passos:**
1. Crie uma rota pública e uma rota restrita no mesmo módulo de exemplo.
2. Defina explicitamente o que marca cada rota como pública ou protegida.
3. Faça o guard de autenticação estabelecer ou exigir o usuário confiável; crie decorator de papel/permissão e leia os metadados com Reflector.
4. Teste pessoa sem autenticação, pessoa autenticada sem papel e pessoa autorizada.
5. Registre a ordem dos guards configurados e explique por que o corpo ainda não passou pelos pipes quando eles executam.

**Dica:** evite um guard que permita acesso por padrão quando não encontra política por acidente. A convenção para rotas públicas precisa ser deliberada e revisável.

