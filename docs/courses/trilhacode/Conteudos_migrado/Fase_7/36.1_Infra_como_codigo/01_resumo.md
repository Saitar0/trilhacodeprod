---
arquivo_id: "f7-36-1-01-resumo-md"
parent_key: "36.1"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- HCL declara estado desejado; `plan` mostra mudanças e `apply` as executa.
- Provider conecta à nuvem; restrição e lockfile de provider tornam a instalação mais previsível.
- Módulos organizam interfaces reutilizáveis com variáveis/outputs; evite abstração sem necessidade.
- State vincula código a recursos, pode conter segredos e exige armazenamento e acesso protegidos.
- Backend remoto e locking ajudam colaboração somente quando as capacidades estão configuradas.
- `sensitive` mascara saída, não apaga dados de state/plano; revise criação, atualização, replacement e destroy.

