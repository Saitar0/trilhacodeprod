---
arquivo_id: "f4-10-2-90-integracao-kp01-gabarito-pratica"
parent_key: "10.2"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_servicos_rede_portas", "02_dados_volumes_configuracao_segura", "03_prontidao_operacao_diagnostico"]
ordem: 1
itens_origem: ["P1"]
---

**Solução de referência:** declare `db) com imagem PostgreSQL 18+, volume em `/var/lib/postgresql), porta `127.0.0.1:5432:5432) e healthcheck com `pg_isready). Declare `cache) com Redis, volume em `/data), publicação local opcional e healthcheck com `redis-cli ping). A API na mesma rede usa `db:5432) e `cache:6379); clientes do host usam as portas publicadas. Credenciais são descartáveis e não devem ser usadas fora do exercício.

