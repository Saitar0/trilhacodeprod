---
arquivo_id: "f1-3-2-02-conflitos-04-pratica-independente-conflito"
parent_key: "3.2"
tipo_arquivo: "practice"
assunto: "02_conflitos"
ordem: 2
itens_origem: ["P2"]
---

### 2. Independente — resolva um conflito com intenção

Em um conflito de merge, o arquivo `agenda.md` contém este trecho:

```text
## Entregas
<<<<<<< HEAD
- publicar o relatório mensal
=======
- publicar o relatório semanal
>>>>>>> feature/frequencia
```

O requisito confirmado pelo grupo é publicar os relatórios mensal e semanal. Descreva a edição final e a sequência para revisar e concluir o merge. Depois, descreva o que faria se não tivesse informação suficiente para escolher uma resolução.

**Dicas progressivas**

- `HEAD` identifica a versão da branch atual nesse conflito; a outra seção mostra a versão vinda da branch integrada. Os marcadores não fazem parte do conteúdo final.
- Consulte `git status` para identificar a operação; revise o arquivo e o diff antes de marcar a resolução. Se não puder decidir, peça contexto ou aborte a operação quando for seguro fazê-lo.

