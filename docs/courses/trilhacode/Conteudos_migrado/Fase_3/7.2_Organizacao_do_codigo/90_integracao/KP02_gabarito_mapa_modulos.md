---
arquivo_id: "f3-7-2-90-integracao-kp02-gabarito-mapa-modulos"
parent_key: "7.2"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_modulos_exportacoes", "03_responsabilidades_coesao"]
ordem: 2
itens_origem: ["P2"]
---

**Solução de referência:** `livros.js` exporta `adicionarLivro`, `marcarComoLido` e `contarLidos`; `interface-livros.js` importa as funções necessárias, registra eventos e atualiza a página; `app.js` importa e chama a inicialização. Direção: `app.js → interface-livros.js → livros.js`. Outras divisões são válidas se mantiverem responsabilidades claras e evitarem ciclos.

