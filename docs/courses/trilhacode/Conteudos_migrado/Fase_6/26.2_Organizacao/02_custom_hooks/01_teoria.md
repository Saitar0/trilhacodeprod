---
arquivo_id: "f6-26-2-02-custom-hooks-01-teoria-md"
parent_key: "26.2"
tipo_arquivo: "theory"
assunto: "02_custom_hooks"
ordem: 2
itens_origem: ["## Microtópico 3 — Custom Hooks compartilham lógica"]
---

## Microtópico 3 — Custom Hooks compartilham lógica

Um custom Hook extrai lógica que usa Hooks e pode ser reutilizada por mais de um componente. Seu nome começa com use seguido de um nome descritivo; ele pode receber parâmetros e retornar valores ou funções. Um custom Hook é uma função chamada no nível superior de um componente ou de outro Hook, respeitando as regras de Hooks.

Cada chamada do mesmo Hook executa sua própria lógica e mantém sua própria instância de estado. Duas chamadas de useField em campos diferentes não compartilham o texto digitado; elas reutilizam a forma de controlar o campo. Para compartilhar o mesmo valor, levante o estado ao pai ou conecte as partes a uma fonte compartilhada apropriada.

Extraia quando a lógica representa um conceito reutilizável — por exemplo, estado de formulário com validação comum, acompanhar online/offline ou assinar uma fonte externa. Não extraia apenas para esconder algumas linhas ou dar prefixo use a uma função pura que não chama Hooks. Para regra sem estado React, uma função JavaScript comum costuma ser mais clara.

