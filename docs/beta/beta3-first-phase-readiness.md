# Beta 3 — prontidão para converter a primeira fase

## Base de planejamento herdada

O plano Beta 2 descreve 10 unidades da Fase 1, 29 tópicos, 263 blocos e 21 relações no pacote daquela análise. Declara ainda 44 quizzes/gabaritos, 26 práticas, 10 rubricas, 14 checklists, 10 feedbacks, 10 objetivos, 10 resumos, 10 critérios de conclusão, 30 teorias, 39 referências e 95 placements. Esses números derivam de artefatos tipados locais da migração, alguns modificados/dirty; devem ser reconciliados contra uma fonte congelada antes de geração. Não são totais aprovados para importação.

Unidades listadas: 1.1 Computação e software; 1.2 Ambiente de desenvolvimento; 2.1 Terminal e navegação; 2.2 Sistema e operação; 2.3 Acesso remoto; 3.1 Git local; 3.2 Trabalho com histórico; 3.3 GitHub; 3.4 Revisita contínua; 3.5 Projeto incremental.

Beta 3 validou apenas uma cópia rastreável da unidade 1.1 no adaptador e no serviço de importação C16. Não converteu nenhuma unidade adicional nem fase completa.

## Trabalho necessário antes da Fase 1

1. Ratificar e congelar commit/arquivos da fonte segmentada, resolver arquivos locais dirty com seus autores e registrar hashes por arquivo/unidade.
2. Definir contrato de árvore fase→módulo→unidade→tópico, incluindo tópico como nó ou relação explícita, e validar IDs e ordem.
3. Comparar origem e payload em todos os campos; materializar avisos e perdas em manifestos, sem destinos arbitrários.
4. Resolver soluções, rubricas, checklists, feedback de gabarito e critérios privados com ACL explícita. Não armazená-los no bloco comum `exercise_open` sem proteção comprovada.
5. Definir a semântica de conclusão por unidade sem converter envio em domínio e sem inventar nota mínima.
6. Resolver 21 relações/refs e testar alvos, ciclos, links e conceitos complementares; decidir destino para 95 placements e progresso compartilhado.
7. Criar conversão determinística fase-wide e teste de round-trip/comparação de hashes, contagens, refs e arquivos não mapeados.
8. Selecionar staging/recuperação e promoção versionada; `run_import` é multi-etapa, não atômico. Aplicar autoridade C8–C16 e conter writers concorrentes antes de integração.
9. Validar quiz versionado, submissão manual, tentativas, feedback, progresso e projeções públicas por serviço/rota/frontend sem publicação antecipada.
10. Testar importação de fase repetida, falha em cada fronteira, concorrência, auditoria, read model e reconciliação em ambiente descartável.
11. Obter revisão pedagógica para critérios de conclusão e aprovação de publicação; manter a origem em draft/private até então.

## Bloqueios atuais

O gabarito de quiz está presente no documento draft e a leitura de estudante foi negada para a trilha privada. A privacidade em publicação via rota e frontend não foi validada. Respostas e critérios de exercício não são persistidos por não haver ACL segura. O backend não armazena descrições de referências, critério de conclusão ou conexões não resolvidas. A política editorial ainda não contém globalmente os escritores que possuem acesso direto ao MongoDB. O importador C16 não transaciona todo o job.

Consequentemente, a fase completa não está pronta para importação operacional. Próxima ação técnica recomendada: congelar fonte/manifesto de uma unidade completa e especificar um adaptador de conteúdo restrito + staging/promote com testes de segurança; requer aprovação humana e autorização operacional futura.
