"""
Line follower robot simulator with Q-learning.
ponytail: single file, stdlib only, no GUI, no overengineering.
"""
import math
import random

# ===================== CONFIG =====================

TRACK_L = 40.0        # half-length of straight sections
TRACK_R = 20.0        # radius of semicircles
TRACK_N = 60          # polyline points (ponytail: enough, fast)

SPEED = 0.8           # units per step
TURN_RATE = math.radians(15)   # rad per action step
SENSOR_DIST = 2.0     # how far ahead sensors look
SENSOR_ANGLE = math.radians(35)  # ponytail: spread > line half-width for distinct states
LINE_HALF_WIDTH = 0.8 # half-width of the line

MAX_STEPS = 1000      # max steps per episode
LOST_LIMIT = 15       # consecutive lost steps before episode ends

ALPHA = 0.1           # learning rate
GAMMA = 0.9           # discount factor
EPS_START = 1.0
EPS_MIN = 0.02
EPS_DECAY = 0.99

N_ACTIONS = 3         # 0=left, 1=straight, 2=right
N_STATES = 8          # 3 binary sensors -> 0..7


# ===================== TRACK =====================

def generate_track(L=TRACK_L, R=TRACK_R, n=TRACK_N):
    """Stadium oval: two straights + two semicircular ends."""
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


def tangent_at(idx, track):
    nxt = (idx + 1) % len(track)
    return math.atan2(track[nxt][1] - track[idx][1],
                      track[nxt][0] - track[idx][0])


# ===================== ROBOT =====================

def robot_step(x, y, theta, action):
    theta += (action - 1) * TURN_RATE   # 0=left, 1=straight, 2=right
    x += SPEED * math.cos(theta)
    y += SPEED * math.sin(theta)
    return x, y, theta


def read_sensors(x, y, theta, track):
    sx = [x + SENSOR_DIST * math.cos(theta + off)
          for off in (-SENSOR_ANGLE, 0.0, SENSOR_ANGLE)]
    sy = [y + SENSOR_DIST * math.sin(theta + off)
          for off in (-SENSOR_ANGLE, 0.0, SENSOR_ANGLE)]
    return tuple(
        1 if dist_to_track(sx[i], sy[i], track) < LINE_HALF_WIDTH else 0
        for i in range(3)
    )


def compute_reward(readings):
    l, m, r = readings
    if (l, m, r) == (0, 0, 0):
        return -3.0
    reward = 0.0
    if m == 1:
        reward += 1.0
    if l == 1:
        reward -= 0.5
    if r == 1:
        reward -= 0.5
    return reward


# ===================== Q-AGENT =====================

def encode_state(left, mid, right):
    return (left << 2) | (mid << 1) | right


def choose_action(state, q, epsilon):
    if random.random() < epsilon:
        return random.randrange(N_ACTIONS)
    row = q[state]
    best = 0
    for a in range(1, N_ACTIONS):
        if row[a] > row[best]:
            best = a
    return best


def q_update(q, state, action, reward, next_state):
    best_next = q[next_state][0]
    for a in range(1, N_ACTIONS):
        if q[next_state][a] > best_next:
            best_next = q[next_state][a]
    q[state][action] += ALPHA * (reward + GAMMA * best_next - q[state][action])


# ===================== TRAINING =====================

def train(track, episodes=200):
    n = len(track)
    q = [[0.0] * N_ACTIONS for _ in range(N_STATES)]
    epsilon = EPS_START
    reward_log = []

    for ep in range(episodes):
        idx = random.randrange(n)
        x, y = track[idx]
        theta = tangent_at(idx, track) + random.uniform(-0.3, 0.3)

        total_reward = 0.0
        lost_steps = 0

        for _ in range(MAX_STEPS):
            readings = read_sensors(x, y, theta, track)
            state = encode_state(*readings)
            action = choose_action(state, q, epsilon)

            x, y, theta = robot_step(x, y, theta, action)

            next_readings = read_sensors(x, y, theta, track)
            next_state = encode_state(*next_readings)
            reward = compute_reward(next_readings)

            q_update(q, state, action, reward, next_state)

            total_reward += reward

            if next_readings == (0, 0, 0):
                lost_steps += 1
            else:
                lost_steps = 0

            if lost_steps >= LOST_LIMIT:
                break

        reward_log.append(total_reward)
        epsilon = max(EPS_MIN, epsilon * EPS_DECAY)

        avg20 = sum(reward_log[-20:]) / min(20, len(reward_log))
        bar_len = min(int(max(0, total_reward) / 5), 40)
        print(f'ep {ep:3d} | e={epsilon:.3f} | R={total_reward:7.0f} '
              f'| avg20={avg20:7.0f} | {"#" * bar_len}')

    return q, reward_log


# ===================== DEMO =====================

def demo(track, q):
    n = len(track)
    idx = random.randrange(n)
    x, y = track[idx]
    theta = tangent_at(idx, track)

    print('\n--- DEMO (greedy policy) ---')
    print(f'start: ({x:.1f}, {y:.1f})  theta={math.degrees(theta):.0f}deg')
    names = ['<', '-', '>']

    for step in range(400):
        readings = read_sensors(x, y, theta, track)
        state = encode_state(*readings)
        action = choose_action(state, q, epsilon=0.0)
        sensor_str = ''.join(str(s) for s in readings)
        if step % 10 == 0:
            print(f'  {step:4d} | [{sensor_str}] | {names[action]} '
                  f'| ({x:6.1f},{y:6.1f}) th={math.degrees(theta):.0f}')

        x, y, theta = robot_step(x, y, theta, action)

        if readings == (0, 0, 0):
            print(f'  {step:4d} | [000] | LOST')
            break


# ===================== MAIN =====================

def print_qtable(q):
    print('\n--- Q-TABLE (best action marked) ---')
    names = [' L', ' S', ' R']
    for s in range(N_STATES):
        l, m, r = (s >> 2) & 1, (s >> 1) & 1, s & 1
        best = max(range(N_ACTIONS), key=lambda a: q[s][a])
        vals = ' '.join(
            f'{q[s][a]:+7.2f}{"*" if a == best else " "}' for a in range(N_ACTIONS)
        )
        print(f'  [{l}{m}{r}] -> {vals}')


if __name__ == '__main__':
    random.seed(42)
    track = generate_track()
    print(f'Track: {len(track)} pts | oval {TRACK_L*2:.0f}x{TRACK_R*2:.0f} '
          f'| line_w={LINE_HALF_WIDTH*2:.1f} sensor_a={math.degrees(SENSOR_ANGLE):.0f}deg')
    print(f'States: {N_STATES} | Actions: {N_ACTIONS} | '
          f'a={ALPHA} g={GAMMA} eps_d={EPS_DECAY}')
    print()

    q, history = train(track)
    print_qtable(q)
    demo(track, q)
