---
arquivo_id: "f6-26-1-02-effects-sincronizacao-limpeza-01-teoria-md"
parent_key: "26.1"
tipo_arquivo: "theory"
assunto: "02_effects_sincronizacao_limpeza"
ordem: 2
itens_origem: ["## Microtópico 2 — useEffect sincroniza um sistema externo"]
---

## Microtópico 2 — useEffect sincroniza um sistema externo

UseEffect coordena um componente com algo que o React não controla diretamente: conexão, assinatura de evento, timer, API imperativa do navegador ou integração externa. Seu código define um ciclo de configuração e, quando necessário, uma limpeza que desfaz a configuração.

```jsx
useEffect(() => {
  const connection = createConnection(roomId);
  connection.connect();

  return () => connection.disconnect();
}, [roomId]);
```

A lista de dependências inclui todos os valores reativos lidos pelo efeito — props, estado e variáveis/funções criadas no componente. Quando uma dependência muda, React executa a limpeza com os valores antigos e depois configura com os novos; ao desmontar, executa a limpeza final. Não silencie o linter para esconder dependência ausente; ajuste o código para que o efeito leia apenas os valores realmente necessários.

Se a lógica não sincroniza com sistema externo, provavelmente não precisa de Effect. Calcular dados derivados pertence à renderização; responder a clique pertence ao handler. Copiar filteredItems para outro estado em um Effect adiciona uma renderização e duas fontes de verdade. Em desenvolvimento, Strict Mode pode executar um ciclo extra de configuração e limpeza para encontrar efeitos sem limpeza adequada; uma sequência configurar → limpar → configurar deve ser segura.

