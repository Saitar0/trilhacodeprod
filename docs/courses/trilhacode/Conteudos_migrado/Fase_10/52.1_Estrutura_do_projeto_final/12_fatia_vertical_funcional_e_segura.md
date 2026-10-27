---
arquivo_id: "f10-52-1-m02"
parent_key: "52.1"
tipo_arquivo: "project_milestone"
ordem: 2
itens_origem: ["M02"]
titulo_marco: "Entrega 2 — Fatia vertical funcional e segura"
---


### Entrega 2 — Fatia vertical funcional e segura
Implemente um fluxo ponta a ponta pequeno no projeto existente: ação na interface, endpoint/backend, dados autorizados e resposta para usuário. Integre o modelo por uma fronteira do servidor. Valide autorização em cada acesso e ferramenta; valide saída no contrato da aplicação; aplique autenticação, limites e tratamento de erro. Para RAG, preserve origem/permissão e cite trechos recuperados; para tool calling, limite operações, parâmetros e efeitos. Inclua estados de carregamento, erro, parcial/cancelado quando houver streaming e alternativa clara quando o provedor falhar.


**Evidência:** alteração em branch, diagrama atualizado, demonstração com dados sintéticos e testes de unidade/integração para comportamento normal, entrada inválida e autorização negada.

**Feedback para revisar:** revise o diff e confirme que cada critério tem evidência. Não exponha segredo, prompt, documento privado ou erro interno. Um mock sozinho não prova integração; explique quais fronteiras cada teste cobre.

