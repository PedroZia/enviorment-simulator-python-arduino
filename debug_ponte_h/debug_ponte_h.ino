/*
 * debug_ponte_h.ino - bancada de testes manual da ponte H (L298N)
 * ---------------------------------------------------------------
 * Mesma pinagem do firmware principal (arduino_agent_sensors.ino):
 *
 *   D3 = ENA (PWM canal A) · D4 = IN1 · D5 = IN2
 *   D11 = ENB (PWM canal B) · D6 = IN3 · D7 = IN4
 *   D8/D9/D10 = sensores IR (ESQ / centro / DIR)
 *
 * ATENCAO - fiacao real deste chassi (diagnostico de bancada):
 *   os canais estao TROCADOS e os dois motores INVERTIDOS:
 *     roda ESQUERDA <- canal B (IN3/IN4/ENB), frente = IN3 0 / IN4 1
 *     roda DIREITA  <- canal A (IN1/IN2/ENA), frente = IN1 0 / IN2 1
 *   O software ja compensa isso (funcao wheel()); nao mexer nos fios.
 *
 * O que imprime no serial (9600 baud):
 *   - relatorio continuo, 1 linha a cada REPORT_MS (ligado por padrao; 'v' alterna):
 *       [ 1234 ms] FRENTE | ESQ FRENTE@120 | DIR FRENTE@120 | sensores 010 [ . X . ]
 *   - bloco detalhado a cada tecla, com os pinos de direcao um a um:
 *       > tecla 'f' -> [ 1234 ms] modo=FRENTE
 *           ESQ: FRENTE  pwm=120  (D6=0 D7=1)
 *           DIR: FRENTE  pwm=120  (D4=0 D5=1)
 *           sensores D8/D9/D10: L=0 C=1 R=0  [ . X . ]  estado=2  (0=branco, 1=preto)
 *
 *   Sentido: FRENTE / RE (re) / LIVRE (coast) / FREIO, ja na convencao do
 *   chassi (mapeamento corrigido por software para a fiacao real).
 *
 * Uso:
 *   1. Suba este sketch no Arduino (nao interfere no firmware).
 *   2. Abra o Monitor Serial a 9600 baud.
 *   3. Digite uma tecla e pressione Enter.
 *
 * Comandos:
 *   f = frente             b = re
 *   l = gira esquerda      r = gira direita
 *   s = parar
 *   1/2 = motor ESQ frente/re      3/4 = motor DIR frente/re
 *   + / - = PWM +-20 (reaplica na hora)
 *   p = rampa de PWM 0->255 nos dois motores
 *       (acha o PWM minimo em que cada roda sai do lugar;
 *        anote e ajuste SPEED_BASE/SPEED_TURN no firmware)
 *   v = liga/desliga relatorio continuo (ligado por padrao)
 *   h = ajuda
 *
 * Checklist de bancada:
 *   - GND do Arduino LIGADO ao GND da fonte dos motores (terra comum).
 *   - Jumpers ENA/ENB do modulo L298N REMOVIDOS, senao o enable fica
 *     fixo em 5V e o PWM nao controla a velocidade.
 *   - Motores alimentados por fonte externa (nao pelo 5V do Arduino).
 */

// ===================== PIN CONFIG (igual ao firmware principal) =====================

#define PIN_SENSOR_L 8
#define PIN_SENSOR_C 9
#define PIN_SENSOR_R 10

#define PIN_ENA  3
#define PIN_IN1  4
#define PIN_IN2  5
#define PIN_IN3  6
#define PIN_IN4  7
#define PIN_ENB 11

// ===================== AJUSTES =====================

#define SPEED_DEFAULT 120
#define PWM_STEP      20
#define REPORT_MS     500   // periodo do relatorio continuo

int pwm_left  = SPEED_DEFAULT;   // velocidade PEDIDA (modos manuais)
int pwm_right = SPEED_DEFAULT;

bool report_on = true;           // relatorio continuo ligado por padrao ('v' alterna)
unsigned long last_report = 0;

// Ultimo modo pedido (para o + / - reaplicar na hora)
enum Mode {
  M_STOP, M_FWD, M_BACK, M_LEFT, M_RIGHT,
  M_LFWD, M_LBACK, M_RFWD, M_RBACK
};
Mode mode = M_STOP;

// Ultimo PWM APLICADO em cada motor (para o relatorio)
int cur_pwm_left  = 0;
int cur_pwm_right = 0;

// ===================== MOTOR =====================

// Aciona UMA roda respeitando a fiacao real do chassi:
//   ESQUERDA = canal B (IN3/IN4/ENB), invertida -> frente = IN3 LOW / IN4 HIGH
//   DIREITA  = canal A (IN1/IN2/ENA), invertida -> frente = IN1 LOW / IN2 HIGH
void wheel(bool left, bool fwd, int speed) {
  if (left) {
    digitalWrite(PIN_IN3, fwd ? LOW : HIGH);
    digitalWrite(PIN_IN4, fwd ? HIGH : LOW);
    analogWrite(PIN_ENB, speed);
  } else {
    digitalWrite(PIN_IN1, fwd ? LOW : HIGH);
    digitalWrite(PIN_IN2, fwd ? HIGH : LOW);
    analogWrite(PIN_ENA, speed);
  }
}

