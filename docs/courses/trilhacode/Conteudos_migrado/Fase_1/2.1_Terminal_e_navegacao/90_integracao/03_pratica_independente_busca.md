---
arquivo_id: "f1-2-1-90-integracao-03-pratica-independente-busca"
parent_key: "2.1"
tipo_arquivo: "practice"
ordem: 2
itens_origem: ["P2"]
---

### 2. Independente — planeje uma busca sem sobrescrever dados

Dentro de uma nova pasta temporária `laboratorio`, você precisa localizar todos os arquivos `.md` de `fontes`, ordenar a lista, gravá-la em `saida/arquivos.txt` e depois acrescentar a linha `Busca revisada`. A pasta `saida` já contém um arquivo `arquivos.txt` com uma anotação que precisa ser preservada.

**Entregue antes de executar:**

1. Os comandos Bash, em ordem, para verificar o diretório atual, inspecionar a pasta de destino, produzir a lista ordenada e acrescentar a anotação.
2. Uma explicação curta do que `find`, `sort`, `|`, `>` e `>>` fazem nessa sequência.
3. Uma forma de conferir que a anotação anterior continua no arquivo e que a nova linha foi acrescentada.

**Dicas progressivas**

- A busca deve começar em `fontes`, não em todo o computador. Use aspas no padrão `"*.md"` para que o shell não tente expandi-lo antes de `find` recebê-lo.
- O arquivo de destino já contém informação: escolha o operador de gravação só depois de decidir se deseja substituir ou acrescentar.

