---
arquivo_id: "f5-17-2-01-reproducao-e-inspector-p01-pratica"
parent_key: "17.2"
tipo_arquivo: "practice"
assunto: "01_reproducao_e_inspector"
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### Atividade 1 — Encontrar a causa de uma falha reproduzível
Considere uma rota de consulta de usuário que funciona para IDs existentes, mas retorna erro interno quando o ID não existe. A implementação tenta acessar o nome do resultado sem verificar se a consulta retornou um usuário. Reproduza o caso com um ID ausente, registre entrada e resposta, inicie o processo com node --inspect-brk ou node --inspect, coloque breakpoint antes do acesso ao nome e siga os valores. Corrija o fluxo para representar a ausência como resposta apropriada e acrescente uma verificação de regressão.

**Dica:** inspecione o resultado da consulta e o frame da aplicação antes de alterar a resposta HTTP. Diferencie ausência esperada de usuário de falha inesperada do banco.

