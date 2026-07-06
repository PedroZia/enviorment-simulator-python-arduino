/*
 * Line Follower Robot - Controle Discreto (versao ESP32)
 * 
 * Controle simples: 
 *   - Linha no centro → Frente (F)
 *   - Linha na esquerda → Esquerda (E)
 *   - Linha na direita → Direita (D)
 *   - Todos fora → Mantem ultima acao
 * 
 * Comunicacao serial com Python (simulador):
 *   Arduino envia: acao (F, E, D)
 *   Python envia: sensores (ex: 101) ou sensores:RESET ou sensores:EPISODE:N
 */

#include <math.h>

// =============================================================================
// PINOS ESP32
// =============================================================================
#define PIN_MOTOR_ENA   5    // PWM motor esquerdo
#define PIN_MOTOR_IN1   18
#define PIN_MOTOR_IN2   19
#define PIN_MOTOR_ENB   23   // PWM motor direito
#define PIN_MOTOR_IN3   16
#define PIN_MOTOR_IN4   17
#define PIN_SENSOR_ESQ  32
#define PIN_SENSOR_CEN  33
#define PIN_SENSOR_DIR  34
#define PIN_BTN_MODE    2
#define PIN_BTN_RESET   4

// =============================================================================
// LEDC PWM (ESP32 core 3.x)
// =============================================================================
#define LEDC_FREQ         5000   // 5 kHz para motores
#define LEDC_RESOLUTION   8      // 8 bits (0-255)

// =============================================================================
// CONTROLE
// =============================================================================
#define PWM_BASE  100  // Velocidade base

char last_action = 'F';  // Ultima acao (para quando perder a linha)
bool waiting_for_sensors = false;
unsigned long step_count = 0;
unsigned long max_steps = 500;

// Sensores recebidos do Python
int s_esq = 0;
int s_cen = 0;
int s_dir = 0;

// Debounce botoes
unsigned long last_btn_mode_press = 0;
unsigned long last_btn_reset_press = 0;
#define DEBOUNCE_MS 300

// =============================================================================
// SETUP
// =============================================================================
void setup() {
  Serial.begin(115200);
  
  // Motores - pinos digitais
  pinMode(PIN_MOTOR_IN1, OUTPUT);
  pinMode(PIN_MOTOR_IN2, OUTPUT);
  pinMode(PIN_MOTOR_IN3, OUTPUT);
  pinMode(PIN_MOTOR_IN4, OUTPUT);
  
  // LEDC PWM setup para ESP32 (core 3.x)
  ledcAttach(PIN_MOTOR_ENA, LEDC_FREQ, LEDC_RESOLUTION);
  ledcAttach(PIN_MOTOR_ENB, LEDC_FREQ, LEDC_RESOLUTION);
  
  // Iniciar com motores parados
  ledcWrite(PIN_MOTOR_ENA, 0);
  ledcWrite(PIN_MOTOR_ENB, 0);
  
  // Sensores (pullup interno)
  pinMode(PIN_SENSOR_ESQ, INPUT_PULLUP);
  pinMode(PIN_SENSOR_CEN, INPUT_PULLUP);
  pinMode(PIN_SENSOR_DIR, INPUT_PULLUP);
  
  // Botoes
  pinMode(PIN_BTN_MODE, INPUT_PULLUP);
  pinMode(PIN_BTN_RESET, INPUT_PULLUP);
  
  // Sinalizar pronto
  delay(1000);
  Serial.println("READY");
}

// =============================================================================
// LOOP PRINCIPAL
// =============================================================================
void loop() {
  // Alimentar watchdog
  yield();
  
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
  execute_step();
}

