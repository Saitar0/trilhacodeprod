---
arquivo_id: "f4-15-1-02-consistencia-atualizacao-invalidacao-01-teoria"
parent_key: "15.1"
tipo_arquivo: "theory"
assunto: "02_consistencia_atualizacao_invalidacao"
ordem: 2
itens_origem: ["3. Atualização, consistência e concorrência"]
---

### 3. Atualização, consistência e concorrência
Uma estratégia simples ao atualizar um registro é gravar na fonte de verdade e apagar a chave correspondente no cache. A próxima leitura busca o valor atualizado e preenche a chave novamente. Para consultas derivadas, uma alteração pode afetar várias combinações de filtros e páginas; por isso, projete nomes e agrupamentos de chaves para que a invalidação seja viável. Uma janela curta de TTL pode ser aceitável quando os dados toleram atraso, mas essa tolerância deve ser uma decisão do produto, não uma suposição escondida.

Quando uma chave popular expira, várias requisições simultâneas podem consultar a origem ao mesmo tempo (cache stampede). TTL com pequena variação aleatória, atualização antecipada ou coordenação de recomputação são alternativas; cada uma aumenta complexidade e deve ser justificada pelo tráfego medido. Falhas do Redis também exigem comportamento definido: timeout curto, fallback para a origem quando seguro e observação de carga para que a degradação do cache não sobrecarregue o banco. Redis acrescenta uma dependência operacional; não substitui automaticamente um banco durável.

