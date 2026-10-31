# Beta 1 — compatibilidade curso-plataforma

## Dois caminhos de atividade na plataforma

C16 tem blocos genéricos e avaliação versionada. O `quiz` genérico sem atividade publicada mostra alternativas e declara que não tem avaliação publicada. Um `quiz` elegível publicado gera definição imutável; `MultipleChoiceActivity` usa tentativas persistidas e o servidor avalia. O bundle C16 não contém bloco quiz: tem apenas teoria, resumo e nota do instrutor, tudo draft. Logo, capacidade da plataforma não significa que o curso revisado esteja importado ou interativo.

| Conteúdo pedagógico | Representação C16 | UI/backend/persistência | Compatibilidade e transformação |
|---|---|---|---|
| Teoria | `theory_text` + Markdown | Markdown renderer; conteúdo editorial | Compatível estruturalmente; publicar só após revisão |
| Resumo | `summary` | Markdown renderer | Compatível |
| Quiz textual | Texto/arquivos separados no pacote segmentado | `QuizBlock` estático não corrige nem salva resposta | Converter perguntas/gabarito explicitamente para atividade, sem automatizar pergunta aberta |
| Quiz objetivo | `activity_publications` por versão | Tentativa do aluno vinculada à publicação; avaliação server-side | Funcionalidade existe; bundle não a fornece |
| Exercício aberto | `exercise_open` / `practical_challenge` ou Markdown | Renderer + `/submissions`; correção manual | Mapear prompt, entregável, rubrica e feedback |
| Programação | Bloco de código copia snippet | Sem editor/execução/sandbox de produto | Não prometer correção automática |
| Miniprojeto/projeto | Markdown, entregas/rubrica | Sem fluxo de projeto específico visto; submission genérica | Decidir artefato, checkpoints, critério e avaliação |
| Conclusão/domínio | Texto/critério do curso | API de progresso registra status por nó/bloco | Critério curricular precisa ser mapeado, não inferido de texto |
| Gabarito | Arquivo/segmento privado no trabalho migratório | Não é bloco de aluno comum | ACL separada; não publicar resposta correta prematuramente |
| Rubrica/feedback | Tabelas/textos | Correção manual e feedback de quiz têm formatos específicos | Transformação explícita necessária |
| Referências/mídia | Links e Markdown | Renderer suporta link/video types | Conferir link, licença, disponibilidade e uso de terceiros |
| Flashcard/checklist | Estrutura proposta/marcador | Renderer simples para tipos correspondentes | Não substitui progresso ou avaliação sem contrato |

## Contrato de importação

`POST /api/import/track` C16 usa `track/options/nodes/relations`, flag `dry_run` default `true` e o serviço `run_import`. O bundle C16 acompanha esse formato legacy. O bundle `phases[].contract` na worktree migratória contém conteúdo tipado e diagnósticos e registra fail-closed do endpoint legacy para essa versão. Não há evidência de que C16 importe esse contrato. Nada foi importado/testado contra Mongo nesta auditoria.

## Conversões exigidas antes do aluno

1. Escolher origem canônica e conservar IDs/rastreabilidade.
2. Mapear Markdown → fases/módulos/unidades/blocos em ordem, com diff de perda.
3. Converter quiz objetivo só se há chave/gabarito aprovados; guardar resposta privada e publicar feedback permitido.
4. Representar exercícios abertos como submissions humanas, com rubrica e critério claro.
5. Definir conclusão, pré-requisitos, tempo estimado, mídia e referências.
6. Resolver links e warnings/pendências; garantir exposição segura de gabaritos.
7. Validar bundle offline, dry-run em banco descartável numa fase autorizada e fluxo de aluno em E2E.

Uma unidade só será “funcional” quando ID/rastreio, conteúdo importado, renderer, resposta/feedback, progresso e teste de jornada se referirem à mesma unidade. Markdown, JSON válido ou componente isolado não bastam.
