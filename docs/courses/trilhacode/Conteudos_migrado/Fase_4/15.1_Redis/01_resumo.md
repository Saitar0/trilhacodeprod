---
arquivo_id: "f4-15-1-01-resumo"
parent_key: "15.1"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- Escolha o tipo Redis pelas operações necessárias; tipos diferentes carregam semânticas diferentes.
- Cache-aside consulta a fonte de verdade no miss; TTL limita a duração da cópia e não garante coerência imediata.
- Invalidação, chaves completas, comportamento em falha e uso de memória fazem parte do desenho do cache.
- Meça acertos, latência, carga na origem e memória; remova ou ajuste o cache quando a evidência não justificar seu custo.
- Listas simples não fornecem, sozinhas, um protocolo completo de fila confiável.

