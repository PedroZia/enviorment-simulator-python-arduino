import pygame
import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class PygameDisplay:
    """Visualizacao Pygame do simulador."""

    def __init__(self, track):
        pygame.init()
        self.track = track

        # Calcular tamanho da janela
        self.cell_size = config.CELL_SIZE
        track_w = track.width * self.cell_size
        track_h = track.height * self.cell_size
        info_height = 120  # Area de informacao

        self.screen_width = track_w
        self.screen_height = track_h + info_height
        self.track_height = track_h

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption(config.WINDOW_TITLE)
        self.font = pygame.font.SysFont("consolas", 16)
        self.clock = pygame.time.Clock()

    def draw(self, robot, episode, epsilon, mode, extra_info=None):
        """Desenha o estado atual do simulador."""
        # Fundo
        self.screen.fill(config.COLOR_BACKGROUND)

        # Desenhar pista
        self._draw_track()

        # Desenhar sensores
        self._draw_sensors(robot)

        # Desenhar robo
        self._draw_robot(robot)

        # Desenhar informacoes
        self._draw_info(robot, episode, epsilon, mode, extra_info)

        pygame.display.flip()
        self.clock.tick(config.FPS)

    def _draw_track(self):
        """Desenha a pista na tela."""
        for y in range(self.track.height):
            for x in range(self.track.width):
                if self.track.grid[y, x] == 1:
                    rect = pygame.Rect(
                        x * self.cell_size,
                        y * self.cell_size,
                        self.cell_size,
                        self.cell_size
                    )
                    pygame.draw.rect(self.screen, config.COLOR_TRACK, rect)

    def _draw_robot(self, robot):
        """Desenha o robo como um triangulo."""
        cx = robot.x * self.cell_size + self.cell_size // 2
        cy = robot.y * self.cell_size + self.cell_size // 2
        size = self.cell_size * 1.2

        theta_rad = math.radians(robot.theta)

        # Pontos do triangulo
        p1 = (
            cx + size * math.cos(theta_rad),
            cy + size * math.sin(theta_rad)
        )
        p2 = (
            cx + size * 0.6 * math.cos(theta_rad + 2.5),
            cy + size * 0.6 * math.sin(theta_rad + 2.5)
        )
        p3 = (
            cx + size * 0.6 * math.cos(theta_rad - 2.5),
            cy + size * 0.6 * math.sin(theta_rad - 2.5)
        )

        pygame.draw.polygon(self.screen, config.COLOR_ROBOT, [p1, p2, p3])

    def _draw_sensors(self, robot):
        """Desenha os sensores como pontos coloridos."""
        sensor_positions = robot.get_sensor_positions()
        sensors = robot.get_sensors()

        for i, (sx, sy) in enumerate(sensor_positions):
            px = sx * self.cell_size + self.cell_size // 2
            py = sy * self.cell_size + self.cell_size // 2

            if sensors[i] == "1":
                color = config.COLOR_SENSOR_ON
            else:
                color = config.COLOR_SENSOR_OFF

            pygame.draw.circle(self.screen, color, (int(px), int(py)), 4)

    def _draw_info(self, robot, episode, epsilon, mode, extra_info=None):
        """Desenha area de informacao."""
        info_y = self.track_height
        info_rect = pygame.Rect(0, info_y, self.screen_width, 120)
        pygame.draw.rect(self.screen, config.COLOR_INFO_BG, info_rect)
        pygame.draw.line(self.screen, (200, 200, 200),
                        (0, info_y), (self.screen_width, info_y), 2)

        y = info_y + 8
        texts = [
            f"Episodio: {episode}  |  Steps: {robot.steps}  |  Modo: {mode}",
            f"Epsilon: {epsilon:.4f}  |  Reward: {robot.total_reward:.1f}",
            f"Pos: ({robot.x:.1f}, {robot.y:.1f})  Theta: {robot.theta:.0f}°",
            f"Sensores: {robot.get_sensors()}  |  [Q] Sair  [R] Reset  [T] Treino/Aplic",
        ]

        if extra_info:
            texts.append(extra_info)

        for text in texts:
            surface = self.font.render(text, True, config.COLOR_TEXT)
            self.screen.blit(surface, (10, y))
            y += 20

    def handle_events(self) -> dict:
        """Processa eventos do Pygame. Retorna dict com acoes."""
        events = {"quit": False, "reset": False, "toggle_mode": False}

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events["quit"] = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    events["quit"] = True
                elif event.key == pygame.K_r:
                    events["reset"] = True
                elif event.key == pygame.K_t:
                    events["toggle_mode"] = True

        return events

    def close(self):
        """Fecha o Pygame."""
        pygame.quit()
