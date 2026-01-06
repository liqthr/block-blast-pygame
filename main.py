import pygame
import random
import sys
import math

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
GRID_SIZE = 8
CELL_SIZE = 50
GRID_MARGIN = (SCREEN_WIDTH - (GRID_SIZE * CELL_SIZE)) // 2
GRID_TOP = 120

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BG = (5, 8, 20)

# Vibrant Block Colors (Glassy variants)
COLORS = [
    (255, 100, 100), # Soft Red
    (100, 255, 150), # Mint Green
    (100, 180, 255), # Sky Blue
    (255, 230, 100), # Golden Yellow
    (230, 130, 255), # Lavender
    (100, 255, 240), # Turquoise
    (255, 170, 100), # Coral
]

# Block Shapes
SHAPES = [
    [(0, 0)], # Single
    [(0, 0), (1, 0)], # 1x2
    [(0, 0), (0, 1)], # 2x1
    [(0, 0), (1, 0), (2, 0)], # 1x3
    [(0, 0), (0, 1), (0, 2)], # 3x1
    [(0, 0), (1, 0), (0, 1), (1, 1)], # 2x2 Square
    [(0, 0), (1, 0), (2, 0), (0, 1)], # L-shape
    [(0, 0), (1, 0), (2, 0), (2, 1)], # J-shape
    [(0, 0), (0, 1), (0, 2), (1, 2)], # L-shape 2
    [(1, 0), (1, 1), (1, 2), (0, 2)], # J-shape 2
    [(0, 0), (1, 0), (1, 1), (2, 1)], # Z-shape
    [(1, 0), (2, 0), (0, 1), (1, 1)], # S-shape
    [(0, 0), (1, 0), (2, 0), (1, 1)], # T-shape
]

