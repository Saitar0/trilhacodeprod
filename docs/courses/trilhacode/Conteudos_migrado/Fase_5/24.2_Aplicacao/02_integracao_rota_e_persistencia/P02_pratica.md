---
arquivo_id: "f5-24-2-02-integracao-rota-e-persistencia-p02-pratica"
parent_key: "24.2"
tipo_arquivo: "practice"
assunto: "02_integracao_rota_e_persistencia"
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Teste rota e persistência sem mockar o que está avaliando

**Desafio:** com um módulo Nest de teste, exercite uma rota de criação e prove a constraint de duplicidade no PostgreSQL descartável.

**Passos:**
1. Prepare uma instância de banco isolada, aplique migrations e confirme que a aplicação de teste usa essa instância.
2. Inicialize o módulo/aplicação com controller, pipes, serviço e adapter de persistência necessários.
3. Envie uma criação válida e verifique status, corpo e registro consultável no banco.
4. Repita a criação com a chave única e verifique resposta de conflito/erro prevista e que não há segunda linha.
5. Envie payload inválido e confirme que nenhuma gravação ocorreu; encerre aplicação/conexões e descarte ou limpe somente o ambiente do teste.

**Dica:** o caso inválido pode ser exercitado numa rota de teste que usa provider controlado; para a constraint, mantenha o banco real.

