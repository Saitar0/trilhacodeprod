---
arquivo_id: "f5-20-1-90-integracao-p01-pratica-compartilhada"
parent_key: "20.1"
tipo_arquivo: "practice"
assuntos: ["01_identidade_sessao_ciclo_de_vida", "02_jwt_e_validacao_de_tokens"]
ordem: 1
itens_origem: ["P1"]
---

## Atividades práticas

### Atividade 1 — Compare sessão e token
**Objetivo:** mapear o ciclo de credenciais e identificar decisões diferentes entre duas abordagens.

**Passos:**
1. Desenhe duas sequências para a mesma aplicação: sessão mantida no servidor e abordagem baseada em access token.
2. Inclua login, primeira resposta autenticada, chamada seguinte, expiração, renovação e logout.
3. Marque a localização de cada credencial, quem a valida e como é invalidada.
4. Anote riscos de roubo/replay, CSRF, XSS, escalabilidade e operação que variam entre as abordagens.
5. Escolha uma delas para o cenário definido e registre trade-offs e questões que dependem do provedor.

**Dica:** não compare “sessão” com “JWT” como se fossem alternativas perfeitamente simétricas: sessão descreve estado de autenticação; JWT descreve um formato de token.

