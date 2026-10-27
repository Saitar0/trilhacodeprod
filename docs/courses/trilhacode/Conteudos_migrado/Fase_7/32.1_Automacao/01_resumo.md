---
arquivo_id: "f7-32-1-01-resumo-md"
parent_key: "32.1"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- Evento inicia o workflow; jobs executam em runners e steps fazem o trabalho verificável.
- `npm ci`, versão de runtime e scripts definidos pelo repositório ajudam a reproduzir o resultado.
- Workflow verde não bloqueia merge sem regra de branch que exija o status check correto.
- Permissões mínimas, cuidado com eventos privilegiados e secrets protegem o runner.
- Actions são dependências executáveis; revisar versões e fixar SHAs aumenta a imutabilidade.
- Análise estática complementa testes e revisão, sem transformar score em prova de qualidade.

