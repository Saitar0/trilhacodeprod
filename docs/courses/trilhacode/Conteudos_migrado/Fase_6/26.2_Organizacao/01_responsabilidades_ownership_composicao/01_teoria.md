---
arquivo_id: "f6-26-2-01-responsabilidades-ownership-composicao-01-teoria-md"
parent_key: "26.2"
tipo_arquivo: "theory"
assunto: "01_responsabilidades_ownership_composicao"
ordem: 1
itens_origem: ["## Microtópico 1 — Organize pelo fluxo e pela responsabilidade", "## Microtópico 2 — Composição e ownership deixam dados explícitos"]
---

## Microtópico 1 — Organize pelo fluxo e pela responsabilidade

Uma árvore React descreve como componentes compõem a interface e trocam dados. Comece perguntando o que cada parte faz: apresentar uma informação, controlar uma interação, coordenar uma tela ou aplicar uma regra reutilizada. Dê nomes a componentes por seu papel no produto e mantenha juntos arquivos que mudam pelo mesmo motivo, conforme o tamanho e as convenções reais do projeto.

Uma divisão comum separa componentes visuais reutilizáveis, componentes de tela que coordenam estado e operações e funções de domínio que implementam regras sem conhecer detalhes visuais. Isso é uma heurística, não uma estrutura obrigatória. Uma aplicação pequena pode ser mais clara com poucos arquivos; uma área grande pode se beneficiar de pastas por funcionalidade. Pasta por componente ou camada só vale se torna navegação e mudanças mais simples.

Evite um componente gigante com muitos modos, várias responsabilidades e contratos difíceis de entender. Também evite fragmentar cada parágrafo em um componente. Extraia quando uma parte tem significado próprio, aparece em mais de um contexto, precisa de comportamento isolado ou mudou por motivos diferentes.

## Microtópico 2 — Composição e ownership deixam dados explícitos

Props são a forma explícita de o pai passar informação e funções ao filho. Se uma propriedade só atravessa um ou dois níveis e continua fazendo parte do contrato, passá-la é frequentemente mais simples do que introduzir Context.

Composição permite ao componente contêiner receber conteúdo por children. Assim, um componente de layout pode cuidar de borda e espaçamento sem conhecer o conteúdo interno. Use slots com props específicas quando o componente precisa organizar regiões como header, actions ou sidebar.

Se dois componentes precisam coordenar o mesmo valor, mantenha uma única fonte de verdade. Remova estado duplicado dos filhos, mova-o ao ancestral comum mais próximo e passe valor e callbacks por props. Não mova todo estado para o topo da aplicação: estado de um campo ou painel pode continuar próximo de quem o usa.

```jsx
function Panel({ title, children }) {
  return (
    <section className="panel">
      <h2>{title}</h2>
      {children}
    </section>
  );
}

<Panel title="Preferências">
  <ThemePicker />
</Panel>
```

O Panel conhece a estrutura compartilhada, enquanto ThemePicker fornece o conteúdo. Essa composição pode evitar passar props por um componente intermediário que não usa os dados.