// Zera os PWMs antes de trocar a direcao (evita tranco/reverso brusco)
void run(bool left_fwd, int left_speed, bool right_fwd, int right_speed) {
  analogWrite(PIN_ENA, 0);
  analogWrite(PIN_ENB, 0);
  wheel(true,  left_fwd,  left_speed);
  wheel(false, right_fwd, right_speed);
  cur_pwm_left  = left_speed;
  cur_pwm_right = right_speed;
}

void stop_all() {
  digitalWrite(PIN_IN1, LOW);
  digitalWrite(PIN_IN2, LOW);
  digitalWrite(PIN_IN3, LOW);
  digitalWrite(PIN_IN4, LOW);
  analogWrite(PIN_ENA, 0);
  analogWrite(PIN_ENB, 0);
  cur_pwm_left  = 0;
  cur_pwm_right = 0;
}

void apply_mode() {
  switch (mode) {
    case M_STOP:  stop_all();                            break;
    case M_FWD:   run(true,  pwm_left,     true,  pwm_right);    break;
    case M_BACK:  run(false, pwm_left,     false, pwm_right);    break;
    case M_LEFT:  run(true,  pwm_left / 2, true,  pwm_right);    break;
    case M_RIGHT: run(true,  pwm_left,     true,  pwm_right / 2); break;
    case M_LFWD:  run(true,  pwm_left,     false, 0);            break;
    case M_LBACK: run(false, pwm_left,     false, 0);            break;
    case M_RFWD:  run(false, 0,            true,  pwm_right);    break;
    case M_RBACK: run(false, 0,            false, pwm_right);    break;
  }
}

const char* mode_name() {
  switch (mode) {
    case M_STOP:  return "PARADO";
    case M_FWD:   return "FRENTE";
    case M_BACK:  return "RE";
    case M_LEFT:  return "GIRA ESQ";
    case M_RIGHT: return "GIRA DIR";
    case M_LFWD:  return "MOTOR ESQ FRENTE";
    case M_LBACK: return "MOTOR ESQ RE";
    case M_RFWD:  return "MOTOR DIR FRENTE";
    case M_RBACK: return "MOTOR DIR RE";
  }
  return "?";
}

// ===================== RELATORIO =====================

// Traduz o par de pinos de direcao para o sentido da RODA
// (motores invertidos no chassi -> frente = LOW/HIGH nos dois canais)
const char* dir_name(int in_a, int in_b) {
  if (in_a == LOW  && in_b == HIGH) return "FRENTE";
  if (in_a == HIGH && in_b == LOW)  return "RE";
  if (in_a == LOW  && in_b == LOW)  return "LIVRE";
  return "FREIO";
}

// Leitura codificada: (L << 2) | (C << 1) | R  ->  0..7
int sensor_state() {
  return (digitalRead(PIN_SENSOR_L) << 2) |
         (digitalRead(PIN_SENSOR_C) << 1) |
          digitalRead(PIN_SENSOR_R);
}

char sensor_char(int v) {
  return v ? 'X' : '.';   // X = preto (linha) · . = branco
}

void print_sensors() {
  int s = sensor_state();
  int l = (s >> 2) & 1;
  int c = (s >> 1) & 1;
  int r = s & 1;
  Serial.print(F("    sensores D8/D9/D10: L="));
  Serial.print(l);
  Serial.print(F(" C="));
  Serial.print(c);
  Serial.print(F(" R="));
  Serial.print(r);
  Serial.print(F("  [ "));
  Serial.print(sensor_char(l));
  Serial.print(' ');
  Serial.print(sensor_char(c));
  Serial.print(' ');
  Serial.print(sensor_char(r));
  Serial.print(F(" ]  estado="));
  Serial.print(s);
  Serial.println(F("  (0=branco, 1=preto)"));
}

// Uma linha por motor: sentido comandado + PWM + nivel dos pinos
void print_motor(const char* label, int pin_a, int pin_b, int pwm) {
  int a = digitalRead(pin_a);
  int b = digitalRead(pin_b);
  Serial.print(F("    "));
  Serial.print(label);
  Serial.print(F(": "));
  Serial.print(dir_name(a, b));
  Serial.print(F("  pwm="));
  Serial.print(pwm);
  Serial.print(F("  (D"));
  Serial.print(pin_a);
  Serial.print('=');
  Serial.print(a);
  Serial.print(F(" D"));
  Serial.print(pin_b);
  Serial.print('=');
  Serial.print(b);
  Serial.println(')');
}

// Bloco detalhado (a cada tecla)
void print_status() {
  Serial.print(F("["));
  Serial.print(millis());
  Serial.print(F(" ms] modo="));
  Serial.println(mode_name());
  print_motor("ESQ", PIN_IN3, PIN_IN4, cur_pwm_left);   // esquerda = canal B
  print_motor("DIR", PIN_IN1, PIN_IN2, cur_pwm_right);  // direita  = canal A
  print_sensors();
}

