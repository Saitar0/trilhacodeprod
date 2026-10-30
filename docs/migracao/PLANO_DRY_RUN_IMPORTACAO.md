# Plano de dry-run para importação curricular versionada

## Finalidade

O leitor/planejador `backend/curriculum_contract/import_adapter.py` valida `trilhacode.import_bundle/1.0` e produz uma proposta determinística sem executar operações. Esta etapa não acessa MongoDB, não executa o importador legado, não publica conteúdo, não modifica progresso e não exclui registros.

O pacote atual está em `docs/courses/trilhacode/trilha-code-bulk-import.json`, SHA-256 `43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2`. O relatório produzido nesta execução está em [DRY_RUN_IMPORTACAO_14A.json](DRY_RUN_IMPORTACAO_14A.json).

## Reprodução segura

Execute a partir de `backend/`, em ambiente Python que contenha as dependências existentes:

```powershell
$env:PYTHONPATH = '.'
python -m curriculum_contract.import_adapter --repo-root .. --bundle docs/courses/trilhacode/trilha-code-bulk-import.json
```

O comando valida e imprime o plano; não grava arquivo. Para guardar um relatório, use `--output` com um caminho novo e exclusivo. O programa abre esse caminho em modo de criação exclusiva e recusa sobrescrever arquivo existente. A saída deve permanecer fora de `Conteudos_migrado/` e fora do JSON de importação.

O planejador não aceita URI MongoDB nem constrói cliente de banco. Não passe snapshots extraídos de produção. Uma futura comparação exigirá etapa separada, autorização explícita, origem sanitizada e somente leitura.

## Validação executada nesta etapa

1. Rejeitar JSON inválido, UTF-8 inválido, chaves JSON duplicadas e versões não suportadas.
2. Validar o schema Pydantic do bundle e os contratos de cada fase.
3. Validar IDs globais, hierarquia, relações, projetos, gabaritos e colocações.
4. Verificar paths seguros e hashes dos 2.889 arquivos de origem mapeados.
5. Conferir os 12 sidecars do manifesto de integridade e o índice estrutural.
6. Reconciliar as 4.311 linhas dos relatórios de fase, os 2.879 destinos físicos únicos, duas sentinelas de remoção aprovadas, 2.890 arquivos migrados e 11 arquivos estruturais.
7. Produzir operação determinística por entidade e por status; não inferir estado persistente.
8. Incluir dependências e uma sequência conceitual não executável: track, nós hierárquicos, blocos compatíveis, quizzes/gabaritos em grupo privado, relações/colocações, projetos e pendências editoriais.

## Estados do plano

- `create`, `update`, `unchanged`, `conflict`: possíveis somente com snapshot explícito e válido. Nenhum foi atribuído nesta execução.
- `pending_database_snapshot`: suporte alvo potencialmente compatível, mas o estado atual não foi lido.
- `blocked`: falta suporte semântico/seguro comprovado.
- `pending_decision`: falta decisão editorial/de produto ou destino aprovado.

A ordem conceitual não é um roteiro autorizativo para escrita. A execução dependeria de uma etapa própria, aprovada, com transação/compensação, índices, limites de lote, relatório de alterações e política de conflitos.

## Resultado quantitativo desta execução

- 10 fases, 572 nós, 3.431 blocos, 15 projetos, 1.001 colocações, 55 relações e 214 pendências editoriais.
- 5.344 entidades identificadas e classificadas.
- `pending_database_snapshot`: 2.063.
- `blocked`: 3.016.
- `pending_decision`: 265.
- Criação/atualização/inalterado/conflito afirmados: zero.
- Exclusões propostas: zero.
- Acesso ao banco/escritas/migrações/publicações/progresso: nenhum.

## Dependências e ordem conceitual

1. Track: identidade estável e comparação com estado atual.
2. Hierarquia: phase → module → submodule → topic, respeitando pais e ordem.
3. Blocos compatíveis: somente após os nós proprietários.
4. Quiz e chave privada: formar versão imutável e publicar em grupo; bloqueado até compatibilizar formatos e correção.
5. Relações e colocações: após nós/blocos referenciados e decisões de semântica/progresso.
6. Projetos e componentes: após nó do projeto e suporte a entregas/aceites/checklists/rubricas.
7. Pendências editoriais e artefatos estruturais: conservar como dados de auditoria, nunca como conteúdo visível ao aluno sem regra própria.

As dependências por entidade constam em `operations_detail`; a ordem acima é explicativa e não executável. Entidades `blocked`/`pending_decision` impedem sua etapa dependente.

## Comparação de estado futura

O utilitário puro `classify_snapshot_state` aplica a regra:

| Estado observado | Classificação proposta |
|---|---|
| Referência ausente | `create` |
| Hash atual igual ao desejado | `unchanged` |
| Hash atual difere, mas coincide com o último importado | `update` |
| Hash atual diverge do último importado | `conflict` |

Registros existentes ausentes do pacote são reportados como snapshot-only; nunca geram delete. A função depende de snapshot explicitamente fornecido e não confirma que ele é autêntico ou atualizado.

## Bloqueios para uma importação futura

1. Definir um registro/índice único de identidade curricular e resolver IDs MongoDB sem depender da ordem.
2. Estender o destino para compartilhamento canônico e colocações contextuais, preservando política de progresso pendente.
3. Modelar projetos, entregas, marcos formais, critérios, checklists, rubricas e opções de variação.
4. Definir suporte seguro aos formatos textuais existentes dos 501 quizzes avaliáveis; não reduzir para múltipla escolha nem publicar gabaritos.
5. Decidir o tratamento das cinco questões sem gabarito.
6. Definir `prerequisite_kind` para relações enforced somente com evidência curricular; as 35 relações atuais ficam sem inferência.
7. Definir destino/retensão para referências pendentes, Wikilinks, notas do instrutor e artefato estrutural.
8. Homologar extensão versionada do importador, rollback/compensação e testes em Mongo efêmero representativo.

Nenhum item acima é resolvido pela existência do plano. A atual rota `/api/import/track` rejeita payloads com `schema_version` e o dry-run legado consulta o banco; não deve ser usado para validar este pacote.
