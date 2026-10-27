---
arquivo_id: "f4-14-1-02-consultas-filtros-projecoes-arrays-01-teoria"
parent_key: "14.1"
tipo_arquivo: "theory"
assunto: "02_consultas_filtros_projecoes_arrays"
ordem: 2
itens_origem: ["2. Consulte com filtros, projeção e arrays"]
---

### 2. Consulte com filtros, projeção e arrays
`find(filtro, projeção)) retorna um cursor de documentos que correspondem ao filtro; o cursor pode ser percorrido por `mongosh) ou por um driver. O filtro restringe quais documentos correspondem; a projeção define quais campos retornar. `_id) é incluído por padrão, a menos que seja excluído explicitamente.

```javascript
db.produtos.find(
  { ativo: true, categoria: "livros" },
  { nome: 1, preco: 1, _id: 0 }
)
```

Para campos aninhados, use notação de ponto, como `"fabricante.pais": "BR"). Para arrays de documentos, `$elemMatch) permite exigir que condições correspondam ao mesmo elemento do array:

```javascript
db.produtos.find({
  especificacoes: {
    $elemMatch: { chave: "formato", valor: "impresso" }
  }
})
```

Sem `$elemMatch), condições independentes em campos de array podem ser satisfeitas por elementos diferentes, dependendo do filtro. Revise exemplos e documentos retornados para confirmar a semântica pretendida.

**Erro comum:** filtrar um campo aninhado como se estivesse no nível raiz ou supor que duas condições de array sempre se referem ao mesmo elemento.