// Linha compacta do relatorio continuo (mostra tudo sem apertar nada)
void print_report() {
  int s = sensor_state();
  Serial.print(F("["));
  Serial.print(millis());
  Serial.print(F(" ms] "));
  Serial.print(mode_name());
  Serial.print(F(" | ESQ "));
  Serial.print(dir_name(digitalRead(PIN_IN3), digitalRead(PIN_IN4)));
  Serial.print('@');
  Serial.print(cur_pwm_left);
  Serial.print(F(" | DIR "));
  Serial.print(dir_name(digitalRead(PIN_IN1), digitalRead(PIN_IN2)));
  Serial.print('@');
  Serial.print(cur_pwm_right);
  Serial.print(F(" | sensores "));
  Serial.print((s >> 2) & 1);
  Serial.print((s >> 1) & 1);
  Serial.print(s & 1);
  Serial.print(F(" [ "));
  Serial.print(sensor_char((s >> 2) & 1));
  Serial.print(' ');
  Serial.print(sensor_char((s >> 1) & 1));
  Serial.print(' ');
  Serial.print(sensor_char(s & 1));
  Serial.println(F(" ]"));
}

void help() {
  Serial.println();
  Serial.println(F("=== DEBUG PONTE H (L298N) ==="));
  Serial.println(F("  f=frente  b=re  l=gira esq  r=gira dir  s=parar"));
  Serial.println(F("  1/2=motor ESQ frente/re   3/4=motor DIR frente/re"));
  Serial.println(F("  + / - = PWM +-20       p = rampa de PWM"));
  Serial.println(F("  v = liga/desliga relatorio continuo   h = ajuda"));
  Serial.println(F("  relatorio: [ms] modo | ESQ dir@pwm | DIR dir@pwm | sensores LCR [visual]"));
  Serial.println(F("  mapeamento ja corrigido p/ a fiacao do chassi (canais trocados)"));
  Serial.println();
}

// ===================== RAMPA DE PWM =====================

void pwm_ramp() {
  mode = M_STOP;
  stop_all();
  Serial.println(F("[p] rampa 0->255 nos dois motores (passo 5, ~10s)"));
  Serial.println(F("    anote o primeiro valor em que CADA roda comeca a girar"));
  for (int v = 0; v <= 255; v += 5) {
    run(true, v, true, v);
    Serial.print(F("    PWM "));
    Serial.println(v);
    delay(200);
  }
  stop_all();
  Serial.println(F("    rampa concluida. Motores parados."));
  print_status();
}

// ===================== MAIN =====================

void setup() {
  pinMode(PIN_SENSOR_L, INPUT);
  pinMode(PIN_SENSOR_C, INPUT);
  pinMode(PIN_SENSOR_R, INPUT);

  pinMode(PIN_ENA, OUTPUT);
  pinMode(PIN_IN1, OUTPUT);
  pinMode(PIN_IN2, OUTPUT);
  pinMode(PIN_IN3, OUTPUT);
  pinMode(PIN_IN4, OUTPUT);
  pinMode(PIN_ENB, OUTPUT);
  stop_all();

  Serial.begin(9600);
  help();
  print_status();
  last_report = millis();
}

void loop() {
  // relatorio continuo: mostra o que esta ocorrendo sem precisar apertar nada
  if (report_on && millis() - last_report >= REPORT_MS) {
    last_report = millis();
    print_report();
  }

  if (!Serial.available()) return;

  char c = Serial.read();
  if (c == '\r' || c == '\n' || c == ' ') return;

  // eco do comando antes do status detalhado
  Serial.print(F("> tecla '"));
  Serial.print(c);
  Serial.print(F("' -> "));

  switch (c) {
    case 'f': mode = M_FWD;   apply_mode(); print_status(); break;
    case 'b': mode = M_BACK;  apply_mode(); print_status(); break;
    case 'l': mode = M_LEFT;  apply_mode(); print_status(); break;
    case 'r': mode = M_RIGHT; apply_mode(); print_status(); break;
    case 's': mode = M_STOP;  apply_mode(); print_status(); break;

    case '1': mode = M_LFWD;  apply_mode(); print_status(); break;
    case '2': mode = M_LBACK; apply_mode(); print_status(); break;
    case '3': mode = M_RFWD;  apply_mode(); print_status(); break;
    case '4': mode = M_RBACK; apply_mode(); print_status(); break;

    case '+':
      pwm_left  = min(255, pwm_left  + PWM_STEP);
      pwm_right = min(255, pwm_right + PWM_STEP);
      apply_mode();
      print_status();
      break;
    case '-':
      pwm_left  = max(0, pwm_left  - PWM_STEP);
      pwm_right = max(0, pwm_right - PWM_STEP);
      apply_mode();
      print_status();
      break;

    case 'p': pwm_ramp(); break;

    case 'v':
      report_on = !report_on;
      Serial.print(F("[v] relatorio continuo: "));
      Serial.println(report_on ? F("LIGADO") : F("DESLIGADO"));
      break;

    case 'h': help(); print_status(); break;

    default:
      Serial.print(F("comando desconhecido: '"));
      Serial.print(c);
      Serial.println(F("'  (aperte h)"));
      break;
  }
}
