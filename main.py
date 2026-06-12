import sys
import os
import time
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from simulator.track import Track
from simulator.robot_sim import RobotSim
from simulator.serial_comm import SerialComm
from visualization.pygame_display import PygameDisplay


class Simulator:
    """Loop principal do simulador."""

    def __init__(self, track_path=None, use_serial=True, use_display=True):
        self.use_serial = use_serial
        self.use_display = use_display
        self.running = True
        self.episode = 0
        self.epsilon = config.EPSILON_START
        self.mode = "TREINO"
        self.steps_since_line = 0

        # Carregar pista
        self.track = Track()
        path = track_path or config.DEFAULT_TRACK
        self.track.load(path)
        print(f"[SIM] Pista carregada: {self.track}")

        # Inicializar robo
        self.robot = RobotSim(self.track)

        # Inicializar serial
        self.serial_comm = None
        if use_serial:
            self.serial_comm = SerialComm()

        # Inicializar display
        self.display = None
        if use_display:
            self.display = PygameDisplay(self.track)

    def connect_serial(self) -> bool:
        """Conecta ao Arduino."""
        if not self.serial_comm:
            return False

        print("[SIM] Procurando Arduino...")
        ports = SerialComm.list_ports()
        for device, desc in ports:
            print(f"  {device}: {desc}")

        if not self.serial_comm.connect():
            print("[SIM] Nao foi possivel conectar ao Arduino")
            print("[SIM] Verifique a porta e se o Arduino esta conectado")
            return False

        # Esperar READY
        print("[SIM] Esperando Arduino...")
        if self.serial_comm.wait_for_ready(timeout=10):
            print("[SIM] Arduino pronto!")
            return True
        else:
            print("[SIM] Arduino nao respondeu com READY")
            return False

    def start_episode(self):
        """Inicia um novo episodio."""
        self.episode += 1
        self.steps_since_line = 0

        # Resetar robo
        sensors = self.robot.reset()
        print(f"[SIM] Episodio {self.episode} iniciado - Pos: ({self.robot.x:.1f}, {self.robot.y:.1f})")

        # Enviar sensores iniciais para Arduino
        if self.serial_comm and self.serial_comm.connected:
            self.serial_comm.send_sensors(sensors, f"EPISODE:{self.episode}")

    def compute_epsilon(self):
        """Calcula epsilon atual baseado no decaimento linear."""
        decay_rate = (config.EPSILON_START - config.EPSILON_END) / max(1, self.episode)
        self.epsilon = max(config.EPSILON_END, config.EPSILON_START - decay_rate * self.episode)

    def run(self):
        """Loop principal do simulador."""
        print("[SIM] Iniciando simulador...")

        # Conectar serial se habilitado
        if self.use_serial:
            if not self.connect_serial():
                print("[SIM] Rodando sem Arduino (modo simulacao local)")

        # Iniciar primeiro episodio
        self.start_episode()

        while self.running:
            # Processar eventos do Pygame
            if self.display:
                events = self.display.handle_events()
                if events["quit"]:
                    self.running = False
                    break
                if events["reset"]:
                    self._handle_episode_end("manual")
                    continue
                if events["toggle_mode"]:
                    self._toggle_mode()

            # Receber acao do Arduino
            action = self._receive_action()
            if not action:
                continue

            # Processar acao
            self._process_action(action)

            # Renderizar
            if self.display:
                self.display.draw(
                    self.robot,
                    self.episode,
                    self.epsilon,
                    self.mode
                )

        self.shutdown()

    def _receive_action(self) -> str:
        """Recebe acao do Arduino ou gera acao local."""
        if self.serial_comm and self.serial_comm.connected:
            action = self.serial_comm.read_action()
            if action:
                return action
            return None
        else:
            # Modo sem Arduino: usar teclado
            return self._get_keyboard_action()

    def _get_keyboard_action(self) -> str:
        """Le acao do teclado (modo sem Arduino)."""
        import pygame
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            return "F"
        elif keys[pygame.K_LEFT]:
            return "E"
        elif keys[pygame.K_RIGHT]:
            return "D"
        elif keys[pygame.K_DOWN]:
            return "R"
        elif keys[pygame.K_SPACE]:
            return "P"

        # Esperar um pouco para nao consumir CPU
        pygame.time.wait(50)
        return None

    def _process_action(self, action: str):
        """Processa uma acao recebida."""
        if action not in config.ACTION_CODES:
            return

        # Executar acao no simulador
        sensors = self.robot.step(action)

        # Verificar se algum sensor esta na linha
        if "1" in sensors:
            self.steps_since_line = 0
        else:
            self.steps_since_line += 1

        # Verificar condicoes de fim de episodio
        if self._check_episode_end(sensors):
            self._handle_episode_end("auto")
            return

        # Enviar sensores para Arduino
        if self.serial_comm and self.serial_comm.connected:
            self.serial_comm.send_sensors(sensors)

    def _check_episode_end(self, sensors: str) -> bool:
        """Verifica se o episodio deve terminar."""
        # Limite de steps
        if self.robot.steps >= config.MAX_STEPS_PER_EPISODE:
            return True

        # Volta completa (coordenada inicial)
        if self.robot.check_start_line_return() and self.robot.steps > 20:
            return True

        # Todos sensores na linha (linha de partida)
        if self.robot.check_all_sensors_on_line() and self.robot.steps > 10:
            return True

        return False

    def _handle_episode_end(self, reason: str):
        """Trata o fim de um episodio."""
        print(f"[SIM] Episodio {self.episode} finalizado ({reason}) - "
              f"Steps: {self.robot.steps}, Reward: {self.robot.total_reward:.1f}")

        # Atualizar epsilon
        self.compute_epsilon()

        # Enviar RESET para Arduino
        if self.serial_comm and self.serial_comm.connected:
            self.serial_comm.send_sensors("000", "RESET")

        # Iniciar novo episodio
        time.sleep(0.5)
        self.start_episode()

    def _toggle_mode(self):
        """Alterna entre modo Treino e Aplicacao."""
        if self.mode == "TREINO":
            self.mode = "APLICACAO"
            self.epsilon = 0.0
        else:
            self.mode = "TREINO"
            self.compute_epsilon()
        print(f"[SIM] Modo alterado: {self.mode}")

    def shutdown(self):
        """Encerra o simulador."""
        print("[SIM] Encerrando...")
        if self.serial_comm:
            self.serial_comm.disconnect()
        if self.display:
            self.display.close()
        print("[SIM] Encerrado.")


