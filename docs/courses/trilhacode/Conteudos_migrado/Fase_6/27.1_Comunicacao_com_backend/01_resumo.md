---
arquivo_id: "f6-27-1-01-resumo-md"
parent_key: "27.1"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- Confirme contrato de método, URL, headers, corpo, status e formato de resposta antes de integrar.
- fetch não rejeita automaticamente por status HTTP; diferencie erro HTTP, rede, CORS e cancelamento.
- Credenciais seguem arquitetura e threat model; token não vai na URL nem segredo de servidor no bundle.
- Trate 401 e 403 segundo seus significados e evite ciclos de renovação/retry ilimitados.
- Sincronize filtros, paginação e respostas; descarte resultado obsoleto sem presumir que abortar desfaz uma escrita.
- CORS exige configuração da origem servidora; o cliente não contorna a política.

