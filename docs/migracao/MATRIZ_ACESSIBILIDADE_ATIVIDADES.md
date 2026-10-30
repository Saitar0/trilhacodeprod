# Matriz de acessibilidade — atividades tipadas

| Tipo | Semântica e teclado | Feedback e foco | Risco/limite |
|---|---|---|---|
| Múltipla escolha | fieldset, legend, radios e labels nativos; navegação padrão por teclado | Estado neutro em role=status, sem indicar correção | Navegação real deve ser confirmada em navegadores e leitor de tela |
| Resposta curta | Label associado a input; limite e contador textual | aria-invalid e mensagem de validação quando vazio após interação | Limite técnico de 2.000 caracteres, sem significado pedagógico |
| Discursiva | Label associado a textarea; edição por teclado | Contador e estado neutro; limite técnico de 10.000 caracteres | Não há salvamento ou avaliação |
| Associação | Label por item e select nativo, operável por teclado | Mensagem neutra após seleção | Itens ausentes permanecem indisponíveis; nenhum par é inferido |
| Ordenação | Botões nomeados para mover itens para cima/baixo; não depende de arrastar | Limites desabilitados para primeiro/último item | Sem correção ou persistência |
| Revisão | Texto estático com indicação de atividade sem pontuação | Mensagem em região de status | Não exige nem expõe gabarito |

## Critérios transversais

- Foco visível nos controles interativos.
- Texto quebra em telas estreitas; contêiner usa largura fluida sem dimensão fixa.
- Erros usam role=alert; estados informativos usam role=status.
- HTML fornecido como conteúdo é mostrado literalmente, nunca executado.
- O teste axe-core percorre os seis tipos; as regras dependentes de canvas do jsdom (contraste e nome acessível incompatível) são verificadas parcialmente por inspeção de labels e ficam fora do resultado automatizado.

A suíte jsdom não mede layout real em viewport nem comprova compatibilidade completa com tecnologias assistivas. Revisão manual e teste em navegador permanecem recomendados antes de qualquer integração.