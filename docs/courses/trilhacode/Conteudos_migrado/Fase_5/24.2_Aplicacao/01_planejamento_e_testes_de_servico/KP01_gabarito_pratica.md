---
arquivo_id: "f5-24-2-01-planejamento-e-testes-de-servico-kp01-gabarito-pratica"
parent_key: "24.2"
tipo_arquivo: "answer_key_pratica"
assunto: "01_planejamento_e_testes_de_servico"
ordem: 1
itens_origem: ["P1"]
---

**Solução de referência:** sucesso retorna/produz pedido criado e solicita gravação uma vez; rejeição de crédito retorna erro de domínio e não grava; indisponibilidade é propagada ou convertida conforme política do serviço, também sem gravar. O teste não comprova migrations, constraints, SQL nem transação.

