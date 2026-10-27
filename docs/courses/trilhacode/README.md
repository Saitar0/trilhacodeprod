# Curso Trilha Code — pacote atualizado

Este pacote acompanha o roadmap atualizado de 10 fases, com 53 módulos e 131 unidades detalhadas em `Conteudos/`. Os arquivos de fase apresentam objetivos, sequência, competências e projetos; os arquivos em `Conteudos/` guardam o material completo de cada unidade.

## Carga horária

`estimated_minutes` corresponde a uma estimativa aproximada de **tempo de estudo ativo** da unidade, incluindo leitura/estudo, prática, tentativa e erro, depuração, correção e revisão quando previstos. Não representa a duração de vídeo. A soma das 131 referências é 26.190 minutos (436,5 horas); a estimativa editorial permanece em faixa de 313–560 horas, conforme opções de projeto e ritmo de cada estudante.

## Importação

O arquivo `trilha-code-bulk-import.json` segue o contrato de `/api/import/track`: fases, módulos e unidades, metadados pedagógicos, conteúdo Markdown em blocos `theory_text`, durações em minutos e pré-requisitos. Foram reaproveitadas as referências estáveis do pacote anterior para os itens com correspondência temática, reduzindo a criação de duplicatas.

Antes de confirmar a importação na plataforma, use a simulação e confira os totais de criação/atualização, pré-requisitos e avisos de tags. A importação não remove automaticamente relações antigas; compare o relatório da simulação com o estado atual da trilha.
