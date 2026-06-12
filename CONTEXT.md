# Contexto da Conversa - Simulador Seguidor de Linha

Data: 12/06/2026

## Objetivo

Criar um simulador para robô seguidor de linha que usa Q-learning no Arduino, com Python simulando o ambiente (pista 2D) via comunicação serial. O Arduino toma decisões e aprende; Python calcula posição e sensores.

## Decisões Confirmadas

### Hardware
- 2 motores DC com PWM via L298N (diferencial)
- 3 sensores IR booleanos (Esquerda, Centro, Direita) em linha reta à frente
- Botão 1: alternar Treino/Aplicação
- Botão 2: reset de episódio
- Serial 115200 baud

### Q-Learning (Arduino)
- 8 estados (3 bits sensores) x 5 ações = 40 floats (160 bytes RAM)
- Ações: Frente(F), Esquerda(E), Direita(D), Parar(P), Ré(R)
- Alpha=0.1, Gamma=0.9
- Epsilon: 1.0 → 0.01, decaimento linear
- Q-table atualizada a cada step
- Arduino sozinho treina, Python só simula ambiente

### Recompensa
- Sensor Centro=1 (movendo): +2
- Sensor lateral=1, Centro=0: +0.5
- Todos sensores=0: -1
- Parado em cima da linha: -2
- Parado fora da linha: -1

### Simulação (Python)
- Matriz 2D NumPy (0/1), carregada de arquivo (.npy, .csv, .png)
- Posição: (x, y, θ) onde θ ∈ [0°, 360°) contínuo
- Movimento: 1 célula por step na direção θ
- Turn: ±30° por ação de giro
- Sensores: 1 célula à frente, 1 célula de espaçamento lateral
- Posição inicial: aleatória sobre a linha
- Ré: anda para trás até sensor encontrar linha (ação repetida)

### Comunicação Serial
- Arduino envia ação (ex: "F\n")
- Python responde sensores (ex: "101\n")
- Sufixos: ":RESET", ":EPISODE:N"
- Arduino espera handshake "READY\n" ao conectar

### Condições de Fim de Episódio (qualquer uma)
- Botão reset físico
- Limite de steps (500, configurável)
- Linha de partida (todos sensores = 1)
- Volta à coordenada inicial (Python envia flag ":RESET")

### Visualização
- Pygame-ce (não pygame) para exibição em tempo real
- Setas=move, Espaço=para, R=reset, T=troca modo, Q=sair

### Pistas
- Formato NumPy .npy (geradas por track_generator.py)
- Exemplos: oval, curves, figure8, straight
- Tamanho dinâmico

## Pinos Arduino (temporários)
- Motor Esq: PWM=5, IN1=6, IN2=7
- Motor Dir: PWM=10, IN3=8, IN4=9
- Sensores: A0, A1, A2
- Botões: 2, 3

## Comandos Úteis
```bash
pip install -r requirements.txt
python tracks/track_generator.py
python main.py --no-serial --track tracks/oval.npy
python main.py --port COM3 --track tracks/oval.npy
```

## Notas Importantes
- Usar `pygame-ce` (community edition), NÃO `pygame`
- Todos os módulos usam `sys.path.insert(0, ...)` para encontrar `config.py`
- Rodar sempre da raiz do projeto
- Porta padrão COM3, alterar via `--port` ou em `config.py`
