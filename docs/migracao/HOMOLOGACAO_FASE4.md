# Homologação da migração estrutural — Fase 4

## Resultado

**APROVADA COM RESSALVAS**

- Commit-base utilizado: `1598dc47eefcb30e40a033870f164eebd79deb93`.
- Branch de trabalho: `migracao-estrutura`.
- Inventário: 17 unidades ativas, 49 assuntos de conteúdo e dois projetos.
- Saída: 395 arquivos e 635 registros de mapeamento.
- Conteúdo, exemplos, comandos, respostas existentes, atividades, rubricas, escalas e metadados foram preservados conforme as regras estruturais aprovadas.
- As Fases 1–3 (678 arquivos), fontes originais, documentos da fase, guia de projetos e JSON permaneceram byte a byte inalterados. O importador não foi executado.

## Validação dos links de 16.3

Os dois links relativos ao `Guia_Projetos_e_Rotacao_de_Tipos.md` tinham destino existente e inequívoco no repositório. Foram corrigidos somente os caminhos `href`, preservando os rótulos visíveis e o restante do texto:

| Arquivo migrado | Linha | Caminho anterior | Caminho corrigido | Destino |
|---|---:|---|---|---|
| `16.3_Projeto_de_fase_Trilho_B/01_projeto_trilho_b/00_escopo.md` | 11 | `../../Guia_Projetos_e_Rotacao_de_Tipos.md` | `../../../../Guia_Projetos_e_Rotacao_de_Tipos.md` | `docs/courses/trilhacode/Guia_Projetos_e_Rotacao_de_Tipos.md` |
| `16.3_Projeto_de_fase_Trilho_B/04_referencias.md` | 10 | `../../Guia_Projetos_e_Rotacao_de_Tipos.md` | `../../../Guia_Projetos_e_Rotacao_de_Tipos.md` | `docs/courses/trilhacode/Guia_Projetos_e_Rotacao_de_Tipos.md` |

Os dois caminhos corrigidos resolvem. A transformação está declarada em `mapa_de_migracao_fase4.yml`, reproduzida pelo gerador e registrada nos relatórios e no CSV. Os hashes e intervalos do CSV continuam correspondendo literalmente às fontes; a alteração de `href` é uma normalização estrutural autorizada, não uma divergência textual.

## Ressalvas remanescentes

- Dois wikilinks Obsidian dependem da raiz do vault e permanecem sem validação fora desse contexto.
- Nenhuma outra ressalva de link relativo permanece na Fase 4.

## Evidências

- `relatorio_mapeamento_fase4.csv`: 635 mapeamentos com origem, destino, intervalos, hashes e identificação das duas normalizações autorizadas.
- `relatorio_validacao_fase4.md`: contagens por tipo e unidade, conversão dos metadados e resultados da validação.
- `auditoria_final_fase4.md`: reconstrução textual, projetos, rubricas, links e arquivos protegidos.
- `python docs/migracao/_migrar_fase4.py --repair-links-dry-run`: reconstrução determinística e verificação sem escrita aprovadas após a correção.
- Nenhum commit foi criado durante a migração; esta homologação acompanha o commit exclusivo da Fase 4 autorizado pelo responsável.
