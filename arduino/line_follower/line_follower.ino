/*
 * Line Follower Robot - Q-Learning
 * 
 * Comunicacao serial com Python (simulador):
 *   Arduino envia: acao (F, E, D, P, R)
 *   Python envia: sensores (ex: 101) ou sensores:RESET ou sensores:EPISODE:N
 * 
 * Modos (botao pino 2):
 *   Treino: epsilon-greedy, Q-table atualizada
 *   Aplicacao: epsilon=0, melhor acao sempre
 */

#include <math.h>

// =============================================================================
// PINOS
// =============================================================================
#define PIN_MOTOR_ENA   5    // PWM motor esquerdo
#define PIN_MOTOR_IN1   6
#define PIN_MOTOR_IN2   7
#define PIN_MOTOR_ENB   10   // PWM motor direito
#define PIN_MOTOR_IN3   8
#define PIN_MOTOR_IN4   9
#define PIN_SENSOR_ESQ  A0
#define PIN_SENSOR_CEN  A1
#define PIN_SENSOR_DIR  A2
#define PIN_BTN_MODE    2
#define PIN_BTN_RESET   3

// =============================================================================
// Q-LEARNING
// =============================================================================
#define NUM_STATES      8    // 3 bits = 8 estados
#define NUM_ACTIONS     5    // F, E, D, P, R
#define ACTION_FRENTE   0
#define ACTION_ESQ      1
#define ACTION_DIR      2
#define ACTION_PARAR    3
#define ACTION_RE       4

// Parametros
float alpha = 0.1;           // Learning rate
float gamma_val = 0.9;       // Discount factor
float epsilon = 1.0;         // Exploracao
float epsilon_min = 0.01;
float epsilon_decay = 0.001; // Decaimento por episodio

// Q-table: 8 estados x 5 acoes = 40 floats (160 bytes)
float q_table[NUM_STATES][NUM_ACTIONS];

// Estado atual e acao
int current_state = 0;
int current_action = 0;
int previous_state = 0;
int previous_action = 0;

// =============================================================================
// MOTORES
// =============================================================================
#define PWM_FRENTE  100
#define PWM_CURVA   50
#define PWM_RE      50

// =============================================================================
// CONTROLE
// =============================================================================
bool modo_treino = true;       // true=treino, false=aplicacao
unsigned long step_count = 0;
unsigned long episode_count = 0;
unsigned long max_steps = 500;
int steps_sem_linha = 0;
bool waiting_for_sensors = false;

// Debounce botoes
unsigned long last_btn_mode_press = 0;
unsigned long last_btn_reset_press = 0;
#define DEBOUNCE_MS 300

// =============================================================================
// SETUP
// =============================================================================
void setup() {
  Serial.begin(115200);
  
  // Motores
  pinMode(PIN_MOTOR_ENA, OUTPUT);
  pinMode(PIN_MOTOR_IN1, OUTPUT);
  pinMode(PIN_MOTOR_IN2, OUTPUT);
  pinMode(PIN_MOTOR_ENB, OUTPUT);
  pinMode(PIN_MOTOR_IN3, OUTPUT);
  pinMode(PIN_MOTOR_IN4, OUTPUT);
  
  // Sensores (pullup interno)
  pinMode(PIN_SENSOR_ESQ, INPUT_PULLUP);
  pinMode(PIN_SENSOR_CEN, INPUT_PULLUP);
  pinMode(PIN_SENSOR_DIR, INPUT_PULLUP);
  
  // Botoes
  pinMode(PIN_BTN_MODE, INPUT_PULLUP);
  pinMode(PIN_BTN_RESET, INPUT_PULLUP);
  
  // Inicializar Q-table com zeros
  init_q_table();
  
  // Sinalizar pronto
  delay(1000);
  Serial.println("READY");
}

// =============================================================================
// LOOP PRINCIPAL
// =============================================================================
void loop() {
  // Verificar botoes
  check_buttons();
  
  // Se esta esperando sensores, ler serial
  if (waiting_for_sensors) {
    String response = read_serial();
    if (response.length() > 0) {
      process_sensor_response(response);
      waiting_for_sensors = false;
    }
    return;
  }
  
  // Se nao esta esperando, executar step
  if (!waiting_for_sensors) {
    execute_step();
  }
}

