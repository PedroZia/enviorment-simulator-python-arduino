/*
 * arduino_agent.ino - Q-learning line follower for Arduino (Uno/Nano/Mega)
 * ponytail: char buffer + strtok instead of String to avoid heap fragmentation
 *
 * Protocol (identical to ESP32 version):
 *   Python -> Arduino: "L,M,R,reward\n"
 *   Arduino -> Python: "action\n"          (0=left, 1=straight, 2=right)
 *   Python -> Arduino: "R\n"              (reset episode, decay epsilon)
 *   Python -> Arduino: "Q\n"              (dump Q-table)
 *   Python -> Arduino: "E<value>\n"       (set epsilon, e.g. "E0" for greedy)
 */

#define N_STATES 8
#define N_ACTIONS 3
#define BUF_SIZE 32

float q[N_STATES][N_ACTIONS] = {0};
float alpha   = 0.1;
float g = 0.9;
float epsilon = 1.0;
float eps_min = 0.02;
float eps_decay = 0.99;

int prev_state = -1;
int prev_action = -1;

static char buf[BUF_SIZE];
static byte buf_idx = 0;


// -- parsing helpers (ponytail: avr-libc lacks sscanf %f, use atof) --

float safe_atof(const char* s) {
  float sign = 1.0;
  if (*s == '-') { sign = -1.0; s++; }
  else if (*s == '+') s++;

  float int_part = 0.0;
  while (*s >= '0' && *s <= '9') {
    int_part = int_part * 10.0f + (*s - '0');
    s++;
  }

  if (*s != '.') return sign * int_part;
  s++;

  float frac_part = 0.0, divisor = 1.0;
  while (*s >= '0' && *s <= '9') {
    frac_part = frac_part * 10.0f + (*s - '0');
    divisor *= 10.0f;
    s++;
  }
  return sign * (int_part + frac_part / divisor);
}


// -- Arduino lacks dtostrf by default on some cores, use Serial.print(float, N) --


void process_line(const char* line) {

  // -- reset episode --
  if (line[0] == 'R' && line[1] == '\0') {
    if (epsilon > eps_min) epsilon *= eps_decay;
    if (epsilon < eps_min) epsilon = eps_min;
    prev_state = -1;
    prev_action = -1;
    return;
  }

  // -- dump Q-table --
  if (line[0] == 'Q' && line[1] == '\0') {
    for (int s = 0; s < N_STATES; s++) {
      Serial.print(s);
      for (int a = 0; a < N_ACTIONS; a++) {
        Serial.print(',');
        Serial.print(q[s][a], 4);
      }
      Serial.println();
    }
    Serial.println("END");
    return;
  }

  // -- set epsilon --
  if (line[0] == 'E') {
    epsilon = safe_atof(line + 1);
    return;
  }

  // -- normal step: "L,M,R,reward" --
  // ponytail: strtok mutates the buffer; parse into locals first
  char work[BUF_SIZE];
  strncpy(work, line, BUF_SIZE - 1);
  work[BUF_SIZE - 1] = '\0';

  char* tok = strtok(work, ",");
  if (!tok) return;
  int l = atoi(tok);

  tok = strtok(NULL, ",");
  if (!tok) return;
  int m = atoi(tok);

  tok = strtok(NULL, ",");
  if (!tok) return;
  int r = atoi(tok);

  tok = strtok(NULL, ",");
  if (!tok) return;
  float reward = safe_atof(tok);

  int state = (l << 2) | (m << 1) | r;

  // Q-update from previous step
  if (prev_state >= 0) {
    float best_next = q[state][0];
    for (int a = 1; a < N_ACTIONS; a++) {
      if (q[state][a] > best_next) best_next = q[state][a];
    }
    q[prev_state][prev_action] +=
      alpha * (reward + g * best_next - q[prev_state][prev_action]);
  }

  // epsilon-greedy action selection
  int action;
  if ((float)random(1000) / 1000.0 < epsilon) {
    action = random(N_ACTIONS);
  } else {
    action = 0;
    for (int a = 1; a < N_ACTIONS; a++) {
      if (q[state][a] > q[state][action]) action = a;
    }
  }

  Serial.println(action);

  prev_state = state;
  prev_action = action;
}


// -- main --

void setup() {
  Serial.begin(115200);
  randomSeed(analogRead(A0));  // ponytail: keep A0 floating for entropy
  Serial.println("READY");
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\r') continue;  // ponytail: ignore CR
    if (c == '\n') {
      buf[buf_idx] = '\0';
      if (buf_idx > 0) process_line(buf);
      buf_idx = 0;
    } else if (buf_idx < BUF_SIZE - 1) {
      buf[buf_idx++] = c;
    }
  }
}
