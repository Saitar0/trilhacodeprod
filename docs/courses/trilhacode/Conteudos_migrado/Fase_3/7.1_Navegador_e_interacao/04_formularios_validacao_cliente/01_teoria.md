---
arquivo_id: "f3-7-1-04-formularios-validacao-cliente-01-teoria"
parent_key: "7.1"
tipo_arquivo: "theory"
assunto: "04_formularios_validacao_cliente"
ordem: 4
itens_origem: ["Formulários e validação nativa", "Limites da validação no cliente"]
---

### Formulários e validação nativa
HTML oferece restrições nativas, como `required`, `type="email"` e `minlength`. Quando os dados não passam pela validação nativa, o navegador normalmente não dispara `submit` e informa o campo inválido. Para dados válidos, o handler de `submit` pode impedir o envio tradicional e atualizar a página. Controles precisam de `name` para aparecer em `FormData`; labels associados ajudam a identificar os campos.

Mensagens adicionais devem explicar o problema em texto e ser associadas ao campo quando necessário; não dependa apenas de cor. Um status de confirmação pode usar uma região `aria-live` para ser anunciado por tecnologias assistivas. Validação no navegador melhora a experiência, mas não estabelece confiança nos dados.

### Limites da validação no cliente
JavaScript executado no navegador pode ser alterado ou contornado. A interface pode sinalizar erros cedo, mas o servidor precisa validar novamente todos os dados recebidos e aplicar as regras de segurança. Uma validação no cliente não autoriza nem protege a persistência por conta própria.

```js
const formulario = document.querySelector("#contato");
const resultado = document.querySelector("#resultado");

if (formulario && resultado) {
  formulario.addEventListener("submit", (event) => {
    event.preventDefault();
    const dados = new FormData(formulario);
    resultado.textContent = `Recebido: ${dados.get("email")}`;
  });
}
```

O navegador verifica as restrições nativas antes de disparar `submit`. O código acima então intercepta o envio válido e apresenta o e-mail como texto. O atributo `name="email"` deve existir no controle; neste exemplo, o handler não envia dados para um servidor.