// =============================================================================
// Q-LEARNING
// =============================================================================
void init_q_table() {
  for (int s = 0; s < NUM_STATES; s++) {
    for (int a = 0; a < NUM_ACTIONS; a++) {
      q_table[s][a] = 0.0;
    }
  }
}

int choose_action(int state) {
  if (modo_treino && random(1000) < (int)(epsilon * 1000)) {
    // Exploracao: acao aleatoria
    return random(NUM_ACTIONS);
  } else {
    // Exploracao: melhor acao
    return get_best_action(state);
  }
}

int get_best_action(int state) {
  int best = 0;
  float best_val = q_table[state][0];
  
  for (int a = 1; a < NUM_ACTIONS; a++) {
    if (q_table[state][a] > best_val) {
      best_val = q_table[state][a];
      best = a;
    }
  }
  return best;
}

float get_max_q(int state) {
  float max_val = q_table[state][0];
  for (int a = 1; a < NUM_ACTIONS; a++) {
    if (q_table[state][a] > max_val) {
      max_val = q_table[state][a];
    }
  }
  return max_val;
}

void update_q_table(int prev_state, int prev_action, float reward, int new_state) {
  if (!modo_treino) return;
  
  float old_q = q_table[prev_state][prev_action];
  float max_next_q = get_max_q(new_state);
  float new_q = old_q + alpha * (reward + gamma_val * max_next_q - old_q);
  
  q_table[prev_state][prev_action] = new_q;
}

float compute_reward(int sensors, int action) {
  int s_esq = (sensors >> 2) & 1;
  int s_cen = (sensors >> 1) & 1;
  int s_dir = sensors & 1;
  
  bool stopped = (action == ACTION_PARAR);
  
  // Sensor do meio na linha (movendo)
  if (s_cen == 1 && !stopped) {
    return 2.0;
  }
  
  // Parado em cima da linha
  if (s_cen == 1 && stopped) {
    return -2.0;
  }
  
  // Sensor lateral na linha (meio fora)
  if ((s_esq == 1 || s_dir == 1) && s_cen == 0) {
    return 0.5;
  }
  
  // Todos fora da linha
  if (s_esq == 0 && s_cen == 0 && s_dir == 0) {
    return -1.0;
  }
  
  // Parado fora da linha
  if (stopped) {
    return -1.0;
  }
  
  return -1.0;
}

// =============================================================================
// EXECUCAO DE STEP
// =============================================================================
void execute_step() {
  // Verificar limite de steps
  if (step_count >= max_steps) {
    reset_episode();
    return;
  }
  
  // Ler sensores locais (para treino, se disponivel)
  // Na simulacao, os sensores vao do Python
  // No robo real, lemos diretamente
  
  // Escolher acao
  previous_state = current_state;
  previous_action = current_action;
  current_action = choose_action(current_state);
  
  // Executar acao nos motores
  execute_action(current_action);
  
  // Enviar acao para Python
  send_action(current_action);
  
  // Marcar que esta esperando sensores
  waiting_for_sensors = true;
  step_count++;
}

void execute_action(int action) {
  switch (action) {
    case ACTION_FRENTE:
      motor_frente(PWM_FRENTE);
      break;
    case ACTION_ESQ:
      motor_esquerda(PWM_CURVA);
      break;
    case ACTION_DIR:
      motor_direita(PWM_CURVA);
      break;
    case ACTION_PARAR:
      motor_parar();
      break;
    case ACTION_RE:
      motor_re(PWM_RE);
      break;
  }
}

// =============================================================================
// COMUNICACAO SERIAL
// =============================================================================
void send_action(int action) {
  char codes[] = {'F', 'E', 'D', 'P', 'R'};
  Serial.println(codes[action]);
}

String read_serial() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    return line;
  }
  return "";
}

