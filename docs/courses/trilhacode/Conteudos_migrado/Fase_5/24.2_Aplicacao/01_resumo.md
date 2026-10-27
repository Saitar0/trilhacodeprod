---
arquivo_id: "f5-24-2-01-resumo"
parent_key: "24.2"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- Defina o comportamento e a fronteira que cada teste precisa provar.
- Serviço com dublê verifica regra e falhas controladas; não comprova SQL ou constraints reais.
- HTTP via aplicação de teste verifica composição e contrato da rota; declare providers simulados.
- Migrations e banco descartável validam persistência real; nunca aponte rotinas destrutivas a dados compartilhados/produção.
- Isolamento depende da conexão, workers, fixtures, limpeza e recursos encerrados.

