---
arquivo_id: "f4-16-2-01-projeto-incremental-c01-aceite-01"
parent_key: "16.2"
tipo_arquivo: "checklist"
assunto: "01_projeto_incremental"
ordem: 1
itens_origem: ["M1"]
titulo_marco: "Marco 1 — Delimitar a fatia e reproduzir o ambiente"
---

**Aceite verificável:**
- README explica qual projeto foi continuado, qual fatia foi escolhida e como iniciar/parar o ambiente.
- Diagrama corresponde aos dados e relações usados na fatia.
- `docker compose config` valida a configuração; os serviços iniciam e ficam acessíveis pelos nomes da rede Compose.
- Configuração local não inclui credenciais reais; `.env` e arquivos com segredos não entram no repositório.
- Está documentado o que a limpeza preserva ou remove, sobretudo dados de volumes.

