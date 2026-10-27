---
arquivo_id: "f2-5-4-01-organizacao-manutencao-css-01-teoria"
parent_key: "5.4"
tipo_arquivo: "theory"
assunto: "01_organizacao_manutencao_css"
ordem: 1
itens_origem: ["Organizar CSS para manutenção", "Convenções de nomes e escopo", "Responsabilidade e risco da alteração"]
---

## Teoria

### Organizar CSS para manutenção
CSS sem organização tende a acumular regras duplicadas, seletores globais difíceis de prever e exceções de alta especificidade. Separe estilos por responsabilidade e mantenha estilos relacionados próximos para facilitar localização e revisão.

Agrupe regras globais (tipografia base, cores, reset pequeno) separadamente de componentes e páginas quando isso ajudar a localizar mudanças. Use custom properties para valores repetidos, como cores ou espaçamentos, quando houver benefício real. Remova duplicação com cuidado e verifique quais elementos dependem da regra antes de alterá-la.

### Convenções de nomes e escopo
Use nomes que indiquem a função do componente, como `.card` ou `.nav-link`, e prefira seletores que não dependam de uma cadeia longa de ancestrais. Uma convenção como BEM (`.card__title`, `.card--featured`) pode ajudar a explicitar partes e variações, mas não é obrigatória. O acordo existente do projeto deve prevalecer; documentação e consistência importam mais que escolher uma sigla.

### Responsabilidade e risco da alteração
Uma regra muito ampla, como `div { ... }`, afeta muitos lugares. Uma classe de componente tende a limitar o efeito. Antes de refatorar, identifique os elementos afetados; faça uma mudança por vez e compare a interface nos contextos relevantes. Comentários devem explicar decisões ou restrições, não repetir literalmente o que a propriedade já diz.

