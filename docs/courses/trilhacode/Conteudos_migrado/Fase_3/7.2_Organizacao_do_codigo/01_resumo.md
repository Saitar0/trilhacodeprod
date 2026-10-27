---
arquivo_id: "f3-7-2-01-resumo"
parent_key: "7.2"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- `export` define a interface consumível; `import` declara a dependência.
- Imports nomeados usam chaves e precisam corresponder ao nome exportado.
- No navegador, carregue o ponto de entrada com `type="module"` e use caminhos resolvíveis.
- O caminho de import é relativo ao arquivo que declara esse import, não ao HTML.
- Separe por responsabilidades coesas; mantenha a transformação de dados independente do DOM quando isso clarificar o código.
- O ponto de entrada conecta módulos; ciclos e arquivos sem coesão indicam que a divisão merece revisão.

