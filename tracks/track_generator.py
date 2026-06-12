import numpy as np
import os


def generate_oval(width=80, height=60, thickness=2) -> np.ndarray:
    """Gera pista oval."""
    grid = np.zeros((height, width), dtype=int)
    cx, cy = width // 2, height // 2
    rx, ry = width // 2 - 5, height // 2 - 5

    for y in range(height):
        for x in range(width):
            dx = (x - cx) / rx
            dy = (y - cy) / ry
            dist = dx ** 2 + dy ** 2
            if abs(dist - 1.0) < thickness / max(rx, ry):
                grid[y, x] = 1

    return grid


def generate_curves(width=100, height=80, thickness=2) -> np.ndarray:
    """Gera pista com curvas e retas."""
    grid = np.zeros((height, width), dtype=int)
    cx, cy = width // 2, height // 2
    rx, ry = width // 3, height // 3

    for y in range(height):
        for x in range(width):
            # Semicirculo esquerdo
            dx_l = (x - rx) / rx
            dy_l = (y - cy) / ry
            dist_l = dx_l ** 2 + dy_l ** 2

            # Semicirculo direito
            dx_r = (x - (width - rx)) / rx
            dy_r = (y - cy) / ry
            dist_r = dx_r ** 2 + dy_r ** 2

            # Retas superior e inferior
            in_top_line = abs(y - (cy - ry)) < thickness and rx < x < width - rx
            in_bottom_line = abs(y - (cy + ry)) < thickness and rx < x < width - rx

            # Curvas
            in_left_curve = abs(dist_l - 1.0) < thickness / max(rx, ry) and x <= rx
            in_right_curve = abs(dist_r - 1.0) < thickness / max(rx, ry) and x >= width - rx

            if in_left_curve or in_right_curve or in_top_line or in_bottom_line:
                grid[y, x] = 1

    return grid


def generate_figure8(width=80, height=80, thickness=2) -> np.ndarray:
    """Gera pista em formato de 8."""
    grid = np.zeros((height, width), dtype=int)
    cx, cy = width // 2, height // 2
    r = min(width, height) // 4

    for y in range(height):
        for x in range(width):
            # Circulo superior
            dx1 = (x - cx) / r
            dy1 = (y - (cy - r)) / r
            dist1 = dx1 ** 2 + dy1 ** 2

            # Circulo inferior
            dx2 = (x - cx) / r
            dy2 = (y - (cy + r)) / r
            dist2 = dx2 ** 2 + dy2 ** 2

            if abs(dist1 - 1.0) < thickness / r or abs(dist2 - 1.0) < thickness / r:
                grid[y, x] = 1

    return grid


def generate_straight(width=100, height=30, thickness=2) -> np.ndarray:
    """Gera pista reta simples (para testes)."""
    grid = np.zeros((height, width), dtype=int)
    cy = height // 2

    for x in range(width):
        for dy in range(-thickness // 2, thickness // 2 + 1):
            y = cy + dy
            if 0 <= y < height:
                grid[y, x] = 1

    return grid


def save_track(grid: np.ndarray, filepath: str):
    """Salva pista em formato .npy."""
    np.save(filepath, grid)
    print(f"[TRACK] Pista salva: {filepath} ({grid.shape[1]}x{grid.shape[0]})")


def generate_all_tracks(output_dir: str = "tracks"):
    """Gera todas as pistas de exemplo."""
    os.makedirs(output_dir, exist_ok=True)

    tracks = {
        "oval": generate_oval(80, 60),
        "curves": generate_curves(100, 80),
        "figure8": generate_figure8(80, 80),
        "straight": generate_straight(100, 30),
    }

    for name, grid in tracks.items():
        filepath = os.path.join(output_dir, f"{name}.npy")
        save_track(grid, filepath)

    print(f"[TRACK] Todas as pistas geradas em {output_dir}/")


if __name__ == "__main__":
    generate_all_tracks()
