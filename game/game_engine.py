import pygame
from .paddle import Paddle
from .ball import Ball
# Game Engine

pygame.mixer.init()  # Initialize mixer before loading sounds

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.paddle_width = 10
        self.paddle_height = 100

        self.player = Paddle(10, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ai = Paddle(width - 20, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ball = Ball(width // 2, height // 2, 7, 7, width, height)

        self.player_score = 0
        self.ai_score = 0
        self.font = pygame.font.SysFont("Arial", 30)

        self.target_score = 5  # default (best of 5)

        # Load sound effects
        self.sound_paddle_hit = pygame.mixer.Sound("assets/sounds/paddle_hit.wav")
        self.sound_wall_bounce = pygame.mixer.Sound("assets/sounds/wall_bounce.wav")
        self.sound_score = pygame.mixer.Sound("assets/sounds/score.wav")

        self.ball.sound_wall_bounce = self.sound_wall_bounce

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.move(-10, self.height)
        if keys[pygame.K_s]:
            self.player.move(10, self.height)

    def update(self):
        # Move the ball first
        self.ball.move()

        # Check for collisions with paddles immediately after movement
        if self.ball.velocity_x < 0 and self.ball.rect().colliderect(self.player.rect()):
            self.ball.x = self.player.x + self.player.width
            self.ball.velocity_x *= -1
            self.sound_paddle_hit.play()

        elif self.ball.velocity_x > 0 and self.ball.rect().colliderect(self.ai.rect()):
            self.ball.x = self.ai.x - self.ball.width
            self.ball.velocity_x *= -1
            self.sound_paddle_hit.play()


        # Scoring
        if self.ball.x <= 0:
            self.ai_score += 1
            self.sound_score.play()
            self.ball.reset()
        elif self.ball.x >= self.width:
            self.player_score += 1
            self.sound_score.play()
            self.ball.reset()

        # AI follows ball
        self.ai.auto_track(self.ball, self.height)


    def render(self, screen):
        # Draw paddles and ball
        pygame.draw.rect(screen, WHITE, self.player.rect())
        pygame.draw.rect(screen, WHITE, self.ai.rect())
        pygame.draw.ellipse(screen, WHITE, self.ball.rect())
        pygame.draw.aaline(screen, WHITE, (self.width//2, 0), (self.width//2, self.height))

        # Draw score
        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (self.width//4, 20))
        screen.blit(ai_text, (self.width * 3//4, 20))

    def reset_game(self, new_target):
        """Resets scores, ball position, and sets a new winning score target."""
        self.player_score = 0
        self.ai_score = 0
        self.target_score = new_target
        self.ball.reset()

    def check_game_over(self, screen):
        # Check if either player reached target score
        if self.player_score >= self.target_score or self.ai_score >= self.target_score:
            winner = "Player Wins!" if self.player_score >= self.target_score else "AI Wins!"

            # Show winner message briefly
            self.render(screen)
            pygame.display.flip()
            pygame.time.delay(700)

            font_large = pygame.font.SysFont("Arial", 60, bold=True)
            font_small = pygame.font.SysFont("Arial", 30)

            # Display game-over text
            screen.fill((0, 0, 0))
            winner_text = font_large.render(winner, True, WHITE)
            screen.blit(winner_text, winner_text.get_rect(center=(self.width // 2, self.height // 3)))

            # Display replay options
            options = [
                "Press 3 for Best of 3",
                "Press 5 for Best of 5",
                "Press 7 for Best of 7",
                "Press ESC to Exit",
            ]
            for i, opt in enumerate(options):
                opt_text = font_small.render(opt, True, WHITE)
                screen.blit(opt_text, opt_text.get_rect(center=(self.width // 2, self.height // 2 + i * 40)))

            pygame.display.flip()

            # Wait for user input
            waiting = True
            chosen_target = None
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return True  # exit game
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            return True
                        elif event.key == pygame.K_3:
                            chosen_target = 3
                        elif event.key == pygame.K_5:
                            chosen_target = 5
                        elif event.key == pygame.K_7:
                            chosen_target = 7

                        if chosen_target:
                            # Reset game for replay
                            self.reset_game(chosen_target)
                            waiting = False
                            return False  # don't exit main loop, replay continues
            return True  # default if quit
        return False

