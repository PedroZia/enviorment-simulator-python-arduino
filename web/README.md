# Simulador de Linha — site

Gerador dos 8 estados dos sensores para o robô seguidor de linha. É um site
estático, sem build e sem dependências de npm: o site em si é só `index.html`,
`styles.css` e `app.js`.

A tipografia usa Bricolage Grotesque e Instrument Sans via Google Fonts. Sem
rede, o navegador cai no fallback do sistema e o site continua funcionando.

## Interface

- A pista branca fica ancorada na parte de baixo da tela. No desktop ela fica
  visível enquanto você rola o conteúdo; no celular ela aparece no fim da
  página.
- Os **oito estados** ficam no topo, em uma matriz clicável. O estado ativo
  aparece em vermelho.
- **Ajustar valores** abre o painel de ajustes logo acima da pista. É ali que
  ficam os três sensores com todos os campos numéricos.
- **Arraste** um retângulo na pista para mover; use a alça vermelha no canto
  para redimensionar. Os campos do painel acompanham o movimento.
- O painel pode ficar aberto enquanto você olha a pista. Feche por **Fechar**,
  `Esc` ou pelo próprio botão **Ajustar valores**.
- **Centralizar** reposiciona o conjunto no palco. **Restaurar** volta todos os
  valores ao padrão (disponível no cabeçalho e dentro do painel).

## Modos

- **Manual:** clique nos estados `000` a `111` ou use as teclas `0` a `7`. No
  painel, cada sensor também pode ser invertido individualmente entre preto e
  branco.
- **Piscar:** cada retângulo pisca no seu próprio período e fase. O botão
  **Pausar/Continuar** (ou `Espaço`) congela e retoma.
- **Sequência:** percorre `000 → 001 → ... → 111` no intervalo definido.
- **Modo robô:** entra em tela cheia, fecha o painel, esconde as guias e deixa
  só a pista branca. Use `F` para entrar/sair e `Esc` para sair.

## Parâmetros

Cada sensor tem:

| Campo | Descrição |
|---|---|
| X, Y | posição em px a partir do canto inferior esquerdo do palco |
| Largura, altura | tamanho em px |
| Período | duração de um ciclo completo de piscar, em ms (50% preto, 50% branco) |
| Fase | deslocamento de 0 a 100% do período, para defasar os retângulos |
| Preto/Branco | cor fixa usada no modo manual |

Convenção dos sensores: **preto = 1 (linha)** e **branco = 0**. O estado é
`s = (L << 2) | (C << 1) | R`, de 0 a 7.

As medidas de posição e tamanho são arredondadas para pixels inteiros. Para o
alinhamento físico bater, mantenha o navegador em **zoom 100%** e use o modo
robô em tela cheia. Os valores em px são relativos ao palco; se mudar de
monitor, use **Centralizar** e ajuste novamente.

## Rodar localmente

Dá para abrir `index.html` direto no navegador. Se preferir um servidor local:

```bash
python -m http.server 8000
```

Depois acesse `http://localhost:8000`.

## Deploy na Vercel

1. Importe o repositório na Vercel.
2. Em **Settings → General → Root Directory**, coloque `web`.
3. Framework Preset: **Other**.
4. Build Command: vazio. Output Directory: `.`.
5. Deploy.

Só o conteúdo de `web/` é publicado; o resto do repositório não fica acessível.
Também é possível usar a CLI:

```bash
npx vercel web --prod
```

## Limitação importante

Com os sensores do robô lendo a tela, o site é um **gerador open-loop**: ele
não recebe a ação do Arduino. Isso é ótimo para alinhar os sensores, testar o
firmware, conferir a Q-table pré-treinada e demonstrar os 8 estados, mas não
fecha o ciclo de aprendizado do Q-learning, porque as ações do robô não alteram
o próximo estado.

Para treino fechado, use o Modo 4 (`train_serial.py` + `arduino_agent.ino`) ou
adicione uma integração Web Serial/híbrida, na qual o Arduino envia a ação
(`action`) e o site move os retângulos em resposta.

## Dicas para a bancada

- Use preto puro e branco puro (o site já faz isso) e evite transições de cor.
- Aproxime os sensores IR da tela e ajuste o potenciômetro de cada módulo se
  necessário.
- Evite luz solar direta ou outras fontes de infravermelho no ambiente.
- O firmware lê os sensores a cada ~100 ms; use períodos de pelo menos 200 ms
  para o Arduino acompanhar as mudanças.
