import numpy as np
import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class RobotSim:
    """Simulacao do robo seguidor de linha."""

    def __init__(self, track):
        self.track = track
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0  # graus
        self.steps = 0
        self.total_reward = 0.0
        self.start_x = 0.0
        self.start_y = 0.0

    def reset(self, start_pos=None):
        """Reseta o robo para uma nova posicao inicial."""
        if start_pos:
            self.x, self.y = start_pos
        else:
            sx, sy = self.track.get_random_line_position()
            self.x = float(sx)
            self.y = float(sy)

        self.theta = np.random.uniform(0, 360)
        self.steps = 0
        self.total_reward = 0.0
        self.start_x = self.x
        self.start_y = self.y
        return self.get_sensors()

    def step(self, action_code: str) -> str:
        """Executa uma acao e retorna os novos sensores."""
        self.steps += 1

        if action_code == "F":
            self._move_forward()
        elif action_code == "E":
            self._turn_left()
        elif action_code == "D":
            self._turn_right()
        elif action_code == "P":
            pass  # Parar, sem movimento
        elif action_code == "R":
            self._move_reverse()
        else:
            raise ValueError(f"Acao desconhecida: {action_code}")

        sensors = self.get_sensors()
        return sensors

    def _move_forward(self):
        """Move o robo 1 celula para frente na direcao theta."""
        theta_rad = math.radians(self.theta)
        self.x += config.ROBOT_SPEED * math.cos(theta_rad)
        self.y += config.ROBOT_SPEED * math.sin(theta_rad)
        self._clamp_position()

    def _move_reverse(self):
        """Move o robo 1 celula para tras na direcao theta."""
        theta_rad = math.radians(self.theta)
        self.x -= config.ROBOT_SPEED * math.cos(theta_rad)
        self.y -= config.ROBOT_SPEED * math.sin(theta_rad)
        self._clamp_position()

    def _turn_left(self):
        """Gira o robo para a esquerda."""
        self.theta -= config.TURN_ANGLE
        self.theta = self.theta % 360

    def _turn_right(self):
        """Gira o robo para a direita."""
        self.theta += config.TURN_ANGLE
        self.theta = self.theta % 360

    def _clamp_position(self):
        """Mantem o robo dentro dos limites da pista."""
        self.x = max(0, min(self.x, self.track.width - 1))
        self.y = max(0, min(self.y, self.track.height - 1))

    def get_sensors(self) -> str:
        """Calcula os 3 sensores IR baseado na posicao atual."""
        theta_rad = math.radians(self.theta)

        # Vetor frente (direcao do movimento)
        fx = math.cos(theta_rad)
        fy = math.sin(theta_rad)

        # Vetor lateral (perpendicular a direcao)
        lx = -fy
        ly = fx

        # Posicao do sensor central (a frente)
        cx = self.x + fx * config.SENSOR_DISTANCE
        cy = self.y + fy * config.SENSOR_DISTANCE

        # Posicao do sensor esquerdo
        ex = cx + lx * config.SENSOR_SPACING
        ey = cy + ly * config.SENSOR_SPACING

        # Posicao do sensor direito
        dx = cx - lx * config.SENSOR_SPACING
        dy = cy - ly * config.SENSOR_SPACING

        # Ler sensores
        sensor_e = 1 if self.track.is_on_line(int(round(ex)), int(round(ey))) else 0
        sensor_c = 1 if self.track.is_on_line(int(round(cx)), int(round(cy))) else 0
        sensor_d = 1 if self.track.is_on_line(int(round(dx)), int(round(dy))) else 0

        return f"{sensor_e}{sensor_c}{sensor_d}"

    def get_sensor_positions(self) -> list:
        """Retorna as posicoes (x, y) dos 3 sensores para visualizacao."""
        theta_rad = math.radians(self.theta)
        fx = math.cos(theta_rad)
        fy = math.sin(theta_rad)
        lx = -fy
        ly = fx

        cx = self.x + fx * config.SENSOR_DISTANCE
        cy = self.y + fy * config.SENSOR_DISTANCE

        ex = cx + lx * config.SENSOR_SPACING
        ey = cy + ly * config.SENSOR_SPACING

        dx = cx - lx * config.SENSOR_SPACING
        dy = cy - ly * config.SENSOR_SPACING

        return [(ex, ey), (cx, cy), (dx, dy)]

    def check_start_line_return(self) -> bool:
        """Verifica se o robo voltou a posicao inicial (volta completa)."""
        dist = math.sqrt((self.x - self.start_x) ** 2 + (self.y - self.start_y) ** 2)
        return dist < 1.5  # Tolerancia de 1.5 celulas

    def check_all_sensors_on_line(self) -> bool:
        """Verifica se todos os sensores estao na linha (linha de partida)."""
        sensors = self.get_sensors()
        return sensors == "111"

    def __str__(self):
        return f"Robot(x={self.x:.1f}, y={self.y:.1f}, theta={self.theta:.0f}, steps={self.steps})"
