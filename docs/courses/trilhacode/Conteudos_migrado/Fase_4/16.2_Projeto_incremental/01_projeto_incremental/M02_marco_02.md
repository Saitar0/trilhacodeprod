---
arquivo_id: "f4-16-2-01-projeto-incremental-m02-marco-02"
parent_key: "16.2"
tipo_arquivo: "milestone"
assunto: "01_projeto_incremental"
ordem: 2
itens_origem: ["M2"]
titulo_marco: "Marco 2 — Persistir a fatia em PostgreSQL"
---

### Marco 2 — Persistir a fatia em PostgreSQL
**Entrega:** migrations versionadas, schema com restrições adequadas, dados de demonstração e uma consulta real da funcionalidade.

Implemente as tabelas e relações necessárias. Use tipos e constraints para expressar invariantes importantes, como `NOT NULL`, unicidade, chaves estrangeiras e verificações de domínio quando fizerem sentido. Separe migrations em arquivos ordenados e inclua um caminho para aplicar o schema do zero. Não dependa apenas de validação no frontend para proteger dados.

Implemente a consulta e a escrita mínimas para completar a fatia. Registre um teste ou roteiro reproduzível que cubra o caminho normal e pelo menos um caso inválido que o próprio banco deve rejeitar.

**Evidências sugeridas:** migrations, diagrama atualizado se necessário, teste/roteiro e saída de consulta.

