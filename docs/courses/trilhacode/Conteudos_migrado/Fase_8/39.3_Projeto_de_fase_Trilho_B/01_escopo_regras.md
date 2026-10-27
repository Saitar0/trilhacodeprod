---
arquivo_id: "f8-39-3-01-escopo-regras-md"
parent_key: "39.3"
tipo_arquivo: "project_scope"
ordem: 0
itens_origem: ["Escopo e regras"]
---

## Escopo e regras

- Este projeto é independente do projeto principal do Trilho A trabalhado em 39.2. Não copie nem reimplemente o mesmo projeto; siga as ideias distintas do [Guia de Projetos — Trilhos A e B e rotação de tipos](../../../Guia_Projetos_e_Rotacao_de_Tipos.md).
- Para a Fase 8, os tipos disponíveis são T1–T5. Consulte a tabela de cobertura atualizada; repetições são opcionais e não completam um tipo pendente.
- Exiba três opções obedecendo à prioridade de rotação do guia. Escolha uma opção pendente e use a ideia indicada para o tipo; marque a cobertura somente depois de comprovar aceite.
- A versão da fase é autocontida: se for a primeira vez do tipo, inclua a base mínima da Fase 5 (schema PostgreSQL com migrations e API simples, conforme o tipo), além do container, pipeline e métrica pedida na Fase 8. Se a base já existe, reutilize-a e faça apenas o recorte necessário.
- Mantenha a fatia vertical mínima: problema central, não aplicação completa. Telas, polimento visual e funcionalidades laterais ficam fora.
- Use ambiente local ou sandbox/staging controlado, dados sintéticos, credenciais temporárias e limite de recursos. Nunca injete falhas em produção. Ao terminar, destrua recursos temporários e confirme que não restaram serviços pagos ativos.

