---
arquivo_id: "f3-7-3-90-integracao-p01-pratica-guiada-resultados-http"
parent_key: "7.3"
tipo_arquivo: "practice"
assuntos: ["01_formato_e_contrato_json", "02_requisicao_async_resposta_erros"]
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### 1. Guiada — rastreie quatro resultados diferentes
Leia cada cenário e classifique o resultado como: (a) falha de rede/CORS antes de obter resposta legível; (b) HTTP não bem-sucedido; (c) erro ao interpretar JSON; ou (d) JSON válido, porém fora do formato esperado. Depois escreva uma mensagem útil ao usuário para cada um.

- **Cenário A:** a conexão é interrompida e o navegador não disponibiliza um objeto `Response`.
- **Cenário B:** `fetch` recebe status 503 e `response.ok` é falso.
- **Cenário C:** status 200, mas o corpo recebido é `{ "produtos": [`.
- **Cenário D:** status 200, JSON válido `{"items":[]}`; o código procura `data.products`.

**Dica:** primeiro pergunte se existe um `Response`; depois confira status, parsing e estrutura do objeto em ordem.

