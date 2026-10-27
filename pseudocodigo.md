# Pseudocódigos — Robô Seguidor de Linha com Q-Learning

Dois pseudocódigos que descrevem o par de programas que trabalham juntos via serial, no treinamento hardware-in-the-loop:

1. **ESP32** (`esp32_agent.ino`) — o agente Q-learning embarcado.
2. **Python** (`train_serial.py`) — o ambiente simulado que roda no PC.

Convenção comum: leituras `0` = branco (fora da linha), `1` = preto (sobre a linha); estado `s = (L<<2)|(M<<1)|R` (8 estados, 0..7); ações `0` = esquerda, `1` = reto, `2` = direita. A Q-table 8×3 vive na RAM da MCU; o PC apenas envia leituras e recompensa e recebe a ação de volta.

---

## Protocolo serial (115200 baud, linhas terminadas em `\n`)

| Sentido | Mensagem | Significado |
|---|---|---|
| Python → MCU | `L,M,R,reward` | passo: leituras + recompensa do passo anterior |
| MCU → Python | `action` (0/1/2) | ação escolhida pelo agente |
| Python → MCU | `R` | reseta episódio e decai ε |
| Python → MCU | `Q` | pede dump da Q-table |
| MCU → Python | `s,Q0,Q1,Q2` ×8 + `END` | conteúdo da Q-table 8×3 |
| Python → MCU | `E<valor>` | fixa ε (`E0` = greedy) |
| MCU → Python | `READY` | boot concluído |

---

## Algoritmo 1 — Firmware do agente Q-Learning embarcado (ESP32)

```
CONSTANTES:
    N_STATES  = 8        // estados 0..7 (3 sensores binários)
    N_ACTIONS = 3        // ações: 0 = esquerda, 1 = reto, 2 = direita
    ALPHA     = 0.1      // taxa de aprendizado
    GAMMA     = 0.9      // fator de desconto
    EPS_START = 1.0      // ε inicial
    EPS_MIN   = 0.02     // ε mínimo
    EPS_DECAY = 0.99     // fator de decaimento de ε por episódio

VARIÁVEIS GLOBAIS:
    q[8][3]     ← 0.0              // Q-table 8×3 na RAM da MCU
    epsilon     ← EPS_START
    prev_state  ← -1               // -1 = nenhum passo anterior
    prev_action ← -1

FUNÇÃO escolhe_acao_epsilon_greedy(state):
    SE aleatório[0,1) < epsilon:
        RETORNA aleatório em 0..2                      // explora
    SENÃO:
        RETORNA argmáximo_a( q[state][a] )             // explota
        // desempate: se todos forem iguais, prefere reto (ação 1)

FUNÇÃO processar_linha(linha):
    SE linha == "R":                                    // reset de episódio
        epsilon ← máximo(EPS_MIN, epsilon × EPS_DECAY)
        prev_state  ← -1
        prev_action ← -1
        RETORNA

    SE linha == "Q":                                    // dump da Q-table
        PARA cada estado s em 0..7:
            envia_serial(s, q[s][0], q[s][1], q[s][2])  // "s,Q0,Q1,Q2\n"
        envia_serial("END")
        RETORNA

    SE linha começa com "E":                            // fixa ε manualmente
        epsilon ← valor_float(linha sem o "E")          // "E0" = greedy
        RETORNA

    // passo normal: "L,M,R,reward"
    separa(linha, ",") em L, M, R, reward
    state ← (L << 2) | (M << 1) | R                     // codifica leituras em 0..7

    // atualização de Bellman do par (estado anterior, ação anterior)
    SE prev_state ≥ 0:
        best_next ← máximo_a( q[state][a] )
        q[prev_state][prev_action] ← q[prev_state][prev_action]
            + ALPHA × (reward + GAMMA × best_next − q[prev_state][prev_action])

    // seleção de ação ε-greedy para o estado atual
    action ← escolhe_acao_epsilon_greedy(state)

    envia_serial(action)                                // "action\n" ao PC

    prev_state  ← state
    prev_action ← action

INICIALIZAÇÃO:
    Serial.inicia(115200)
    aguarda a porta serial ficar pronta
    randomSeed(leitura de entrada analógica)            // semente do gerador aleatório
    envia_serial("READY")                               // boot concluído

LOOP PRINCIPAL:
    SE "READY" ainda não foi enviado:
        envia_serial("READY")
    SE não há dados recebidos na serial: RETORNA

    linha ← lê a string recebida até '\n'
    remove espaços e o caractere '\r' da linha
    SE linha vazia: RETORNA
    processar_linha(linha)
```

