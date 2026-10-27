---
arquivo_id: "f4-10-1-02-ciclo-vida-portas-armazenamento-kp02-gabarito-pratica"
parent_key: "10.1"
tipo_arquivo: "answer_key_pratica"
assunto: "02_ciclo_vida_portas_armazenamento"
ordem: 2
itens_origem: ["P2"]
---

**Solução de referência:** crie o volume `estudo_pg`, monte-o em `/var/lib/postgresql` para a imagem oficial PostgreSQL 18 ou superior, e use `docker stop` e `docker rm` para recriar o container mantendo o mesmo volume. Conecte-se novamente e consulte a tabela. Remover o volume apaga o armazenamento persistente associado. Para versões 17 ou anteriores, confirme o ponto de montagem documentado para aquela tag. Use uma senha descartável, mantenha o serviço restrito ao host de estudo e não confunda o exercício com backup.

