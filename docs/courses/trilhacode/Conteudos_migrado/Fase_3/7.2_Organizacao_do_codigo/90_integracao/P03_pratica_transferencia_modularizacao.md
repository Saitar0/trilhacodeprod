---
arquivo_id: "f3-7-2-90-integracao-p03-pratica-transferencia-modularizacao"
parent_key: "7.2"
tipo_arquivo: "practice"
assuntos: ["01_modulos_exportacoes", "02_carregamento_diagnostico", "03_responsabilidades_coesao"]
ordem: 3
itens_origem: ["P3"]
---

### 3. Transferência — modularize uma página de tarefas
Use uma página simples com campo de texto, botão “Adicionar” e lista (ou crie uma). Separe em um módulo de dados, outro de interação com o DOM e um ponto de entrada. Preserve a adição e a atualização visual da lista. Use exportações nomeadas para funções compartilhadas.

**Entregáveis:** arquivos, mapa de imports, instrução de execução por servidor local e uma nota justificando uma decisão de separação e uma mudança que agora ficaria localizada em um módulo.

**Dicas:** faça a transformação de dados funcionar sem DOM; na interface, selecione elementos e registre eventos; deixe `app.js` iniciar a aplicação; confira cada caminho a partir do arquivo que o declara.

**Estrutura sugerida:**
```text
projeto/
  index.html
  app.js
  tarefas.js
  interface-tarefas.js
```

