---
arquivo_id: "f4-13-1-01-dialetos-consultas-paginadas-01-teoria"
parent_key: "13.1"
tipo_arquivo: "theory"
assunto: "01_dialetos_consultas_paginadas"
ordem: 1
itens_origem: ["1. Separe conceitos relacionais de detalhes do produto", "2. Compare o dialeto em um caso concreto"]
---

## Teoria

### 1. Separe conceitos relacionais de detalhes do produto
Bancos relacionais organizam dados em relações/tabelas e oferecem conceitos como chaves, joins, constraints e transações. Isso facilita transferir conhecimento, mas não garante que um mesmo script ou comportamento funcione sem ajustes em todos os SGBDs.

MySQL e MariaDB têm histórias e pontos de compatibilidade, mas são produtos distintos, com versões e recursos que evoluem separadamente. Oracle Database e Microsoft SQL Server também possuem dialetos, ferramentas e ecossistemas próprios. Nesta fase, PostgreSQL é o banco usado nas práticas; os demais entram como repertório para leitura e comparação.

**Flashcards**
- **Pergunta:** SQL padrão garante que todas as funções e comportamentos sejam iguais em qualquer SGBD? **Resposta:** não. **Lembrete:** há extensões, diferenças de implementação e recursos que variam por versão.
- **Pergunta:** MySQL e MariaDB são o mesmo produto? **Resposta:** não, são produtos distintos. **Lembrete:** compatibilidade em alguns recursos não garante equivalência completa.

### 2. Compare o dialeto em um caso concreto
Uma diferença pode aparecer em algo simples, como paginação. PostgreSQL e MySQL 8.4 aceitam `LIMIT ... OFFSET`. No SQL Server, paginação usa `ORDER BY ... OFFSET ... ROWS FETCH NEXT ... ROWS ONLY` e exige ordenação. Em todos, a consulta precisa de uma ordem explícita e estável para que páginas sejam previsíveis.

**PostgreSQL ou MySQL 8.4:**
```sql
SELECT id, nome
FROM produto
ORDER BY id
LIMIT 10 OFFSET 20;
```

**SQL Server:**
```sql
SELECT id, nome
FROM produto
ORDER BY id
OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY;
```

Não extrapole uma diferença observada para todo o dialeto. Verifique produto, versão e feature específica na documentação oficial. Uma sintaxe que existe em uma versão pode ter limites ou semântica diferente em outra.

**Flashcard**
- **Pergunta:** o que verificar ao portar uma consulta ou schema? **Resposta:** sintaxe, tipos, funções, paginação, identidade/sequences, NULL, upsert, transações, migrations, driver e plano de execução. **Lembrete:** valide cada item na versão e configuração de destino.

