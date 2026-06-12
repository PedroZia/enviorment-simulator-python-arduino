# RELATORIO - Simulador Seguidor de Linha com Q-Learning

## 1. Visao Geral

Sistema composto por dois modulos que se comunicam via serial:

| Modulo | Responsabilidade |
|---|---|
| **Arduino** | Q-learning, controle de motores, leitura de sensores, botoes |
| **Python** | Simulacao da pista, calculo de posicao/sensores, visualizacao Pygame |

O Arduino nao conhece a posicao do robo. Ele conhece apenas os 3 sensores (0/1). O Python rastreia a posicao (x, y, theta) e calcula quais sensores estao sobre a linha.

---

## 2. Hardware

| Componente | Especificacao |
|---|---|
| Microcontrolador | Arduino UNO (ou similar) |
| Motores | 2x DC com PWM via L298N (diferencial) |
| Sensores | 3x IR booleanos (Esquerda, Centro, Direita) em linha reta a frente |
| Botao 1 | Alternar modo Treino / Aplicacao |
| Botao 2 | Reset de episodio |
| Comunicacao | Serial USB 115200 baud |

### Pinos Padrao (temporarios)

| Funcao | Pino |
|---|---|
| Motor Esquerdo - PWM (ENA) | 5 |
| Motor Esquerdo - IN1 | 6 |
| Motor Esquerdo - IN2 | 7 |
| Motor Direito - PWM (ENB) | 10 |
| Motor Direito - IN3 | 8 |
| Motor Direito - IN4 | 9 |
| Sensor Esquerdo | A0 |
| Sensor Centro | A1 |
| Sensor Direito | A2 |
| Botao Modo (Treino/Aplicacao) | 2 |
| Botao Reset Episodio | 3 |

---

## 3. Q-Learning (Arduino)

### 3.1 Espaco de Estados e Acoes

| Parametro | Valor |
|---|---|
| Estados | 8 (3 bits: `000` a `111`) |
| Acoes | 5 (Frente, Esquerda, Direita, Parar, Re) |
| Q-table | 8x5 = 40 floats = **160 bytes** na RAM |
| Inicializacao | Zeros (futuro: carregar pre-treinada via serial) |

### 3.2 Acoes e Motores

| Acao | Codigo | Motor Esq | Motor Dir | PWM |
|---|---|---|---|---|
| Frente | `F` | Para frente | Para frente | 100 |
| Esquerda | `E` | Parado | Para frente | 50 |
| Direita | `D` | Para frente | Parado | 50 |
| Parar | `P` | Desligado | Desligado | 0 |
| Re | `R` | Para tras | Para tras | 50 |

### 3.3 Parametros

| Parametro | Valor | Descricao |
|---|---|---|
| alpha | 0.1 | Learning rate |
| gamma | 0.9 | Discount factor |
| epsilon inicial | 1.0 | Taxa de exploracao inicial |
| epsilon final | 0.01 | Taxa de exploracao minima |
| Decay epsilon | Linear | Por episodio |
| Steps por episodio | 500 (configuravel) | Limite de steps |

### 3.4 Formula de Atualizacao

```
Q(s, a) = Q(s, a) + alpha * (r + gamma * max(Q(s', a')) - Q(s, a))
```

Onde:
- `s` = estado atual (3 bits dos sensores)
- `a` = acao escolhida
- `r` = recompensa calculada pelo Arduino
- `s'` = novo estado (recebido do Python)

### 3.5 Estrategia Epsilon-Greedy

```
Se random() < epsilon -> acao aleatoria (exploracao)
Senao -> acao com maior Q(s, a) (exploracao)
```

epsilon decresce linearmente de 1.0 a 0.01 ao longo dos episodios.

### 3.6 Modos (Botao 1)

| Modo | Comportamento |
|---|---|
| **Treino** | Epsilon-greedy ativo, Q-table atualizada a cada step |
| **Aplicacao** | Epsilon = 0, sempre escolhe melhor acao, Q-table nao atualiza |

---

## 4. Funcao de Recompensa

Calculada pelo **Arduino** baseada nos sensores recebidos:

| Condicao | Recompensa |
|---|---|
| Sensor Centro = 1 (movendo) | **+2** |
| Sensor Esq ou Dir = 1, Centro = 0 | **+0.5** |
| Todos sensores = 0 (movendo) | **-1** |
| Acao = Parar, Centro = 1 | **-2** |
| Acao = Parar, Centro = 0 | **-1** |

**Logica**: O objetivo e manter o sensor CENTRO na linha. Sensores laterais sao pistas (recompensa menor). Parar sobre a linha e fortemente penalizado.

---

## 5. Simulacao (Python)

### 5.1 Pista

- Matriz 2D NumPy: `0` = fundo (branco), `1` = linha preta
- Tamanho dinamico (carregado de arquivo)
- Formatos suportados:
  - `.npy` (NumPy nativo)
  - `.csv` (texto)
  - `.png`/`.bmp` (imagem, limiarizado para 0/1)

### 5.2 Pistas de Exemplo

| Pista | Descricao |
|---|---|
| `oval.npy` | Oval simples (bom para testes iniciais) |
| `curves.npy` | Curvas e retas (intermediario) |
| `figure8.npy` | Figura 8 (avancado) |

### 5.3 Estado do Robo

```python
(x: float, y: float, theta: float)
```

- `x, y` = posicao na matriz (celula)
- `theta` = direcao em graus [0, 360), continuo

### 5.4 Movimento por Step

Cada acao move o robo **1 celula** na direcao theta:

| Acao | Efeito em (x, y, theta) |
|---|---|
| Frente | x += cos(theta), y += sin(theta) |
| Esquerda | theta -= 30 (giro) |
| Direita | theta += 30 (giro) |
| Parar | Sem mudanca |
| Re | x -= cos(theta), y -= sin(theta) |

### 5.5 Calculo dos Sensores

Para cada sensor (Esq, Centro, Dir):
1. Calcular offset lateral em relacao a direcao theta
2. Projetar posicao a `sensor_distance` celulas a frente
3. Verificar se a celula na matriz e `1` (linha) ou `0` (fundo)
4. Retornar 3 bits (ex: `"101"`)

Distancia dos sensores: **1 celula** a frente (configuravel).
Espacamento lateral: **1 celula** (configuravel).

### 5.6 Inicio do Episodio

- Posicao inicial: **aleatoria sobre a linha** (Python escolhe)
- theta inicial: **aleatorio** (0-360)
- Python envia sensores iniciais para Arduino

### 5.7 Condicoes de Fim de Episodio

| Condicao | Quem detecta | Como |
|---|---|---|
| Botao reset | Arduino | Botao fisico |
| Limite de steps | Arduino | Contador interno |
| Linha de partida | Arduino | Todos sensores = 1 (cruzamento) |
| Volta completa | Python | Coordenada volta ao ponto inicial -> envia flag `:RESET` |

**Qualquer uma** das condicoes encerra o episodio.

---

## 6. Comunicacao Serial

### 6.1 Formato

```
Arduino -> Python:  "ACAO\n"
Python -> Arduino:  "SEN\n"
```

### 6.2 Mensagens Arduino -> Python

| Mensagem | Significado |
|---|---|
| `F\n` | Acao Frente |
| `E\n` | Acao Esquerda |
| `D\n` | Acao Direita |
| `P\n` | Acao Parar |
| `R\n` | Acao Re |
| `READY\n` | Arduino pronto para novo episodio |

### 6.3 Mensagens Python -> Arduino

| Mensagem | Significado |
|---|---|
| `101\n` | Sensores (Esq=1, Centro=0, Dir=1) |
| `000\n` | Todos sensores fora da linha |
| `111\n` | Todos sensores na linha (linha de partida?) |
| `000:RESET\n` | Sensores + flag de volta completa |
| `101:EPISODE:42\n` | Sensores + numero do episodio |

### 6.4 Fluxo por Step