def main():
    """Funcao principal."""
    import argparse

    parser = argparse.ArgumentParser(description="Simulador Seguidor de Linha com Q-Learning")
    parser.add_argument("--track", type=str, default=None, help="Caminho da pista (.npy)")
    parser.add_argument("--no-serial", action="store_true", help="Rodar sem Arduino (teclado)")
    parser.add_argument("--no-display", action="store_true", help="Rodar sem visualizacao")
    parser.add_argument("--generate-tracks", action="store_true", help="Gerar pistas de exemplo")
    parser.add_argument("--port", type=str, default=None, help="Porta serial do Arduino")

    args = parser.parse_args()

    # Gerar pistas se solicitado
    if args.generate_tracks:
        from tracks.track_generator import generate_all_tracks
        generate_all_tracks()
        return

    # Atualizar porta se especificada
    if args.port:
        config.SERIAL_PORT = args.port

    # Verificar se pista existe
    track_path = args.track or config.DEFAULT_TRACK
    if not os.path.exists(track_path):
        print(f"[ERRO] Pista nao encontrada: {track_path}")
        print("[DICA] Execute com --generate-tracks para criar pistas de exemplo")
        return

    # Criar e executar simulador
    sim = Simulator(
        track_path=track_path,
        use_serial=not args.no_serial,
        use_display=not args.no_display
    )
    sim.run()


if __name__ == "__main__":
    main()
