---
arquivo_id: "f5-24-2-03-isolamento-e-repetibilidade-kp03-gabarito-pratica"
parent_key: "24.2"
tipo_arquivo: "answer_key_pratica"
assunto: "03_isolamento_e_repetibilidade"
ordem: 3
itens_origem: ["P3"]
---

**Solução de referência:** cada execução usa banco/schema exclusivo ou namespace com IDs próprios; fixtures são criadas no setup; registros são consultados e removidos por identificador da execução ou o banco temporário é descartado; a conexão é configurada explicitamente para teste e validada antes de tarefas destrutivas; a sequência isolado/repetido/ordem aleatória/paralelo evidencia dependências restantes.

