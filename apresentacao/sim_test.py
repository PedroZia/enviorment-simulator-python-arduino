import sys, os
base = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(base))
import re, math, random
import sim

qt = [[0.0]*3 for _ in range(8)]
for line in open(os.path.join(base, '..', 'snapshots', 'qtable_ep_0200.txt')):
    m = re.match(r'\s*\[([01]{3})\]\s*->\s*([+\-\d.]+)\s+([+\-\d.]+)\s+([+\-\d.]+)', line)
    if m:
        s = int(m.group(1), 2)
        qt[s] = [float(m.group(2)), float(m.group(3)), float(m.group(4))]

track = sim.generate_track()
def run(policy, idx=0, max_steps=600):
    x,y = track[idx]
    th = sim.tangent_at(idx, track)
    path=[(x,y)]; lost=0
    for i in range(max_steps):
        r = sim.read_sensors(x,y,th,track)
        s = sim.encode_state(*r)
        if policy=='greedy':
            a = max(range(3), key=lambda k: qt[s][k])
        else:
            a = random.randrange(3)
        x,y,th = sim.robot_step(x,y,th,a)
        path.append((x,y))
        r2 = sim.read_sensors(x,y,th,track)
        if r2==(0,0,0): lost+=1
        else: lost=0
        if lost>=15: break
    return path, r2, lost

random.seed(7)
p, r, lost = run('random')
print('random steps', len(p), 'end sensors', r, 'lost', lost)
p2, r2, lost2 = run('greedy')
print('greedy steps', len(p2), 'end sensors', r2, 'lost', lost2)
def length(p): return sum(math.dist(p[i],p[i+1]) for i in range(len(p)-1))
print('lengths', round(length(p),1), round(length(p2),1))
print('track perimeter approx', 4*sim.TRACK_L + 2*math.pi*sim.TRACK_R)
print('start', track[0], 'end', p2[-1])
