#Shared link with ChatGPT:
#https://chat.openai.com/share/5f721367-80e8-4253-8610-1a8f526bab0c

import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Define constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20

# Calculate the actual screen size based on the grid dimensions
SCREEN_SIZE = (GRID_WIDTH * GRID_SIZE + GRID_SIZE * 4, GRID_HEIGHT * GRID_SIZE)

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Sound effects
sound_breaker = False
SOUND_EFFECTS = {
    'level_completion': None,
    'collision': None,
    'line_clear': None,
    'game_over': None
}
try:
    SOUND_EFFECTS['level_completion'] = pygame.mixer.Sound('level_completion.wav')
    SOUND_EFFECTS['collision'] = pygame.mixer.Sound('collision.wav')
    SOUND_EFFECTS['line_clear'] = pygame.mixer.Sound('line_clear.wav')
    SOUND_EFFECTS['game_over'] = pygame.mixer.Sound('game_over.wav')
except FileNotFoundError:
    sound_breaker = True
    print()
    print('Error. One of the sound effect files not present in the directory, check:')
    print('level_completion.wav, collision.wav, line_clear.wav, game_over.wav')

# Game variables
level = 1
score = 0
lines = 0
best_score = 0
minute_start_time = time.time()
paused_elapsed_time = minute_start_time

# Create the game window
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Tetris")

clock = pygame.time.Clock()


class Tetrimino:
    def __init__(self):
        self.shapes = [
            [[1, 1, 1, 1]],
            [[1, 1], [1, 1]],
            [[1, 1, 1], [0, 1, 0]],
            [[1, 1, 1], [1, 0, 0]],
            [[1, 1, 1], [0, 0, 1]],
            [[1, 1, 0], [0, 1, 1]],
            [[0, 1, 1], [1, 1, 0]]
        ]
        self.shape = random.choice(self.shapes)
        self.color = random.choice([RED, GREEN, BLUE])
        self.x = (GRID_WIDTH - len(self.shape[0])) // 2
        self.y = 0

    def move_down(self):
        self.y += 1

    def move_left(self):
        self.x -= 1

    def move_right(self):
        self.x += 1

    def rotate(self):
        self.shape = list(zip(*self.shape))[::-1]  # Rotate the shape counter-clockwise

    def draw(self, surface):
        for i in range(len(self.shape)):
            for j in range(len(self.shape[i])):
                if self.shape[i][j]:
                    pygame.draw.rect(surface, self.color,
                                     (self.x * GRID_SIZE + j * GRID_SIZE,
                                      self.y * GRID_SIZE + i * GRID_SIZE,
                                      GRID_SIZE, GRID_SIZE))


