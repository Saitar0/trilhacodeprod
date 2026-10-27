---
arquivo_id: "f10-53-4-p03"
parent_key: "53.4"
tipo_arquivo: "practice"
assuntos: ["03_complexidade_e_correcao", "04_testes_debug_comunicacao"]
ordem: 3
itens_origem: ["P03"]
---


### Atividade 3 — Depurar busca binária (transferência)
**Contexto e objetivo:** encontrar erro de limite, criar testes que o exponham e explicar precondições.

**Código com falha (pseudocódigo):**

```text
funcao buscar(a, alvo):
    esquerda = 0
    direita = tamanho(a)
    enquanto esquerda < direita:
        meio = (esquerda + direita) // 2
        se a[meio] == alvo:
            retornar meio
        se a[meio] < alvo:
            esquerda = meio
        senao:
            direita = meio
    retornar -1
```

**Instruções:** identifique pelo menos dois problemas possíveis; crie o menor teste que não termina ou retorna resultado incorreto; corrija os limites mantendo um intervalo coerente; teste alvo presente, ausente, primeiro/último elemento, lista vazia e duplicatas. Declare se qualquer índice correspondente serve quando houver mais de uma ocorrência.

**Entrega:** descrição dos bugs, versão corrigida, tabela de testes e explicação da invariante dos limites.

**Dica gradual:** o limite direito inicial não pode ser usado como índice válido nesse código; além disso, atribuir `esquerda = meio` pode deixar o intervalo igual quando há dois candidatos. Escolha intervalos fechado `[esquerda, direita]` ou semiaberto `[esquerda, direita)` e atualize todos os passos de forma consistente.


