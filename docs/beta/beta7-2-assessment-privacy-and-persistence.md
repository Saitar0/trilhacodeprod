# Beta 7.2 — privacidade, persistência e recuperação

Os endpoints de avaliação são exclusivos do servidor de testes isolado. O aluno vê somente estado/feedback da própria entrega; a rubrica e a fila exigem a permissão e o grant por lote do avaliador. Os documentos de avaliação contêm evidências e feedback restritos e não são incluídos em manifesto curricular público, projeção da aula ou logs da rota. A fonte proposta não é devolvida ao aluno.

O serviço grava eventos em `beta7_2_assessments` e versões em `beta7_2_rubrics` dentro do namespace descartável Beta 7.1, já criado pelo harness com verificação de propriedade. A decisão, o CAS da submissão, a revisão do grant e o evento imutável compartilham uma transação MongoDB do replica set. Conflito retorna `409`; o retry com mesma chave e fingerprint retorna o recibo anterior. A validação persistente adicionou uma segunda versão sintética e confirmou que a avaliação anterior continua ligada à versão e ao hash originais.

Limites: a prova depende do MongoDB descartável/replica set e dos grants sintéticos da prévia. Não demonstra integração com IAM global, writers editoriais C8–C16 ou retenção operacional. A reconciliação não recalcula aprovação real porque não existe regra pedagógica aprovada. Histórico anterior permanece armazenado; submissão seguinte referencia a anterior. Não há exclusão de progresso ou tentativas.
