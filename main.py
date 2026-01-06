import pygame
import random
import sys
import math

# --- CONSTANTS ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
GRID_SIZE = 8
CELL_SIZE = 50
GRID_MARGIN = (SCREEN_WIDTH - (GRID_SIZE * CELL_SIZE)) // 2
GRID_TOP = 120

# --- COLORS ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BG = (5, 8, 20)

BLOCK_COLORS = [
    (255, 100, 100), (100, 255, 150), (100, 180, 255),
    (255, 230, 100), (230, 130, 255), (100, 255, 240), (255, 170, 100)
]

SHAPES = [
    [(0, 0)], [(0, 0), (1, 0)], [(0, 0), (0, 1)],
    [(0, 0), (1, 0), (2, 0)], [(0, 0), (0, 1), (0, 2)],
    [(0, 0), (1, 0), (0, 1), (1, 1)], [(0, 0), (1, 0), (2, 0), (0, 1)],
    [(0, 0), (1, 0), (2, 0), (2, 1)], [(0, 0), (0, 1), (0, 2), (1, 2)],
    [(1, 0), (1, 1), (1, 2), (0, 2)], [(0, 0), (1, 0), (1, 1), (2, 1)],
    [(1, 0), (2, 0), (0, 1), (1, 1)], [(0, 0), (1, 0), (2, 0), (1, 1)]
]

# --- GLOBAL GAME STATE ---
grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
score = 0
game_over = False
available_blocks = [] # List of dictionaries
dragging_block = None
aurora_time = 0

# --- FUNCTIONS ---

