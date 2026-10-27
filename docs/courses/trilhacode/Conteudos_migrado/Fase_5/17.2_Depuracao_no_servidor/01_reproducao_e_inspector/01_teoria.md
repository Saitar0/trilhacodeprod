---
arquivo_id: "f5-17-2-01-reproducao-e-inspector-01-teoria"
parent_key: "17.2"
tipo_arquivo: "theory"
assunto: "01_reproducao_e_inspector"
ordem: 1
itens_origem: ["theory-container", "1. Reproduzir antes de alterar", "2. Inspector e breakpoints"]
---

## Teoria

### 1. Reproduzir antes de alterar
Comece descrevendo o sintoma: rota ou operação afetada, entrada, resultado esperado e resultado observado. Reproduza com a menor entrada que ainda causa o problema e registre os passos. Se o erro for intermitente, anote condições relevantes, como ordem de chamadas, concorrência ou estado do banco. Uma hipótese de causa deve ser testada com uma mudança por vez; esconder a falha com um catch vazio ou alterar várias partes ao mesmo tempo reduz a informação disponível.

### 2. Inspector e breakpoints
O inspector do Node conecta o processo a uma ferramenta de depuração, como DevTools ou IDE compatível. Iniciar com node --inspect permite que a aplicação comece a executar; node --inspect-brk interrompe no início para conectar o depurador antes de seguir. Um breakpoint pausa a execução em uma linha; a partir dele, examine variáveis locais, pilha de chamadas e o caminho até a linha seguinte. Step over executa a linha atual sem entrar em outra função; step into entra na função chamada; continue retoma até o próximo breakpoint.

O inspector não é uma interface de leitura apenas: uma conexão pode controlar e executar código no processo. Por padrão, o inspector local usa 127.0.0.1:9229. Não o exponha em um endereço público ou a uma rede não confiável; um listener aberto pode permitir execução remota de código. [Node.js — Debugging Guide](https://nodejs.org/en/learn/getting-started/debugging) e [Node.js — opções do inspector](https://nodejs.org/api/cli.html#--inspecthostport).

