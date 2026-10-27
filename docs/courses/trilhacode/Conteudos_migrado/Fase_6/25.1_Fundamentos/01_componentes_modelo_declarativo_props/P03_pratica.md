---
arquivo_id: "f6-25-1-01-componentes-modelo-declarativo-props-p03-pratica-md"
parent_key: "25.1"
tipo_arquivo: "practice"
assunto: "01_componentes_modelo_declarativo_props"
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Detecte renderização impura

**Desafio:** um componente incrementa uma variável global para gerar número de cartão e modifica task.title para capitalizar o texto durante a renderização.

**Passos:**
1. Identifique os valores externos que estão sendo modificados.
2. Descreva por que repetir a chamada pode produzir outro resultado.
3. Faça o pai fornecer um número de ordem estável se ele for necessário na interface.
4. Calcule a versão capitalizada em uma variável local sem alterar task, ou faça a transformação antes de passar o dado se isso pertencer ao pai.
5. Compare a saída para as mesmas props em chamadas repetidas e explique por que ela deve permanecer igual.

**Dica:** mutação local de valor criado durante a própria renderização pode ser segura; alterar objeto que veio de fora não é.

