---
arquivo_id: "f4-9-1-90-integracao-kp02-gabarito-pratica"
parent_key: "9.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["02_chaves_primarias_identificacao", "03_chaves_estrangeiras_integridade_referencial", "04_cardinalidades_associacoes"]
ordem: 2
itens_origem: ["P2"]
---

**Solução de referência:** estudante e turma têm suas PKs; matricula guarda estudante_id e turma_id como FKs, além de data_inscricao e estado. A cardinalidade entre estudante e turma é N:N e se materializa em duas relações 1:N a partir de matricula. Se o mesmo estudante só puder se matricular uma vez na mesma turma, a combinação (estudante_id, turma_id) pode ser PK composta; se houver mais de uma tentativa/registro por período, inclua o atributo que diferencia a matrícula ou escolha outra chave e declare a regra de unicidade correspondente.

