---
arquivo_id: "f4-10-2-90-integracao-kp03-gabarito-pratica"
parent_key: "10.2"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_servicos_rede_portas", "02_dados_volumes_configuracao_segura", "03_prontidao_operacao_diagnostico"]
ordem: 3
itens_origem: ["P3"]
---

**Solução de referência:** configure a API com `DATABASE_HOST=db), `DATABASE_PORT=5432) e dependência `db: condition: service_healthy), após definir o healthcheck do banco. A API ainda precisa repetir/reabrir conexões diante de falhas ocorridas depois. Use `docker compose config) para resolver/inspecionar configuração, `ps) para estados e saúde, `logs api) e `logs db) para erros de inicialização e credenciais, e `exec) para inspecionar o container em execução. `down) remove containers e rede, mantendo volumes nomeados; `down --volumes) remove também os volumes gerenciados e seus dados.

