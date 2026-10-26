---
arquivo_id: "f1-2-1-90-integracao-01-pratica-guiada-caminhos"
parent_key: "2.1"
tipo_arquivo: "practice"
ordem: 1
itens_origem: ["P1"]
---

## Prática — três níveis

Faça as atividades em ordem e trabalhe somente dentro de uma pasta temporária criada para elas. A primeira é guiada; a segunda pede que você planeje uma sequência segura; a terceira reúne as operações em uma tarefa completa. Os exemplos de comandos são para Bash em GNU/Linux, macOS, WSL ou Git Bash.

### 1. Guiada — leia caminhos e confira o efeito

Considere que seu diretório atual é `/home/ana/curso/exercicios` e que a estrutura abaixo já existe:

```text
exercicios/
├── entrada/
│   └── roteiro.md
└── estudo/
    ├── docs/
    └── saida/
```

**Parte A — interprete antes de executar:** diga qual arquivo cada caminho aponta:

- `entrada/roteiro.md`
- `../curso/exercicios/entrada/roteiro.md`
- `/home/ana/curso/exercicios/entrada/roteiro.md`

**Parte B — execute em uma cópia temporária da estrutura:**

```bash
pwd
ls entrada
cat entrada/roteiro.md
mkdir -p estudo/entrada estudo/docs estudo/saida
cp entrada/roteiro.md estudo/docs/roteiro-copia.md
find estudo -type f -name "*.md"
```

Antes de cada comando que cria ou copia, explique o diretório de origem e o destino. `mkdir -p` pode deixar os diretórios existentes como estão; `cp` cria uma cópia. Nenhum comando deste roteiro remove arquivos.

