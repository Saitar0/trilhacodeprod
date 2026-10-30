# Matriz de compatibilidade de atividades — 14E

## Contagens do inventário convertido em memória

| Tipo | Quantidade total | Situação no protótipo | Avaliador atual |
|---|---:|---|---|
| Múltipla escolha | 155 | 143 candidatas válidas; 11 chaves ambíguas; 1 conjunto incompleto | Os 143 candidatos são compatíveis; demais bloqueados |
| Resposta curta | 314 | Enunciados e chaves preservados separadamente; revisão pendente | Não compatível com `option_id` |
| Discursiva | 23 | Enunciados e chaves preservados separadamente; revisão pendente | Não compatível; sem avaliação manual implementada |
| Associação | 4 | Prompts preservados; sem decompor lados ou pares sem prova | Não compatível |
| Ordenação | 4 | Prompts preservados; sem inferir itens ou sequência correta | Não compatível |
| Revisão | 6 | Uma com material de chave somente privado; cinco R1–R5 sem chave | Sem pontuação |
| **Total** | **506** | 501 com gabarito + cinco revisões sem gabarito | 143 candidatos suportados |

## Comparação com a 14D

| Estado da 14D | Quantidade | Tipo 14E | Resultado |
|---|---:|---|---|
| `converted_candidate` | 143 | Múltipla escolha | Preservado; estruturalmente validado, não publicável |
| `blocked_alternatives` | 347 | Curta, discursiva, associação, ordenação, revisão ou MC incompleta | Preservado como tipo específico com diagnóstico |
| `blocked_gabarito` | 11 | Múltipla escolha | Preservado como ambiguidade privada; sem opção resolvida |
| `unscored_review_pending` | 5 | Revisão | R1–R5 preservadas sem chave, nota ou política objetiva |

As 501 classificações e 358 bloqueios permanecem rastreáveis por ID. A classificação por tipo utiliza os sinais estruturais documentados na 14D; `pending_review` indica que esse rótulo não é aprovação editorial.

## Campos e limites

| Campo / capacidade | Compatibilidade | Validação ou limite |
|---|---|---|
| Identidade curricular | Direta no contrato experimental | Reutiliza ID `fN-...`; não cria ObjectId |
| Versão | Parcial / offline | Ref público deriva do SHA da fonte do enunciado; não é ID de versão Mongo |
| Proveniência | Direta | Mantém caminhos, roles, IDs e hashes de fonte |
| Enunciado e instruções | Direta | Texto original preservado em memória; instruções ausentes ficam `null` |
| Alternativas | Direta para as 143 candidatas e MC recuperáveis | Ordem, ID e texto preservados; duplicidades de ID rejeitadas |
| Gabarito e explicação | Privado | Nunca aparecem em `public_payload` ou CSV 14E |
| Resposta curta | Representável | Resposta esperada fica privada; sem avaliação automática |
| Discursiva / rubrica | Representável | Campos de critérios privados existem; vazios quando fonte não fornece critérios |
| Associação / ordenação | Representável, incompleto nos casos atuais | Sem criar pares, listas ou sequência a partir de suposição |
| Revisão | Direta, não pontuada | R1–R5 não recebem gabarito |
| Referências | Contrato tipado disponível | Nenhuma referência estrutural é inventada; texto inline permanece bruto |
| Publicação | Apenas estados descritivos | Nenhum item 14E é `publishable` ou `published` |
| Persistência privada | Não implementada | Depende de aprovação de armazenamento/versionamento e autorização posterior |

## Política aplicada

O contrato objetiva atual é reproduzido somente nos 143 candidatos: três tentativas, 70%, melhor resultado e revisão após a terceira. Não é aplicado a respostas curtas, discursivas, associação, ordenação ou revisão. As perguntas abertas não podem produzir `passed` neste adaptador.

## Evidência e testes

Os testes validam cada tipo, rejeição de tipos desconhecidos, identidade/versão, proveniência e hashes, relações, opções duplicadas, separação pública/privada, compatibilidade dos candidatos com o schema e corretor reais, os 358 bloqueios, R1–R5 e determinismo. As verificações desta etapa não conectam a MongoDB, não publicam e não alteram o JSON.
