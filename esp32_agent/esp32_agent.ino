/*
 * esp32_agent.ino - Q-learning line follower agent for ESP32
 * ponytail: minimal protocol, single file, no RTOS, no classes
 *
 * Protocol:
 *   Python -> ESP: "L,M,R,reward\n"   (step data)
 *   ESP -> Python: "action\n"          (0=left, 1=straight, 2=right)
 *   Python -> ESP: "R\n"              (reset episode, decay epsilon)
 *   Python -> ESP: "Q\n"              (dump Q-table)
 *   Python -> ESP: "E<value>\n"       (set epsilon, e.g. "E0" for greedy)
 */

#define N_STATES 8
#define N_ACTIONS 3

float q[N_STATES][N_ACTIONS] = {0};
float alpha   = 0.1;
float g = 0.9;
float epsilon = 1.0;
float eps_min = 0.02;
float eps_decay = 0.99;

int prev_state = -1;
int prev_action = -1;
bool ready_sent = false;

void setup() {
  Serial.begin(115200);
  while (!Serial);
  randomSeed(analogRead(0));
}

void loop() {
  if (!ready_sent) {
    Serial.println("READY");
    ready_sent = true;
  }

  if (!Serial.available()) return;

  String line = Serial.readStringUntil('\n');
  line.trim();
  if (line.length() == 0) return;

  // -- reset episode --
  if (line == "R") {
    if (epsilon > eps_min) epsilon *= eps_decay;
    if (epsilon < eps_min) epsilon = eps_min;
    prev_state = -1;
    prev_action = -1;
    return;
  }

  // -- dump Q-table --
  if (line == "Q") {
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
  if (line.startsWith("E")) {
    epsilon = line.substring(1).toFloat();
    return;
  }

  // -- normal step: "L,M,R,reward" --
  int c1 = line.indexOf(',');
  int c2 = line.indexOf(',', c1 + 1);
  int c3 = line.indexOf(',', c2 + 1);
  if (c1 < 0 || c2 < 0 || c3 < 0) return;

  int l = line.substring(0, c1).toInt();
  int m = line.substring(c1 + 1, c2).toInt();
  int r = line.substring(c2 + 1, c3).toInt();
  float reward = line.substring(c3 + 1).toFloat();

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
