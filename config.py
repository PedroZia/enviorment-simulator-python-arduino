import numpy as np

# =============================================================================
# CONFIGURACAO DO SIMULADOR - Seguidor de Linha com Q-Learning
# =============================================================================

# --- Comunicacao Serial ---
SERIAL_PORT = "COM3"            # Porta serial do Arduino
BAUD_RATE = 115200              # Baud rate
SERIAL_TIMEOUT = 0.1            # Timeout de leitura (segundos)

# --- Pista ---
DEFAULT_TRACK = "tracks/oval.npy"   # Pista padrao
CELL_SIZE = 8                       # Tamanho de cada celula em pixels (Pygame)

# --- Robo ---
ROBOT_SPEED = 1.0               # Celulas por step
TURN_ANGLE = 15.0               # Graus por acao de giro
SENSOR_DISTANCE = 1.0           # Distancia dos sensores a frente (celulas)
SENSOR_SPACING = 1.0            # Espacamento lateral dos sensores (celulas)
BOUNDARY_MODE = "wrap"          # "wrap" = teletransporta, "clamp" = trava na borda

# --- Q-Learning ---
NUM_STATES = 8                  # 3 bits dos sensores = 8 estados
NUM_ACTIONS = 3                 # Frente, Esquerda, Direita (sem Parar e sem Re)
ALPHA = 0.1                     # Learning rate
GAMMA = 0.9                     # Discount factor
EPSILON_START = 1.0             # Epsilon inicial
EPSILON_END = 0.01              # Epsilon final
EPSILON_DECAY = 0.001           # Decaimento por episodio (~990 episodios para explorar)

# --- Recompensa (valores iguais ao ESP32) ---
# Centro na linha + frente: +2.0
# Centro na linha + girando: +0.5
# Lateral esquerda na linha + frente: +0.5
# Lateral esquerda na linha + esquerda: +1.0 (gira para recuperar)
# Lateral esquerda na linha + direita: -0.5 (gira para piorar)
# Lateral direita na linha + frente: +0.5
# Lateral direita na linha + esquerda: -0.5 (gira para piorar)
# Lateral direita na linha + direita: +1.0 (gira para recuperar)
# Todos fora + frente: -1.0
# Todos fora + esquerda: +0.5 (gira para tentar achar)
# Todos fora + direita: +0.5 (gira para tentar achar)

# --- Episodio ---
MAX_STEPS_PER_EPISODE = 500     # Limite de steps por episodio
START_POSITION = "random_line"  # "random_line" ou "fixed"
FIXED_START_X = 0               # Posicao fixa X (se START_POSITION = "fixed")
FIXED_START_Y = 0               # Posicao fixa Y (se START_POSITION = "fixed")

# --- Acoes (3 acoes: Frente, Esquerda, Direita) ---
ACTION_NAMES = ["Frente", "Esquerda", "Direita"]
ACTION_CODES = ["F", "E", "D"]

# Indices das acoes
ACTION_FORWARD = 0
ACTION_LEFT = 1
ACTION_RIGHT = 2

# --- Motores (PWM) ---
PWM_FORWARD = 100               # Velocidade para frente (0-255)
PWM_TURN = 50                   # Velocidade para curvas (0-255)

# --- Pinos ESP32 ---
PIN_MOTOR_LEFT_PWM = 5      # ENA (LEDC canal 0)
PIN_MOTOR_LEFT_IN1 = 18
PIN_MOTOR_LEFT_IN2 = 19
PIN_MOTOR_RIGHT_PWM = 23    # ENB (LEDC canal 1)
PIN_MOTOR_RIGHT_IN3 = 16
PIN_MOTOR_RIGHT_IN4 = 17
PIN_SENSOR_LEFT = 32
PIN_SENSOR_CENTER = 33
PIN_SENSOR_RIGHT = 34
PIN_BUTTON_MODE = 2
PIN_BUTTON_RESET = 4

# --- Visualizacao ---
WINDOW_TITLE = "Simulador Seguidor de Linha - Q-Learning"
COLOR_BACKGROUND = (255, 255, 255)      # Branco
COLOR_TRACK = (0, 0, 0)                 # Preto
COLOR_ROBOT = (0, 100, 255)             # Azul
COLOR_SENSOR_ON = (0, 200, 0)           # Verde (na linha)
COLOR_SENSOR_OFF = (255, 0, 0)          # Vermelho (fora)
COLOR_TEXT = (0, 0, 0)                  # Preto
COLOR_INFO_BG = (240, 240, 240)         # Cinza claro
FPS = 10                                # Frames por segundo
