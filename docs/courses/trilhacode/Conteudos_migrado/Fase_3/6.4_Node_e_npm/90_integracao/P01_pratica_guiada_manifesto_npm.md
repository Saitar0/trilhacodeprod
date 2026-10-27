---
arquivo_id: "f3-6-4-90-integracao-p01-pratica-guiada-manifesto-npm"
parent_key: "6.4"
tipo_arquivo: "practice"
assuntos: ["01_node_execucao_modulos", "02_manifesto_dependencias", "03_lockfile_instalacao_reproduzivel", "04_scripts_ferramentas_qualidade"]
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### 1. Guiada — leia um manifesto npm
Analise este trecho sem executar comandos:

```json
{
  "type": "module",
  "scripts": {
    "start": "node src/index.js",
    "lint": "eslint .",
    "format": "prettier . --write"
  },
  "dependencies": { "date-fns": "^4.0.0" },
  "devDependencies": { "eslint": "^9.0.0", "prettier": "^3.0.0" }
}
```

**Tarefa:** classifique cada pacote; escolha os comandos para iniciar, analisar e formatar; indique a sintaxe de módulos esperada em `src/index.js`; explique por que `node_modules` não substitui o lockfile no Git.

**Dicas graduais:** (1) associe o nome do script ao comando `npm run`; (2) diferencie uso da aplicação e ferramenta de desenvolvimento; (3) confira o campo `type`.

