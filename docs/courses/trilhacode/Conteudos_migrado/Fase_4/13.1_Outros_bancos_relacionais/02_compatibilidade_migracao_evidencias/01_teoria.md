---
arquivo_id: "f4-13-1-02-compatibilidade-migracao-evidencias-01-teoria"
parent_key: "13.1"
tipo_arquivo: "theory"
assunto: "02_compatibilidade_migracao_evidencias"
ordem: 2
itens_origem: ["3. Planeje migração com evidências"]
---

### 3. Planeje migração com evidências
Migrar significa validar comportamento e dados, não trocar apenas o nome do driver. Faça um inventário do schema e das consultas importantes; identifique recursos específicos; confirme como os tipos e constraints são representados; confira funções de data, paginação, geração de IDs, upsert, locking e isolamento. Em seguida, execute testes de compatibilidade com dados representativos e compare resultados, não apenas se o script compila.

Considere também operação: backup e restore, permissões, ferramentas de migration, monitoramento, custo de execução e plano para voltar ou corrigir. Uma tabela genérica de “compatibilidade total” tende a esconder diferenças de versão e de configuração. Registre a fonte oficial e a versão que confirmou cada conclusão.

**Erro comum:** concluir que uma migração foi bem-sucedida porque DDL e consultas foram aceitos, sem comparar semântica, dados, transações e comportamento operacional.