---

## Algoritmo 2 — Ambiente simulado (Python, no PC)

```
CONFIGURAÇÃO:
    Pista: TRACK_L = 40.0 (meia-reta) · TRACK_R = 20.0 (raio dos semicírculos)
           TRACK_N = 60 (pontos da poligonal)
    Robô:  SPEED = 0.8 (deslocamento por passo) · TURN_RATE = 15° (giro por ação)
           SENSOR_DIST = 2.0 (alcance dos feixes) · SENSOR_ANGLE = 35° (abertura lateral)
           LINE_HALF_WIDTH = 0.8 (meia-largura da linha)
    Treinamento: MAX_STEPS = 1000 · LOST_LIMIT = 15 · EPISODES = 200 (oval)
                 FEATURE_EPISODES = 40 (pista de recursos) · total = 240
    Serial: PORT = "COM3" · BAUD = 115200

FUNÇÃO generate_track():
    // pista em formato estádio, fechada: 4 trechos de TRACK_N/4 pontos
    // semicírculo direito → reta superior → semicírculo esquerdo → reta inferior
    RETORNA lista de 60 pontos (x, y)

FUNÇÃO dist_to_track(x, y, pista):
    RETORNA a menor distância de (x, y) a qualquer segmento da poligonal fechada

FUNÇÃO tangent_at(índice, pista):
    RETORNA o ângulo do segmento entre pista[índice] e pista[índice + 1]

FUNÇÃO robot_step(x, y, θ, action):
    θ ← θ + (action − 1) × TURN_RATE        // 0 = esquerda, 1 = reto, 2 = direita
    x ← x + SPEED × cos(θ)
    y ← y + SPEED × sin(θ)
    RETORNA (x, y, θ)

FUNÇÃO pista_de_recursos():
    RETORNA reta y = 0, x de −35 a +35
    // trecho de linha larga em x ∈ [−15, −5]  → 111
    // cruzamento com gap central em x ∈ [5, 9] → 101

FUNÇÃO is_on_ink(ponto, pista):
    SE pista é a pista de recursos:
        base   ← |y| < LINE_HALF_WIDTH, exceto no gap x ∈ [5,9]
        larga  ← x ∈ [−15,−5] E |y| < 1.4
        cruz   ← x ∈ [4.5,9.5] E 1.0 ≤ |y| ≤ 3.5
        RETORNA base OU larga OU cruz
    RETORNA dist_to_track(ponto, pista) < LINE_HALF_WIDTH

FUNÇÃO read_sensors(x, y, θ, pista):
    PARA offset em (−SENSOR_ANGLE, 0, +SENSOR_ANGLE):
        ponto ← (x + SENSOR_DIST × cos(θ + offset),
                 y + SENSOR_DIST × sin(θ + offset))
        leitura ← 1 SE is_on_ink(ponto, pista) SENÃO 0
    RETORNA (L, M, R)                       // L = esquerdo, M = central, R = direito

FUNÇÃO compute_reward(L, M, R, ação = nulo, atual = nulo):
    SE (L, M, R) == (0, 0, 0):                         // perdeu a linha
        recompensa ← −1.0 SE ação == 1 SENÃO −3.0      // reto é a melhor busca
    SENÃO:
        recompensa ← 0.0
        SE M == 1: recompensa ← recompensa + 1.0       // central sobre a linha
        SE L == 1: recompensa ← recompensa − 0.5       // lateral esquerdo ativo
        SE R == 1: recompensa ← recompensa − 0.5       // lateral direito ativo

    origem ← atual SE atual ≠ nulo SENÃO (L, M, R)
    SE ação ≠ nulo:
        SE origem == (0, 0, 0) E ação ≠ 1:
            recompensa ← recompensa − 3.0              // não sai perdido virando
        SENÃO SE origem ∈ {(1,0,1), (1,1,1)}:
            recompensa ← recompensa + 2.0 SE ação == 1 SENÃO −2.0
    RETORNA recompensa

// ---------- camada serial ----------

FUNÇÃO connect_serial(porta, baud):
    PARA tentativa em 1..10:
        abre a porta serial (timeout 2 s)
        POR até 5 s:
            linha ← lê linha da serial
            SE linha == "READY": RETORNA conexão       // handshake
        fecha a porta e aguarda 1 s
    ERRO: não foi possível conectar

FUNÇÃO send_step(conexão, leituras, reward):
    envia "L,M,R,reward\n"
    aguarda a linha de resposta
    RETORNA a ação (0/1/2) — ou vazio em caso de timeout

FUNÇÃO reset_episodio(conexão):
    envia "R\n"      // MCU aplica o decaimento de ε e zera prev_state/prev_action

FUNÇÃO get_qtable(conexão):
    envia "Q\n"
    lê linhas "s,Q0,Q1,Q2" até receber "END"
    RETORNA a Q-table 8×3

FUNÇÃO set_epsilon(conexão, ε):
    envia "E<ε>\n"   // "E0" = política greedy

// ---------- treinamento ----------

FUNÇÃO train_feature(pista_recursos, conexão, episódios = 40,
                     save_interval = 0, timestamp):
    PARA episódio em 1..40:
        envia "E0.10"                                  // ε fixo para explorar
        reset_episodio(conexão)
        // com --save: snapshot a cada N episódios, inclusive nesta fase
        SE save_interval > 0 E episódio % save_interval == 0:
            salvar_qtable(get_qtable(conexão), episódio, timestamp)

        (x, y) ← pista_recursos[0]                     // começa centrado na reta
        θ ← 0

        recompensa_total ← 0.0
        reward_anterior ← 0.0
        leituras ← read_sensors(x, y, θ, pista_recursos)

        PARA passo em 1..FEATURE_MAX_STEPS:
            ação ← send_step(conexão, leituras, reward_anterior)
            SE timeout serial: encerra o episódio

            (x, y, θ) ← robot_step(x, y, θ, ação)
            novas_leituras ← read_sensors(x, y, θ, pista_recursos)
            reward_anterior ← compute_reward(novas_leituras, ação, leituras)
            recompensa_total ← recompensa_total + reward_anterior

            SE novas_leituras == (0,0,0): passos_perdidos++
            SENÃO: passos_perdidos ← 0
            SE passos_perdidos ≥ LOST_LIMIT: encerra

            leituras ← novas_leituras

        registra recompensa_total no histórico

    SE save_interval > 0:
        salvar_qtable(get_qtable(conexão), 40, timestamp)  // fim da fase 1

    RETORNA o histórico


FUNÇÃO train(pista, conexão, episódios = 200):
    PARA episódio em 1..200:
        reset_episodio(conexão)
        // com --save: snapshot a cada N episódios (offset = 40 da fase 1)
        SE save_interval > 0 E episódio % save_interval == 0:
            salvar_qtable(get_qtable(conexão), episódio + 40, timestamp)
        // posição inicial aleatória sobre a pista, com leve desalinhamento
        índice ← aleatório na pista
        (x, y) ← pista[índice]
        θ ← tangent_at(índice, pista) + ruído aleatório

        recompensa_total ← 0.0
        passos_perdidos ← 0
        reward_anterior ← 0.0                            // 1º passo: recompensa nula
        leituras ← read_sensors(x, y, θ, pista)

        PARA passo em 1..MAX_STEPS:
            ação ← send_step(conexão, leituras, reward_anterior)
            SE timeout serial: encerra o episódio

            (x, y, θ) ← robot_step(x, y, θ, ação)
            novas_leituras ← read_sensors(x, y, θ, pista)
            reward_anterior ← compute_reward(novas_leituras, ação, leituras)
            recompensa_total ← recompensa_total + reward_anterior

            SE novas_leituras == (0, 0, 0):
                passos_perdidos ← passos_perdidos + 1
            SENÃO:
                passos_perdidos ← 0
            SE passos_perdidos ≥ LOST_LIMIT: encerra o episódio

            leituras ← novas_leituras

        registra recompensa_total no histórico

    RETORNA o histórico de recompensas

// ---------- saída (arquivos gerados) ----------

FUNÇÃO salvar_qtable(q, episódio = 240, timestamp):
    cria o diretório "snapshots/" se não existir
    escreve "snapshots/qtable_<AAAAMMDD_HHMMSS>_ep0240.txt":
        cabeçalho "episode 240"
        8 linhas "[LMR] -> Q0  Q1  Q2", com a melhor ação de cada estado
        marcada com "*"

FUNÇÃO salvar_historico(histórico, timestamp):
    escreve "history_<AAAAMMDD_HHMMSS>.csv":
        cabeçalho "episode,reward"
        1 linha por episódio: "número,recompensa_total"

// ---------- conexão: serial real ou modo --fake ----------

SE modo --fake:                                    // sem hardware
    conexão ← FakeESP32()                          // reproduz o protocolo da MCU
                                                   // em Python puro:
                                                   //   "R" → decai ε, zera passo anterior
                                                   //   "Q" → envia 8× "s,Q0,Q1,Q2" + "END"
                                                   //   "E<ε>" → fixa ε
                                                   //   "L,M,R,reward" → Bellman +
                                                   //     ε-greedy + responde "action"
SENÃO:
    conexão ← connect_serial(PORT, BAUD)          // handshake: espera "READY"

// ---------- principal ----------

PRINCIPAL:
    define a semente do gerador aleatório (reprodutibilidade)
    timestamp ← data/hora atual (AAAAMMDD_HHMMSS)
    pista ← generate_track()
    pista_recursos ← pista_de_recursos()
    conexão ← (modo --fake ou serial real, conforme acima)

    histórico ← train_feature(pista_recursos, conexão, 40 episódios)
    envia "E1.0"                                  // exploração total na oval
    histórico ← histórico + train(pista, conexão, 200 episódios)

    q ← get_qtable(conexão)                        // Q-table final
    imprime a Q-table 8×3 (melhor ação de cada estado)
    salvar_qtable(q, 240, timestamp)               // qtable_<timestamp>_ep0240.txt
    salvar_historico(histórico, timestamp)         // history_<timestamp>.csv

    set_epsilon(conexão, 0)                        // demo greedy (ε = 0)
    demo: 1 episódio (até 400 passos ou perda da linha)
    fecha a conexão serial
```

