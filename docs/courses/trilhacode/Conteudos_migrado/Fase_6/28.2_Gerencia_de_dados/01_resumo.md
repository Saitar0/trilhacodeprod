---
arquivo_id: "f6-28-2-01-resumo-md"
parent_key: "28.2"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- Classifique dados por origem, escopo e ciclo de vida; o servidor continua autoritativo para dados remotos.
- A chave da consulta deve conter os parâmetros que mudam a resposta, sem carregar segredos desnecessários.
- Frescor (`staleTime`) e permanência de dados inativos no cache controlam aspectos diferentes.
- Após mutações, escolha invalidação, atualização com resposta do servidor ou atualização otimista com reconciliação adequada.
- Falhas, mudanças de conta e logout exigem cuidado com dados obsoletos ou pertencentes a outra identidade.

