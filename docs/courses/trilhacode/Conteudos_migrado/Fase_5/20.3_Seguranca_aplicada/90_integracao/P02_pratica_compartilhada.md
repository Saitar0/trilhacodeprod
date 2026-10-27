---
arquivo_id: "f5-20-3-90-integracao-p02-pratica-compartilhada"
parent_key: "20.3"
tipo_arquivo: "practice"
assuntos: ["02_propriedades_e_minimizacao", "04_finalidade_retencao_e_logs"]
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Minimização de propriedades e dados
**Objetivo:** reduzir exposição em respostas, atualizações e logs.

**Passos:**
1. Escolha um endpoint que retorna ou atualiza um objeto do projeto.
2. Compare propriedades do modelo com as necessárias na resposta e nas alterações aceitas.
3. Crie DTOs/serialização por allowlist e rejeite ou ignore campos não permitidos segundo o contrato da API.
4. Revise logs e dados de teste; remova credenciais, tokens e valores pessoais não necessários.
5. Para cada campo pessoal retido, registre finalidade de produto, quem acessa e regra de retenção; encaminhe dúvidas de base legal para avaliação apropriada.

**Dica:** não confunda ocultar o campo na UI com removê-lo da resposta HTTP. Revise a resposta real e o corpo de atualização.