> Nota (fora do pseudocódigo): o código real permite salvar snapshots intermediários da Q-table a cada N episódios (flag `--save`, default 10). Os arquivos usam timestamp no nome (`qtable_<AAAAMMDD_HHMMSS>_epNNNN.txt`) para não sobrescrever execuções antigas; a especificação fixa apenas o snapshot final.

---

## Decisões a confirmar

1. **Microcontrolador — ESP32 ou Arduino UNO?** O texto do TCC afirma ESP32 (usado nos pseudocódigos), mas o repositório contém `esp32_agent.ino` **e** `arduino_agent.ino`. Diferenças reais: ESP32 usa `String` + `toFloat()`; Arduino usa buffer de caracteres + `safe_atof()` (o AVR não tem `sscanf %f`) e ignora `'\r'` no byte a byte, enquanto o ESP32 remove `'\r'` com `trim()`.
2. **Nomes `ALPHA`/`GAMMA` no artigo vs. código.** O pseudocódigo usa `ALPHA`/`GAMMA`/`EPS_*` conforme a especificação, mas o `.ino` real declara `alpha`, `g`, `eps_min`, `eps_decay`. **Recomendo renomear no código** (ou usar `α` e `γ` na notação e manter as declarações) para a banca não apontar divergência.
3. **Demo ainda aprende.** No código real, a demo (ε=0) continua executando a atualização de Bellman a cada passo (só o `R` zera `prev_state`). Se o artigo afirmar que "na demo a Q-table é congelada", será inconsistente — confirme o texto.
4. **Snapshots intermediários (`--save`).** Fora da especificação (que fixa apenas `qtable_ep_0200.txt`), mas existem no código e no repositório (10 em 10 episódios). Já incluídos como nota; o artigo pode citá-los como verificação da evolução do aprendizado.
5. **Porta serial.** `PORT = 'COM3'` é o default do código; no artigo, escreva apenas "porta configurável".

