import pygame
import random
import sys

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
GRID_SIZE = 8
CELL_SIZE = 50
GRID_MARGIN = (SCREEN_WIDTH - (GRID_SIZE * CELL_SIZE)) // 2
GRID_TOP = 100

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
COLORS = [
    (255, 50, 50),   # Red
    (50, 255, 50),   # Green
    (50, 50, 255),   # Blue
    (255, 255, 50),  # Yellow
    (255, 50, 255),  # Magenta
    (50, 255, 255),  # Cyan
    (255, 165, 0),   # Orange
]

# Block Shapes (relative coordinates)
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
        self.scale = 0.6 # Smaller scale when in preview

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
            pygame.draw.rect(surface, self.color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Block Blast")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 32)
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
                # Position blocks at the bottom
                x = 100 + i * 150
                y = 650
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
            self.score += (cleared * 100) * cleared # Bonus for multiple lines

    def draw_grid(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = pygame.Rect(GRID_MARGIN + c * CELL_SIZE, GRID_TOP + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, DARK_GRAY, rect, 1)
                if self.grid[r][c]:
                    pygame.draw.rect(self.screen, self.grid[r][c], rect)
                    pygame.draw.rect(self.screen, BLACK, rect, 1)

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
                                block.offset_x = pos[0] - block.pos[0]
                                block.offset_y = pos[1] - block.pos[1]
                                break
                        if self.dragging_block: break

                if event.type == pygame.MOUSEBUTTONUP:
                    if self.dragging_block:
                        # Check if dropped on grid
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

            self.screen.fill(BLACK)
            self.draw_grid()
            
            for block in self.blocks:
                if block != self.dragging_block:
                    block.draw(self.screen)
            
            if self.dragging_block:
                self.dragging_block.draw(self.screen)

            # Draw Score
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (20, 20))

            if self.game_over:
                over_text = self.font.render("GAME OVER! Press R to Restart", True, WHITE)
                self.screen.blit(over_text, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2))

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
