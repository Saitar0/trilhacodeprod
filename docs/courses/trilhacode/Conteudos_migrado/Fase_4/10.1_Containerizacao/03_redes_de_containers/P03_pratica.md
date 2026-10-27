---
arquivo_id: "f4-10-1-03-redes-de-containers-p03-pratica"
parent_key: "10.1"
tipo_arquivo: "practice"
assunto: "03_redes_de_containers"
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Conecte aplicação e banco em rede
Considere uma aplicação Node.js containerizada e um container PostgreSQL. A aplicação roda em container separado e precisa consultar o banco. Não use Compose nesta atividade.

**Tarefas**
1. Crie uma rede bridge de usuário e conecte os dois containers.
2. Configure a aplicação para usar o nome do container do banco e a porta interna.
3. Diferencie a conexão da aplicação daquela feita por um cliente executado no host.
4. Explique como diagnosticar falhas consultando estado, logs e configuração de rede.

**Dica:** teste primeiro se ambos estão na mesma rede; não suponha que localhost tenha o mesmo significado dentro e fora de um container.

