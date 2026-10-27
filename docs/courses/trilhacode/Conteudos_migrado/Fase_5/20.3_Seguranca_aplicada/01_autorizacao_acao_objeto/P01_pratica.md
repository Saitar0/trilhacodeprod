---
arquivo_id: "f5-20-3-01-autorizacao-acao-objeto-p01-pratica"
parent_key: "20.3"
tipo_arquivo: "practice"
assunto: "01_autorizacao_acao_objeto"
ordem: 1
itens_origem: ["P1"]
---

## Atividades práticas

### Atividade 1 — Matriz de autorização e teste negativo
**Objetivo:** detectar acesso indevido por objeto e por ação.

**Passos:**
1. Escolha um recurso do projeto, como pedido, documento ou perfil, com ao menos dois proprietários ou tenants.
2. Liste ações relevantes: ler, atualizar e excluir; inclua papel administrativo somente se fizer sentido.
3. Escreva uma matriz identidade × recurso × ação, indicando permissões e negações.
4. Implemente a regra no servidor perto da operação; derive identidade e tenant do contexto confiável.
5. Teste dono, pessoa de outro tenant, pessoa sem autenticação e papel privilegiado, trocando IDs de rota e corpo.

**Dica:** teste também lista, busca e operações em lote. Proteger leitura individual não garante que uma listagem não misture tenants.

