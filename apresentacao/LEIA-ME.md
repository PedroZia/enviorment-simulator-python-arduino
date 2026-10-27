# Apresentação — Como um robô aprende?

## Arquivos finais

- `Apresentacao_Feira_Ciencias.pptx` — versão editável (21 slides, 16:9), com **notas do apresentador em todos os slides**.
- `Apresentacao_Feira_Ciencias.pdf` — backup para apresentar sem PowerPoint.
- `preview_apresentacao.png` — visão geral de todos os slides.
- `Roteiro_Apresentacao.docx` — roteiro completo para imprimir (7 min + versão estendida + perguntas + checklist).
- `Roteiro_Apresentacao.md` — a mesma versão em texto.

## Estrutura

- **Slides 1–17:** apresentação principal para visitantes da feira.
- **Slides 18–21:** apêndice técnico para a banca ou para perguntas mais profundas.
  - 18 · Q-learning por dentro
  - 19 · Se o robô fosse um bicho (analogia)
  - 20 · Arquiteturas
  - 21 · Números do experimento

## Roteiro sugerido (7 minutos)

1. Capa
2. O desafio
3. Regras prontas × aprender fazendo
4. A recompensa
5. Os 8 estados
6. A Q-table
7. A evolução da tabela
8. O ciclo
9. Explorar × confiar
10. O treinamento
11. Resultado
12. Comportamento antes/depois
13. A curva completa
17. Fechamento + demo ao vivo

Deixe os slides 14–16 e o apêndice para perguntas.

## Notas do apresentador

O `.pptx` tem notas em todos os slides, com **tempo, fala e ação de palco**. No PowerPoint, abra `Exibir > Anotações` ou use o **Modo Apresentador** (`Alt + F5`). O roteiro em `.docx` é a versão para imprimir ou deixar no celular.

## Dados usados

- Curva de aprendizado e médias: `history.csv`.
- Q-table final: `snapshots/qtable_ep_0200.txt`.
- Comportamento antes/depois: simulação com a política aleatória e com a Q-table final.

## Identidade visual

- Papel `#F4F1EA`, tinta `#171512`, terracota `#C24E2E`, areia `#E7DCCB`.
- Tipografia: Bahnschrift (títulos), Segoe UI (texto), Georgia (ênfases), Consolas (dados).
- Sem neon, sem gradientes, sem bordas laterais.

## Personalização rápida

- **Nome/escola:** adicione no slide 1, abaixo do subtítulo, ou no rodapé.
- **Fotos do robô:** se quiser incluir uma foto real, o melhor lugar é o slide 2 ou 14; o deck foi desenhado para funcionar sem elas.
- **Edição:** o arquivo `.pptx` é totalmente editável; as cores e fontes estão aplicadas diretamente nos elementos.
