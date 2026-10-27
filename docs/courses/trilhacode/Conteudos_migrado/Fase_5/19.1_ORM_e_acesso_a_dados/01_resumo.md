---
arquivo_id: "f5-19-1-01-resumo"
parent_key: "19.1"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- O ORM traduz operações da aplicação, mas o banco continua impondo integridade e executando SQL.
- Relações, projeções e paginação devem ser avaliadas pelo SQL, volume e plano, não apenas pela conveniência da API.
- Transações devem cobrir uma unidade de negócio curta e todas as operações participantes.
- Migrations registram mudanças reproduzíveis; SQL explícito parametrizado é uma alternativa legítima quando justificada.