---

## Checklist de consistência contra o código-fonte

**Firmware (`esp32_agent.ino`):**
1. Constantes e globais: `q[8][3]=0`, `alpha=0.1`, `g=0.9`, `epsilon=1.0`, `eps_min=0.02`, `eps_decay=0.99`, `prev_state/prev_action=-1` — linhas 13–25.
2. `Serial.begin(115200)`, `randomSeed(analogRead(0))`, `READY` enviado uma única vez (flag `ready_sent` no `loop`) — linhas 27–37.
3. Comando `R`: decaimento `ε = max(EPS_MIN, ε×0.99)` e zera `prev_state/prev_action` — linhas 46–52.
4. Comando `Q`: 8 linhas `s,Q0,Q1,Q2` (4 casas decimais) + `END` — linhas 55–66.
5. Comando `E<valor>`: `epsilon = toFloat(...)` — linhas 69–72.
6. Passo normal: parse por índices de vírgula; `state = (l<<2)|(m<<1)|r` — linhas 74–85.
7. Bellman: `SE prev_state ≥ 0` → `q[prev][prev] += α×(reward + γ×max q[state][·] − q[prev][prev])`, antes da seleção de ação — linhas 87–95.
8. ε-greedy: `random(1000)/1000.0 < ε` → aleatória; senão argmax; envia `action`; atualiza `prev_state/prev_action` — linhas 97–111.
9. Tratamento de `\r`: ESP32 via `trim()` (linha 42); versão Arduino descarta `'\r'` no loop de bytes (`arduino_agent.ino:154`) — escolha a versão do artigo.