class GameGrid:
    def __init__(self):
        self.grid = [[BLACK] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.cleared_lines = 0

    def is_collision(self, tetrimino):
        for i in range(len(tetrimino.shape)):
            for j in range(len(tetrimino.shape[i])):
                if tetrimino.shape[i][j] and (
                        tetrimino.x + j < 0 or tetrimino.x + j >= GRID_WIDTH or
                        tetrimino.y + i >= GRID_HEIGHT or
                        self.grid[tetrimino.y + i][tetrimino.x + j] != BLACK
                ):
                    return True
        return False

    def merge_tetrimino(self, tetrimino):
        for i in range(len(tetrimino.shape)):
            for j in range(len(tetrimino.shape[i])):
                if tetrimino.shape[i][j]:
                    self.grid[tetrimino.y + i][tetrimino.x + j] = tetrimino.color
        if not sound_breaker:
            SOUND_EFFECTS['collision'].play()

    def clear_rows(self):
        full_rows = []
        for i in range(GRID_HEIGHT):
            if all(cell != BLACK for cell in self.grid[i]):
                full_rows.append(i)

        for row in full_rows:
            del self.grid[row]
            self.grid.insert(0, [BLACK] * GRID_WIDTH)
            self.cleared_lines += 1
        
        # Increment the score by the number of cleared rows
        num_cleared_rows = len(full_rows)
        if num_cleared_rows > 0:
            global score, lines, best_score, level
            lines += num_cleared_rows
            score += num_cleared_rows * num_cleared_rows
            if not sound_breaker:
                SOUND_EFFECTS['line_clear'].play()
        
        if score > best_score:
            best_score = score
            
def draw_grid(surface, grid):
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            pygame.draw.rect(surface, grid[i][j],
                             (j * GRID_SIZE, i * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)

    # Draw the space to the right of the grid
    pygame.draw.rect(surface, BLACK, (GRID_WIDTH * GRID_SIZE, 0, GRID_SIZE * 4, SCREEN_HEIGHT), 0)


def draw_game(surface, tetrimino, next_tetrimino, game_grid, level, score, sound_breaker, game_paused):
    surface.fill(BLACK)
    draw_grid(surface, game_grid.grid)

    tetrimino.draw(surface)
    # Calculate the x position to center the next tetrimino in the interface field
    next_tetrimino.x = GRID_WIDTH + (4 - len(next_tetrimino.shape[0])) // 2
    next_tetrimino.draw(surface)

    # Draw the border around the space
    pygame.draw.rect(surface, WHITE, (GRID_WIDTH * GRID_SIZE, 0, GRID_SIZE * 4, SCREEN_HEIGHT), 2)

    # Draw the "Level" label
    font = pygame.font.Font(None, 36)
    level_label = font.render("Level:", True, WHITE)
    level_label_rect = level_label.get_rect(center=(GRID_WIDTH * GRID_SIZE + GRID_SIZE * 2, GRID_SIZE * 3))
    surface.blit(level_label, level_label_rect)

    # Draw the level number
    level_number = font.render(str(level), True, WHITE)
    level_number_rect = level_number.get_rect(center=(GRID_WIDTH * GRID_SIZE + GRID_SIZE * 2, GRID_SIZE * 4))
    surface.blit(level_number, level_number_rect)
    
    # Draw the "Lines" label
    lines_label = font.render("Lines:", True, WHITE)
    lines_label_rect = lines_label.get_rect(center=(GRID_WIDTH * GRID_SIZE + GRID_SIZE * 2, GRID_SIZE * 6))
    surface.blit(lines_label, lines_label_rect)

    # Draw the lines number
    lines_number = font.render(str(lines), True, WHITE)
    lines_number_rect = lines_number.get_rect(center=(GRID_WIDTH * GRID_SIZE + GRID_SIZE * 2, GRID_SIZE * 7))
    surface.blit(lines_number, lines_number_rect)
    
    # Draw the "Score" label
    score_label = font.render("Score:", True, WHITE)
    score_label_rect = score_label.get_rect(center=(GRID_WIDTH * GRID_SIZE + GRID_SIZE * 2, GRID_SIZE * 8))
    surface.blit(score_label, score_label_rect)

    # Draw the score number
    score_number = font.render(str(score), True, WHITE)
    score_number_rect = score_number.get_rect(center=(GRID_WIDTH * GRID_SIZE + GRID_SIZE * 2, GRID_SIZE * 9))
    surface.blit(score_number, score_number_rect)
    
    # Draw the "Best Score" label
    best_score_label = font.render("Best:", True, WHITE)
    best_score_label_rect = best_score_label.get_rect(center=(GRID_WIDTH * GRID_SIZE + GRID_SIZE * 2, GRID_SIZE * 11))
    surface.blit(best_score_label, best_score_label_rect)

    # Draw the best_score number
    best_score_number = font.render(str(best_score), True, WHITE)
    best_score_number_rect = best_score_number.get_rect(center=(GRID_WIDTH * GRID_SIZE + GRID_SIZE * 2, GRID_SIZE * 12))
    surface.blit(best_score_number, best_score_number_rect)
   
    # Draw the sound on/off message
    message = "[S]ound " + ("On" if not sound_breaker else "Off")
    font = pygame.font.Font(None, 24)
    sound_label = font.render(message, True, WHITE)
    sound_label_rect = sound_label.get_rect(center=(GRID_WIDTH * GRID_SIZE + GRID_SIZE * 2, GRID_SIZE * 18))
    surface.blit(sound_label, sound_label_rect)
     
    # Draw the pause/resume message
    message = "Esc to " + ("pause" if not game_paused else "resume")
    resume_label = font.render(message, True, WHITE)
    resume_label_rect = resume_label.get_rect(center=(GRID_WIDTH * GRID_SIZE + GRID_SIZE * 2, GRID_SIZE * 19))
    surface.blit(resume_label, resume_label_rect)
        
    pygame.display.update()

def game_loop():
    tetrimino = Tetrimino()
    next_tetrimino = Tetrimino()
    game_grid = GameGrid()
    game_paused = False

    tetrimino_interval_initial = 1000  # Initial interval between tetrimino movements in milliseconds
    tetrimino_interval = tetrimino_interval_initial  # Interval between tetrimino movements in milliseconds
    tetrimino_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(tetrimino_timer, tetrimino_interval)

    repeat_timer = pygame.USEREVENT + 2
    repeat_interval = 100  # Interval for repeated key presses in milliseconds
    pygame.time.set_timer(repeat_timer, repeat_interval)

    rapid_descent = False

    keys_down = set()

    while True:
        for event in pygame.event.get():
            global level, minute_start_time, paused_elapsed_time, sound_breaker
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == tetrimino_timer and not game_paused:
                tetrimino.move_down()

                if game_grid.is_collision(tetrimino):
                    tetrimino.y -= 1
                    game_grid.merge_tetrimino(tetrimino)
                    game_grid.clear_rows()
                    next_tetrimino.x = (GRID_WIDTH - len(next_tetrimino.shape[0])) // 2
                    tetrimino = next_tetrimino
                    next_tetrimino = Tetrimino()

                    rapid_descent = False
                    tetrimino_interval = tetrimino_interval_initial
                    pygame.time.set_timer(tetrimino_timer, tetrimino_interval)

            if event.type == repeat_timer and not game_paused:
                if pygame.K_LEFT in keys_down and not rapid_descent:
                    tetrimino.move_left()
                    if game_grid.is_collision(tetrimino):
                        tetrimino.move_right()

                if pygame.K_RIGHT in keys_down and not rapid_descent:
                    tetrimino.move_right()
                    if game_grid.is_collision(tetrimino):
                        tetrimino.move_left()

                if pygame.K_DOWN in keys_down and not rapid_descent:
                    tetrimino.move_down()
                    if game_grid.is_collision(tetrimino):
                        tetrimino.y -= 1
                        game_grid.merge_tetrimino(tetrimino)
                        game_grid.clear_rows()
                        next_tetrimino.x = (GRID_WIDTH - len(next_tetrimino.shape[0])) // 2
                        tetrimino = next_tetrimino
                        next_tetrimino = Tetrimino()

            if event.type == pygame.KEYDOWN and not rapid_descent:
                if event.key == pygame.K_ESCAPE:
                    game_paused = not game_paused
                    if game_paused:
                        paused_elapsed_time = time.time()
                    else:
                        minute_start_time += time.time() - paused_elapsed_time
                elif event.key == pygame.K_s:
                    sound_breaker = not sound_breaker
                elif not game_paused:
                    if event.key == pygame.K_LEFT:
                        keys_down.add(pygame.K_LEFT)
                    elif event.key == pygame.K_RIGHT:
                        keys_down.add(pygame.K_RIGHT)
                    elif event.key == pygame.K_DOWN:
                        keys_down.add(pygame.K_DOWN)
                    elif event.key == pygame.K_UP:
                        tetrimino.rotate()
                        if game_grid.is_collision(tetrimino):
                            tetrimino.rotate()
                            tetrimino.rotate()
                            tetrimino.rotate()
                    elif event.key == pygame.K_SPACE:
                        rapid_descent = True
                        tetrimino_interval = 50
                        pygame.time.set_timer(tetrimino_timer, tetrimino_interval)  # Resume the timer

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    keys_down.discard(pygame.K_LEFT)
                elif event.key == pygame.K_RIGHT:
                    keys_down.discard(pygame.K_RIGHT)
                elif event.key == pygame.K_DOWN:
                    keys_down.discard(pygame.K_DOWN)

        draw_game(screen, tetrimino, next_tetrimino, game_grid, level, score, sound_breaker, game_paused)

        if not game_paused and not rapid_descent:
            # Calculate the elapsed time since the minute started
            elapsed_time = time.time() - minute_start_time

            # Check if a minute has passed
            if elapsed_time >= 120:
                level += 1
                minute_start_time = time.time()
                tetrimino_interval_initial -= int(tetrimino_interval_initial / 15)
                tetrimino_interval = tetrimino_interval_initial
                pygame.time.set_timer(tetrimino_timer, tetrimino_interval)
                if not sound_breaker:
                    SOUND_EFFECTS['level_completion'].play()

        if game_grid.is_collision(tetrimino) and tetrimino.y == 0:
            font = pygame.font.Font(None, 64)
            game_over_text = font.render("GAME OVER", True, WHITE)
            game_over_rect = game_over_text.get_rect(center=(GRID_WIDTH * GRID_SIZE // 2, GRID_HEIGHT * GRID_SIZE // 2 - 50))
            screen.blit(game_over_text, game_over_rect)
            if not sound_breaker:
                SOUND_EFFECTS['game_over'].play()

            font = pygame.font.Font(None, 36)
            press_any_key_text = font.render("Press Enter...", True, WHITE)
            press_any_key_rect = press_any_key_text.get_rect(center=(GRID_WIDTH * GRID_SIZE // 2, GRID_HEIGHT * GRID_SIZE // 2))
            screen.blit(press_any_key_text, press_any_key_rect)

            pygame.display.update()

            # Wait for a key press to restart the game
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            return
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return

                pygame.time.Clock().tick(10)
        else:
            clock.tick(60)

# Start the game loop
while True:
    game_loop()
    level = 1
    score = 0
    lines = 0
    minute_start_time = time.time()
    tetrimino_interval_initial = 1000
    tetrimino_interval = tetrimino_interval_initial
    game_grid = GameGrid()
    tetrimino = Tetrimino()
    next_tetrimino = Tetrimino()

