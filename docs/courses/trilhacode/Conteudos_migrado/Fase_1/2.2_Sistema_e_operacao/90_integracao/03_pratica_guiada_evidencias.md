---
arquivo_id: "f1-2-2-90-integracao-03-pratica-guiada-evidencias"
parent_key: "2.2"
tipo_arquivo: "practice"
ordem: 1
itens_origem: ["P1"]
---

## Prática — três níveis

Use apenas os dados fictícios desta unidade ou uma pasta temporária. Não altere permissões reais da máquina e não publique logs que possam conter dados sensíveis.

### 1. Guiada — separe evidência de hipótese

Leia este trecho fictício de `app.log`:

```text
2026-10-14T09:00:00Z INFO  process=webapp event=started
2026-10-14T09:01:12Z INFO  process=webapp request_id=r-104 event=report_generated
2026-10-14T14:31:58Z INFO  process=webapp request_id=r-221 event=upload_started
2026-10-14T14:32:01Z ERROR process=webapp request_id=r-221 operation=write path=/srv/app/uploads/relatorio.csv error=EACCES
2026-10-14T14:32:02Z WARN  process=webapp request_id=r-221 event=upload_failed
2026-10-14T14:33:10Z INFO  process=webapp request_id=r-222 event=health_check_ok
```

**Tarefa:** registre (a) dois fatos observáveis, (b) uma hipótese que ainda precisa ser confirmada e (c) duas verificações seguras que ajudariam a investigar. Depois, diga o que estes comandos selecionariam em uma cópia do arquivo:

```bash
grep -n -C 1 "ERROR" app.log
tail -n 3 app.log
```

