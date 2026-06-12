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
TURN_ANGLE = 30.0               # Graus por acao de giro
SENSOR_DISTANCE = 1.0           # Distancia dos sensores a frente (celulas)
SENSOR_SPACING = 1.0            # Espacamento lateral dos sensores (celulas)

# --- Q-Learning ---
NUM_STATES = 8                  # 3 bits dos sensores = 8 estados
NUM_ACTIONS = 5                 # Frente, Esquerda, Direita, Parar, Re
ALPHA = 0.1                     # Learning rate
GAMMA = 0.9                     # Discount factor
EPSILON_START = 1.0             # Epsilon inicial
EPSILON_END = 0.01              # Epsilon final
EPSILON_DECAY_METHOD = "linear" # "linear" ou "exponencial"

# --- Recompensa ---
REWARD_CENTER_ON_LINE = 2.0     # Sensor do meio na linha (movendo)
REWARD_LATERAL_ON_LINE = 0.5    # Sensor lateral na linha (meio fora)
REWARD_ALL_OFF_LINE = -1.0      # Todos sensores fora da linha
REWARD_STOP_ON_LINE = -2.0      # Parado em cima da linha
REWARD_STOP_OFF_LINE = -1.0     # Parado fora da linha

# --- Episodio ---
MAX_STEPS_PER_EPISODE = 500     # Limite de steps por episodio
START_POSITION = "random_line"  # "random_line" ou "fixed"
FIXED_START_X = 0               # Posicao fixa X (se START_POSITION = "fixed")
FIXED_START_Y = 0               # Posicao fixa Y (se START_POSITION = "fixed")

# --- Acoes ---
ACTION_NAMES = ["Frente", "Esquerda", "Direita", "Parar", "Re"]
ACTION_CODES = ["F", "E", "D", "P", "R"]

# Indices das acoes
ACTION_FORWARD = 0
ACTION_LEFT = 1
ACTION_RIGHT = 2
ACTION_STOP = 3
ACTION_REVERSE = 4

# --- Motores (PWM) ---
PWM_FORWARD = 100               # Velocidade para frente (0-255)
PWM_TURN = 50                   # Velocidade para curvas (0-255)
PWM_STOP = 0                    # Motores desligados

# --- Pinos Arduino (temporarios) ---
PIN_MOTOR_LEFT_PWM = 5
PIN_MOTOR_LEFT_IN1 = 6
PIN_MOTOR_LEFT_IN2 = 7
PIN_MOTOR_RIGHT_PWM = 10
PIN_MOTOR_RIGHT_IN3 = 8
PIN_MOTOR_RIGHT_IN4 = 9
PIN_SENSOR_LEFT = "A0"
PIN_SENSOR_CENTER = "A1"
PIN_SENSOR_RIGHT = "A2"
PIN_BUTTON_MODE = 2
PIN_BUTTON_RESET = 3

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
