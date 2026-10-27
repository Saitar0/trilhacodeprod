---
arquivo_id: "f5-20-2-01-armazenamento-de-senhas-p01-pratica"
parent_key: "20.2"
tipo_arquivo: "practice"
assunto: "01_armazenamento_de_senhas"
ordem: 1
itens_origem: ["P1"]
---

## Atividades práticas

### Atividade 1 — Armazenamento de senha em ambiente local
**Objetivo:** substituir armazenamento inseguro por verificação com hash adaptativo usando biblioteca mantida.

**Passos:**
1. Em um exemplo descartável, localize o armazenamento e a verificação de senha.
2. Substitua texto puro ou hash rápido por Argon2id por meio de uma biblioteca mantida; use configuração recomendada atual e calibre custo no ambiente.
3. Confirme que o formato salvo inclui parâmetros e salt necessários para a biblioteca verificar a senha.
4. Verifique um login correto e um incorreto sem retornar a senha ou o hash em respostas/logs.
5. Escreva como uma eventual atualização de parâmetros poderia ser aplicada depois de autenticação bem-sucedida.

**Dica:** não invente salt, codificação ou comparação criptográfica própria. Use a biblioteca para gerar, armazenar e verificar o hash codificado.

