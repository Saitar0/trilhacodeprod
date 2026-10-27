---
arquivo_id: "f4-14-1-02-consultas-filtros-projecoes-arrays-kp01-gabarito-pratica"
parent_key: "14.1"
tipo_arquivo: "answer_key_pratica"
assunto: "02_consultas_filtros_projecoes_arrays"
ordem: 1
itens_origem: ["P1"]
---

**Solução de referência:**
```javascript
db.produtos.find(
  { ativo: true, categoria: "livros" },
  { nome: 1, preco: 1, _id: 0 }
)

db.produtos.find({
  especificacoes: {
    $elemMatch: { chave: "formato", valor: "impresso" }
  }
})
```
A primeira retorna Romance A e E-book B com somente nome e preço. A segunda retorna Romance A. Caneca C está inativa e não pertence à categoria livros, então não satisfaz a primeira consulta.

