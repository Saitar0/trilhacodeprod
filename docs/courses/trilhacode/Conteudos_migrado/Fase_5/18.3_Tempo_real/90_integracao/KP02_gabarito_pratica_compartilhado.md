---
arquivo_id: "f5-18-3-90-integracao-kp02-gabarito-pratica-compartilhado"
parent_key: "18.3"
tipo_arquivo: "answer_key_pratica"
assuntos: ["03_seguranca_de_canais", "04_estado_compartilhado_e_concorrencia"]
ordem: 2
itens_origem: ["P2"]
---

**Solução de referência:** o cliente autorizado conecta/assina o recurso depois da verificação; ao alterar o estado, o serviço valida a entrada, grava a nova versão e publica evento com ID/versão; ambos os clientes recebem a atualização. A identidade sem acesso não recebe estado e não consegue publicar mudança. A persistência/serviço de domínio segue como fonte autoritativa.