**Ambiente (`train_serial.py`):**
10. Parâmetros de pista/robô idênticos (`TRACK_L=40`, `TRACK_R=20`, `TRACK_N=60`, `SPEED=0.8`, `TURN_RATE=15°`, `SENSOR_DIST=2.0`, `SENSOR_ANGLE=35°`, `LINE_HALF_WIDTH=0.8`, `MAX_STEPS=1000`, `LOST_LIMIT=15`, `EPISODES=200` + `FEATURE_EPISODES=40`).
11. `generate_track`: 4 trechos de 15 pontos = 60, formato estádio fechado — linhas 40–55.
12. `dist_to_track` por segmentos com poligonal fechada — linhas 58–76; `tangent_at` com `atan2` do segmento seguinte — 79–82.
13. `robot_step`: `θ += (action−1)×TURN_RATE` — linhas 87–91.
14. `read_sensors`: 3 feixes a 2.0 à frente, offsets −35°/0/+35°, limiar 0.8 — linhas 94–102.
15. `compute_reward`: perdido reto −1 / virando −3 (+ penalidade extra); M→+1.0; L/R→−0.5; `101/111` reto +2 / virando −2.
16. `connect_serial`: 10 tentativas, espera `READY` até 5 s; `send_step` com timeout e retorno de ação.
17. Treino em **duas fases**: 40 episódios na pista de recursos (linha larga `111` e cruzamento com gap `101`) + 200 na oval; `R` no início de cada episódio; `prev_reward=0` no 1º passo; recompensa calculada **após** o `robot_step` e enviada no passo seguinte.
18. Fim de episódio: `MAX_STEPS`/`FEATURE_MAX_STEPS` ou `lost_steps ≥ 15`.
19. Final: `get_qtable` → impressão → `snapshots/qtable_<timestamp>_ep0240.txt` → `history_<timestamp>.csv` → `E0` + demo (máx. 400 passos).
20. `random.seed(seed)` antes de gerar a pista.
21. `--fake`: `FakeESP32` reproduz o protocolo (R/Q/E/passo com Bellman + ε-greedy) e usa o mesmo desempate (reto).
22. Salvamento: `save_qtable` grava `snapshots/qtable_<timestamp>_ep{episódio:04d}.txt` com melhor ação marcada `*`; `save_history` grava `history_<timestamp>.csv`.
23. Demo: `set_epsilon(0)` + até 400 passos ou perda da linha.

---

## Diferenças entre a especificação recebida e este documento

1. **Nomes `ALPHA`/`GAMMA` vs. código.** A especificação manda usar `ALPHA`, `GAMMA`, `EPS_START`, `EPS_MIN`, `EPS_DECAY` como nomes das variáveis reais, mas o `.ino` declara `alpha`, `g`, `eps_min`, `eps_decay` (e o `sim.py` usa `ALPHA`/`GAMMA`/`EPS_*`). O pseudocódigo seguiu a especificação; recomenda-se renomear as variáveis do firmware (ou ajustar o texto do artigo) para eliminar a divergência (ver Decisão 2).
2. **Demo ainda aprende.** A especificação descreve a demo como "ε = 0 (greedy)"; no código real a demo continua executando a atualização de Bellman a cada passo, pois `prev_state`/`prev_action` só são zerados pelo comando `R` (ver Decisão 3).
3. **Modo `--fake`.** A especificação o lista como parte do Algoritmo 2; incluído no pseudocódigo e na nota. O `--fake` é para teste do fluxo sem hardware — o artigo deve deixar claro que o treinamento oficial é hardware-in-the-loop.
4. **Leitura de `\r`.** A especificação pede "tratamento de `\r`"; o ESP32 o remove via `trim()`, a versão Arduino o descarta byte a byte no `loop`. O pseudocódigo descreve "remove `\r`"; a versão do artigo depende da plataforma escolhida (Decisão 1).
5. **Demais parâmetros e fluxo** (hiperparâmetros, recompensa moldada, protocolo, 40 episódios de recursos + 200 na oval = 240, MAX_STEPS=1000, LOST_LIMIT=15, arquivos `snapshots/qtable_<timestamp>_ep0240.txt` e `history_<timestamp>.csv`, formato estádio da pista, sensores a 2.0 com abertura 35°, SPEED=0.8, TURN_RATE=15°): idênticos ao código real.