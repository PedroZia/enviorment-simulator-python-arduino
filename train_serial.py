"""
Train line follower using ESP32/Arduino as Q-learning agent via serial.
ponytail: environment simulator only — track, robot, sensors, rewards.
           All Q-learning runs on the MCU.
"""
import datetime
import math
import os
import random
import time
import sys

try:
    import serial
except ImportError:
    serial = None  # ponytail: allow --fake mode without pyserial

# ===================== CONFIG =====================

TRACK_L = 40.0
TRACK_R = 20.0
TRACK_N = 60

SPEED = 0.8
TURN_RATE = math.radians(15)
SENSOR_DIST = 2.0
SENSOR_ANGLE = math.radians(35)
LINE_HALF_WIDTH = 0.8

MAX_STEPS = 1000
LOST_LIMIT = 15
EPISODES = 200
EPS_DECAY = 0.99   # ponytail: Python needs this for progress display only

PORT = 'COM3'      # ponytail: change to your ESP32/Arduino port
BAUD = 115200

# Ambiguous states: crossing with a central gap and thick/wide line.
# They are trained on a separate straight track (see generate_feature_track).
CROSS_STATES = ((1, 0, 1), (1, 1, 1))
CROSS_STRAIGHT_BONUS = 2.0
CROSS_TURN_PENALTY = -2.0

# Lost-line recovery: keep searching straight instead of turning at random.
# The straight reward stays negative so losing the line is never attractive.
LOST_TURN_PENALTY = -3.0

# Feature track used before the oval: wide line -> 111, gap -> 101.
FEATURE_EPISODES = 40
FEATURE_EPSILON = 0.10
FEATURE_MAX_STEPS = 140
FEATURE_X_MIN = -35.0
FEATURE_X_MAX = 35.0
FEATURE_WIDE_ZONE = (-15.0, -5.0)
FEATURE_WIDE_HALF_WIDTH = 1.4
FEATURE_GAP_ZONE = (5.0, 9.0)
FEATURE_CROSS_ZONE = (4.5, 9.5)
FEATURE_CROSS_Y = (1.0, 3.5)


# ===================== TRACK =====================

def generate_track(L=TRACK_L, R=TRACK_R, n=TRACK_N):
    pts = []
    step = n // 4
    for i in range(step):
        a = -math.pi / 2 + (i / step) * math.pi
        pts.append((L + R * math.cos(a), R * math.sin(a)))
    for i in range(step):
        t = i / step
        pts.append((L - 2 * L * t, R))
    for i in range(step):
        a = math.pi / 2 + (i / step) * math.pi
        pts.append((-L + R * math.cos(a), R * math.sin(a)))
    for i in range(step):
        t = i / step
        pts.append((-L + 2 * L * t, -R))
    return pts


