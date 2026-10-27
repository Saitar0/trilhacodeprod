---
arquivo_id: "f10-47-1-t04"
parent_key: "47.1"
tipo_arquivo: "theory"
assunto: "04_revisao_e_verificacao"
ordem: 4
itens_origem: ["### 4. Revisar e verificar a alteração"]
---


### 4. Revisar e verificar a alteração
Inspecione o diff inteiro, incluindo arquivos novos, removidos, configuração e dependências. Compare cada mudança com os critérios. Procure alterações não solicitadas, validação fraca, bypass de autenticação/autorização, exposição de dados, tratamento incompleto de erros, teste removido, API inventada ou pacote suspeito. Revise especialmente mudanças que “parecem plausíveis” mas você não consegue explicar.

Escolha evidência independente conforme o risco: teste existente, novo teste de comportamento, análise estática, execução local ou inspeção manual de um contrato. Execute as verificações adequadas antes de integrar e examine o resultado, não só o relato do agente. Testes aprovados aumentam evidência para os casos cobertos; não provam ausência de bugs ou segurança total. Uma revisão automatizada pode sugerir problemas, mas pode também deixar passar falhas ou apontar falsos positivos.

Se a proposta falhar, forneça a evidência concreta e peça uma correção menor. Se a ferramenta propuser apagar um teste para “resolver” falha, alterar requisito sem justificativa ou adicionar dependência não validada, pare e investigue. Registre o que foi aceito, rejeitado e ainda não verificado.

