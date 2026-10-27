---
arquivo_id: "f5-17-2-01-reproducao-e-inspector-kp01-gabarito-pratica"
parent_key: "17.2"
tipo_arquivo: "answer_key_pratica"
assunto: "01_reproducao_e_inspector"
ordem: 1
itens_origem: ["P1"]
---

**Solução de referência:** o breakpoint mostra que o resultado é ausente antes da leitura da propriedade. A causa é a suposição de que toda consulta encontra um registro. Trate a ausência explicitamente com resposta de recurso não encontrado; mantenha erros de banco no fluxo de falha apropriado. Reexecute o mesmo caso e confirme que a rota ainda funciona para ID existente.

