---
arquivo_id: "f4-10-1-03-redes-de-containers-kp03-gabarito-pratica"
parent_key: "10.1"
tipo_arquivo: "answer_key_pratica"
assunto: "03_redes_de_containers"
ordem: 3
itens_origem: ["P3"]
---

**Solução de referência:** crie a rede `estudo-net`; conecte o banco e a aplicação com `--network estudo-net`. Configure a aplicação com host `estudo-db` e porta 5432. Um cliente no host usa uma porta publicada, por exemplo localhost:5432; um container na mesma rede usa o nome do banco e a porta interna. Investigue com `docker ps -a`, `docker logs`, `docker inspect` e a inspeção da rede para confirmar nomes, status e associação.

