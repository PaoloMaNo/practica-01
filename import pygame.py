import pygame
import random
import sys

# Inicialización
pygame.init()

# Configuración
GRID_SIZE = 10
TILE_SIZE = 60
WIDTH = HEIGHT = GRID_SIZE * TILE_SIZE
FPS = 60

# Colores
GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
RED = (220, 20, 60)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)
GRAY = (105, 105, 105)
DARK_GRAY = (70, 70, 70)

# Ventana
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Conejito Recolector")
clock = pygame.time.Clock()

# Estado inicial
def iniciar_juego():
    return {
        "player_pos": [GRID_SIZE // 2, GRID_SIZE // 2],
        "player_pixel_pos": [GRID_SIZE // 2 * TILE_SIZE, GRID_SIZE // 2 * TILE_SIZE],
        "moving": False,
        "target_pixel_pos": None,
        "direction": None,
        "apples": [],
        "spikes": [],
        "game_over": False,
        "spike_move_timer": 0,
        "spike_move_delay": 100,
    }

estado = iniciar_juego()

# === FUNCIONES DE DIBUJO ===
def draw_grid():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, GREEN, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

def draw_player(pixel_pos):
    center = (int(pixel_pos[0] + TILE_SIZE//2), int(pixel_pos[1] + TILE_SIZE//2))
    radius = TILE_SIZE // 3
    pygame.draw.circle(screen, WHITE, center, radius)

def draw_apples(apples):
    for x, y, tipo in apples:
        center = (x*TILE_SIZE + TILE_SIZE//2, y*TILE_SIZE + TILE_SIZE//2)
        radius = TILE_SIZE // 4
        color = RED if tipo == "roja" else GOLD
        pygame.draw.circle(screen, color, center, radius)
        pygame.draw.rect(screen, (139,69,19), (center[0]-2, center[1]-radius-6, 4, 6))

def draw_spikes(spikes):
    for x, y in spikes:
        center = (x*TILE_SIZE + TILE_SIZE//2, y*TILE_SIZE + TILE_SIZE//2)
        pygame.draw.polygon(screen, GRAY, [
            (center[0], center[1] - 15),
            (center[0] - 10, center[1] + 10),
            (center[0] + 10, center[1] + 10)
        ])

# === FUNCIONES DE LÓGICA ===
def get_occupied_positions():
    positions = {tuple(estado["player_pos"])}
    for x, y, _ in estado["apples"]:
        positions.add((x, y))
    for x, y in estado["spikes"]:
        positions.add((x, y))
    return positions

def spawn_items():
    occupied = get_occupied_positions()
    if random.random() < 0.3:
        empty = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE) if (x, y) not in occupied]
        if empty:
            x, y = random.choice(empty)
            tipo = random.choice(["roja", "dorada"])
            estado["apples"].append((x, y, tipo))
    if len(estado["spikes"]) < 4 and random.random() < 0.5:
        empty = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE) if (x, y) not in occupied]
        if empty:
            x, y = random.choice(empty)
            estado["spikes"].append((x, y))

def handle_collisions():
    px, py = estado["player_pos"]
    nuevas_apples = []
    for x, y, tipo in estado["apples"]:
        if (x, y) != (px, py):
            nuevas_apples.append((x, y, tipo))
    estado["apples"] = nuevas_apples

    nuevas_spikes = []
    for x, y in estado["spikes"]:
        if (x, y) != (px, py):
            nuevas_spikes.append((x, y))
    estado["spikes"] = nuevas_spikes

def move_spikes():
    jugador = tuple(estado["player_pos"])
    nuevas_spikes = []
    occupied = get_occupied_positions()

    for x, y in estado["spikes"]:
        dx = 0 if x == jugador[0] else (1 if jugador[0] > x else -1)
        dy = 0 if y == jugador[1] else (1 if jugador[1] > y else -1)

        movimientos = [(x + dx, y), (x, y + dy), (x + dx, y + dy)]
        random.shuffle(movimientos)

        moved = False
        for nx, ny in movimientos:
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                if (nx, ny) == jugador:
                    nuevas_spikes.append((nx, ny))
                    moved = True
                    break
                elif (nx, ny) not in occupied:
                    nuevas_spikes.append((nx, ny))
                    moved = True
                    break

        if not moved:
            nuevas_spikes.append((x, y))

    estado["spikes"] = nuevas_spikes

def start_move(direction):
    if estado["moving"] or estado["game_over"]:
        return
    dx, dy = direction
    x, y = estado["player_pos"]
    nx, ny = x + dx, y + dy
    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
        estado["player_pos"] = [nx, ny]
        estado["target_pixel_pos"] = [nx * TILE_SIZE, ny * TILE_SIZE]
        estado["direction"] = direction
        estado["moving"] = True

# === LOOP PRINCIPAL ===
while True:
    dt = clock.tick(FPS)
    screen.fill(BLACK)

    estado["spike_move_timer"] += 1

    draw_grid()
    draw_apples(estado["apples"])
    draw_spikes(estado["spikes"])

    if estado["moving"]:
        speed = 8
        for i in (0, 1):
            if estado["player_pixel_pos"][i] < estado["target_pixel_pos"][i]:
                estado["player_pixel_pos"][i] = min(estado["player_pixel_pos"][i] + speed, estado["target_pixel_pos"][i])
            elif estado["player_pixel_pos"][i] > estado["target_pixel_pos"][i]:
                estado["player_pixel_pos"][i] = max(estado["player_pixel_pos"][i] - speed, estado["target_pixel_pos"][i])

        if estado["player_pixel_pos"] == estado["target_pixel_pos"]:
            estado["moving"] = False
            estado["direction"] = None
            handle_collisions()
            spawn_items()

    draw_player(estado["player_pixel_pos"])

    if estado["spike_move_timer"] >= estado["spike_move_delay"]:
        move_spikes()
        estado["spike_move_timer"] = 0

    pygame.display.flip()

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if estado["game_over"] and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            estado = iniciar_juego()

    # Movimiento por teclas
    keys = pygame.key.get_pressed()
    if not estado["moving"] and not estado["game_over"]:
        if keys[pygame.K_a]:
            start_move((-1, 0))
        elif keys[pygame.K_d]:
            start_move((1, 0))
        elif keys[pygame.K_w]:
            start_move((0, -1))
        elif keys[pygame.K_s]:
            start_move((0, 1))