```
1. Arduino escolhe acao (epsilon-greedy ou greedy)
2. Arduino envia acao via serial (ex: "F\n")
3. Python recebe acao
4. Python atualiza posicao (x, y, theta)
5. Python calcula novos sensores
6. Python responde com sensores (ex: "101\n")
7. Arduino recebe sensores
8. Arduino calcula recompensa
9. Arduino atualiza Q-table
10. Repete
```

### 6.5 Fluxo de Re

```
1. Arduino decide dar re (apos X steps sem linha)
2. Arduino envia "R\n"
3. Python move robo 1 celula para tras
4. Python calcula sensores e responde
5. Se sensores ainda = "000", Arduino envia "R\n" novamente
6. Repete ate algum sensor encontrar a linha
```

---

## 7. Visualizacao (Pygame)

| Elemento | Representacao |
|---|---|
| Pista | Fundo branco, linha preta |
| Robo | Triangulo/seta na posicao (x, y, theta) |
| Sensor Esq | Ponto colorido (verde=linha, vermelho=fora) |
| Sensor Centro | Ponto colorido |
| Sensor Dir | Ponto colorido |
| Info | Episodio, steps, reward, epsilon, modo |

---

## 8. Estrutura de Arquivos

```
├── main.py                        # Entry point, loop principal
├── config.py                      # Parametros configuraveis
├── requirements.txt               # Dependencias Python
├── RELATORIO.md                   # Este documento
├── simulator/
│   ├── __init__.py
│   ├── track.py                   # Carregamento e gestao de pistas
│   ├── robot_sim.py               # Simulacao do robo
│   └── serial_comm.py             # Comunicacao serial
├── visualization/
│   ├── __init__.py
│   └── pygame_display.py          # Visualizacao Pygame
├── tracks/
│   ├── oval.npy
│   ├── curves.npy
│   ├── figure8.npy
│   └── track_generator.py         # Gerador de pistas
└── arduino/
    └── line_follower/
        └── line_follower.ino      # Codigo Arduino
```

---

## 9. Dependencias Python

```
pyserial>=3.5
numpy>=1.24
pygame>=2.5
opencv-python>=4.8  # opcional, para carregar imagens
```

---

## 10. Resumo do Fluxo Completo

```
┌──────────────────┐     Serial 115200     ┌──────────────────┐
│     ARDUINO      │◄─────────────────────►│      PYTHON      │
│                  │                       │                  │
│  ┌────────────┐  │    "F\n" ──────────►  │  ┌────────────┐  │
│  │ Q-Learning │  │                       │  │ Simulador  │  │
│  │ 8 estados  │  │    ◄──────────────    │  │ Pista 2D   │  │
│  │ 5 acoes    │  │        "101\n"        │  │ (x,y,theta)│  │
│  │ 40 floats  │  │                       │  │ Sensores   │  │
│  └────────────┘  │                       │  └────────────┘  │
│                  │                       │                  │
│  ┌────────────┐  │                       │  ┌────────────┐  │
│  │  Motores   │  │                       │  │   Pygame   │  │
│  │  L298N     │  │                       │  │ Visualizar │  │
│  └────────────┘  │                       │  └────────────┘  │
│                  │                       │                  │
│  ┌────────────┐  │                       │                  │
│  │  Sensores  │  │                       │                  │
│  │  3x IR     │  │                       │                  │
│  └────────────┘  │                       │                  │
│                  │                       │                  │
│  ┌────────────┐  │                       │                  │
│  │  Botoes    │  │                       │                  │
│  │ Modo/Reset │  │                       │                  │
│  └────────────┘  │                       │                  │
└──────────────────┘                       └──────────────────┘
```

---

## 11. Decisoes de Design

| Decisao | Justificativa |
|---|---|
| Q-table no Arduino | Robo precisa funcionar standalone apos treino |
| Python rastreia posicao | Arduino nao tem como saber posicao sem GPS/encoders |
| Serial assincrono | Simplicidade, funciona via USB |
| Sensores booleanos | Simplicidade, compativel com IR TCRT5000 |
| theta continuo (graus) | Mais realista que 4/8 direcoes discretas |
| Re repetida | Arduino mantem acao ate resolver o problema |
| Epsilon linear | Simples, previsivel, funciona bem na pratica |