void process_sensor_response(String response) {
  // Formato: "101" ou "101:RESET" ou "101:EPISODE:42"
  String sensors_str = "";
  String extra = "";
  
  int colon_idx = response.indexOf(':');
  if (colon_idx >= 0) {
    sensors_str = response.substring(0, colon_idx);
    extra = response.substring(colon_idx + 1);
  } else {
    sensors_str = response;
  }
  
  // Parse sensores (3 bits)
  if (sensors_str.length() >= 3) {
    int s_esq = sensors_str.charAt(0) - '0';
    int s_cen = sensors_str.charAt(1) - '0';
    int s_dir = sensors_str.charAt(2) - '0';
    
    // Converter para estado (0-7)
    current_state = (s_esq << 2) | (s_cen << 1) | s_dir;
    
    // Verificar se tem linha
    if (current_state > 0) {
      steps_sem_linha = 0;
    } else {
      steps_sem_linha++;
    }
    
    // Calcular recompensa e atualizar Q-table
    float reward = compute_reward(current_state, previous_action);
    update_q_table(previous_state, previous_action, reward, current_state);
  }
  
  // Processar extras
  if (extra == "RESET") {
    reset_episode();
  } else if (extra.startsWith("EPISODE:")) {
    // Python informou numero do episodio
    // Nao fazer nada, so registrar
  }
}

// =============================================================================
// MOTORES
// =============================================================================
void motor_frente(int pwm) {
  digitalWrite(PIN_MOTOR_IN1, HIGH);
  digitalWrite(PIN_MOTOR_IN2, LOW);
  analogWrite(PIN_MOTOR_ENA, pwm);
  
  digitalWrite(PIN_MOTOR_IN3, HIGH);
  digitalWrite(PIN_MOTOR_IN4, LOW);
  analogWrite(PIN_MOTOR_ENB, pwm);
}

void motor_esquerda(int pwm) {
  digitalWrite(PIN_MOTOR_IN1, LOW);
  digitalWrite(PIN_MOTOR_IN2, LOW);
  analogWrite(PIN_MOTOR_ENA, 0);
  
  digitalWrite(PIN_MOTOR_IN3, HIGH);
  digitalWrite(PIN_MOTOR_IN4, LOW);
  analogWrite(PIN_MOTOR_ENB, pwm);
}

void motor_direita(int pwm) {
  digitalWrite(PIN_MOTOR_IN1, HIGH);
  digitalWrite(PIN_MOTOR_IN2, LOW);
  analogWrite(PIN_MOTOR_ENA, pwm);
  
  digitalWrite(PIN_MOTOR_IN3, LOW);
  digitalWrite(PIN_MOTOR_IN4, LOW);
  analogWrite(PIN_MOTOR_ENB, 0);
}

void motor_parar() {
  digitalWrite(PIN_MOTOR_IN1, LOW);
  digitalWrite(PIN_MOTOR_IN2, LOW);
  analogWrite(PIN_MOTOR_ENA, 0);
  
  digitalWrite(PIN_MOTOR_IN3, LOW);
  digitalWrite(PIN_MOTOR_IN4, LOW);
  analogWrite(PIN_MOTOR_ENB, 0);
}

void motor_re(int pwm) {
  digitalWrite(PIN_MOTOR_IN1, LOW);
  digitalWrite(PIN_MOTOR_IN2, HIGH);
  analogWrite(PIN_MOTOR_ENA, pwm);
  
  digitalWrite(PIN_MOTOR_IN3, LOW);
  digitalWrite(PIN_MOTOR_IN4, HIGH);
  analogWrite(PIN_MOTOR_ENB, pwm);
}

// =============================================================================
// BOTOES
// =============================================================================
void check_buttons() {
  unsigned long now = millis();
  
  // Botao modo (Treino/Aplicacao)
  if (digitalRead(PIN_BTN_MODE) == LOW && now - last_btn_mode_press > DEBOUNCE_MS) {
    last_btn_mode_press = now;
    modo_treino = !modo_treino;
    if (!modo_treino) {
      epsilon = 0.0;
    } else {
      epsilon = epsilon_min; // Restaurar epsilon minimo
    }
  }
  
  // Botao reset episodio
  if (digitalRead(PIN_BTN_RESET) == LOW && now - last_btn_reset_press > DEBOUNCE_MS) {
    last_btn_reset_press = now;
    reset_episode();
  }
}

// =============================================================================
// EPISODIO
// =============================================================================
void reset_episode() {
  episode_count++;
  step_count = 0;
  steps_sem_linha = 0;
  
  // Decaimento de epsilon (linear)
  if (modo_treino) {
    epsilon = max(epsilon_min, epsilon - epsilon_decay);
  }
  
  // Resetar motores
  motor_parar();
  
  // Enviar READY para Python
  Serial.println("READY");
}
