---
arquivo_id: "f3-7-1-03-eventos-comportamento-padrao-01-teoria"
parent_key: "7.1"
tipo_arquivo: "theory"
assunto: "03_eventos_comportamento_padrao"
ordem: 3
itens_origem: ["Eventos e comportamento padrão"]
---

### Eventos e comportamento padrão
**Eventos** representam acontecimentos como clique, envio de formulário e digitação. `addEventListener()` associa uma função ao evento. O objeto recebido pelo handler oferece contexto, como o alvo do evento. Em formulários, ouça `submit` no próprio `<form>` para cobrir envio pelo botão e envio por teclado.

`preventDefault()` cancela o comportamento padrão do evento. Use-o somente quando a aplicação vai tratar a ação no lugar do navegador, como mostrar uma confirmação local sem navegar ou recarregar. Não impede a execução dos outros handlers e não valida dados por si só.

