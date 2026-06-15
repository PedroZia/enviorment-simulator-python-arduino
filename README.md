# Simulador Seguidor de Linha com Q-Learning

Simulador de ambiente para robô seguidor de linha que usa Q-learning no Arduino. Python simula o ambiente (pista 2D, sensores IR) e o Arduino toma decisões e aprende via comunicação serial.

## Requisitos

- Python 3.12+
- Arduino UNO (opcional — pode rodar sem Arduino em modo teclado)

## Instalação

```bash
pip install -r requirements.txt
python main.py --generate-tracks
```

Dependências: `numpy`, `pyserial`, `pygame-ce` (community fork, **não** `pygame`).

## Uso

```bash
# Com Arduino
python main.py --track tracks/oval.npy --port COM3

# Sem Arduino (controle por teclado)
python main.py --no-serial --track tracks/oval.npy

# Sem visualização (headless)
python main.py --no-serial --no-display --track tracks/oval.npy
```

### Controles (modo teclado)

| Tecla | Ação |
|-------|------|
| Setas | Mover (Frente, Esquerda, Direita, Ré) |
| Espaço | Parar |
| R | Resetar episódio |
| T | Alternar Treino/Aplicação |
| Q | Sair |

## Arquitetura

```
├── config.py                    # Constantes (porta serial, hiperparâmetros, pinos)
├── main.py                      # Entry point, classe Simulator
├── simulator/
│   ├── track.py                 # Carrega pistas (.npy, .csv, .png)
│   ├── robot_sim.py             # Simula posição (x, y, θ) e sensores IR
│   └── serial_comm.py           # Comunicação serial com Arduino
├── visualization/
│   └── pygame_display.py        # Exibição em tempo real (pygame-ce)
├── arduino/
│   └── line_follower/
│       └── line_follower.ino    # Código Arduino (Q-learning)
└── tracks/
    ├── track_generator.py       # Gera pistas de exemplo
    ├── oval.npy
    ├── curves.npy
    ├── figure8.npy
    └── straight.npy
```

## Protocolo de Comunicação

Arduino envia código da ação (`F`/`E`/`D`/`P`/`R`), Python responde com string de 3 bits dos sensores (ex: `101`). Sufixos opcionais: `:RESET`, `:EPISODE:N`.

Handshake: Arduino envia `READY\n` ao conectar antes de iniciar o loop de Q-learning.

## Q-Learning

| Parâmetro | Valor |
|-----------|-------|
| Estados | 8 (3 bits sensores) |
| Ações | 5 (Frente, Esquerda, Direita, Parar, Ré) |
| Alpha | 0.1 |
| Gamma | 0.9 |
| Épsilon | 1.0 → 0.01 (decaimento linear) |
| Recompensa (centro na linha) | +2.0 |
| Recompensa (lateral na linha) | +0.5 |
| Recompensa (todos fora) | -1.0 |
| Max steps/episódio | 500 |

## Pistas

As pistas são matrizes NumPy 2D (0=fundo, 1=linha). Gere com:

```bash
python main.py --generate-tracks
```

Ou crie customizadas e salve como `.npy`.

## Layout dos Pinos (Arduino)

| Função | Pino |
|--------|------|
| Motor Esquerdo (PWM/IN1/IN2) | 5 / 6 / 7 |
| Motor Direito (PWM/IN3/IN4) | 10 / 8 / 9 |
| Sensor Esquerdo | A0 |
| Sensor Centro | A1 |
| Sensor Direito | A2 |
| Botão Modo | 2 |
| Botão Reset | 3 |
