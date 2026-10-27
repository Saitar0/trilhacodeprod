---
arquivo_id: "f6-26-1-04-memoizacao-decisao-por-evidencia-01-teoria-md"
parent_key: "26.1"
tipo_arquivo: "theory"
assunto: "04_memoizacao_decisao_por_evidencia"
ordem: 4
itens_origem: ["## Microtópico 4 — useMemo e useCallback otimizam valores diferentes", "## Microtópico 5 — Escolha pelo problema e confira o ciclo"]
---

## Microtópico 4 — useMemo e useCallback otimizam valores diferentes

useMemo guarda o resultado de uma função de cálculo enquanto suas dependências permanecem iguais. Pode evitar repetir um cálculo comprovadamente caro ou manter identidade de um objeto quando isso habilita uma otimização. A função é executada durante renderização quando necessário; por isso o cálculo deve ser puro.

useCallback guarda a própria função para manter sua identidade entre renderizações até uma dependência mudar. Não chama a função armazenada. Pode ajudar quando a função é prop para um componente memoizado ou é dependência de outro Hook; não é necessário para todo handler.

```jsx
const visibleItems = useMemo(
  () => filterItems(items, filter),
  [items, filter]
);

const handleSelect = useCallback((id) => {
  onSelect(id);
}, [onSelect]);
```

Ambos recebem todas as dependências reativas usadas pela função. Omitir uma dependência pode congelar um valor antigo e criar defeitos sutis. Memoização é uma otimização, não uma condição de correção: se retirar useMemo ou useCallback muda o resultado do programa, procure o erro de lógica.

O React Compiler, quando instalado e habilitado no projeto, pode automatizar várias memoizações. Não presuma que existe só porque o código usa React. Verifique configuração e medição antes de escrever otimizações manuais; elas podem reduzir re-renderizações em alguns casos, mas também aumentam a quantidade de conceitos e dependências que a equipe mantém.

## Microtópico 5 — Escolha pelo problema e confira o ciclo

Antes de adicionar um Hook, formule o problema:
- Preciso manter um valor que muda a interface? Estado.
- Preciso sincronizar conexão, assinatura ou outra API externa? Effect, com dependências e limpeza.
- Preciso acessar um nó DOM ou guardar informação imperativa que não desenha a UI? Ref.
- Preciso evitar um cálculo ou identidade referencial comprovadamente custosos? Avalie memoização e meça.
- Preciso compartilhar lógica com estado entre componentes? Custom Hook; lembre que cada chamada possui sua própria instância de estado.

Para um Effect, trace setup, valores reativos, situação que dispara nova configuração e limpeza. Para memoização, observe o perfil antes/depois e confirme que as dependências incluem as entradas. Para ref, confirme que mudar current não deveria ser motivo para atualizar a tela. Essa análise evita usar um Hook conhecido por hábito, em vez de resolver uma necessidade.

