---
arquivo_id: "f6-27-1-90-integracao-kp03-solucao-md"
parent_key: "27.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["02_autenticacao_credenciais", "03_requisicao_vigente_paginacao", "04_cors_erros_integracao"]
ordem: 3
itens_origem: ["P03"]
---

**Solução de referência:** usar exatamente o transporte de credencial definido pela arquitetura, tratar implicações de XSS ou CSRF do mecanismo, armazenar/gerar token conforme política acordada e nunca como segredo no bundle; encaminhar o cursor opaco recebido e parar quando hasMore for falso; configurar CORS no gateway/API para origem e headers reais; 401 segue renovação/logout controlado, 403 não faz login automático, retry limita-se a operação segura e política definida.