// =============================================================================
// CONTROLE DISCRETO
// =============================================================================
char choose_action(int s_esq, int s_cen, int s_dir) {
  // Centro na linha → Frente
  if (s_cen == 1) {
    return 'F';
  }
  
  // Apenas esquerda na linha → Vira esquerda
  if (s_esq == 1 && s_dir == 0) {
    return 'E';
  }
  
  // Apenas direita na linha → Vira direita
  if (s_dir == 1 && s_esq == 0) {
    return 'D';
  }
  
  // Ambos laterais (cruzamento) → Frente
  if (s_esq == 1 && s_dir == 1) {
    return 'F';
  }
  
  // Todos fora → Manter ultima acao
  return last_action;
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
  
  // Usar sensores recebidos do Python (ou ler dos pinos se robo real)
  // Para simulador: sensores vao do Python via serial
  // Para robo real: ler dos pinos
  #ifdef USE_LOCAL_SENSORS
    s_esq = digitalRead(PIN_SENSOR_ESQ) == LOW ? 1 : 0;
    s_cen = digitalRead(PIN_SENSOR_CEN) == LOW ? 1 : 0;
    s_dir = digitalRead(PIN_SENSOR_DIR) == LOW ? 1 : 0;
  #endif
  
  // Escolher acao
  char action = choose_action(s_esq, s_cen, s_dir);
  last_action = action;
  
  // Executar acao nos motores (apenas para robo real)
  // execute_action(action);
  
  // Enviar acao para Python
  Serial.println(action);
  
  // Marcar que esta esperando sensores
  waiting_for_sensors = true;
  step_count++;
}

void execute_action(char action) {
  switch (action) {
    case 'F':
      motor_frente(PWM_BASE);
      break;
    case 'E':
      motor_esquerda(PWM_BASE);
      break;
    case 'D':
      motor_direita(PWM_BASE);
      break;
  }
}

// =============================================================================
// COMUNICACAO SERIAL
// =============================================================================
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
    s_esq = sensors_str.charAt(0) - '0';
    s_cen = sensors_str.charAt(1) - '0';
    s_dir = sensors_str.charAt(2) - '0';
  }
  
  // Processar extras
  if (extra == "RESET") {
    reset_episode();
  } else if (extra.startsWith("EPISODE:")) {
    // Python informou numero do episodio
  }
}

// =============================================================================
// MOTORES (LEDC PWM para ESP32)
// =============================================================================
void motor_frente(int pwm) {
  digitalWrite(PIN_MOTOR_IN1, HIGH);
  digitalWrite(PIN_MOTOR_IN2, LOW);
  ledcWrite(PIN_MOTOR_ENA, pwm);
  
  digitalWrite(PIN_MOTOR_IN3, HIGH);
  digitalWrite(PIN_MOTOR_IN4, LOW);
  ledcWrite(PIN_MOTOR_ENB, pwm);
}

void motor_esquerda(int pwm) {
  // Motor esquerdo para tras (ou parado), motor direito para frente
  digitalWrite(PIN_MOTOR_IN1, LOW);
  digitalWrite(PIN_MOTOR_IN2, HIGH);
  ledcWrite(PIN_MOTOR_ENA, pwm);
  
  digitalWrite(PIN_MOTOR_IN3, HIGH);
  digitalWrite(PIN_MOTOR_IN4, LOW);
  ledcWrite(PIN_MOTOR_ENB, pwm);
}

void motor_direita(int pwm) {
  // Motor esquerdo para frente, motor direito para tras (ou parado)
  digitalWrite(PIN_MOTOR_IN1, HIGH);
  digitalWrite(PIN_MOTOR_IN2, LOW);
  ledcWrite(PIN_MOTOR_ENA, pwm);
  
  digitalWrite(PIN_MOTOR_IN3, LOW);
  digitalWrite(PIN_MOTOR_IN4, HIGH);
  ledcWrite(PIN_MOTOR_ENB, pwm);
}

void motor_parar() {
  digitalWrite(PIN_MOTOR_IN1, LOW);
  digitalWrite(PIN_MOTOR_IN2, LOW);
  ledcWrite(PIN_MOTOR_ENA, 0);
  
  digitalWrite(PIN_MOTOR_IN3, LOW);
  digitalWrite(PIN_MOTOR_IN4, LOW);
  ledcWrite(PIN_MOTOR_ENB, 0);
}

// =============================================================================
// BOTOES
// =============================================================================
void check_buttons() {
  unsigned long now = millis();
  
  // Botao modo (start/stop)
  if (digitalRead(PIN_BTN_MODE) == LOW && now - last_btn_mode_press > DEBOUNCE_MS) {
    last_btn_mode_press = now;
    // Toggle running
    static bool running = true;
    running = !running;
    if (!running) {
      motor_parar();
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
  step_count = 0;
  last_action = 'F';
  
  motor_parar();
  
  Serial.println("READY");
}
