---
arquivo_id: "f3-7-1-90-integracao-p03-pratica-transferencia-formulario"
parent_key: "7.1"
tipo_arquivo: "practice"
assuntos: ["01_dom_selecao", "02_texto_seguro_dom", "03_eventos_comportamento_padrao", "04_formularios_validacao_cliente"]
ordem: 3
itens_origem: ["P3"]
---

### 3. Transferência — formulário interativo acessível
Construa um formulário de contato sem framework com nome, e-mail e mensagem. Use labels associados, `name` nos controles, `required`, `type="email"` e uma restrição mínima razoável para mensagem. Adicione um handler de `submit` que processe apenas o envio válido e mostre uma confirmação sem recarregar a página. Associe o status a uma região `aria-live="polite"`; mantenha mensagens compreensíveis e não dependa apenas de cor.

Teste campos vazios, e-mail malformado, mensagem abaixo do mínimo e envio válido com teclado. Use `FormData` para ler os valores. Mostre o conteúdo recebido com `textContent`; não envie HTML digitado para `innerHTML`. Como não há servidor nesta atividade, indique que validação real e persistência ainda precisariam ocorrer no servidor.

**Entregue:** HTML e JavaScript, evidência dos quatro cenários de validação, comportamento do formulário sem JavaScript e nota sobre o limite de confiança do cliente. Na submissão válida interceptada, explique por que `preventDefault()` é necessário.

**Dicas graduais:** (1) deixe a validação nativa impedir `submit` inválido; (2) só no evento válido, chame `preventDefault()` para manter a pessoa na página; (3) construa `FormData` com controles que tenham `name`; (4) atualize a confirmação com texto e região anunciável.

