# Contrato proposto — conteúdo curricular compartilhado

**Status: proposta; depende de decisão de produto sobre progresso.**

## Estado da fonte

O pacote tem **406 blocos canônicos** com **1.001 colocações**. Cada colocação preserva ID, referência do bloco, assunto consumidor, ordem, proveniência e `progress_scope`. Todas as 1.001 scopes estão atualmente `undecided`; não há política derivável do pacote.

## Modelo lógico

```text
CanonicalContent
  curriculum_ref                 # ID estável do bloco, único
  owner_ref                      # proprietário curricular/autoria
  type + typed_payload           # conteúdo integral e tipado
  source_provenance + source_hash
  content_version + canonical_hash
  visibility / status            # publicado só sob regra autorizada

ContentPlacement
  placement_ref                  # ID estável da colocação
  canonical_content_ref
  subject_ref                    # assunto consumidor
  order                          # posição dentro daquele assunto
  progress_scope                 # undecided até decisão aprovada
  placement_version + provenance
```

Um bloco tem uma identidade e um conteúdo físico canônico. Cada assunto referencia esse bloco por uma colocação. A resposta do tópico inclui as colocações ordenadas no contexto, sem clonar os dados do bloco. Relações do pacote continuam relações curriculares separadas; uma colocação não cria pré-requisito.

## Atualização, remoção e progresso

- Mesmo `curriculum_ref` + mesmo hash: candidato a inalterado após snapshot.
- Mesmo ID + novo hash e destino sem mudança local: candidato a atualização de conteúdo, com versão e auditoria.
- Mesmo ID + divergência local: conflito; não sobrescrever automaticamente.
- Nova colocação: criar referência contextual sem duplicar canonical content.
- Colocação ausente do novo pacote: somente relatório de diferença; não apagar nem desassociar automaticamente.
- Remoção intencional exige instrução explícita, confirmação de impacto, política de progresso e registro reversível. A remoção de uma colocação não remove o conteúdo canônico se outros consumidores ainda o referenciam.
- Alterar o bloco canônico não reinicia progresso silenciosamente. A regra sobre versões de conteúdo/progresso precisa ser aprovada; conservar histórico e versão que o aluno concluiu.
- Integridade referencial exige `canonical_content_ref` existente, `subject_ref` existente, unicidade de `(canonical_content_ref, subject_ref)` quando duplicidade não for uma ocorrência intencional e ordem estável por contexto.

## Políticas de progresso

| Política | Como registra | Benefícios | Custos/riscos |
|---|---|---|---|
| **A. Global por conteúdo canônico** | `(user, canonical_content_ref)` | Uma conclusão em qualquer assunto vale para todos os usos; progresso compacto. | Pode marcar como concluído em outros contextos antes de o aluno estudar a sequência/objetivo local; pré-requisitos/contextos distintos ficam acoplados. |
| **B. Independente por colocação** | `(user, placement_ref)` | Respeita sequência, revisão e contexto de cada assunto; evita desbloqueio cruzado acidental. | O aluno pode repetir conteúdo e cria mais estados de progresso; exige index e migração/UI por contexto. |
| **C. Híbrida por scope** | Por bloco ou colocação conforme `progress_scope` | Permite exceções explícitas por fonte. | Mais complexa; exige que cada scope seja decidido e testado antes de habilitar. Atualmente todas são `undecided`. |

**Recomendação `[PROPOSTA]`: política B, progresso por colocação.** As posições, ordens e associações são contextuais, e uma conclusão global poderia satisfazer indevidamente pré-requisito de outro assunto. A aprovação humana é necessária. A política C pode ser considerada depois, mas nenhuma das 1.001 colocações deve receber scope automaticamente.

## Requisitos de segurança e compatibilidade

- Endpoints e serializers carregam o canonical block por referência e validam acesso a cada assunto/curso.
- Gabaritos, soluções e notas de instrutor não podem ser servidos pelo mesmo payload público de blocos.
- Atualização de uma colocação não pode editar o conteúdo canônico para todos inadvertidamente; alteração de conteúdo pertence à identidade/versionamento canônico.
- Reimportação usa refs curriculares estáveis e hashes; IDs Mongo continuam internos.
- Reexecução não cria nova colocação para o mesmo par nem duplica progresso.
- Progresso existente ligado a `(user,node,block)` requer plano de reconciliação para placement-ref; não migrar ou mesclar registros sem snapshot e decisão.

## Critérios de aceite futuros

Testar uma identidade canônica com múltiplas colocações; ordem distinta por contexto; percurso e progresso independentes; segurança de gabarito; atualização do canonical content; remoção reportada sem delete; conflitos locais; dois usuários; referências órfãs; e ausência de alteração em progresso histórico. Nenhum destes testes ou modelos foi implementado nesta etapa.
