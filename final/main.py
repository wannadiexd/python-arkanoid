import pygame
import sys
import random
import math
from game_objects import Paddle, Ball, Brick, PowerUp, Laser, Particle, Firework

# -- General Setup --
pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()

# -- Screen Setup --
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("PyGame Arkanoid")

# -- Colors --
BG_COLOR = pygame.Color('grey12')
BRICK_COLORS = [(178, 34, 34), (255, 165, 0), (255, 215, 0), (50, 205, 50)]
BUTTON_COLOR = (100, 100, 100)
BUTTON_HOVER_COLOR = (150, 150, 150)
BUTTON_TEXT_COLOR = (255, 255, 255)
BUTTON_BORDER_COLOR = (200, 200, 200)
RESUME_BUTTON_COLOR = (60, 120, 60)
RESUME_BUTTON_HOVER_COLOR = (80, 180, 80)
RESET_BUTTON_COLOR = (150, 60, 60)
RESET_BUTTON_HOVER_COLOR = (200, 80, 80)

# -- Font Setup --
title_font = pygame.font.Font(None, 70)
game_font = pygame.font.Font(None, 40)
message_font = pygame.font.Font(None, 30)
button_font = pygame.font.Font(None, 36)

# -- Sound Setup --
try:
    bounce_sound = pygame.mixer.Sound('bounce.wav')
    brick_break_sound = pygame.mixer.Sound('brick_break.wav')
    game_over_sound = pygame.mixer.Sound('game_over.wav')
    laser_sound = pygame.mixer.Sound('laser.wav')
except pygame.error as e:
    print(f"Warning: Sound file not found. {e}")
    class DummySound:
        def play(self): pass
    bounce_sound, brick_break_sound, game_over_sound, laser_sound = DummySound(), DummySound(), DummySound(), DummySound()

# -- Mute Button Setup --
is_muted = False
mute_button_rect = pygame.Rect(screen_width - 50, 10, 40, 40)

def toggle_mute():
    global is_muted
    is_muted = not is_muted
    volume = 0.0 if is_muted else 1.0
    for sound in [bounce_sound, brick_break_sound, game_over_sound, laser_sound]:
        if hasattr(sound, 'set_volume'):  # Check if it's a real sound object
            sound.set_volume(volume)

def draw_mute_button(screen):
    # Draw button background
    button_color = (100, 100, 100)
    pygame.draw.rect(screen, button_color, mute_button_rect)
    
    # Draw button border
    pygame.draw.rect(screen, (200, 200, 200), mute_button_rect, 2)
    
    # Draw speaker icon
    icon_color = (255, 255, 255)
    speaker_x = mute_button_rect.left + 10
    speaker_y = mute_button_rect.centery
    
    # Speaker base
    pygame.draw.rect(screen, icon_color, (speaker_x, speaker_y - 8, 8, 16))
    
    # Speaker cone
    points = [
        (speaker_x + 8, speaker_y - 8),
        (speaker_x + 18, speaker_y - 15),
        (speaker_x + 18, speaker_y + 15),
        (speaker_x + 8, speaker_y + 8)
    ]
    pygame.draw.polygon(screen, icon_color, points)
    
    # If muted, draw a line through the speaker
    if is_muted:
        pygame.draw.line(screen, (255, 0, 0), 
                         (speaker_x + 3, speaker_y - 12), 
                         (speaker_x + 22, speaker_y + 12), 
                         3)

# --- Ball Reset Function ---
def safe_reset_ball(ball, bricks, paddle):
    # Reset the ball to appear just above the paddle
    ball.rect.centerx = paddle.rect.centerx
    ball.rect.bottom = paddle.rect.top - 5
    ball.speed_x = ball.base_speed * random.choice((1, -1))
    ball.speed_y = -ball.base_speed
    ball.is_glued = True  # Start with the ball glued to the paddle
    ball.is_slowed = False
    ball.slow_timer = 0

# -- Game Objects --
paddle = Paddle(screen_width, screen_height)
ball = Ball(screen_width, screen_height)

# --- Level Design Functions ---
def create_basic_wall(rows=4, cols=10):
    bricks = []
    brick_width = 75
    brick_height = 20
    brick_padding = 5
    wall_start_y = 50
    for row in range(rows):
        for col in range(cols):
            x = col * (brick_width + brick_padding) + brick_padding
            y = row * (brick_height + brick_padding) + wall_start_y
            color = BRICK_COLORS[row % len(BRICK_COLORS)]
            bricks.append(Brick(x, y, brick_width, brick_height, color))
    return bricks

