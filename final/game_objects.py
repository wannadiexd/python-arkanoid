import pygame
import random
import math

# Initialize the font module for the power-up letters
pygame.font.init()
POWERUP_FONT = pygame.font.Font(None, 20)

class Paddle:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.original_width = 100
        self.height = 10
        self.speed = 7
        self.color = (200, 200, 200)
        
        self.width = self.original_width
        self.power_up_timers = {
            'grow': 0,
            'laser': 0,
            'glue': 0,
            'shrink': 0  # Add timer for shrink power-up
        }
        self.has_laser = False
        self.has_glue = False
        self.has_shrink = False  # Add tracking for shrink state

        self.rect = pygame.Rect(
            self.screen_width // 2 - self.width // 2,
            self.screen_height - 30,
            self.width,
            self.height
        )

    def reset(self):
        self.rect.x = self.screen_width // 2 - self.original_width // 2
        self.width = self.original_width
        self.rect.width = self.width
        self.has_laser = False
        self.has_glue = False
        self.has_shrink = False  # Reset shrink state
        for power_up in self.power_up_timers:
            self.power_up_timers[power_up] = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.screen_width:
            self.rect.right = self.screen_width
            
        self._update_power_ups()

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        
    def activate_power_up(self, power_type):
        # Store the current center position of the paddle
        current_center = self.rect.centerx
        
        if power_type == 'grow':
            self.width = min(self.width + 40, 200)  # Increase width but cap at 200
            self.rect.width = self.width
            self.power_up_timers['grow'] = 600  # 10 seconds at 60 FPS
            
        elif power_type == 'laser':
            self.has_laser = True
            self.power_up_timers['laser'] = 600
            
        elif power_type == 'glue':
            self.has_glue = True
            self.power_up_timers['glue'] = 600
            
        elif power_type == 'shrink':
            self.width = max(self.width - 30, 50)  # Decrease width but not below 50
            self.rect.width = self.width
            self.power_up_timers['shrink'] = 450  # 7.5 seconds
            self.has_shrink = True
        
        # Re-center the paddle after width change
        self.rect.centerx = current_center
            
    def _update_power_ups(self):
        # Grow power-up timer
        if self.power_up_timers['grow'] > 0:
            self.power_up_timers['grow'] -= 1
            if self.power_up_timers['grow'] <= 0:
                current_center = self.rect.centerx
                self.width = self.original_width
                self.rect.width = self.width
                self.rect.centerx = current_center
        
        # Laser power-up timer
        if self.power_up_timers['laser'] > 0:
            self.power_up_timers['laser'] -= 1
            if self.power_up_timers['laser'] <= 0:
                self.has_laser = False
        
        # Glue power-up timer
        if self.power_up_timers['glue'] > 0:
            self.power_up_timers['glue'] -= 1
            if self.power_up_timers['glue'] <= 0:
                self.has_glue = False
                
        # Shrink power-up timer
        if self.power_up_timers['shrink'] > 0:
            self.power_up_timers['shrink'] -= 1
            if self.power_up_timers['shrink'] <= 0:
                self.has_shrink = False
                current_center = self.rect.centerx
                self.width = self.original_width
                self.rect.width = self.width
                self.rect.centerx = current_center


