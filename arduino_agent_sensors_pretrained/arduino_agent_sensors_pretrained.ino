/*
 * arduino_agent_sensors_pretrained.ino - standalone line follower with a
 * PRE-TRAINED Q-table (follows the learned policy from the first step).
 *
 * Table source: snapshots/qtable_ep_0200.txt (200 episodes trained via
 * train_serial.py + ESP32 agent). epsilon = 0, so no exploration.
 *
 *   LEARN_ONBOARD 0 -> frozen table (pure test/demo, no Q-updates)
 *   LEARN_ONBOARD 1 -> keeps learning from the pre-trained values
 *                      (set epsilon > 0 as well if you want exploration)
 *
 * Wiring (identical to arduino_agent_sensors.ino):
 *   IR sensors (digital, 0=white 1=black):
 *     D2 = left, D3 = center, D4 = right
 *   L298N motor driver:
 *     D5  = ENA  (PWM left speed)
 *     D6  = IN1  (left dir A)
 *     D7  = IN2  (left dir B)
 *     D8  = IN3  (right dir A)
 *     D9  = IN4  (right dir B)
 *     D10 = ENB  (PWM right speed)
 */

// ===================== PIN CONFIG =====================

#define PIN_SENSOR_L    2
#define PIN_SENSOR_C    3
#define PIN_SENSOR_R    4

#define PIN_ENA         5
#define PIN_IN1         6
#define PIN_IN2         7
#define PIN_IN3         8
#define PIN_IN4         9
#define PIN_ENB         10

// ===================== Q-LEARNING =====================

#define N_STATES  8
#define N_ACTIONS 3   // 0=left, 1=straight, 2=right

// Pre-trained Q-table from snapshots/qtable_ep_0200.txt
// (state = L<<2 | C<<1 | R; the snapshot marks the best action with '*')
float q[N_STATES][N_ACTIONS] = {
  //  [LCR]      left     straight     right
  { -11.23,   -9.52,   -8.83 },  // [000] -> right
  {  -1.39,   +6.67,   +7.83 },  // [001] -> right
  {  +7.71,   +8.96,   +8.35 },  // [010] -> straight
  {  +6.83,   +8.59,   +9.04 },  // [011] -> right
  {  +8.38,   +6.35,   -0.08 },  // [100] -> left
  {  +0.00,   +0.00,   +0.00 },  // [101] -> left (never visited in training)
  {  +9.01,   +8.61,   +7.21 },  // [110] -> left
  {  +3.42,   +0.74,   +0.00 },  // [111] -> left
};

const float alpha   = 0.1;
const float gama    = 0.9;
float epsilon = 0.0;
const float eps_min = 0.02;
const float eps_decay = 0.995;

#define LEARN_ONBOARD 0   // 0 = frozen table (test); 1 = keep learning from it

int prev_state = -1;
int prev_action = -1;

// ===================== MOTOR =====================

#define SPEED_BASE   120
#define SPEED_TURN   150
#define DELAY_MS     60

// ===================== EPSILON AUTO-DECAY =====================

#define DECAY_STEPS  500
unsigned long step_count = 0;


// ===================== HELPERS =====================

int read_sensors() {
  int l = digitalRead(PIN_SENSOR_L);
  int c = digitalRead(PIN_SENSOR_C);
  int r = digitalRead(PIN_SENSOR_R);
  return (l << 2) | (c << 1) | r;
}

float compute_reward(int state) {
  int l = (state >> 2) & 1;
  int c = (state >> 1) & 1;
  int r = state & 1;
  if (l == 0 && c == 0 && r == 0) return -3.0;
  float reward = 0.0;
  if (c == 1) reward += 1.0;
  if (l == 1) reward -= 0.5;
  if (r == 1) reward -= 0.5;
  return reward;
}

void set_motors(int action) {
  int left_speed  = SPEED_BASE;
  int right_speed = SPEED_BASE;

  if (action == 0) {         // turn left
    left_speed = SPEED_BASE / 2;
    right_speed = SPEED_TURN;
  } else if (action == 2) {  // turn right
    left_speed = SPEED_TURN;
    right_speed = SPEED_BASE / 2;
  }

  digitalWrite(PIN_IN1, HIGH);
  digitalWrite(PIN_IN2, LOW);
  analogWrite(PIN_ENA, left_speed);

  digitalWrite(PIN_IN3, HIGH);
  digitalWrite(PIN_IN4, LOW);
  analogWrite(PIN_ENB, right_speed);
}

void stop_motors() {
  digitalWrite(PIN_IN1, LOW);
  digitalWrite(PIN_IN2, LOW);
  digitalWrite(PIN_IN3, LOW);
  digitalWrite(PIN_IN4, LOW);
  analogWrite(PIN_ENA, 0);
  analogWrite(PIN_ENB, 0);
}


// ===================== Q-AGENT =====================

int choose_action(int state) {
  if ((float)random(1000) / 1000.0 < epsilon) {
    return random(N_ACTIONS);
  }
  int best = 0;
  for (int a = 1; a < N_ACTIONS; a++) {
    if (q[state][a] > q[state][best]) best = a;
  }
  return best;
}

void q_update(int state, int action, float reward, int next_state) {
  float best_next = q[next_state][0];
  for (int a = 1; a < N_ACTIONS; a++) {
    if (q[next_state][a] > best_next) best_next = q[next_state][a];
  }
  q[state][action] += alpha * (reward + gama * best_next - q[state][action]);
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
  stop_motors();

  randomSeed(analogRead(A0));
}

void loop() {
  // 1. read state & compute reward
  int state = read_sensors();
  float reward = compute_reward(state);

  // 2. q-update from previous step (skipped when the table is frozen)
  if (LEARN_ONBOARD && prev_state >= 0) {
    q_update(prev_state, prev_action, reward, state);
  }

  // 3. choose & execute action
  int action = choose_action(state);
  set_motors(action);
  delay(DELAY_MS);

  // 4. store for next iteration
  prev_state = state;
  prev_action = action;

  // 5. auto-decay epsilon (inert while epsilon = 0)
  step_count++;
  if (step_count % DECAY_STEPS == 0 && epsilon > eps_min) {
    epsilon *= eps_decay;
    if (epsilon < eps_min) epsilon = eps_min;
  }
}
