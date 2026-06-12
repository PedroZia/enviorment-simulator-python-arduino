import serial
import serial.tools.list_ports
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class SerialComm:
    """Gerencia comunicacao serial com Arduino."""

    def __init__(self, port=None, baudrate=None):
        self.port = port or config.SERIAL_PORT
        self.baudrate = baudrate or config.BAUD_RATE
        self.ser = None
        self.connected = False

    def connect(self) -> bool:
        """Conecta ao Arduino via serial."""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=config.SERIAL_TIMEOUT
            )
            time.sleep(2)  # Esperar Arduino resetar apos conexao
            self.connected = True
            print(f"[SERIAL] Conectado a {self.port} @ {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            print(f"[SERIAL] Erro ao conectar: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Desconecta do Arduino."""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False
        print("[SERIAL] Desconectado")

    def send_sensors(self, sensors: str, extra: str = ""):
        """Envia estado dos sensores para Arduino."""
        if not self.connected:
            return
        msg = sensors
        if extra:
            msg += f":{extra}"
        msg += "\n"
        self.ser.write(msg.encode("ascii"))

    def read_action(self) -> str:
        """Le acao enviada pelo Arduino."""
        if not self.connected:
            return ""
        try:
            line = self.ser.readline().decode("ascii").strip()
            return line
        except Exception:
            return ""

    def wait_for_ready(self, timeout=5.0) -> bool:
        """Espera mensagem READY do Arduino."""
        if not self.connected:
            return False
        start = time.time()
        while time.time() - start < timeout:
            msg = self.read_action()
            if msg == "READY":
                return True
        return False

    def flush(self):
        """Limpa buffer serial."""
        if self.connected:
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()

    @staticmethod
    def list_ports() -> list:
        """Lista portas seriais disponiveis."""
        ports = serial.tools.list_ports.comports()
        return [(p.device, p.description) for p in ports]

    def __str__(self):
        status = "Conectado" if self.connected else "Desconectado"
        return f"Serial({self.port} @ {self.baudrate}, {status})"
