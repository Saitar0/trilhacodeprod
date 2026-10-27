---
arquivo_id: "f3-7-3-90-integracao-p02-pratica-independente-leitura-robusta"
parent_key: "7.3"
tipo_arquivo: "practice"
assuntos: ["01_formato_e_contrato_json", "02_requisicao_async_resposta_erros"]
ordem: 2
itens_origem: ["P2"]
---

### 2. Independente — implemente uma função de leitura robusta
Implemente `carregarCatalogo(url)` com `fetch` e `async/await`. A função deve solicitar JSON, verificar o status, interpretar o corpo e validar que o resultado contém `items` como array. Ela deve retornar esse array. Em falha HTTP, parsing ou contrato inválido, lance erro com uma mensagem que identifique a etapa, sem esconder o status quando disponível.

**Dica:** resolva em camadas: aguarde a resposta; verifique `ok`; leia JSON; cheque `Array.isArray(dados.items)`.

