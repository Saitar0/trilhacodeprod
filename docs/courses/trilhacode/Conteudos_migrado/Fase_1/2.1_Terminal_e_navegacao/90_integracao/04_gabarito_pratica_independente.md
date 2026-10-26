---
arquivo_id: "f1-2-1-90-integracao-04-gabarito-pratica-independente"
parent_key: "2.1"
tipo_arquivo: "answer_key_pratica"
ordem: 2
itens_origem: ["P2"]
---

**Referência para autocorreção:** confira `pwd` e `ls saida` primeiro. Como a anotação existente precisa ser preservada, uma solução direta é `find fontes -type f -name "*.md" | sort >> saida/arquivos.txt`; assim, a lista ordenada é acrescentada. Depois, use `printf '%s\n' 'Busca revisada' >> saida/arquivos.txt` e confira com `cat saida/arquivos.txt`. O operador `>` criaria ou substituiria o destino e apagaria a anotação; `>>` cria o arquivo se necessário e acrescenta ao final. O pipe envia a saída de `find` para `sort`. Não use `>` diretamente sobre o único arquivo que contém informação a preservar.

