---
arquivo_id: "f4-16-3-01-projeto-trilho-b-m02-marco-02"
parent_key: "16.3"
tipo_arquivo: "milestone"
assunto: "01_projeto_trilho_b"
ordem: 2
itens_origem: ["M2"]
titulo_marco: "Marco 2 — Criar schema, migrations e invariantes"
---

### Marco 2 — Criar schema, migrations e invariantes
**Entrega:** migrations versionadas, estrutura relacional, constraints e dados reproduzíveis.

Implemente um conjunto pequeno de tabelas no PostgreSQL para o caso escolhido. Use chaves primárias, estrangeiras, unicidade e regras `NOT NULL`, `CHECK` quando expressarem invariantes do domínio. Inclua instruções para aplicar as migrations do zero e preparar dados de demonstração.

**Foco conforme o tipo:**
- **T1:** modele estoque e pedidos. Uma reserva/venda concorrente deve usar transação e mecanismo atômico adequado, como atualização condicional sob concorrência; uma checagem feita separadamente antes da escrita não é prova suficiente.
- **T2:** inclua identificador de tenant nas relações relevantes e torne o escopo verificável. Para agenda, avalie intervalo de tempo e constraint de exclusão com tipo range/índice apropriado; documente extensões e limites do ambiente.
- **T4:** modele os campos realmente usados na listagem; paginação deve ter ordenação estável para evitar resultados imprevisíveis.
- **T5:** documente colunas de destino e validações. Para ingestão, explique estágio, conversões e como linhas inválidas são identificadas sem perder o arquivo de origem ou esconder falhas.

**Evidências sugeridas:** migrations, comando de carga, amostra sanitizada e saída do caso normal/inválido.

