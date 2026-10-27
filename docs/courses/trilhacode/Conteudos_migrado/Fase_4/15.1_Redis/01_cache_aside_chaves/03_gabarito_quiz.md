---
arquivo_id: "f4-15-1-01-cache-aside-chaves-03-gabarito-quiz"
parent_key: "15.1"
tipo_arquivo: "answer_key"
assunto: "01_cache_aside_chaves"
ordem: 1
itens_origem: ["Q1", "Q3"]
---

**Resposta:** consultar a fonte de verdade, devolver o resultado e gravar a cópia no Redis conforme a política de cache.  
   **Feedback:** o cache não inventa o valor nem vira a autoridade. Em um miss, a aplicação busca a origem e pode preencher o cache para leituras seguintes.

**Resposta:** todos os parâmetros que mudam o resultado, como filtro, página e, se aplicável, idioma, escopo de usuário ou versão.  
   **Feedback:** chaves incompletas podem fazer duas consultas diferentes receberem a mesma resposta armazenada.

