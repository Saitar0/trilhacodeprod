---
arquivo_id: "f6-27-4-01-resumo-md"
parent_key: "27.4"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- Trace fonte, transformações e destino para localizar risco de XSS.
- Renderização de texto é preferível a HTML bruto; HTML rico exige sanitização apropriada.
- CSP reduz impacto, mas não substitui correção da injeção.
- Cookies e tokens têm riscos diferentes; escolha defesa CSRF conforme a arquitetura.
- CORS não é autenticação; segredos do servidor não pertencem ao bundle cliente.
- Auditoria de dependências encontra avisos conhecidos, não certifica segurança.

