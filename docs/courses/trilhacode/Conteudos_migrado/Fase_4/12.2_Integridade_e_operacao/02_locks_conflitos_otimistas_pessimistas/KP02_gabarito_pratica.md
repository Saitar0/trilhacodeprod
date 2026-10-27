---
arquivo_id: "f4-12-2-02-locks-conflitos-otimistas-pessimistas-kp02-gabarito-pratica"
parent_key: "12.2"
tipo_arquivo: "answer_key_pratica"
assunto: "02_locks_conflitos_otimistas_pessimistas"
ordem: 2
itens_origem: ["P2"]
---

**Solução de referência:**
```sql
UPDATE documento
SET conteudo = 'versão da sessão',
    versao = versao + 1
WHERE id = 7
  AND versao = 5
RETURNING versao;
```
A primeira sessão atualiza e recebe versão 6. A segunda, ainda esperando versão 5, atualiza zero linhas. Ela deve recarregar a versão atual e pedir resolução/reaplicação conforme a regra. Atualizar apenas por id permite que a última escrita substitua a primeira sem detectar o conflito.

