---
arquivo_id: "f3-8-2-01-formas-dados-unions-kp01-gabarito-resultado"
parent_key: "8.2"
tipo_arquivo: "answer_key_pratica"
assunto: "01_formas_dados_unions"
ordem: 1
itens_origem: ["P1"]
---

**Solução esperada:**
```ts
function mensagemDoResultado(resultado: Resultado<Produto>): string {
  if (resultado.estado === "sucesso") {
    return resultado.dados.nome;
  }
  return resultado.mensagem;
}
```

