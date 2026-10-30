# Relatório — Etapa 14G

## Escopo e resultado

Foram adicionados componentes React isolados para múltipla escolha, resposta curta, resposta discursiva, associação, ordenação e revisão não pontuada. Eles aceitam apenas projeções públicas tipadas e não foram ligados às rotas curriculares, ao backend, à persistência, à API de quiz ou ao progresso.

A flag independente VITE_TYPED_ACTIVITIES_ENABLED só ativa o renderer quando o valor é exatamente true. Ausente ou qualquer outro valor mantém o recurso desativado. VITE_QUIZ_API_ENABLED não foi alterada.

## Componentes e validação

TypedActivityRenderer.tsx exporta o renderer isolado e seis renderizadores especializados. types.ts define os tipos públicos e valida runtime com allowlist estrita. Campos desconhecidos — incluindo campos privados de resposta e explicação — fazem a atividade ser rejeitada; não são removidos silenciosamente.

fixtures.ts contém exemplos demonstrativos escritos para teste, sem gabaritos reais. As strings são renderizadas como texto React, sem interpretação Markdown ou HTML.

## Segurança e comportamento

A seleção, o texto, as associações e a ordenação existem somente no estado React local enquanto a tela está aberta. Nenhuma correção, nota, aprovação, submissão, armazenamento, chamada de API ou gravação de progresso é executada. A interface informa que o envio não está conectado nesta etapa.

Não há integração com BlockRenderer, QuizBlock, QuizApiSession, NodeReader ou o repositório editorial. O fluxo legado permanece fora do escopo e inalterado por esta etapa.

## Acessibilidade

Foram usados fieldset/legend e radios nativos, labels explícitos, campos nativos, estados role=status/role=alert, foco visível e controles de subir/descer para ordenação. Os controles de associação usam selects acessíveis por teclado. O layout usa largura fluida, quebra de texto e colunas responsivas.

Os testes de DOM e axe-core cobrem semântica e acessibilidade automatizável nos seis tipos. As regras axe que dependem de canvas no jsdom (contraste de cores e detecção de divergência do nome acessível) foram excluídas da análise automatizada; os testes verificam labels, roles e controles nativos diretamente. Isso não substitui revisão com leitor de tela nem validação visual em navegador com diferentes larguras.

## Testes e verificações

Resultados executados nesta revisão:

- Testes focados (renderer e flag): 15 aprovados.
- Suíte frontend completa (Vitest): 71 testes aprovados em 11 arquivos.
- TypeScript: aprovado.
- ESLint: aprovado.
- Build de produção Vite: aprovado.
- git diff --check: aprovado (exit 0); os nove arquivos novos também foram verificados sem espaços em branco no fim das linhas.

A suíte incluiu as regressões existentes do fluxo de quizzes. Não foi necessário E2E: o componente está deliberadamente fora das rotas e não chama serviços.

## Limitações e próxima etapa

Os controles não submetem nem avaliam respostas. Em matching/ordering, se a fonte não fornecer dados públicos estruturados, a interface explica a ausência em vez de inventar itens. O limite de 2.000 caracteres para resposta curta e 10.000 para resposta discursiva é apenas um limite técnico de entrada da demonstração; não é critério pedagógico nem regra de aprovação.

Qualquer integração futura com API, persistência, publicação ou progresso requer autorização e homologação separadas.