---
title: "Guia de produção de conteúdo"
aliases:
  - Guia de produção
tags:
  - trilhas
  - producao-de-conteudo
tipo: guia
status: planejamento
---

# Guia de produção de conteúdo

Este guia define o padrão editorial para novas unidades e revisões da Trilha Code. O conteúdo deve ajudar a pessoa a explicar e aplicar uma competência observável, com profundidade proporcional à classificação indicada.

## 1. Estrutura de uma unidade

Cada arquivo de `Conteudos/Fase_N` representa uma unidade com chave estável (`key`) e deve conter, quando aplicável:

1. **Objetivo:** descreva o que a pessoa fará ou explicará ao concluir. Prefira verbos observáveis, como implementar, comparar, diagnosticar ou justificar.
2. **Teoria:** explique os conceitos em sequência, defina termos novos, use exemplos pequenos e indique limites, riscos e trade-offs relevantes.
3. **Resumo:** sintetize as ideias que a pessoa deve conseguir recuperar sem reler a unidade inteira.
4. **Verificação:** use perguntas com resposta explicada para corrigir equívocos, sem substituir a prática quando a competência exige execução.
5. **Prática:** proponha uma tarefa delimitada com entregável, evidência e orientação de revisão.
6. **Critério de conclusão:** descreva evidências suficientes para decidir se o objetivo foi atingido.
7. **Conexões:** relacione pré-requisitos, revisitas e aplicações posteriores por referências existentes.
8. **Referências:** inclua fontes primárias adequadas, URL direta e data de consulta.

Não force seções que não acrescentem valor. Projetos podem usar etapas, critérios de aceite, evidências e rubrica. Unidades de repertório podem ser curtas, mas ainda precisam deixar claro o que a pessoa deve saber reconhecer ou comparar.

## 2. Objetivos, prática e avaliação

- Alinhe objetivo, explicação, atividade e critério de conclusão: todos devem avaliar a mesma competência.
- Transforme atividades vagas em instruções reproduzíveis. Declare pré-requisitos, dados de exemplo, ambiente esperado, resultado e como inspecioná-lo.
- Prefira dados sintéticos ou públicos autorizados. Não solicite credenciais, dados pessoais reais ou exposição de serviços sem necessidade.
- Em tarefas técnicas, peça evidência adequada: teste, saída observável, medição, diagrama ou cenário reproduzível.
- Diferencie resposta conceitual de demonstração prática. Uma pessoa pode explicar um conceito sem ter provado que o implementou.
- Para avaliação automática, escreva opções sem ambiguidade, resposta correta e explicação. Para avaliação aberta, declare critérios observáveis e limites da rubrica.
- Não apresente uma ferramenta, biblioteca ou arquitetura como obrigatória quando o objetivo pode ser demonstrado de outra forma. Identifique repertório, alternativas e dependências de versão.

## 3. Taxonomia de tags (vocabulário controlado)

Use no máximo duas tags por unidade, escolhidas deste vocabulário:

`fundamentos`, `web`, `dados`, `seguranca`, `arquitetura`, `infra`, `ferramentas`, `qualidade`, `ia`, `mercado`, `projeto`.

As tags agrupam assuntos transversais. Elas não substituem fase, tipo pedagógico, caráter, profundidade nem relações entre unidades. Não crie uma nova tag sem atualizar este guia e conferir o uso no pacote.

### Classificação editorial

- **Tipo pedagógico:** `solo`, `integrado`, `revisita`, `pratica` ou `projeto`.
- **Caráter:** `obrigatorio`, `repertorio` ou `opcional`.
- **Profundidade:** `alta`, `media` ou `repertorio`.

O caráter expressa prioridade curricular; a profundidade expressa domínio esperado. Um tópico obrigatório pode ter profundidade média. Use repertório para familiarização e comparação, sem cobrar domínio de produção.

## 4. Carga horária

Registre `estimativa_minutos` como tempo aproximado de estudo ativo para atingir o critério, incluindo leitura, prática, tentativa e erro, depuração e revisão previstos. Não use duração de vídeo. Projetos devem ter faixa e premissas próprias, compatíveis com o escopo mínimo descrito. Atualize `Estimativa_de_Carga_Horaria.md` quando uma mudança afetar os totais.

## 5. Referências e conteúdo sujeito a mudança

- Prefira documentação oficial, especificações, livros técnicos reconhecidos e artigos de pesquisa diretamente relacionados ao objetivo.
- Use fontes secundárias para complementar, não para sustentar sozinhas afirmações técnicas importantes.
- Registre o que a fonte cobre e a data de consulta. Para APIs, preços, versões, políticas de serviço e práticas que mudam, revalide antes de publicar.
- Evite reproduzir documentação extensa. Explique com palavras próprias e faça links para a fonte.
- Confira exemplos, comandos e versões. Marque claramente o que é ilustrativo e o que foi executado.

## 6. Arquivos e importação

- Preserve as chaves estáveis das unidades já importadas; não reutilize uma chave para outro assunto.
- Mantenha uma unidade canônica por chave em `Conteudos/Fase_N`. Conteúdo histórico deve ficar fora das pastas ativas e sem chave importável.
- Ao alterar conteúdo, atualize o arquivo da unidade e o JSON `trilha-code-bulk-import.json` de forma consistente.
- Confira contagem de fases, módulos e unidades, durações, tags e relações. Verifique se os destinos de pré-requisitos existem e se não há referências duplicadas ou ciclos.
- Faça uma simulação de importação e revise totais de criação/atualização, pré-requisitos e avisos antes de confirmar.
- Mantenha a visibilidade privada enquanto o material estiver em rascunho. Só mude para público após revisão editorial, verificação das referências e decisão explícita de lançamento.

## 7. Revisão editorial

Antes de considerar uma unidade pronta, confirme:

- [ ] O objetivo é compreensível e verificável.
- [ ] A explicação define termos e não depende de conhecimento que ainda não foi ensinado.
- [ ] A atividade cabe no nível e tempo estimados.
- [ ] O critério de conclusão corresponde às evidências pedidas.
- [ ] As instruções evitam segredos, dados reais desnecessários e operações em ambientes não autorizados.
- [ ] Links, versões, comandos e referências foram conferidos.
- [ ] As relações curriculares e a representação no JSON estão atualizadas.
