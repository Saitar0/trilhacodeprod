---
arquivo_id: "f9-40-2-03-offsets-retencao-replay-01-teoria"
parent_key: "40.2"
tipo_arquivo: "theory"
assunto: "03_offsets_retencao_replay"
ordem: 3
itens_origem: ["### Microtópico 3 — Usar offsets, retenção e replay corretamente"]
---


### Microtópico 3 — Usar offsets, retenção e replay corretamente

O consumer acompanha a posição de leitura por partição. O **offset commitado** registra o progresso que o grupo pode usar ao retomar o consumo. Ele não confirma automaticamente que uma gravação num banco externo foi concluída. Se a aplicação confirmar o offset antes do efeito externo e falhar, pode pular trabalho; se concluir o efeito e falhar antes do commit, pode repetir o registro depois. Idempotência no destino ou uma coordenação transacional apropriada é necessária para evitar efeitos duplicados.

Kafka não apaga um registro simplesmente porque um consumer o leu ou commitou o offset. A política do tópico controla por quanto tempo ou quanto espaço os segmentos podem permanecer, independentemente do progresso de cada consumer. Um consumer pode voltar a uma posição anterior e reproduzir registros enquanto ainda estiverem disponíveis. Se ficar para trás além da janela de retenção, registros antigos podem deixar de estar disponíveis para replay.

Há também tópicos configurados para **compactação por chave**, que preserva o valor mais recente conhecido de cada chave após o processo de compactação, em vez de servir como histórico completo de cada alteração. Compactação e retenção por tempo/tamanho atendem a necessidades diferentes; escolha e configure conforme o tipo de replay esperado.

