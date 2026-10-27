---
arquivo_id: "f5-23-1-01-fronteiras-e-ports-adapters-kp03-gabarito-pratica"
parent_key: "23.1"
tipo_arquivo: "answer_key_pratica"
assunto: "01_fronteiras_e_ports_adapters"
ordem: 3
itens_origem: ["P3"]
---

**Solução de referência:** o caso de uso depende do contrato em seu tipo e recebe um token de runtime por meio do construtor; o módulo associa esse token ao adapter concreto; o teste fornece um fake sob o mesmo token ou instancia o caso de uso com o fake. O teste verifica o resultado e a regra de conflito sem conectar ao banco. Detalhes de serialização SQL pertencem ao adapter.

