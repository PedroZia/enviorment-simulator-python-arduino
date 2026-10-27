/*
 * debug_sensores.ino - leitura dos 3 sensores IR discretos (D8/D9/D10)
 * --------------------------------------------------------------------
 * Mesma pinagem do firmware principal (arduino_agent_sensors.ino):
 *
 *   D8 = sensor ESQUERDO
 *   D9 = sensor CENTRAL
 *   D10 = sensor DIREITO
 *
 *   Leitura digital: 0 = branco (fora da linha) · 1 = preto (sobre a linha)
 *   Estado codificado = (L << 2) | (C << 1) | R  ->  0..7
 *   (mesma codificacao usada pelo Q-learning do projeto)
 *
 * Uso:
 *   1. Suba este sketch no Arduino (nao interfere no firmware).
 *   2. Abra o Monitor Serial a 9600 baud.
 *   3. Passe cada sensor sobre a linha e confira a coluna correspondente:
 *      imprime na hora que a leitura muda e repete a cada REPORT_MS.
 *
 * Ligacao tipica de um modulo IR:
 *   VCC -> 5V · GND -> GND · OUT -> D8/D9/D10
 *   (se a leitura sair invertida, o seu modulo marca 0 sobre a linha)
 */

// ===================== PIN CONFIG (igual ao firmware principal) =====================

#define PIN_SENSOR_L 8
#define PIN_SENSOR_C 9
#define PIN_SENSOR_R 10

// ===================== AJUSTES =====================

#define BAUD      9600   // mesma velocidade do debug_ponte_h
#define REPORT_MS 1000   // repete a leitura mesmo sem mudanca (0 = desliga)

// ===================== LEITURA =====================

int read_sensors() {
  int l = digitalRead(PIN_SENSOR_L);
  int c = digitalRead(PIN_SENSOR_C);
  int r = digitalRead(PIN_SENSOR_R);
  return (l << 2) | (c << 1) | r;
}

char sensor_char(int v) {
  return v ? 'X' : '.';   // X = preto (linha) · . = branco
}

void print_reading() {
  int state = read_sensors();
  int l = (state >> 2) & 1;
  int c = (state >> 1) & 1;
  int r = state & 1;

  Serial.print(F("L="));
  Serial.print(l);
  Serial.print(F(" C="));
  Serial.print(c);
  Serial.print(F(" R="));
  Serial.print(r);
  Serial.print(F("  estado="));
  Serial.print(state);
  Serial.print(F("  [ "));
  Serial.print(sensor_char(l));
  Serial.print(' ');
  Serial.print(sensor_char(c));
  Serial.print(' ');
  Serial.print(sensor_char(r));
  Serial.print(F(" ]"));
  if (state == 0) Serial.print(F("  <-- linha perdida"));
  Serial.println();
}

// ===================== MAIN =====================

void setup() {
  pinMode(PIN_SENSOR_L, INPUT);
  pinMode(PIN_SENSOR_C, INPUT);
  pinMode(PIN_SENSOR_R, INPUT);

  Serial.begin(BAUD);
  delay(300);  // deixa o serial/USB estabilizar

  Serial.println();
  Serial.println(F("=== LEITURA DOS SENSORES IR (D8/D9/D10) ==="));
  Serial.println(F("0 = branco (fora da linha) · 1 = preto (sobre a linha)"));
  Serial.println(F("[ ESQ  CENTRO  DIR ]  ->  X = preto · . = branco"));
}

void loop() {
  static int last_state = -1;
  static unsigned long last_report = 0;

  int state = read_sensors();

  // mudou a leitura: imprime na hora
  if (state != last_state) {
    print_reading();
    last_state = state;
    last_report = millis();
    return;
  }

  // sem mudanca: repete de tempo em tempo (mostra que esta vivo)
  if (REPORT_MS > 0 && millis() - last_report >= REPORT_MS) {
    last_report = millis();
    print_reading();
  }
}