def draw_glass_rect(surface, color, rect, border_radius=12):
    """Draws a rectangle with Apple's 'Liquid Glass' effect."""
    # 1. Base translucent layer
    base_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(base_surf, (*color, 180), (0, 0, rect.width, rect.height), border_radius=border_radius)
    surface.blit(base_surf, (rect.x, rect.y))
    
    # 2. Inner Glow / Bevel
    # Top highlight (specular)
    highlight_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(highlight_surf, (255, 255, 255, 80), (2, 2, rect.width-4, rect.height//2), border_radius=border_radius)
    surface.blit(highlight_surf, (rect.x, rect.y))
    
    # 3. Glass Reflection (Diagonal streak)
    reflect_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.polygon(reflect_surf, (255, 255, 255, 40), [
        (rect.width*0.2, 0), (rect.width*0.5, 0), 
        (rect.width*0.3, rect.height), (0, rect.height)
    ])
    surface.blit(reflect_surf, (rect.x, rect.y))

    # 4. Crisp Border
    pygame.draw.rect(surface, (255, 255, 255, 100), rect, 1, border_radius=border_radius)
    
    # 5. Bottom Shadow (Inner)
    shadow_color = [max(0, c - 80) for c in color]
    pygame.draw.rect(surface, (*shadow_color, 100), (rect.x+2, rect.bottom-6, rect.width-4, 4), border_radius=border_radius)

class AuroraBackground:
    def __init__(self):
        self.time = 0
        self.waves = [
            {"color": (0, 255, 180), "amplitude": 50, "frequency": 0.01, "speed": 0.015, "y_offset": 250},
            {"color": (100, 100, 255), "amplitude": 70, "frequency": 0.007, "speed": -0.01, "y_offset": 400},
            {"color": (200, 50, 255), "amplitude": 60, "frequency": 0.009, "speed": 0.008, "y_offset": 550},
        ]

    def draw(self, surface):
        self.time += 1
        surface.fill(DARK_BG)
        aurora_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        for wave in self.waves:
            points = []
            for x in range(0, SCREEN_WIDTH + 20, 20):
                y_var = math.sin(x * wave["frequency"] + self.time * wave["speed"]) * wave["amplitude"]
                y_var += math.sin(x * 0.004 + self.time * 0.012) * 30
                points.append((x, wave["y_offset"] + y_var))

            for i in range(len(points) - 1):
                p1, p2 = points[i], points[i+1]
                for glow in range(12):
                    alpha = int(35 * (1 - glow / 12))
                    shimmer = (math.sin(self.time * 0.04 + p1[0] * 0.01) + 1) / 2
                    final_alpha = int(alpha * (0.4 + 0.6 * shimmer))
                    pygame.draw.line(aurora_surf, (*wave["color"], final_alpha), 
                                     (p1[0], p1[1] - glow * 5), (p2[0], p2[1] - glow * 5), 10)
                    pygame.draw.line(aurora_surf, (*wave["color"], final_alpha), 
                                     (p1[0], p1[1] + glow * 5), (p2[0], p2[1] + glow * 5), 10)
        surface.blit(aurora_surf, (0, 0))

class Block:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.rects = []
        self.dragging = False
        self.pos = [0, 0]
        self.original_pos = (0, 0)
        self.scale = 0.6

    def update_rects(self):
        self.rects = []
        current_cell_size = CELL_SIZE if self.dragging else int(CELL_SIZE * self.scale)
        for dx, dy in self.shape:
            rect = pygame.Rect(
                self.pos[0] + dx * current_cell_size,
                self.pos[1] + dy * current_cell_size,
                current_cell_size,
                current_cell_size
            )
            self.rects.append(rect)

    def draw(self, surface):
        self.update_rects()
        for rect in self.rects:
            draw_glass_rect(surface, self.color, rect)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Block Blast - Liquid Glass Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Verdana", 42, bold=True)
        self.small_font = pygame.font.SysFont("Verdana", 18, bold=True)
        self.aurora = AuroraBackground()
        self.reset_game()

    def reset_game(self):
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.score = 0
        self.game_over = False
        self.blocks = []
        self.spawn_blocks()
        self.dragging_block = None

    def spawn_blocks(self):
        if not self.blocks:
            for i in range(3):
                shape = random.choice(SHAPES)
                color = random.choice(COLORS)
                block = Block(shape, color)
                x = 80 + i * 160
                y = 640
                block.pos = [x, y]
                block.original_pos = (x, y)
                self.blocks.append(block)
            if self.check_game_over(): self.game_over = True

    def check_game_over(self):
        for block in self.blocks:
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if self.can_place(block, r, c): return False
        return True

    def can_place(self, block, row, col):
        for dx, dy in block.shape:
            nr, nc = row + dy, col + dx
            if nr < 0 or nr >= GRID_SIZE or nc < 0 or nc >= GRID_SIZE or self.grid[nr][nc] is not None:
                return False
        return True

    def place_block(self, block, row, col):
        for dx, dy in block.shape:
            self.grid[row + dy][col + dx] = block.color
        self.score += len(block.shape) * 10
        self.clear_lines()
        self.blocks.remove(block)
        self.spawn_blocks()

    def clear_lines(self):
        rows_to_clear = [r for r in range(GRID_SIZE) if all(self.grid[r][c] is not None for c in range(GRID_SIZE))]
        cols_to_clear = [c for c in range(GRID_SIZE) if all(self.grid[r][c] is not None for r in range(GRID_SIZE))]
        for r in rows_to_clear:
            for c in range(GRID_SIZE): self.grid[r][c] = None
        for c in cols_to_clear:
            for r in range(GRID_SIZE): self.grid[r][c] = None
        cleared = len(rows_to_clear) + len(cols_to_clear)
        if cleared > 0: self.score += (cleared * 100) * cleared

    def draw_grid(self):
        # Glassy Grid Panel
        panel_rect = pygame.Rect(GRID_MARGIN - 15, GRID_TOP - 15, (GRID_SIZE * CELL_SIZE) + 30, (GRID_SIZE * CELL_SIZE) + 30)
        s = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (255, 255, 255, 20), (0, 0, panel_rect.width, panel_rect.height), border_radius=20)
        pygame.draw.rect(s, (255, 255, 255, 40), (0, 0, panel_rect.width, panel_rect.height), 2, border_radius=20)
        self.screen.blit(s, (panel_rect.x, panel_rect.y))
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = pygame.Rect(GRID_MARGIN + c * CELL_SIZE, GRID_TOP + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, (255, 255, 255, 30), rect, 1)
                if self.grid[r][c]:
                    draw_glass_rect(self.screen, self.grid[r][c], rect)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if self.game_over:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r: self.reset_game()
                    continue
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for block in self.blocks:
                        block.update_rects()
                        for rect in block.rects:
                            if rect.collidepoint(pos):
                                self.dragging_block = block
                                block.dragging = True
                                block.offset_x = (len(set(d[0] for d in block.shape)) * CELL_SIZE) // 2
                                block.offset_y = (len(set(d[1] for d in block.shape)) * CELL_SIZE) // 2
                                break
                        if self.dragging_block: break
                if event.type == pygame.MOUSEBUTTONUP:
                    if self.dragging_block:
                        gx = (self.dragging_block.pos[0] - GRID_MARGIN + CELL_SIZE // 2) // CELL_SIZE
                        gy = (self.dragging_block.pos[1] - GRID_TOP + CELL_SIZE // 2) // CELL_SIZE
                        if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE and self.can_place(self.dragging_block, gy, gx):
                            self.place_block(self.dragging_block, gy, gx)
                        else:
                            self.dragging_block.pos = list(self.dragging_block.original_pos)
                        self.dragging_block.dragging = False
                        self.dragging_block = None
                if event.type == pygame.MOUSEMOTION:
                    if self.dragging_block:
                        pos = pygame.mouse.get_pos()
                        self.dragging_block.pos[0] = pos[0] - self.dragging_block.offset_x
                        self.dragging_block.pos[1] = pos[1] - self.dragging_block.offset_y

            self.aurora.draw(self.screen)
            self.draw_grid()
            for block in self.blocks:
                if block != self.dragging_block: block.draw(self.screen)
            if self.dragging_block: self.dragging_block.draw(self.screen)

            # UI
            score_surf = self.font.render(f"{self.score}", True, WHITE)
            self.screen.blit(score_surf, score_rect := score_surf.get_rect(center=(SCREEN_WIDTH // 2, 70)))
            label_surf = self.small_font.render("SCORE", True, (180, 200, 255))
            self.screen.blit(label_surf, label_rect := label_surf.get_rect(center=(SCREEN_WIDTH // 2, 30)))

            if self.game_over:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                self.screen.blit(overlay, (0, 0))
                over_t = self.font.render("GAME OVER", True, WHITE)
                rest_t = self.small_font.render("Press R to Restart", True, (200, 200, 200))
                self.screen.blit(over_t, over_t.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)))
                self.screen.blit(rest_t, rest_t.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)))

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
