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
DARK_BG = (5, 10, 25)

# Vibrant Block Colors
COLORS = [
    (255, 80, 80),   # Soft Red
    (80, 255, 120),  # Mint Green
    (80, 150, 255),  # Sky Blue
    (255, 220, 80),  # Golden Yellow
    (220, 100, 255), # Lavender
    (80, 255, 240),  # Turquoise
    (255, 150, 80),  # Coral
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

def draw_3d_rect(surface, color, rect, border_radius=4):
    """Draws a rectangle with a 3D beveled effect."""
    pygame.draw.rect(surface, color, rect, border_radius=border_radius)
    
    # Highlight
    highlight_color = [min(255, c + 70) for c in color]
    pygame.draw.line(surface, highlight_color, (rect.left + 2, rect.top + 2), (rect.right - 2, rect.top + 2), 3)
    pygame.draw.line(surface, highlight_color, (rect.left + 2, rect.top + 2), (rect.left + 2, rect.bottom - 2), 3)
    
    # Shadow
    shadow_color = [max(0, c - 70) for c in color]
    pygame.draw.line(surface, shadow_color, (rect.left + 2, rect.bottom - 2), (rect.right - 2, rect.bottom - 2), 3)
    pygame.draw.line(surface, shadow_color, (rect.right - 2, rect.top + 2), (rect.right - 2, rect.bottom - 2), 3)
    
    pygame.draw.rect(surface, (0, 0, 0, 40), rect, 1, border_radius=border_radius)

class AuroraBackground:
    def __init__(self):
        self.time = 0
        # Define multiple "waves" for the aurora
        self.waves = [
            {"color": (0, 255, 150), "amplitude": 40, "frequency": 0.01, "speed": 0.02, "y_offset": 200},
            {"color": (0, 150, 255), "amplitude": 60, "frequency": 0.008, "speed": -0.015, "y_offset": 350},
            {"color": (150, 0, 255), "amplitude": 50, "frequency": 0.012, "speed": 0.01, "y_offset": 500},
            {"color": (0, 255, 100), "amplitude": 30, "frequency": 0.015, "speed": -0.025, "y_offset": 150}
        ]

    def draw(self, surface):
        self.time += 1
        surface.fill(DARK_BG)
        
        # Create a surface for the aurora with alpha support
        aurora_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        for wave in self.waves:
            points = []
            color = wave["color"]
            # Draw the wave as a series of vertical lines or a polygon
            for x in range(0, SCREEN_WIDTH + 10, 10):
                # Calculate wave height using sine waves
                y_var = math.sin(x * wave["frequency"] + self.time * wave["speed"]) * wave["amplitude"]
                y_var += math.sin(x * 0.005 + self.time * 0.01) * 20 # Secondary wave for complexity
                y_pos = wave["y_offset"] + y_var
                points.append((x, y_pos))

            # Draw glowing bands
            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i+1]
                # Draw multiple lines with decreasing alpha to create a glow/blur effect
                for glow in range(15):
                    alpha = int(40 * (1 - glow / 15))
                    # Vary alpha over time for "shimmer"
                    shimmer = (math.sin(self.time * 0.05 + p1[0] * 0.01) + 1) / 2
                    final_alpha = int(alpha * (0.5 + 0.5 * shimmer))
                    
                    pygame.draw.line(aurora_surf, (*color, final_alpha), 
                                     (p1[0], p1[1] - glow * 4), (p2[0], p2[1] - glow * 4), 8)
                    pygame.draw.line(aurora_surf, (*color, final_alpha), 
                                     (p1[0], p1[1] + glow * 4), (p2[0], p2[1] + glow * 4), 8)

        surface.blit(aurora_surf, (0, 0))

class Block:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.rects = []
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.original_pos = (0, 0)
        self.pos = [0, 0]
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
            draw_3d_rect(surface, self.color, rect)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Block Blast - Aurora Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Verdana", 36, bold=True)
        self.small_font = pygame.font.SysFont("Verdana", 20)
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
            
            if self.check_game_over():
                self.game_over = True

    def check_game_over(self):
        for block in self.blocks:
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if self.can_place(block, r, c):
                        return False
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
        rows_to_clear = []
        cols_to_clear = []

        for r in range(GRID_SIZE):
            if all(self.grid[r][c] is not None for c in range(GRID_SIZE)):
                rows_to_clear.append(r)
        
        for c in range(GRID_SIZE):
            if all(self.grid[r][c] is not None for r in range(GRID_SIZE)):
                cols_to_clear.append(c)

        for r in rows_to_clear:
            for c in range(GRID_SIZE):
                self.grid[r][c] = None
        
        for c in cols_to_clear:
            for r in range(GRID_SIZE):
                self.grid[r][c] = None

        cleared = len(rows_to_clear) + len(cols_to_clear)
        if cleared > 0:
            self.score += (cleared * 100) * cleared

    def draw_grid(self):
        # Draw grid background panel with transparency
        panel_rect = pygame.Rect(GRID_MARGIN - 10, GRID_TOP - 10, (GRID_SIZE * CELL_SIZE) + 20, (GRID_SIZE * CELL_SIZE) + 20)
        s = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        s.fill((255, 255, 255, 15))
        self.screen.blit(s, (panel_rect.x, panel_rect.y))
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = pygame.Rect(GRID_MARGIN + c * CELL_SIZE, GRID_TOP + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, (60, 70, 100), rect, 1)
                if self.grid[r][c]:
                    draw_3d_rect(self.screen, self.grid[r][c], rect)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if self.game_over:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        self.reset_game()
                    continue

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for block in self.blocks:
                        block.update_rects()
                        for rect in block.rects:
                            if rect.collidepoint(pos):
                                self.dragging_block = block
                                block.dragging = True
                                # Center block on mouse
                                block.offset_x = (len(set(d[0] for d in block.shape)) * CELL_SIZE) // 2
                                block.offset_y = (len(set(d[1] for d in block.shape)) * CELL_SIZE) // 2
                                break
                        if self.dragging_block: break

                if event.type == pygame.MOUSEBUTTONUP:
                    if self.dragging_block:
                        grid_x = (self.dragging_block.pos[0] - GRID_MARGIN + CELL_SIZE // 2) // CELL_SIZE
                        grid_y = (self.dragging_block.pos[1] - GRID_TOP + CELL_SIZE // 2) // CELL_SIZE
                        
                        if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE and self.can_place(self.dragging_block, grid_y, grid_x):
                            self.place_block(self.dragging_block, grid_y, grid_x)
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
                if block != self.dragging_block:
                    block.draw(self.screen)
            
            if self.dragging_block:
                self.dragging_block.draw(self.screen)

            # UI
            score_surf = self.font.render(f"{self.score}", True, WHITE)
            score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, 60))
            self.screen.blit(score_surf, score_rect)
            
            label_surf = self.small_font.render("SCORE", True, (200, 220, 255))
            label_rect = label_surf.get_rect(center=(SCREEN_WIDTH // 2, 25))
            self.screen.blit(label_surf, label_rect)

            if self.game_over:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0, 0))
                
                over_text = self.font.render("GAME OVER", True, WHITE)
                restart_text = self.small_font.render("Press R to Restart", True, (200, 200, 200))
                
                self.screen.blit(over_text, over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)))
                self.screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)))

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
