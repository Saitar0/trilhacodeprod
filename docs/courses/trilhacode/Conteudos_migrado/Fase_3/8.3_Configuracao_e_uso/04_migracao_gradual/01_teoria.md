---
arquivo_id: "f3-8-3-04-migracao-gradual-01-teoria"
parent_key: "8.3"
tipo_arquivo: "theory"
assunto: "04_migracao_gradual"
ordem: 4
itens_origem: ["4. Migração gradual de JavaScript"]
---

### 4. Migração gradual de JavaScript
allowJs permite que arquivos JavaScript sejam entradas do projeto; checkJs ativa diagnósticos neles. Isso possibilita uma evolução por etapas: delimite a pasta de entrada, separe saída, escolha um módulo de baixo risco, registre o comportamento atual, adicione tipos, ajuste consumidores e repita checagem e execução.

Mantenha a aplicação executável e limite o escopo de cada etapa. Registre exceções temporárias com contexto e plano de remoção. Não transforme cada aviso em any; resolva um contrato de cada vez.

**Erro comum:** renomear todos os arquivos de uma vez e interpretar uma avalanche de erros como um único problema. A migração incremental ajuda a localizar cada origem.

