---
arquivo_id: "f9-44-2-01-resumo"
parent_key: "44.2"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---


## Resumo
- WebForms renderiza páginas no servidor e usa controles com eventos, postback e ciclo de vida.
- `Page_Load` pode rodar em toda requisição; `IsPostBack` distingue carga inicial de postback.
- ViewState carrega estado com a página e pode aumentar o payload; não é lugar para segredos.
- ASP.NET Core tem modelo e pipeline distintos; modernização pode acontecer por partes e exige estratégia de coexistência/reversão.
- Verifique .NET Framework, Windows, bibliotecas e controles antes de avaliar suporte e prazo de migração.

