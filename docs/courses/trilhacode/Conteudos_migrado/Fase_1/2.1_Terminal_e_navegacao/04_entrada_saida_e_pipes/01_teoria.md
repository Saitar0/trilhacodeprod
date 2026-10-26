---
arquivo_id: "f1-2-1-04-entrada-saida-e-pipes-01-teoria"
parent_key: "2.1"
tipo_arquivo: "theory"
assunto: "04_entrada_saida_e_pipes"
ordem: 4
itens_origem: ["Entrada, saída, redirecionamento e pipes"]
---

### Entrada, saída, redirecionamento e pipes
Programas podem ler da entrada padrão e escrever na saída padrão; mensagens de erro costumam ir para um fluxo separado. `>` direciona a saída para um arquivo e normalmente o sobrescreve; `>>` acrescenta ao final. `|` conecta a saída de um programa à entrada do próximo. Isso permite combinar ferramentas pequenas.

```bash
find . -type f -name "*.md" | sort
```

O exemplo envia os caminhos encontrados para `sort`. O pipe não significa “executar o segundo comando sobre o arquivo”; ele transmite dados entre processos. Em PowerShell, `|` também conecta comandos, mas o que passa pelo pipeline são objetos e os comandos diferem.

