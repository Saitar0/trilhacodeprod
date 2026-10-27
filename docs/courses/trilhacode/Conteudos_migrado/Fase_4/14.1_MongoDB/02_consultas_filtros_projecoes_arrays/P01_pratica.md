---
arquivo_id: "f4-14-1-02-consultas-filtros-projecoes-arrays-p01-pratica"
parent_key: "14.1"
tipo_arquivo: "practice"
assunto: "02_consultas_filtros_projecoes_arrays"
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### Atividade 1 — Consulte um catálogo flexível
Considere estes documentos:

```javascript
[
  { _id: 1, nome: "Romance A", categoria: "livros", ativo: true, preco: 40,
    especificacoes: [{ chave: "formato", valor: "impresso" }] },
  { _id: 2, nome: "E-book B", categoria: "livros", ativo: true, preco: 25,
    especificacoes: [{ chave: "formato", valor: "digital" }] },
  { _id: 3, nome: "Caneca C", categoria: "casa", ativo: false, preco: 30,
    especificacoes: [{ chave: "material", valor: "cerâmica" }] }
]
```

**Tarefas**
1. Consulte produtos ativos da categoria livros e retorne nome/preço sem `_id).
2. Consulte itens cuja especificação inclua formato impresso.
3. Explique o que a projeção muda e por que documento 3 não corresponde à primeira consulta.

**Dica:** filtre sobre campos de nível raiz na primeira consulta e use `$elemMatch) para o array.

