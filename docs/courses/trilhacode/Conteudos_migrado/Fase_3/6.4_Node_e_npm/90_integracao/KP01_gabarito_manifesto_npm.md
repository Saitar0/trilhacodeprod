---
arquivo_id: "f3-6-4-90-integracao-kp01-gabarito-manifesto-npm"
parent_key: "6.4"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_node_execucao_modulos", "02_manifesto_dependencias", "03_lockfile_instalacao_reproduzivel", "04_scripts_ferramentas_qualidade"]
ordem: 1
itens_origem: ["P1"]
---

**Gabarito comentado:** `date-fns` é dependência de runtime neste exemplo; ESLint e Prettier são ferramentas de desenvolvimento. `npm start` chama `node src/index.js`; `npm run lint` executa a análise; `npm run format` altera arquivos por causa de `--write`. `"type": "module"` indica sintaxe ESM no `.js`. `node_modules` é a instalação local recriável; o lockfile registra a árvore destinada à instalação.

**Erro comum:** dizer que `npm run format` só verifica o estilo; no exemplo, `--write` modifica arquivos.

