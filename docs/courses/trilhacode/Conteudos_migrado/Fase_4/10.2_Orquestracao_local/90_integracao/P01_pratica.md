---
arquivo_id: "f4-10-2-90-integracao-p01-pratica"
parent_key: "10.2"
tipo_arquivo: "practice"
assuntos: ["01_servicos_rede_portas", "02_dados_volumes_configuracao_segura", "03_prontidao_operacao_diagnostico"]
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### Atividade 1 — Monte o ambiente mínimo
Crie um `compose.yaml) para PostgreSQL e Redis destinados a desenvolvimento local. Use nomes de serviço claros, volumes nomeados, portas acessíveis apenas pelo host local e valores de credenciais descartáveis.

**Tarefas**
1. Declare os dois serviços e associe os volumes.
2. Publique as portas locais necessárias para ferramentas do host.
3. Inclua um healthcheck adequado para cada serviço.
4. Explique como a aplicação em container acessará cada serviço.

**Dica:** use os nomes DNS `db) e `cache); para PostgreSQL 18+, confirme o caminho de dados da imagem.

