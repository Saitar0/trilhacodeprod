---
arquivo_id: "f9-44-1-90-integracao-p02-pratica"
parent_key: "44.1"
tipo_arquivo: "practice"
assuntos: ["02_injecao_dependencia_persistencia", "03_testes_suporte_producao"]
ordem: 2
itens_origem: ["P02"]
---


### Atividade 2 — Escolha persistência e revise migração
**Contexto:** um endpoint precisa gravar pedidos com mudanças de modelo frequentes e relações; outro endpoint monta um relatório com consulta SQL já otimizada. Uma migration gerada renomeia `CustomerName` para `Name` por meio de `DropColumn` seguido de `AddColumn`.

**Instruções:** indique onde EF Core pode ser adequado e onde Dapper pode ser considerado; proponha como parametrizar a consulta do relatório; explique o risco de dados da migration; descreva artefato e revisão necessários antes de aplicar em produção. Selecione um teste unitário e um de integração que forneçam evidência distinta.

**Entrega:** nota técnica com decisão por endpoint, migration corrigida/revisada em nível conceitual, evidências de testes e uma condição de rollback.

**Dica gradual:** a migration não sabe sempre se uma coluna removida e outra criada representam renomeação; Dapper ainda recebe parâmetros de consulta, não valores concatenados.

