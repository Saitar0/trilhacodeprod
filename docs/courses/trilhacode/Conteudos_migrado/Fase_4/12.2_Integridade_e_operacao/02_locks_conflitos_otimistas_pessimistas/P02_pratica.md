---
arquivo_id: "f4-12-2-02-locks-conflitos-otimistas-pessimistas-p02-pratica"
parent_key: "12.2"
tipo_arquivo: "practice"
assunto: "02_locks_conflitos_otimistas_pessimistas"
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Detecte conflito com versão
Uma tabela documento tem id, conteudo e versao. Duas sessões leem o mesmo documento na versão 5. A primeira salva uma alteração; a segunda tenta salvar outra usando a versão antiga.

**Tarefas**
1. Escreva o UPDATE otimista que incrementa a versão.
2. Demonstre qual sessão atualiza e o que a segunda recebe.
3. Descreva como apresentar o conflito sem perder a alteração vencedora.
4. Explique por que uma atualização por id apenas poderia sobrescrever o conteúdo.

**Dica:** compare id e versão lida no WHERE e examine o número de linhas alteradas.

