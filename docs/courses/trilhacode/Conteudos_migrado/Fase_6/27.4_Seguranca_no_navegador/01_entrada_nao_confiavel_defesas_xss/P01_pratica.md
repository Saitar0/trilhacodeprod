---
arquivo_id: "f6-27-4-01-entrada-nao-confiavel-defesas-xss-p01-pratica-md"
parent_key: "27.4"
tipo_arquivo: "practice"
assunto: "01_entrada_nao_confiavel_defesas_xss"
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Revisar renderização de comentários (XSS)
**Contexto e objetivo:** encontrar um destino perigoso e escolher correção alinhada ao requisito.

**Código de laboratório em aplicação local descartável:**

```tsx
function Comment({ text }: { text: string }) {
  return <div dangerouslySetInnerHTML={{ __html: text }} />;
}
```

**Instruções:** trate `text` como conteúdo controlável por usuário. Faça revisão da cadeia fonte→destino; defina se produto precisa de texto simples ou HTML formatado. Corrija usando renderização normal de texto ou, se o requisito justificar HTML, um sanitizador mantido e allowlist documentada. Acrescente um teste com entrada contendo marcação e um marcador inofensivo que mostre se foi interpretada como HTML. Execute somente na aplicação local; não use credenciais ou dado real.

**Entrega:** anotação da ameaça, diff/solução, teste antes/depois e limite da defesa escolhida.

**Dica gradual:** pergunte primeiro se a formatação rica é indispensável. Se não, retire `dangerouslySetInnerHTML`; se sim, defina tags/atributos permitidos e sanitize imediatamente antes de inserir.

**Feedback e erro comum:** o teste deve confirmar que conteúdo de texto não vira elemento ativo. Erro comum: substituir alguns caracteres com regex ou confiar que validação do formulário, React em outra parte ou CSP corrige este destino.

