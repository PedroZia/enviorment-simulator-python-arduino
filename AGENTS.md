# AGENTS.md - Simulador Seguidor de Linha com Q-Linearning

## Project type

Python 3.14 + Arduino UNO. No test suite, no linter, no typechecker.

## Setup

```bash
pip install -r requirements.txt
python tracks/track_generator.py   # generates oval.npy, curves.npy, etc. in tracks/
```

Dependencies: `numpy`, `pyserial`, `pygame-ce` (NOT `pygame`). pygame-ce is the community fork with Python 3.14 support.

## Run

```bash
# With Arduino
python main.py --track tracks/oval.npy --port COM3

# Without Arduino (keyboard control: arrows=move, space=stop, R=reset, T=toggle mode)
python main.py --no-serial --track tracks/oval.npy
```

## Architecture

- `config.py` — all constants (serial port, Q-learning params, reward values, pin mapping)
- `main.py` — entry point, `Simulator` class orchestrates everything
- `simulator/track.py` — loads track from .npy/.csv/.image
- `simulator/robot_sim.py` — simulates robot position (x, y, theta), computes IR sensor readings
- `simulator/serial_comm.py` — serial communication with Arduino
- `visualization/pygame_display.py` — pygame-ce display
- `arduino/line_follower/line_follower.ino` — Arduino Q-learning code (upload via Arduino IDE)
- `tracks/track_generator.py` — generates example tracks

## Communication protocol

Arduino sends action code (`F`/`E`/`D`/`P`/`R`), Python responds with 3-bit sensor string (e.g. `101`). Optional suffixes: `:RESET`, `:EPISODE:N`.

## Gotchas

- All modules use `sys.path.insert(0, os.path.dirname(...))` to find `config.py`. Run from project root.
- Port defaults to `COM3` in `config.py`. Change via `--port` flag or edit the file.
- Arduino expects `READY\n` handshake on connect before starting Q-learning loop.
- Tracks must exist as `.npy` files before running. Run `python tracks/track_generator.py` first.