class Ball:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.radius = 10
        self.color = (200, 200, 200)
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        
        self.is_glued = False
        self.is_slowed = False
        self.is_fast = False    # Add fast state tracking
        self.is_strong = False  # Add strong state tracking
        
        self.slow_timer = 0
        self.fast_timer = 0     # Add fast timer
        self.strong_timer = 0   # Add strong timer
        
        self.base_speed = 6
        
        self.reset()

    def reset(self):
        self.rect.center = (self.screen_width // 2, self.screen_height // 2)
        self.speed_x = self.base_speed * random.choice((1, -1))
        self.speed_y = -self.base_speed
        self.is_glued = False
        self.is_slowed = False
        self.is_fast = False
        self.is_strong = False
        self.slow_timer = 0
        self.fast_timer = 0
        self.strong_timer = 0

    def update(self, paddle, launch_ball=False):
        # Handle power-up timers
        if self.is_slowed:
            self.slow_timer -= 1
            if self.slow_timer <= 0:
                self.is_slowed = False
        
        if self.is_fast:
            self.fast_timer -= 1
            if self.fast_timer <= 0:
                self.is_fast = False
                
        if self.is_strong:
            self.strong_timer -= 1
            if self.strong_timer <= 0:
                self.is_strong = False
        
        collision_object = None

        if self.is_glued:
            self.rect.centerx = paddle.rect.centerx
            self.rect.bottom = paddle.rect.top
            if launch_ball:
                self.is_glued = False
                self.speed_x = self.base_speed * random.choice((1, -1))
                self.speed_y = -self.base_speed
            return 'playing', None

        # Calculate actual speed based on power-ups
        speed_multiplier = 1.0
        if self.is_slowed:
            speed_multiplier *= 0.5
        if self.is_fast:
            speed_multiplier *= 2.0
        
        current_speed_x = self.speed_x * speed_multiplier
        current_speed_y = self.speed_y * speed_multiplier

        # Apply movement with modified speed
        self.rect.x += current_speed_x
        self.rect.y += current_speed_y

        # Handle collisions
        if self.rect.top <= 0:
            self.speed_y *= -1
            collision_object = 'wall'
        if self.rect.left <= 0 or self.rect.right >= self.screen_width:
            self.speed_x *= -1
            collision_object = 'wall'

        if self.rect.colliderect(paddle.rect) and self.speed_y > 0:
            if paddle.has_glue:
                self.is_glued = True
            self.speed_y *= -1
            collision_object = 'paddle'
        
        if self.rect.top > self.screen_height:
            return 'lost', None
        
        return 'playing', collision_object

    def draw(self, screen):
        # Change color based on power-ups
        color = self.color
        if self.is_strong:
            color = (139, 0, 139)  # Purple for strong ball
        elif self.is_fast:
            color = (255, 69, 0)   # Orange for fast ball
        elif self.is_slowed:
            color = (100, 100, 255) # Blue for slow ball
            
        pygame.draw.ellipse(screen, color, self.rect)
        
    def activate_power_up(self, power_type):
        if power_type == 'slow':
            self.is_slowed = True
            self.is_fast = False  # Cancel fast if active
            self.slow_timer = 600  # 10 seconds at 60 FPS
        elif power_type == 'fast':
            self.is_fast = True
            self.is_slowed = False  # Cancel slow if active
            self.fast_timer = 600  # 10 seconds
        elif power_type == 'strong':
            self.is_strong = True
            self.strong_timer = 900  # 15 seconds


class Brick:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


class PowerUp:
    # Update properties to include new power-ups with character identifiers
    PROPERTIES = {
        # Original power-ups
        'grow': {'color': (60, 60, 255), 'char': 'G', 'message': 'PADDLE GROW'},
        'laser': {'color': (255, 60, 60), 'char': 'L', 'message': 'LASER CANNONS'},
        'glue': {'color': (60, 255, 60), 'char': 'C', 'message': 'CATCH PADDLE'},
        'slow': {'color': (255, 165, 0), 'char': 'S', 'message': 'SLOW BALL'},
        
        # New power-ups
        'multi': {'color': (0, 255, 255), 'char': 'M', 'message': 'MULTI BALL!'},
        'extra_life': {'color': (255, 105, 180), 'char': 'E', 'message': 'EXTRA LIFE!'},
        'strong': {'color': (139, 0, 139), 'char': 'T', 'message': 'STRONG BALL!'},
        'fast': {'color': (255, 69, 0), 'char': 'F', 'message': 'FAST BALL! (Watch out!)'},
        'shrink': {'color': (255, 0, 0), 'char': 'R', 'message': 'PADDLE SHRINK! (Be careful!)'}
    }
    
    def __init__(self, x, y, type):
        self.width = 30
        self.height = 15
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.speed_y = 3
        self.type = type
        self.color = self.PROPERTIES[type]['color']
        self.char = self.PROPERTIES[type]['char']

    def update(self):
        self.rect.y += self.speed_y

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surf = POWERUP_FONT.render(self.char, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


class Laser:
    def __init__(self, x, y):
        self.width = 5
        self.height = 15
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = (255, 255, 0)
        self.speed_y = -8

    def update(self):
        self.rect.y += self.speed_y

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

# !!! PHASE: VISUAL EFFECTS !!!
class Particle:
    def __init__(self, x, y, color, min_size, max_size, min_speed, max_speed, gravity):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(min_size, max_size)
        self.gravity = gravity
        angle = random.uniform(0, 360)
        speed = random.uniform(min_speed, max_speed)
        self.vx = speed * math.cos(math.radians(angle))
        self.vy = speed * math.sin(math.radians(angle))

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.size -= 0.1 # Particles shrink over time

    def draw(self, screen):
        if self.size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

class Firework:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = random.randint(0, screen_width)
        self.y = screen_height
        self.vy = -random.uniform(8, 12) # Speed of the rocket
        self.color = (255, 255, 255) # White rocket
        self.exploded = False
        self.particles = []
        self.explosion_y = random.uniform(screen_height * 0.2, screen_height * 0.5)

    def update(self):
        if not self.exploded:
            self.y += self.vy
            if self.y <= self.explosion_y:
                self.exploded = True
                explosion_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
                for _ in range(50): # Create 50 particles on explosion
                    self.particles.append(Particle(self.x, self.y, explosion_color, 2, 4, 1, 4, 0.1))
        else:
            for particle in self.particles[:]:
                particle.update()
                if particle.size <= 0:
                    self.particles.remove(particle)

    def draw(self, screen):
        if not self.exploded:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 3)
        else:
            for particle in self.particles:
                particle.draw(screen)

    def is_dead(self):
        return self.exploded and not self.particles
# !!! END PHASE: VISUAL EFFECTS !!!