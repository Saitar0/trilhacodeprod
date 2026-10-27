---
arquivo_id: "f4-12-2-02-locks-conflitos-otimistas-pessimistas-01-teoria"
parent_key: "12.2"
tipo_arquivo: "theory"
assunto: "02_locks_conflitos_otimistas_pessimistas"
ordem: 2
itens_origem: ["3. Escolha locking pessimista ou otimista e trate conflitos"]
---

### 3. Escolha locking pessimista ou otimista e trate conflitos
Locking pessimista bloqueia linhas que serão alteradas, como com SELECT ... FOR UPDATE. É útil quando a disputa é esperada e a decisão depende de dados protegidos, mas pode fazer outras transações aguardarem. Locks devem ser mantidos pelo menor tempo necessário; transações que bloqueiam recursos em ordem diferente podem formar deadlock.

O PostgreSQL detecta deadlocks e aborta uma das transações. A aplicação deve reconhecer a falha e, quando a operação for segura para repetição, tentar novamente toda a transação com limite e pequeno atraso. Repetir apenas a última instrução pode usar decisões baseadas em um estado antigo. Evite efeitos externos irreversíveis antes de confirmar a transação; uma chamada a pagamento ou envio de e-mail não é desfeita automaticamente por ROLLBACK.

Locking otimista evita bloquear durante toda a leitura: guarde uma versão e faça a atualização condicional:

```sql
UPDATE documento
SET conteudo = 'novo conteúdo',
    versao = versao + 1
WHERE id = 7
  AND versao = 3
RETURNING versao;
```

Se nenhuma linha for atualizada, outra alteração venceu ou o registro não existe; a aplicação deve tratar o conflito, recarregar e pedir decisão conforme o caso. Não sobrescreva silenciosamente uma atualização concorrente.

**Erro comum:** tratar deadlock, conflito otimista e falha de validação como se fossem o mesmo resultado.

