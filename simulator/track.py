import numpy as np
import os
from pathlib import Path


class Track:
    """Carrega e gere pistas de seguidor de linha."""

    def __init__(self):
        self.grid = None
        self.height = 0
        self.width = 0

    def load(self, filepath: str) -> np.ndarray:
        """Carrega pista de arquivo (.npy, .csv, .png, .bmp)."""
        ext = Path(filepath).suffix.lower()

        if ext == ".npy":
            self.grid = np.load(filepath)
        elif ext == ".csv":
            self.grid = np.loadtxt(filepath, delimiter=",", dtype=int)
        elif ext in (".png", ".bmp", ".jpg", ".jpeg"):
            self.grid = self._load_image(filepath)
        else:
            raise ValueError(f"Formato nao suportado: {ext}")

        # Garantir que e binario (0 ou 1)
        self.grid = (self.grid > 0).astype(int)
        self.height, self.width = self.grid.shape
        return self.grid

    def _load_image(self, filepath: str) -> np.ndarray:
        """Carrega imagem e converte para matriz binaria."""
        try:
            import cv2
            img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise FileNotFoundError(f"Nao foi possivel carregar: {filepath}")
            # Limiarizacao
            _, binary = cv2.threshold(img, 127, 1, cv2.THRESH_BINARY)
            return binary
        except ImportError:
            raise ImportError("opencv-python necessario para carregar imagens")

    def get_line_cells(self) -> list:
        """Retorna lista de (x, y) de todas as celulas que sao linha."""
        cells = []
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y, x] == 1:
                    cells.append((x, y))
        return cells

    def is_on_line(self, x: int, y: int) -> bool:
        """Verifica se uma posicao esta na linha."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y, x] == 1
        return False

    def get_random_line_position(self) -> tuple:
        """Retorna uma posicao aleatoria sobre a linha."""
        line_cells = self.get_line_cells()
        if not line_cells:
            raise ValueError("Pista nao contem nenhuma linha")
        idx = np.random.randint(0, len(line_cells))
        return line_cells[idx]

    def __str__(self):
        if self.grid is None:
            return "Track(nao carregada)"
        return f"Track({self.width}x{self.height}, {np.sum(self.grid)} celulas de linha)"
