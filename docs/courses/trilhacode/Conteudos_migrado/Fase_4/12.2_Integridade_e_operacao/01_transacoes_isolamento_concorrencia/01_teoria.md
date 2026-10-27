---
arquivo_id: "f4-12-2-01-transacoes-isolamento-concorrencia-01-teoria"
parent_key: "12.2"
tipo_arquivo: "theory"
assunto: "01_transacoes_isolamento_concorrencia"
ordem: 1
itens_origem: ["1. Delimite transações e entenda isolamento", "2. Faça operações concorrentes de forma atômica"]
---

## Teoria

### 1. Delimite transações e entenda isolamento
Uma transação agrupa operações relacionadas: COMMIT confirma o conjunto; ROLLBACK desfaz alterações ainda não confirmadas. ACID resume propriedades esperadas: atomicidade, consistência, isolamento e durabilidade. O nível de isolamento define quais efeitos de transações concorrentes podem ser observados.

PostgreSQL usa READ COMMITTED por padrão: cada comando enxerga dados confirmados antes do início daquele comando. Dois SELECTs na mesma transação podem, portanto, observar estados diferentes se outra transação confirmar mudanças entre eles. REPEATABLE READ mantém uma visão estável para os comandos da transação no PostgreSQL, mas ainda pode haver anomalias de serialização. SERIALIZABLE oferece a garantia mais forte de que transações confirmadas equivalem a alguma execução serial, mas pode abortar transações concorrentes para preservar essa garantia.

Se o banco abortar por conflito de serialização, a aplicação precisa repetir a transação inteira a partir do início, com limite e política de espera apropriados. Não continue usando resultados lidos por uma tentativa que falhou. Uma transação curta e focada reduz bloqueios e facilita a recuperação.

**Erro comum:** supor que BEGIN sozinho torna qualquer sequência de leitura e escrita segura contra concorrência.

### 2. Faça operações concorrentes de forma atômica
Imagine duas pessoas tentando reservar as últimas unidades de um produto. Se ambas leem estoque 1 antes de qualquer uma atualizar, uma verificação feita apenas na aplicação pode permitir duas vendas. Combine a condição e a alteração em uma única instrução:

```sql
UPDATE produto
SET estoque = estoque - 2
WHERE id = 42
  AND estoque >= 2
RETURNING estoque;
```

Se uma linha for retornada, a reserva foi aplicada; se nenhuma linha for retornada, o produto não existe ou não havia saldo suficiente — a aplicação pode distinguir os casos com uma leitura adicional conforme a regra. No READ COMMITTED do PostgreSQL, atualizações concorrentes da mesma linha aguardam e reavaliam a condição na versão atualizada da linha.

Quando uma operação exige ler vários valores ou aplicar várias regras, SELECT ... FOR UPDATE bloqueia as linhas selecionadas até o fim da transação. Leia, valide e atualize rapidamente, sem manter a transação aberta durante chamadas de rede ou interação humana. Constraints continuam importantes: elas protegem invariantes mesmo se outro caminho de escrita não seguir a validação da aplicação.

**Erro comum:** ler o saldo, decidir na aplicação e gravar depois sem bloqueio nem condição atômica, deixando uma janela para outra transação mudar o dado.

