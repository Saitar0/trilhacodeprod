---
arquivo_id: "f5-24-3-02-decisoes-a-demonstrar"
parent_key: "24.3"
tipo_arquivo: "project_decisions"
ordem: 0
itens_origem: ["Decisões que precisam ser demonstradas"]
---

## Decisões que precisam ser demonstradas
- Identidade e autorização vêm de contexto validado no servidor; campos enviados pelo cliente não concedem acesso por si só.
- Testes com mocks validam regras isoladas, mas não substituem ao menos um teste de integração com banco descartável.
- Cache não é obrigatório por checklist: se foi usado, sua coerência tem teste; se não foi usado, a decisão e o motivo ficam documentados.

