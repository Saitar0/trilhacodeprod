---
arquivo_id: "f4-9-1-90-integracao-kp01-gabarito-pratica"
parent_key: "9.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_modelo_relacional_esquema_json", "02_chaves_primarias_identificacao", "03_chaves_estrangeiras_integridade_referencial", "04_cardinalidades_associacoes"]
ordem: 1
itens_origem: ["P1"]
---

**Solução de referência:** tabela pessoa com id como PK e nome; tabela telefone com id como PK, pessoa_id como FK para pessoa.id e numero. A cardinalidade é 1:N, com a FK na tabela telefone. Se todo telefone precisa pertencer a alguém, pessoa_id é obrigatório (NOT NULL). A unicidade do número depende da regra: não imponha uma restrição global sem saber se o mesmo telefone pode ser compartilhado; se a regra for “não repetir telefone da mesma pessoa”, considere unicidade composta entre pessoa_id e numero.