def create_pyramid_wall():
    bricks = []
    brick_width = 75
    brick_height = 20
    brick_padding = 5
    wall_start_y = 50
    max_cols = 15
    
    for row in range(8):  # 8 rows for the pyramid
        cols = max_cols - row
        start_x = (row * (brick_width + brick_padding)) // 2
        
        for col in range(cols):
            x = start_x + col * (brick_width + brick_padding)
            y = row * (brick_height + brick_padding) + wall_start_y
            color = BRICK_COLORS[row % len(BRICK_COLORS)]
            bricks.append(Brick(x, y, brick_width, brick_height, color))
    
    return bricks

def create_diamond_wall():
    bricks = []
    brick_width = 75
    brick_height = 20
    brick_padding = 5
    wall_start_y = 50
    max_width = 12  # Maximum number of bricks in the middle row
    
    # Top half (increasing width)
    for row in range(max_width // 2):
        num_bricks = 2 * row + 1
        start_x = (screen_width - num_bricks * (brick_width + brick_padding)) // 2
        
        for col in range(num_bricks):
            x = start_x + col * (brick_width + brick_padding)
            y = row * (brick_height + brick_padding) + wall_start_y
            color = BRICK_COLORS[row % len(BRICK_COLORS)]
            bricks.append(Brick(x, y, brick_width, brick_height, color))
    
    # Bottom half (decreasing width)
    for row in range(max_width // 2, max_width):
        row_from_middle = row - max_width // 2
        num_bricks = max_width - 2 * row_from_middle
        start_x = (screen_width - num_bricks * (brick_width + brick_padding)) // 2
        
        for col in range(num_bricks):
            x = start_x + col * (brick_width + brick_padding)
            y = row * (brick_height + brick_padding) + wall_start_y
            color = BRICK_COLORS[row % len(BRICK_COLORS)]
            bricks.append(Brick(x, y, brick_width, brick_height, color))
    
    return bricks

def create_wave_wall():
    bricks = []
    brick_width = 75
    brick_height = 20
    brick_padding = 5
    wall_start_y = 50
    rows = 6
    cols = 10
    
    for row in range(rows):
        wave_offset = int(math.sin(row * 0.8) * 40)  # Create a wave pattern
        
        for col in range(cols):
            x = col * (brick_width + brick_padding) + brick_padding + wave_offset
            y = row * (brick_height + brick_padding) + wall_start_y
            color = BRICK_COLORS[row % len(BRICK_COLORS)]
            bricks.append(Brick(x, y, brick_width, brick_height, color))
    
    return bricks

def create_checkerboard_wall():
    bricks = []
    brick_width = 75
    brick_height = 20
    brick_padding = 5
    wall_start_y = 50
    rows = 5
    cols = 10
    
    for row in range(rows):
        for col in range(cols):
            # Skip every other brick to create checkerboard
            if (row + col) % 2 == 0:
                x = col * (brick_width + brick_padding) + brick_padding
                y = row * (brick_height + brick_padding) + wall_start_y
                color = BRICK_COLORS[row % len(BRICK_COLORS)]
                bricks.append(Brick(x, y, brick_width, brick_height, color))
    
    return bricks

# Level configurations
LEVELS = [
    {"name": "Level 1", "create_function": create_basic_wall, "args": {"rows": 4, "cols": 10}},
    {"name": "Level 2", "create_function": create_pyramid_wall, "args": {}},
    {"name": "Level 3", "create_function": create_diamond_wall, "args": {}},
    {"name": "Level 4", "create_function": create_wave_wall, "args": {}},
    {"name": "Level 5", "create_function": create_checkerboard_wall, "args": {}}
]

# -- Main Menu Setup --
def create_level_buttons():
    buttons = []
    button_width = 200
    button_height = 50
    button_y_start = 200
    button_spacing = 60
    
    for i, level in enumerate(LEVELS):
        button_rect = pygame.Rect(
            (screen_width - button_width) // 2,
            button_y_start + i * button_spacing,
            button_width,
            button_height
        )
        buttons.append({"rect": button_rect, "text": level["name"], "level": i})
    
    return buttons

level_buttons = create_level_buttons()

# Create resume game button
resume_button_rect = pygame.Rect(
    (screen_width - 200) // 2,
    140,
    200,
    50
)

# Create main menu button (clears saved game)
main_menu_button_rect = pygame.Rect(
    (screen_width - 200) // 2,
    200,
    200,
    50
)

# Create back to menu button
back_to_menu_button_rect = pygame.Rect(10, 10, 120, 40)

def draw_button(screen, rect, text, hover=False, is_resume=False, is_reset=False):
    if is_resume:
        color = RESUME_BUTTON_HOVER_COLOR if hover else RESUME_BUTTON_COLOR
    elif is_reset:
        color = RESET_BUTTON_HOVER_COLOR if hover else RESET_BUTTON_COLOR
    else:
        color = BUTTON_HOVER_COLOR if hover else BUTTON_COLOR
        
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BUTTON_BORDER_COLOR, rect, 2)
    
    text_surf = button_font.render(text, True, BUTTON_TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def is_button_hovered(rect, mouse_pos):
    return rect.collidepoint(mouse_pos)

# Initialize game objects
current_level = 0
bricks = []
power_ups = []
lasers = []
particles = []
fireworks = []

# --- Game Variables ---
game_state = 'main_menu'  # Start with main menu instead of title screen
score = 0
lives = 3
display_message = ""
message_timer = 0
firework_timer = 0
has_paused_game = False  # Track if there's a paused game to resume

# Game progress storage
saved_game_state = {
    'level': 0,
    'bricks': [],
    'score': 0,
    'lives': 3,
    'paddle_state': None,
    'ball_state': None,
    'power_ups': [],
    'lasers': []
}

def save_game_state():
    global saved_game_state, has_paused_game
    
    # Save current game state
    saved_game_state = {
        'level': current_level,
        'bricks': bricks.copy(),
        'score': score,
        'lives': lives,
        'paddle_state': {
            'rect': paddle.rect.copy(),
            'width': paddle.width,
            'has_laser': paddle.has_laser,
            'has_glue': paddle.has_glue,
            'power_up_timers': paddle.power_up_timers.copy()
        },
        'ball_state': {
            'rect': ball.rect.copy(),
            'speed_x': ball.speed_x,
            'speed_y': ball.speed_y,
            'is_glued': ball.is_glued,
            'is_slowed': ball.is_slowed,
            'slow_timer': ball.slow_timer
        },
        'power_ups': power_ups.copy(),
        'lasers': lasers.copy()
    }
    has_paused_game = True

def restore_game_state():
    global current_level, bricks, score, lives, power_ups, lasers
    
    # Restore game state from saved state
    current_level = saved_game_state['level']
    bricks = saved_game_state['bricks']
    score = saved_game_state['score']
    lives = saved_game_state['lives']
    
    # Restore paddle state
    paddle_state = saved_game_state['paddle_state']
    paddle.rect = paddle_state['rect']
    paddle.width = paddle_state['width']
    paddle.has_laser = paddle_state['has_laser']
    paddle.has_glue = paddle_state['has_glue']
    paddle.power_up_timers = paddle_state['power_up_timers']
    
    # Restore ball state
    ball_state = saved_game_state['ball_state']
    ball.rect = ball_state['rect']
    ball.speed_x = ball_state['speed_x']
    ball.speed_y = ball_state['speed_y']
    ball.is_glued = ball_state['is_glued']
    ball.is_slowed = ball_state['is_slowed']
    ball.slow_timer = ball_state['slow_timer']
    
    # Restore other objects
    power_ups = saved_game_state['power_ups']
    lasers = saved_game_state['lasers']

def reset_game(level_index=0):
    global bricks, score, lives, power_ups, lasers, particles, fireworks, current_level
    
    paddle.reset()
    
    current_level = level_index
    level = LEVELS[current_level]
    bricks = level["create_function"](**level["args"])
    
    # Use the safe ball reset function instead of the standard reset
    safe_reset_ball(ball, bricks, paddle)
    
    score = 0
    lives = 3
    power_ups.clear()
    lasers.clear()
    particles.clear()
    fireworks.clear()

# -- Main Game Loop --
while True:
    # Get mouse position for button hover effects
    mouse_pos = pygame.mouse.get_pos()
    
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # In playing state, launch glued ball
                if game_state == 'playing' and ball.is_glued:
                    ball.is_glued = False
                # In game over or win state, return to main menu
                elif game_state in ['game_over', 'you_win']:
                    game_state = 'main_menu'
                    has_paused_game = False  # Reset paused game flag when game is over
            
            # ESC key to return to main menu with saved state (pause)
            if event.key == pygame.K_ESCAPE and game_state == 'playing':
                save_game_state()  # Save current game state before returning to menu
                game_state = 'main_menu'
                
            if event.key == pygame.K_f and paddle.has_laser and game_state == 'playing':
                lasers.append(Laser(paddle.rect.centerx - 30, paddle.rect.top))
                lasers.append(Laser(paddle.rect.centerx + 30, paddle.rect.top))
                if not is_muted:
                    laser_sound.play()
                
        # Handle mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check mute button in all states
            if mute_button_rect.collidepoint(event.pos):
                toggle_mute()
                
            # Main menu level selection
            if game_state == 'main_menu':
                # Check resume button first if available
                if has_paused_game and resume_button_rect.collidepoint(event.pos):
                    restore_game_state()
                    game_state = 'playing'
                
                # Check main menu button (clears saved game)
                if has_paused_game and main_menu_button_rect.collidepoint(event.pos):
                    has_paused_game = False  # Clear the saved game
                
                # Check level buttons
                for button in level_buttons:
                    if button["rect"].collidepoint(event.pos):
                        reset_game(button["level"])
                        game_state = 'playing'
                        has_paused_game = False  # Starting a new game clears the saved game
            
            # Back to menu button when playing
            if game_state == 'playing' and back_to_menu_button_rect.collidepoint(event.pos):
                save_game_state()  # Save current game state before returning to menu
                game_state = 'main_menu'

    # --- Drawing and Updating based on Game State ---
    screen.fill(BG_COLOR)

    # Main Menu
    if game_state == 'main_menu':
        # Draw title
        title_surface = title_font.render("ARKANOID", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(screen_width / 2, 80))
        screen.blit(title_surface, title_rect)
        
        # Draw buttons for paused game if there is one
        if has_paused_game:
            # Resume button
            resume_hover = is_button_hovered(resume_button_rect, mouse_pos)
            draw_button(screen, resume_button_rect, "Resume Game", resume_hover, is_resume=True)
            
            # Main menu button (clears saved game)
            main_menu_hover = is_button_hovered(main_menu_button_rect, mouse_pos)
            draw_button(screen, main_menu_button_rect, "Main Menu", main_menu_hover, is_reset=True)
            
            # Header for level selection
            select_text = message_font.render("Or Select New Level:", True, (255, 255, 255))
            select_rect = select_text.get_rect(center=(screen_width / 2, 270))
            screen.blit(select_text, select_rect)
            
            # Draw level selection buttons with offset
            for i, button in enumerate(level_buttons):
                # Reposition buttons below the main menu option
                button_rect = pygame.Rect(
                    (screen_width - 200) // 2,
                    300 + i * 60,
                    200,
                    50
                )
                button["rect"] = button_rect
                hover = is_button_hovered(button["rect"], mouse_pos)
                draw_button(screen, button["rect"], button["text"], hover)
        else:
            # Draw standard level selection buttons
            for i, button in enumerate(level_buttons):
                # Standard button positions
                button_rect = pygame.Rect(
                    (screen_width - 200) // 2,
                    200 + i * 60,
                    200,
                    50
                )
                button["rect"] = button_rect
                hover = is_button_hovered(button["rect"], mouse_pos)
                draw_button(screen, button["rect"], button["text"], hover)

    # Gameplay
    elif game_state == 'playing':
        # --- Update all game objects ---
        paddle.update()
        keys = pygame.key.get_pressed()
        ball_status, collision_object = ball.update(paddle, keys[pygame.K_SPACE])

        if ball_status == 'lost':
            lives -= 1
            if lives <= 0:
                game_state = 'game_over'
                has_paused_game = False  # Clear paused game when game over
                if not is_muted:
                    game_over_sound.play()
            else:
                # Use safe ball reset
                safe_reset_ball(ball, bricks, paddle)
                paddle.reset()
        elif collision_object in ['wall', 'paddle']:
            if not is_muted:
                bounce_sound.play()
            for _ in range(5):
                particles.append(Particle(ball.rect.centerx, ball.rect.centery, (255, 255, 0), 1, 3, 1, 3, 0))

        for brick in bricks[:]:
            if ball.rect.colliderect(brick.rect):
                ball.speed_y *= -1
                for _ in range(15):
                    particles.append(Particle(brick.rect.centerx, brick.rect.centery, brick.color, 1, 4, 1, 4, 0.05))
                bricks.remove(brick)
                score += 10
                if not is_muted:
                    brick_break_sound.play()
                if random.random() < 0.3:
                    power_up_type = random.choice(['grow', 'laser', 'glue', 'slow'])
                    power_up = PowerUp(brick.rect.centerx, brick.rect.centery, power_up_type)
                    power_ups.append(power_up)
                break
        
        for power_up in power_ups[:]:
            power_up.update()
            if power_up.rect.top > screen_height:
                power_ups.remove(power_up)
            elif paddle.rect.colliderect(power_up.rect):
                display_message = power_up.PROPERTIES[power_up.type]['message']
                message_timer = 120
                if power_up.type in ['grow', 'laser', 'glue']:
                    paddle.activate_power_up(power_up.type)
                elif power_up.type == 'slow':
                    ball.activate_power_up(power_up.type)
                power_ups.remove(power_up)
        
        for laser in lasers[:]:
            laser.update()
            if laser.rect.bottom < 0:
                lasers.remove(laser)
            else:
                for brick in bricks[:]:
                    if laser.rect.colliderect(brick.rect):
                        for _ in range(10):
                            particles.append(Particle(brick.rect.centerx, brick.rect.centery, brick.color, 1, 3, 1, 3, 0.05))
                        bricks.remove(brick)
                        lasers.remove(laser)
                        score += 10
                        if not is_muted:
                            brick_break_sound.play()
                        break
        
        if not bricks:
            # If current level is not the last one, advance to next level
            if current_level < len(LEVELS) - 1:
                current_level += 1
                paddle.reset()
                level = LEVELS[current_level]
                bricks = level["create_function"](**level["args"])
                display_message = f"Level {current_level + 1}: {level['name']}"
                message_timer = 180
                power_ups.clear()
                lasers.clear()
                # Use safe ball reset for next level
                safe_reset_ball(ball, bricks, paddle)
            else:
                game_state = 'you_win'
                has_paused_game = False  # Clear paused game when win

        # --- Draw all game objects ---
        paddle.draw(screen)
        ball.draw(screen)
        for brick in bricks:
            brick.draw(screen)
        for power_up in power_ups:
            power_up.draw(screen)
        for laser in lasers:
            laser.draw(screen)
        
        # --- Draw UI ---
        # Level indicator
        level_text = game_font.render(f"Level {current_level + 1}", True, (255, 255, 255))
        screen.blit(level_text, (screen_width // 2 - level_text.get_width() // 2, 10))
        
        # Score text
        score_text = game_font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (140, 10))  # Positioned right after the menu button
        
        # Lives
        lives_text = game_font.render(f"Lives: {lives}", True, (255, 255, 255))
        screen.blit(lives_text, (screen_width - lives_text.get_width() - 10 - 50, 10))
        
        # Back to menu button
        hover = is_button_hovered(back_to_menu_button_rect, mouse_pos)
        draw_button(screen, back_to_menu_button_rect, "Menu", hover)

    # Game Over / You Win screens
    elif game_state in ['game_over', 'you_win']:
        if game_state == 'you_win':
            firework_timer -= 1
            if firework_timer <= 0:
                fireworks.append(Firework(screen_width, screen_height))
                firework_timer = random.randint(20, 50)
            
            for firework in fireworks[:]:
                firework.update()
                if firework.is_dead():
                    fireworks.remove(firework)
            
            for firework in fireworks:
                firework.draw(screen)

        message = "GAME OVER" if game_state == 'game_over' else "YOU WIN!"
        text_surface = game_font.render(message, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen_width / 2, screen_height / 2 - 20))
        screen.blit(text_surface, text_rect)
        
        # Final score
        score_surface = game_font.render(f"Final Score: {score}", True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(screen_width / 2, screen_height / 2 + 20))
        screen.blit(score_surface, score_rect)
        
        # Return to main menu message
        restart_surface = game_font.render("Press SPACE to return to Menu", True, (255, 255, 255))
        restart_rect = restart_surface.get_rect(center=(screen_width / 2, screen_height / 2 + 60))
        screen.blit(restart_surface, restart_rect)

    # --- Update effects and messages (these run in all states) ---
    if message_timer > 0:
        message_timer -= 1
        message_surface = message_font.render(display_message, True, (255, 255, 255))
        message_rect = message_surface.get_rect(center=(screen_width / 2, screen_height - 60))
        screen.blit(message_surface, message_rect)
        
    for particle in particles[:]:
        particle.update()
        if particle.size <= 0:
            particles.remove(particle)
    for particle in particles:
        particle.draw(screen)

    # Draw mute button (shown in all game states)
    draw_mute_button(screen)

    # --- Final Display Update ---
    pygame.display.flip()
    clock.tick(60)