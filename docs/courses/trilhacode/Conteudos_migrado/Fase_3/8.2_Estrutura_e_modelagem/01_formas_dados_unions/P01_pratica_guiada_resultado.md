---
arquivo_id: "f3-8-2-01-formas-dados-unions-p01-pratica-guiada-resultado"
parent_key: "8.2"
tipo_arquivo: "practice"
assunto: "01_formas_dados_unions"
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### 1. Guiada — estreite o resultado
Complete a função para retornar o nome em caso de sucesso ou a mensagem no caso de erro:

```ts
function mensagemDoResultado(resultado: Resultado<Produto>): string {
  // completar
}
```

Explique por que acessar `resultado.dados.nome` antes de verificar `estado` não é seguro.

**Dica:** `estado` tem um literal que identifica cada forma.

