---
arquivo_id: "f5-24-2-03-isolamento-e-repetibilidade-p03-pratica"
parent_key: "24.2"
tipo_arquivo: "practice"
assunto: "03_isolamento_e_repetibilidade"
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Audite a suíte entre execuções

**Desafio:** a primeira execução passa, a segunda falha por e-mail repetido e uma execução paralela às vezes encontra dados de outra.

**Passos:**
1. Localize dados fixos, tabelas compartilhadas, conexão, fixtures e teardown.
2. Defina escopo único para execução e para cada worker, escolhendo entre banco/schema descartável ou identificadores e limpeza delimitados.
3. Faça setup criar dados necessários e teardown apagar apenas o que a execução possui, inclusive diante de falha.
4. Verifique que a aplicação não aponta para ambiente de produção e que a estratégia de rollback é compatível com suas conexões.
5. Descreva uma sequência de validação: teste sozinho, repetir, inverter ordem e executar em paralelo.

**Dica:** limpar a tabela inteira pode mascarar o problema e apagar dados que pertencem a outro processo; prefira isolar antes de limpar.

