---
arquivo_id: "f4-10-1-01-imagens-contexto-build-p01-pratica"
parent_key: "10.1"
tipo_arquivo: "practice"
assunto: "01_imagens_contexto_build"
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### Atividade 1 — Leia e corrija um Dockerfile
Considere um projeto Node.js com package.json, package-lock.json, consulta.js e node_modules local. A imagem deve executar consulta.js.

**Tarefas**
1. Escreva um Dockerfile que instale dependências usando o lockfile.
2. Crie um .dockerignore que exclua node_modules, .git, .env e arquivos temporários.
3. Explique qual pasta será o contexto e por que COPY não alcança arquivos fora dela.
4. Indique uma mudança na ordem de COPY que ajuda a reutilizar cache de dependências.

**Dica:** copie manifestos e lockfile antes do código da aplicação.