def _dist_point_seg(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    d2 = dx * dx + dy * dy
    if d2 == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / d2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def dist_to_track(x, y, track):
    n = len(track)
    best = float('inf')
    for i in range(n):
        j = (i + 1) % n
        d = _dist_point_seg(x, y, track[i][0], track[i][1],
                            track[j][0], track[j][1])
        if d < best:
            best = d
    return best


class FeatureTrack(list):
    """Straight track with a wide line and a central-gap crossing."""


def generate_feature_track():
    return FeatureTrack((x * 1.0, 0.0)
                        for x in range(int(FEATURE_X_MIN), int(FEATURE_X_MAX) + 1))


def _on_feature_ink(x, y):
    # normal line, interrupted at the central gap
    base = (FEATURE_X_MIN <= x <= FEATURE_X_MAX
            and abs(y) < LINE_HALF_WIDTH
            and not (FEATURE_GAP_ZONE[0] <= x <= FEATURE_GAP_ZONE[1]))
    # wide section: side beams also see the line -> 111
    wide = (FEATURE_WIDE_ZONE[0] <= x <= FEATURE_WIDE_ZONE[1]
            and abs(y) < FEATURE_WIDE_HALF_WIDTH)
    # perpendicular crossing, with a central gap -> 101
    cross = (FEATURE_CROSS_ZONE[0] <= x <= FEATURE_CROSS_ZONE[1]
             and FEATURE_CROSS_Y[0] <= abs(y) <= FEATURE_CROSS_Y[1])
    return base or wide or cross


def is_on_ink(x, y, track):
    if isinstance(track, FeatureTrack):
        return _on_feature_ink(x, y)
    return dist_to_track(x, y, track) < LINE_HALF_WIDTH


def tangent_at(idx, track):
    nxt = (idx + 1) % len(track)
    return math.atan2(track[nxt][1] - track[idx][1],
                      track[nxt][0] - track[idx][0])


# ===================== ROBOT =====================

def robot_step(x, y, theta, action):
    theta += (action - 1) * TURN_RATE
    x += SPEED * math.cos(theta)
    y += SPEED * math.sin(theta)
    return x, y, theta


def read_sensors(x, y, theta, track):
    sx = [x + SENSOR_DIST * math.cos(theta + off)
          for off in (-SENSOR_ANGLE, 0.0, SENSOR_ANGLE)]
    sy = [y + SENSOR_DIST * math.sin(theta + off)
          for off in (-SENSOR_ANGLE, 0.0, SENSOR_ANGLE)]
    return tuple(
        1 if is_on_ink(sx[i], sy[i], track) else 0
        for i in range(3)
    )


def compute_reward(readings, action=None, current=None):
    """Reward for reaching `readings` with `action`.

    `current` is the state the action was taken from. It is used to teach the
    ambiguous crossing/wide states to go straight; when omitted the reached
    state itself is used.
    """
    l, m, r = readings
    if (l, m, r) == (0, 0, 0):
        # Lost the line: going straight is the best search move.
        reward = -1.0 if action == 1 else -3.0
    else:
        reward = 0.0
        if m == 1:
            reward += 1.0
        if l == 1:
            reward -= 0.5
        if r == 1:
            reward -= 0.5

    src = readings if current is None else current
    if action is not None:
        if src == (0, 0, 0):
            if action != 1:
                reward += LOST_TURN_PENALTY
        elif src in CROSS_STATES:
            reward += CROSS_STRAIGHT_BONUS if action == 1 else CROSS_TURN_PENALTY
    return reward


# ===================== SERIAL =====================

def connect_serial(port, baud, retries=10):
    for i in range(retries):
        try:
            ser = serial.Serial(port, baud, timeout=2)
            print(f'Connecting to {port}...')
            # wait for ESP32 READY signal
            t0 = time.time()
            while time.time() - t0 < 5:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line == 'READY':
                    print(f'Connected!')
                    return ser
            ser.close()
        except serial.SerialException as e:
            print(f'  attempt {i+1}: {e}')
        time.sleep(1)
    raise Exception(f'Could not connect to {port}')


def send_step(ser, readings, reward):
    """Send sensor state and previous reward; return MCU's action."""
    msg = f'{readings[0]},{readings[1]},{readings[2]},{reward}\n'
    ser.write(msg.encode())
    ser.flush()
    resp = ser.readline().decode('utf-8', errors='ignore').strip()
    if resp == '':
        return None
    return int(resp)


def reset_esp(ser):
    ser.write(b'R\n')
    ser.flush()


def get_qtable(ser):
    """Request Q-table dump from ESP32."""
    ser.write(b'Q\n')
    ser.flush()
    q = [[0.0] * 3 for _ in range(8)]
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line == 'END':
            break
        if line == '':
            continue
        parts = line.split(',')
        if len(parts) >= 4:
            s = int(parts[0])
            for a in range(3):
                q[s][a] = float(parts[a + 1])
    return q


def set_epsilon(ser, eps):
    ser.write(f'E{eps}\n'.encode())
    ser.flush()


# ===================== SAVE =====================

def format_qtable(q, episode=None):
    lines = []
    if episode is not None:
        lines.append(f'episode {episode}')
    for s in range(8):
        l, m, r = (s >> 2) & 1, (s >> 1) & 1, s & 1
        best = max(range(3), key=lambda a: q[s][a])
        vals = ' '.join(f'{q[s][a]:+7.2f}{"*" if a == best else " "}' for a in range(3))
        lines.append(f'  [{l}{m}{r}] -> {vals}')
    return '\n'.join(lines)


def save_qtable(q, episode, folder='snapshots', stamp=None):
    """Save a timestamped snapshot so older runs are never overwritten."""
    os.makedirs(folder, exist_ok=True)
    stamp = stamp or datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    path = os.path.join(folder, f'qtable_{stamp}_ep{episode:04d}.txt')
    with open(path, 'w') as f:
        f.write(format_qtable(q, episode))
    return path


def save_history(reward_log, filepath='history.csv'):
    with open(filepath, 'w') as f:
        f.write('episode,reward\n')
        for ep, r in enumerate(reward_log):
            f.write(f'{ep},{r:.1f}\n')
    return filepath


# ===================== FAKE ESP32 =====================

N_STATES = 8
N_ACTIONS = 3
ALPHA = 0.1
GAMMA = 0.9
EPS_START = 1.0
EPS_MIN = 0.02

class FakeESP32:
    """ponytail: mimics ESP32 serial protocol in pure Python for local testing."""
    def __init__(self):
        self.q = [[0.0] * N_ACTIONS for _ in range(N_STATES)]
        self.epsilon = EPS_START
        self.prev_state = -1
        self.prev_action = -1
        self._buf = []  # ponytail: buffer for simulated serial reads

    def _choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randrange(N_ACTIONS)
        # Prefer straight when the values are tied (safe default on 101/111).
        best = 1
        for a in (0, 2):
            if self.q[state][a] > self.q[state][best]:
                best = a
        return best

    def write(self, data):
        msg = data.decode() if isinstance(data, bytes) else data
        msg = msg.strip()
        if msg == 'R':
            self.epsilon = max(EPS_MIN, self.epsilon * EPS_DECAY)
            self.prev_state = -1
            self.prev_action = -1
        elif msg == 'Q':
            for s in range(N_STATES):
                parts = [str(s)] + [f'{self.q[s][a]:.4f}' for a in range(N_ACTIONS)]
                self._buf.append(','.join(parts))
            self._buf.append('END')
        elif msg.startswith('E'):
            self.epsilon = float(msg[1:]) if len(msg) > 1 else 0.0
        else:
            parts = msg.split(',')
            if len(parts) == 4:
                l, m, r = int(parts[0]), int(parts[1]), int(parts[2])
                reward = float(parts[3])
                state = (l << 2) | (m << 1) | r
                if self.prev_state >= 0:
                    best_next = max(self.q[state])
                    td = reward + GAMMA * best_next - self.q[self.prev_state][self.prev_action]
                    self.q[self.prev_state][self.prev_action] += ALPHA * td
                action = self._choose_action(state)
                self._buf.append(str(action))
                self.prev_state = state
                self.prev_action = action

    def flush(self):
        pass

    def readline(self):
        while not self._buf:
            time.sleep(0.001)
        line = self._buf.pop(0)
        return (line + '\n').encode()

    def close(self):
        pass


# ===================== TRAINING =====================

def train_feature(track, ser, episodes=FEATURE_EPISODES,
                  epsilon=FEATURE_EPSILON):
    """Phase 1: learn 101 (gap) and 111 (wide line) on a straight track."""
    reward_log = []

    for ep in range(episodes):
        set_epsilon(ser, epsilon)
        reset_esp(ser)

        x, y = track[0]
        theta = tangent_at(0, track)

        total_reward = 0.0
        lost_steps = 0
        prev_reward = 0.0
        readings = read_sensors(x, y, theta, track)

        for step in range(FEATURE_MAX_STEPS):
            action = send_step(ser, readings, prev_reward)
            if action is None:
                print(f'  [serial timeout at step {step}]')
                break

            x, y, theta = robot_step(x, y, theta, action)

            next_readings = read_sensors(x, y, theta, track)
            prev_reward = compute_reward(next_readings, action, readings)
            total_reward += prev_reward

            if next_readings == (0, 0, 0):
                lost_steps += 1
            else:
                lost_steps = 0
            if lost_steps >= LOST_LIMIT:
                break

            readings = next_readings

        reward_log.append(total_reward)
        print(f'feat {ep:3d} | R={total_reward:7.0f}')

    return reward_log


def train(track, ser, episodes=EPISODES, save_interval=0, stamp=None,
          episode_offset=0):
    n = len(track)
    reward_log = []

    for ep in range(episodes):
        reset_esp(ser)

        # ponytail: save Q-table snapshot between episodes (after reset, before first step)
        if save_interval > 0 and ep > 0 and ep % save_interval == 0:
            q = get_qtable(ser)
            path = save_qtable(q, ep + episode_offset, stamp=stamp)
            print(f'  [snapshot saved: {path}]')

        idx = random.randrange(n)
        x, y = track[idx]
        theta = tangent_at(idx, track) + random.uniform(-0.3, 0.3)

        total_reward = 0.0
        lost_steps = 0
        prev_reward = 0.0
        readings = read_sensors(x, y, theta, track)

        for step in range(MAX_STEPS):
            action = send_step(ser, readings, prev_reward)
            if action is None:
                print(f'  [serial timeout at step {step}]')
                break

            x, y, theta = robot_step(x, y, theta, action)

            next_readings = read_sensors(x, y, theta, track)
            prev_reward = compute_reward(next_readings, action, readings)
            total_reward += prev_reward

            if next_readings == (0, 0, 0):
                lost_steps += 1
            else:
                lost_steps = 0
            if lost_steps >= LOST_LIMIT:
                break

            readings = next_readings

        reward_log.append(total_reward)

        avg20 = sum(reward_log[-20:]) / min(20, len(reward_log))
        bar_len = min(int(max(0, total_reward) / 5), 40)
        print(f'ep {ep + episode_offset:3d} | R={total_reward:7.0f} '
              f'| avg20={avg20:7.0f} | {"#" * bar_len}')

    return reward_log


# ===================== DEMO =====================

def demo(track, ser):
    """Run one greedy episode, printing sensor states."""
    set_epsilon(ser, 0)

    n = len(track)
    idx = random.randrange(n)
    x, y = track[idx]
    theta = tangent_at(idx, track)

    print('\n--- DEMO (greedy) ---')
    print(f'start: ({x:.1f}, {y:.1f})  theta={math.degrees(theta):.0f}deg')
    names = ['<', '-', '>']

    readings = read_sensors(x, y, theta, track)
    prev_reward = 0.0

    for step in range(400):
        action = send_step(ser, readings, prev_reward)
        if action is None:
            break

        sensor_str = ''.join(str(s) for s in readings)
        if step % 10 == 0:
            print(f'  {step:4d} | [{sensor_str}] | {names[action]} '
                  f'| ({x:6.1f},{y:6.1f}) th={math.degrees(theta):.0f}')

        x, y, theta = robot_step(x, y, theta, action)
        next_readings = read_sensors(x, y, theta, track)
        prev_reward = compute_reward(next_readings, action, readings)

        if next_readings == (0, 0, 0):
            print(f'  {step:4d} | [000] | LOST')
            break

        readings = next_readings


# ===================== MAIN =====================

if __name__ == '__main__':
    fake_mode = False
    save_interval = 0
    episodes = EPISODES
    feature_episodes = FEATURE_EPISODES
    seed = 42
    for arg in sys.argv[1:]:
        if arg.startswith('--save='):
            save_interval = int(arg.split('=', 1)[1])
        elif arg == '--save':
            save_interval = 10  # default every 10 episodes
        elif arg == '--fake':
            fake_mode = True
        elif arg.startswith('--episodes='):
            episodes = int(arg.split('=', 1)[1])
        elif arg.startswith('--feature-episodes='):
            feature_episodes = int(arg.split('=', 1)[1])
        elif arg.startswith('--seed='):
            seed = int(arg.split('=', 1)[1])
        elif arg.startswith('--'):
            print(f'unknown option: {arg}')
            sys.exit(2)
        else:
            PORT = arg

    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    total_episodes = feature_episodes + episodes

    print('Line Follower - MCU Agent Trainer')
    if fake_mode:
        print('Mode: LOCAL (--fake)')
        ser = FakeESP32()
    else:
        if serial is None:
            print('Error: pyserial not installed. Install it or use --fake mode.')
            sys.exit(1)
        print(f'Port: {PORT} | Baud: {BAUD}')
        ser = connect_serial(PORT, BAUD)

    random.seed(seed)
    track = generate_track()
    feature_track = generate_feature_track()
    print(f'Track: {len(track)} pts | oval {TRACK_L*2:.0f}x{TRACK_R*2:.0f}')
    print(f'Phases: {feature_episodes} feature + {episodes} oval '
          f'= {total_episodes} episodes | seed: {seed}')
    if save_interval:
        print(f'Saving Q-table snapshots every {save_interval} episodes -> snapshots/')
    print()

    history = []
    try:
        print('--- PHASE 1: feature track (101 gap / 111 wide line) ---')
        history += train_feature(feature_track, ser, episodes=feature_episodes)

        print('\n--- PHASE 2: oval track ---')
        set_epsilon(ser, 1.0)   # full exploration for the normal states
        history += train(track, ser, episodes=episodes,
                         save_interval=save_interval, stamp=stamp,
                         episode_offset=feature_episodes)
    except KeyboardInterrupt:
        print('\nInterrupted.')

    print('\nFetching Q-table from MCU...')
    q = get_qtable(ser)

    print('\n--- Q-TABLE ---')
    for s in range(8):
        l, m, r = (s >> 2) & 1, (s >> 1) & 1, s & 1
        best = max(range(3), key=lambda a: q[s][a])
        vals = ' '.join(f'{q[s][a]:+7.2f}{"*" if a == best else " "}' for a in range(3))
        print(f'  [{l}{m}{r}] -> {vals}')

    # save final Q-table
    final_path = save_qtable(q, total_episodes, stamp=stamp)
    print(f'\nFinal Q-table saved: {final_path}')

    # save history with the same timestamp (never overwrite old runs)
    hist_path = save_history(history, f'history_{stamp}.csv')
    print(f'Reward history saved: {hist_path}')

    demo(track, ser)
    ser.close()
    print('\nDone.')
