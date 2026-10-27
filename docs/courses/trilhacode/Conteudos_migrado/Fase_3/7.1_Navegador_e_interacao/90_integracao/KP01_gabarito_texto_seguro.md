---
arquivo_id: "f3-7-1-90-integracao-kp01-gabarito-texto-seguro"
parent_key: "7.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_dom_selecao", "02_texto_seguro_dom"]
ordem: 1
itens_origem: ["P1"]
---

**Solução comentada:** o seletor contém erro de digitação e retorna `null`; acessar `resultado.innerHTML` então gera erro. Corrija para `#resultado`, verifique `if (resultado)` e use `resultado.textContent = entrada`. A página exibirá os caracteres `<strong>Olá</strong>` como texto, sem criar um elemento em negrito. Não é necessário sanitizar uma string se a intenção é exibi-la como texto.

**Erro comum:** corrigir o seletor e manter `innerHTML`; isso transforma texto fornecido pela pessoa em marcação interpretável.