def draw_glass_rect(surface, color, rect):
    """Draws a rectangle with Apple's 'Liquid Glass' effect."""
    # Base translucent layer
    base_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(base_surf, (*color, 180), (0, 0, rect.width, rect.height), border_radius=12)
    surface.blit(base_surf, (rect.x, rect.y))
    
    # Inner Glow / Bevel
    highlight_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(highlight_surf, (255, 255, 255, 80), (2, 2, rect.width-4, rect.height//2), border_radius=12)
    surface.blit(highlight_surf, (rect.x, rect.y))
    
    # Glass Reflection
    reflect_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.polygon(reflect_surf, (255, 255, 255, 40), [
        (rect.width*0.2, 0), (rect.width*0.5, 0), 
        (rect.width*0.3, rect.height), (0, rect.height)
    ])
    surface.blit(reflect_surf, (rect.x, rect.y))

    # Border and Shadow
    pygame.draw.rect(surface, (255, 255, 255, 100), rect, 1, border_radius=12)
    shadow_color = [max(0, c - 80) for c in color]
    pygame.draw.rect(surface, (*shadow_color, 100), (rect.x+2, rect.bottom-6, rect.width-4, 4), border_radius=12)

def draw_aurora(surface):
    global aurora_time
    aurora_time += 1
    surface.fill(DARK_BG)
    aurora_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    
    waves = [
        {"color": (0, 255, 180), "amp": 50, "freq": 0.01, "speed": 0.015, "y": 250},
        {"color": (100, 100, 255), "amp": 70, "freq": 0.007, "speed": -0.01, "y": 400},
        {"color": (200, 50, 255), "amp": 60, "freq": 0.009, "speed": 0.008, "y": 550},
    ]
    
    for w in waves:
        for x in range(0, SCREEN_WIDTH + 20, 20):
            y_var = math.sin(x * w["freq"] + aurora_time * w["speed"]) * w["amp"]
            y_var += math.sin(x * 0.004 + aurora_time * 0.012) * 30
            y_pos = w["y"] + y_var
            
            for glow in range(10):
                alpha = int(30 * (1 - glow / 10))
                shimmer = (math.sin(aurora_time * 0.04 + x * 0.01) + 1) / 2
                final_alpha = int(alpha * (0.4 + 0.6 * shimmer))
                pygame.draw.circle(aurora_surf, (*w["color"], final_alpha), (x, int(y_pos)), glow * 6)
                
    surface.blit(aurora_surf, (0, 0))

def create_block(index):
    shape = random.choice(SHAPES)
    color = random.choice(BLOCK_COLORS)
    x = 80 + index * 160
    y = 640
    return {
        "shape": shape,
        "color": color,
        "pos": [x, y],
        "orig_pos": (x, y),
        "dragging": False,
        "scale": 0.6
    }

def spawn_blocks():
    global available_blocks, game_over
    if not available_blocks:
        for i in range(3):
            available_blocks.append(create_block(i))
        
        # Check if any block can be placed
        can_move = False
        for b in available_blocks:
            if can_place_anywhere(b):
                can_move = True
                break
        if not can_move:
            game_over = True

def can_place_anywhere(block):
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if can_place(block, r, c):
                return True
    return False

def can_place(block, row, col):
    for dx, dy in block["shape"]:
        nr, nc = row + dy, col + dx
        if nr < 0 or nr >= GRID_SIZE or nc < 0 or nc >= GRID_SIZE or grid[nr][nc] is not None:
            return False
    return True

def place_block(block, row, col):
    global score
    for dx, dy in block["shape"]:
        grid[row + dy][col + dx] = block["color"]
    score += len(block["shape"]) * 10
    clear_lines()
    available_blocks.remove(block)
    spawn_blocks()

def clear_lines():
    global score
    rows_to_clear = [r for r in range(GRID_SIZE) if all(grid[r][c] is not None for c in range(GRID_SIZE))]
    cols_to_clear = [c for c in range(GRID_SIZE) if all(grid[r][c] is not None for r in range(GRID_SIZE))]
    
    for r in rows_to_clear:
        for c in range(GRID_SIZE): grid[r][c] = None
    for c in cols_to_clear:
        for r in range(GRID_SIZE): grid[r][c] = None
        
    cleared = len(rows_to_clear) + len(cols_to_clear)
    if cleared > 0:
        score += (cleared * 100) * cleared

def draw_grid(surface):
    panel_rect = pygame.Rect(GRID_MARGIN - 15, GRID_TOP - 15, (GRID_SIZE * CELL_SIZE) + 30, (GRID_SIZE * CELL_SIZE) + 30)
    s = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(s, (255, 255, 255, 20), (0, 0, panel_rect.width, panel_rect.height), border_radius=20)
    pygame.draw.rect(s, (255, 255, 255, 40), (0, 0, panel_rect.width, panel_rect.height), 2, border_radius=20)
    surface.blit(s, (panel_rect.x, panel_rect.y))
    
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            rect = pygame.Rect(GRID_MARGIN + c * CELL_SIZE, GRID_TOP + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, (255, 255, 255, 30), rect, 1)
            if grid[r][c]:
                draw_glass_rect(surface, grid[r][c], rect)

def draw_block(surface, block):
    current_cell_size = CELL_SIZE if block["dragging"] else int(CELL_SIZE * block["scale"])
    for dx, dy in block["shape"]:
        rect = pygame.Rect(
            block["pos"][0] + dx * current_cell_size,
            block["pos"][1] + dy * current_cell_size,
            current_cell_size,
            current_cell_size
        )
        draw_glass_rect(surface, block["color"], rect)

def reset_game():
    global grid, score, game_over, available_blocks, dragging_block
    grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    score = 0
    game_over = False
    available_blocks = []
    dragging_block = None
    spawn_blocks()

# --- MAIN LOOP ---
def main():
    global dragging_block, game_over
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Block Blast - Liquid Glass")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Verdana", 42, bold=True)
    small_font = pygame.font.SysFont("Verdana", 18, bold=True)
    
    reset_game()
    
    offset_x, offset_y = 0, 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    reset_game()
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for b in available_blocks:
                    # Check collision for each cell in block
                    size = int(CELL_SIZE * b["scale"])
                    for dx, dy in b["shape"]:
                        rect = pygame.Rect(b["pos"][0] + dx * size, b["pos"][1] + dy * size, size, size)
                        if rect.collidepoint(pos):
                            dragging_block = b
                            b["dragging"] = True
                            offset_x = (len(set(d[0] for d in b["shape"])) * CELL_SIZE) // 2
                            offset_y = (len(set(d[1] for d in b["shape"])) * CELL_SIZE) // 2
                            break
                    if dragging_block: break

            if event.type == pygame.MOUSEBUTTONUP:
                if dragging_block:
                    gx = (dragging_block["pos"][0] - GRID_MARGIN + CELL_SIZE // 2) // CELL_SIZE
                    gy = (dragging_block["pos"][1] - GRID_TOP + CELL_SIZE // 2) // CELL_SIZE
                    if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE and can_place(dragging_block, gy, gx):
                        place_block(dragging_block, gy, gx)
                    else:
                        dragging_block["pos"] = list(dragging_block["orig_pos"])
                    dragging_block["dragging"] = False
                    dragging_block = None

            if event.type == pygame.MOUSEMOTION:
                if dragging_block:
                    pos = pygame.mouse.get_pos()
                    dragging_block["pos"][0] = pos[0] - offset_x
                    dragging_block["pos"][1] = pos[1] - offset_y

        draw_aurora(screen)
        draw_grid(screen)
        
        for b in available_blocks:
            if b != dragging_block: draw_block(screen, b)
        if dragging_block: draw_block(screen, dragging_block)

        # UI
        score_surf = font.render(f"{score}", True, WHITE)
        screen.blit(score_surf, score_surf.get_rect(center=(SCREEN_WIDTH // 2, 70)))
        label_surf = small_font.render("SCORE", True, (180, 200, 255))
        screen.blit(label_surf, label_rect := label_surf.get_rect(center=(SCREEN_WIDTH // 2, 30)))

        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            over_t = font.render("GAME OVER", True, WHITE)
            rest_t = small_font.render("Press R to Restart", True, (200, 200, 200))
            screen.blit(over_t, over_t.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)))
            screen.blit(rest_t, rest_t.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
