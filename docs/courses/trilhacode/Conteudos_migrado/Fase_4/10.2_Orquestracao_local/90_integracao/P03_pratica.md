---
arquivo_id: "f4-10-2-90-integracao-p03-pratica"
parent_key: "10.2"
tipo_arquivo: "practice"
assuntos: ["01_servicos_rede_portas", "02_dados_volumes_configuracao_segura", "03_prontidao_operacao_diagnostico"]
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Faça API esperar pelo banco e investigue falhas
Adicione um serviço `api) construído pelo Dockerfile do projeto. A API depende do banco e deve receber o endereço interno do serviço. Simule conceitualmente falhas de configuração, inicialização lenta e credencial incorreta e descreva o diagnóstico.

**Tarefas**
1. Configure `build), variáveis de conexão e dependência do serviço `db).
2. Faça a dependência aguardar um healthcheck válido.
3. Explique por que a API ainda deve lidar com desconexões após iniciar.
4. Descreva como usar `config), `ps), `logs) e `exec) para localizar a falha.
5. Liste quais dados são preservados após `down) e o que `down --volumes) remove.

**Dica:** diferencie “container iniciou”, “healthcheck passou” e “aplicação conseguiu executar sua consulta”.

