---
arquivo_id: "f4-13-1-01-dialetos-consultas-paginadas-kp01-gabarito-pratica"
parent_key: "13.1"
tipo_arquivo: "answer_key_pratica"
assunto: "01_dialetos_consultas_paginadas"
ordem: 1
itens_origem: ["P1"]
---

**Solução de referência:**
```sql
-- PostgreSQL ou MySQL 8.4
SELECT id, nome
FROM produto
ORDER BY id
LIMIT 10 OFFSET 20;
```

```sql
-- SQL Server
SELECT id, nome
FROM produto
ORDER BY id
OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY;
```

Ambas selecionam colunas, usam FROM e ordenam por id; a forma de limitar e pular linhas difere. Como id deve ser único, ORDER BY id define desempate único. Consulte a versão específica antes de aplicar a mesma sintaxe a outro SGBD.

