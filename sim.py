"""
Line follower robot simulator with Q-learning.
ponytail: single file, stdlib only, no GUI, no overengineering.
"""
import datetime
import math
import os
import random
import sys

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


# ===================== Q-AGENT =====================

def encode_state(left, mid, right):
    return (left << 2) | (mid << 1) | right


def choose_action(state, q, epsilon):
    if random.random() < epsilon:
        return random.randrange(N_ACTIONS)
    row = q[state]
    # Prefer straight when the values are tied (safe default on 101/111).
    best = 1
    for a in (0, 2):
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

def train_feature(track, q, episodes=FEATURE_EPISODES,
                  epsilon=FEATURE_EPSILON, save_interval=0, stamp=None):
    """Phase 1: learn 101 (gap) and 111 (wide line) on a straight track."""
    reward_log = []

    for ep in range(episodes):
        # Snapshot at the start of an interval episode: the table already has
        # the result of the previous `ep` episodes.
        if save_interval > 0 and ep > 0 and ep % save_interval == 0:
            path = save_qtable(q, ep, stamp=stamp)
            print(f'  [snapshot saved: {path}]')

        x, y = track[0]
        theta = tangent_at(0, track)

        total_reward = 0.0
        lost_steps = 0

        for _ in range(FEATURE_MAX_STEPS):
            readings = read_sensors(x, y, theta, track)
            state = encode_state(*readings)
            action = choose_action(state, q, epsilon)

            x, y, theta = robot_step(x, y, theta, action)

            next_readings = read_sensors(x, y, theta, track)
            next_state = encode_state(*next_readings)
            reward = compute_reward(next_readings, action, readings)
            q_update(q, state, action, reward, next_state)
            total_reward += reward

            if next_readings == (0, 0, 0):
                lost_steps += 1
            else:
                lost_steps = 0
            if lost_steps >= LOST_LIMIT:
                break

        reward_log.append(total_reward)
        print(f'feat {ep:3d} | R={total_reward:7.0f}')

    # Always leave a snapshot of the final feature-phase table.
    if save_interval > 0 and episodes > 0:
        path = save_qtable(q, episodes, stamp=stamp)
        print(f'  [snapshot saved: {path}]')

    return reward_log


def train(track, episodes=200, q=None, episode_offset=0,
          save_interval=0, stamp=None):
    n = len(track)
    if q is None:
        q = [[0.0] * N_ACTIONS for _ in range(N_STATES)]
    epsilon = EPS_START
    reward_log = []

    for ep in range(episodes):
        if save_interval > 0 and ep > 0 and ep % save_interval == 0:
            path = save_qtable(q, ep + episode_offset, stamp=stamp)
            print(f'  [snapshot saved: {path}]')

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
            reward = compute_reward(next_readings, action, readings)

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
        print(f'ep {ep + episode_offset:3d} | e={epsilon:.3f} | R={total_reward:7.0f} '
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
    for s in range(N_STATES):
        l, m, r = (s >> 2) & 1, (s >> 1) & 1, s & 1
        best = max(range(N_ACTIONS), key=lambda a: q[s][a])
        vals = ' '.join(
            f'{q[s][a]:+7.2f}{"*" if a == best else " "}' for a in range(N_ACTIONS)
        )
        print(f'  [{l}{m}{r}] -> {vals}')


def format_qtable(q, episode=None):
    lines = []
    if episode is not None:
        lines.append(f'episode {episode}')
    for s in range(N_STATES):
        l, m, r = (s >> 2) & 1, (s >> 1) & 1, s & 1
        best = max(range(N_ACTIONS), key=lambda a: q[s][a])
        vals = ' '.join(
            f'{q[s][a]:+7.2f}{"*" if a == best else " "}' for a in range(N_ACTIONS)
        )
        lines.append(f'  [{l}{m}{r}] -> {vals}')
    return '\n'.join(lines)


def save_qtable(q, episode=None, folder='snapshots', stamp=None):
    """Save a timestamped snapshot so older runs are never overwritten."""
    os.makedirs(folder, exist_ok=True)
    stamp = stamp or datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    name = f'qtable_{stamp}'
    if episode is not None:
        name += f'_ep{episode:04d}'
    path = os.path.join(folder, name + '.txt')
    with open(path, 'w') as f:
        f.write(format_qtable(q, episode))
    return path


if __name__ == '__main__':
    episodes = 200
    feature_episodes = FEATURE_EPISODES
    save_interval = 0
    seed = 42
    for arg in sys.argv[1:]:
        if arg.startswith('--episodes='):
            episodes = int(arg.split('=', 1)[1])
        elif arg.startswith('--feature-episodes='):
            feature_episodes = int(arg.split('=', 1)[1])
        elif arg.startswith('--save='):
            save_interval = int(arg.split('=', 1)[1])
        elif arg == '--save':
            save_interval = 10
        elif arg.startswith('--seed='):
            seed = int(arg.split('=', 1)[1])
        else:
            print(f'unknown option: {arg}')
            sys.exit(2)
    random.seed(seed)
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    track = generate_track()
    feature_track = generate_feature_track()
    total_episodes = feature_episodes + episodes
    print(f'Track: {len(track)} pts | oval {TRACK_L*2:.0f}x{TRACK_R*2:.0f} '
          f'| line_w={LINE_HALF_WIDTH*2:.1f} sensor_a={math.degrees(SENSOR_ANGLE):.0f}deg')
    print(f'States: {N_STATES} | Actions: {N_ACTIONS} | '
          f'a={ALPHA} g={GAMMA} eps_d={EPS_DECAY}')
    print(f'Phases: {feature_episodes} feature + {episodes} oval '
          f'= {total_episodes} episodes')
    if save_interval:
        print(f'Saving Q-table snapshots every {save_interval} episodes '
              f'(both phases) -> snapshots/')
    print()

    q = [[0.0] * N_ACTIONS for _ in range(N_STATES)]
    print('--- PHASE 1: feature track (101 gap / 111 wide line) ---')
    history = train_feature(feature_track, q, episodes=feature_episodes,
                            save_interval=save_interval, stamp=stamp)

    print('\n--- PHASE 2: oval track ---')
    q, oval_history = train(track, episodes=episodes, q=q,
                            episode_offset=feature_episodes,
                            save_interval=save_interval, stamp=stamp)
    history += oval_history

    print_qtable(q)

    path = save_qtable(q, episode=total_episodes, stamp=stamp)
    print(f'\nSnapshot saved: {path}')

    demo(track, q)
