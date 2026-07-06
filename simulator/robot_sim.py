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

        # Theta alinhado com a direcao da linha + variacao
        self.theta = self._get_line_direction(self.x, self.y)
        self.steps = 0
        self.total_reward = 0.0
        self.start_x = self.x
        self.start_y = self.y
        return self.get_sensors()

    def _get_line_direction(self, x, y) -> float:
        """Estima a direcao da linha na posicao (x, y) baseado nos vizinhos."""
        x_int, y_int = int(round(x)), int(round(y))
        
        # Procurar celulas de linha em volta (raio 3)
        found = []
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                nx, ny = x_int + dx, y_int + dy
                if self.track.is_on_line(nx, ny):
                    found.append((nx, ny))
        
        if len(found) < 2:
            # Poucos vizinhos, usar angulo aleatorio
            return np.random.uniform(0, 360)
        
        # Calcular direcao media entre vizinhos
        # Usar PCA simplificado: direcao do primeiro eigenvector
        points = np.array(found, dtype=float)
        mean = points.mean(axis=0)
        centered = points - mean
        cov = np.cov(centered.T)
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        # O eigenvector com maior eigenvalue e a direcao principal
        main_dir = eigenvectors[:, np.argmax(eigenvalues)]
        angle = math.degrees(math.atan2(main_dir[1], main_dir[0]))
        
        # Adicionar variacao aleatoria (-30 a +30 graus)
        angle += np.random.uniform(-30, 30)
        return angle % 360

    def step(self, action_code: str) -> str:
        """Executa uma acao e retorna os novos sensores."""
        self.steps += 1

        if action_code == "F":
            self._move_forward()
        elif action_code == "E":
            self._turn_left()
        elif action_code == "D":
            self._turn_right()
        else:
            raise ValueError(f"Acao desconhecida: {action_code}")

        sensors = self.get_sensors()
        reward = self.compute_reward(sensors, action_code)
        self.total_reward += reward
        return sensors

    def compute_reward(self, sensors: str, action_code: str) -> float:
        """Calcula recompensa baseada nos sensores e acao (igual ao ESP32).
        
        Tabela de recompensas:
        | Estado            | Frente | Esquerda | Direita |
        |-------------------|--------|----------|---------|
        | Centro na linha   | +2.0   | +0.5     | +0.5    |
        | Lateral esquerda  | +0.5   | +1.0     | -0.5    |
        | Lateral direita   | +0.5   | -0.5     | +1.0    |
        | Todos fora        | -1.0   | +0.5     | +0.5    |
        """
        s_esq = int(sensors[0])
        s_cen = int(sensors[1])
        s_dir = int(sensors[2])
        
        is_forward = (action_code == "F")
        is_left = (action_code == "E")
        is_right = (action_code == "D")

        # Centro na linha
        if s_cen == 1:
            return 2.0 if is_forward else 0.5

        # Apenas sensor esquerdo na linha
        if s_esq == 1 and s_dir == 0:
            if is_left:
                return 1.0    # Gira para recuperar
            elif is_right:
                return -0.5   # Gira para piorar
            else:
                return 0.5    # Frente

        # Apenas sensor direito na linha
        if s_dir == 1 and s_esq == 0:
            if is_right:
                return 1.0    # Gira para recuperar
            elif is_left:
                return -0.5   # Gira para piorar
            else:
                return 0.5    # Frente

        # Ambos laterais na linha (centro fora) - caso raro
        if s_esq == 1 and s_dir == 1:
            return 0.5 if is_forward else 0.5

        # Todos fora da linha
        if is_forward:
            return -1.0       # Seguir em frente e pior
        else:
            return 0.5        # Girar para tentar achar

    def _move_forward(self):
        """Move o robo 1 celula para frente na direcao theta."""
        theta_rad = math.radians(self.theta)
        self.x += config.ROBOT_SPEED * math.cos(theta_rad)
        self.y += config.ROBOT_SPEED * math.sin(theta_rad)
        self._apply_boundary()

    def _turn_left(self):
        """Gira o robo para a esquerda."""
        self.theta -= config.TURN_ANGLE
        self.theta = self.theta % 360

    def _turn_right(self):
        """Gira o robo para a direita."""
        self.theta += config.TURN_ANGLE
        self.theta = self.theta % 360

    def _apply_boundary(self):
        """Aplica limites da pista (wraparound ou clamp)."""
        if config.BOUNDARY_MODE == "wrap":
            self.x = self.x % self.track.width
            self.y = self.y % self.track.height
        else:
            self.x = max(0, min(self.x, self.track.width - 1))
            self.y = max(0, min(self.y, self.track.height - 1))

    def get_sensors(self) -> str:
        """Calcula os 3 sensores IR baseado na posicao atual."""
        theta_rad = math.radians(self.theta)

        # Vetor frente (direcao do movimento)
        fx = math.cos(theta_rad)
        fy = math.sin(theta_rad)

        # Vetor lateral (perpendicular a direcao)
        # Negativo para apontar para a esquerda em coordenadas de tela (y baixo)
        lx = fy
        ly = -fx

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
        lx = fy
        ly = -fx

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
