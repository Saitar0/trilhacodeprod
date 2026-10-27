---
arquivo_id: "f5-18-3-04-estado-compartilhado-e-concorrencia-01-teoria"
parent_key: "18.3"
tipo_arquivo: "theory"
assunto: "04_estado_compartilhado_e_concorrencia"
ordem: 4
itens_origem: ["4. Estado compartilhado e concorrência"]
---

### 4. Estado compartilhado e concorrência
O servidor mantém ou consulta o estado autoritativo do recurso; o canal notifica clientes sobre mudanças. Cada instância consegue distribuir mensagens apenas aos clientes que conhece, a menos que exista mecanismo de difusão compartilhado. Escala horizontal e broadcast distribuído são assuntos de fases posteriores; nesta unidade, mantenha o escopo em uma instância e documente essa limitação.

Se dois clientes alterarem o mesmo estado, defina uma política. Last-write-wins é simples, mas pode apagar silenciosamente uma atualização concorrente. Uma versão do recurso permite rejeitar uma escrita obsoleta e pedir ao cliente que recarregue. OT e CRDTs são famílias de técnicas para colaboração avançada; conhecer a existência delas não exige implementá-las aqui.

