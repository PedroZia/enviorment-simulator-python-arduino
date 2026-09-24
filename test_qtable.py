"""
Validate a saved Q-table (snapshots/qtable_ep_XXXX.txt) on the simulator.

Runs greedy episodes (epsilon=0) from start points spread across the track,
with no training — useful to test a pre-trained table before flashing it
to the robot.

ponytail: reuses sim.py for track/sensors/reward; only loading + metrics here.

Usage:
    python test_qtable.py [snapshot] [--episodes=8] [--steps=1000]

Exit code: 0 if every episode stayed on the line, 1 otherwise.
"""
import math
import re
import sys

import sim

DEFAULT_SNAPSHOT = 'snapshots/qtable_ep_0200.txt'


def load_qtable(path):
    """Parse the snapshot format '  [LCR] ->  +1.23  +4.56  +7.89*'."""
    q = [[0.0] * sim.N_ACTIONS for _ in range(sim.N_STATES)]
    seen = set()
    with open(path) as f:
        for line in f:
            m = re.match(r'\s*\[([01])([01])([01])\]\s*->\s*(.*)', line)
            if not m:
                continue
            s = (int(m.group(1)) << 2) | (int(m.group(2)) << 1) | int(m.group(3))
            vals = re.findall(r'[-+]?\d+\.\d+', m.group(4))
            if len(vals) != sim.N_ACTIONS:
                raise ValueError(f'{path}: state [{m.group(1)}{m.group(2)}{m.group(3)}] '
                                 f'has {len(vals)} values, expected {sim.N_ACTIONS}')
            q[s] = [float(v) for v in vals]
            seen.add(s)
    missing = [s for s in range(sim.N_STATES) if s not in seen]
    if missing:
        print(f'warning: {path} is missing states {missing} (kept at 0.0)')
    return q


def track_perimeter(track):
    n = len(track)
    return sum(math.hypot(track[(i + 1) % n][0] - track[i][0],
                          track[(i + 1) % n][1] - track[i][1])
               for i in range(n))


def run_episode(track, q, start_idx, max_steps):
    """One greedy episode from a fixed start; returns a metrics dict."""
    x, y = track[start_idx]
    theta = sim.tangent_at(start_idx, track)

    actions = [0] * sim.N_ACTIONS
    steps = lost_steps = off_steps = 0
    max_dev = 0.0

    for _ in range(max_steps):
        readings = sim.read_sensors(x, y, theta, track)
        state = sim.encode_state(*readings)
        action = sim.choose_action(state, q, epsilon=0.0)
        actions[action] += 1

        x, y, theta = sim.robot_step(x, y, theta, action)
        steps += 1
        max_dev = max(max_dev, sim.dist_to_track(x, y, track))

        next_readings = sim.read_sensors(x, y, theta, track)
        if next_readings == (0, 0, 0):
            off_steps += 1
            lost_steps += 1
        else:
            lost_steps = 0
        if lost_steps >= sim.LOST_LIMIT:
            break

    return {'steps': steps, 'lost': lost_steps >= sim.LOST_LIMIT,
            'actions': actions, 'max_dev': max_dev, 'off_steps': off_steps}


def main():
    snapshot = DEFAULT_SNAPSHOT
    episodes = 8
    max_steps = sim.MAX_STEPS
    for arg in sys.argv[1:]:
        if arg.startswith('--episodes='):
            episodes = int(arg.split('=', 1)[1])
        elif arg.startswith('--steps='):
            max_steps = int(arg.split('=', 1)[1])
        elif arg.startswith('--'):
            print(f'unknown option: {arg}')
            sys.exit(2)
        else:
            snapshot = arg

    q = load_qtable(snapshot)
    track = sim.generate_track()
    n = len(track)
    perim = track_perimeter(track)

    print(f'snapshot: {snapshot}')
    print(f'track: {n} pts | perimeter {perim:.1f} | episodes {episodes} '
          f'| max steps {max_steps} | epsilon 0 (greedy)')

    sim.print_qtable(q)

    print('\n--- TEST RUNS (greedy, starts spread over the track) ---')
    names = ['L', 'S', 'R']
    results = []
    for ep in range(episodes):
        idx = ep * n // episodes
        r = run_episode(track, q, idx, max_steps)
        results.append(r)
        laps = r['steps'] * sim.SPEED / perim
        off_pct = 100.0 * r['off_steps'] / r['steps']
        act = ' '.join(f'{names[a]}{r["actions"][a]:4d}' for a in range(sim.N_ACTIONS))
        status = 'LOST' if r['lost'] else 'OK'
        print(f'  ep {ep:2d} | start {idx:2d} | steps {r["steps"]:4d} | laps {laps:5.2f} '
              f'| maxdev {r["max_dev"]:4.2f} | off {off_pct:4.1f}% | {act} | {status}')

    lost = sum(1 for r in results if r['lost'])
    total_steps = sum(r['steps'] for r in results)
    total_off = sum(r['off_steps'] for r in results)
    total_actions = [sum(r['actions'][a] for r in results) for a in range(sim.N_ACTIONS)]
    print('\n--- SUMMARY ---')
    print(f'episodes: {episodes} | completed: {episodes - lost}/{episodes} | lost: {lost}')
    print(f'avg laps: {sum(r["steps"] * sim.SPEED for r in results) / perim / episodes:.2f} '
          f'| worst maxdev: {max(r["max_dev"] for r in results):.2f} '
          f'| off-track: {100.0 * total_off / total_steps:.1f}%')
    print('actions: ' + ' | '.join(
        f'{names[a]} {total_actions[a]:4d} ({100.0 * total_actions[a] / total_steps:.0f}%)'
        for a in range(sim.N_ACTIONS)))

    sys.exit(1 if lost else 0)


if __name__ == '__main__':
    main()
