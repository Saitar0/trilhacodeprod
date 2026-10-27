---
arquivo_id: "f3-7-5-02-network-requisicoes-p02-pratica-independente-network"
parent_key: "7.5"
tipo_arquivo: "practice"
assunto: "02_network_requisicoes"
ordem: 2
itens_origem: ["P2"]
---

### 2. Independente — classifique evidências da Network
Investigue estes registros de uma aplicação didática. Para cada um, anote o que foi observado, o que ainda é hipótese e qual é o próximo passo.

- A: `GET /api/livros` retorna status 404.
- B: `GET /api/livros` aparece como `(failed)` sem status.
- C: `GET /api/livros` retorna 200, mas o corpo contém uma lista vazia.
- D: `GET /api/livros` retorna 500 com uma resposta de erro.

**Dica:** status HTTP e ausência de status não são equivalentes; uma lista vazia também pode ser válida conforme o contrato.

