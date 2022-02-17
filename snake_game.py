from tkinter.tix import WINDOW
from abc import ABC, abstractmethod
import pygame
import copy
import time
import random

SNAKE_SPEED = 30
WINDOW_X = 720
WINDOW_Y = 480

black = pygame.Color(0,0,0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)

pygame.init()
pygame.display.set_caption('Smart Snakes!')
game_window = pygame.display.set_mode((WINDOW_X, WINDOW_Y))
fps = pygame.time.Clock()

class BoardObject(ABC):
    """Anything that's going to exist on the snake grid"""
    @abstractmethod
    def __init__(self, position):
        """Set initial position"""
        pass

    @abstractmethod
    def reset(self):
        """Reset position on board"""
        pass


class Snake(BoardObject):
    def __init__(self, position: list):
        self.starting_position = copy.copy(position)
        self.position = position
        self.body = []
        for i in range(0,4):
            self.body.append([self.position[0] - i * 10, self.position[1]])
        self.direction = 'RIGHT'
        self.change_to = self.direction
    
    def set_direction(self, event: pygame.KEYDOWN):
        """Sets snake direction and checks for directionaly validity"""
        if event.key == pygame.K_UP:
            self.change_to = 'UP'
        if event.key == pygame.K_DOWN:
            self.change_to = 'DOWN'
        if event.key == pygame.K_LEFT:
            self.change_to = 'LEFT'
        if event.key == pygame.K_RIGHT:
            self.change_to = 'RIGHT'

        # If two keys pressed simultaneously
        # we don't want snake to move into two directions
        # simultaneously
        if self.change_to == 'UP' and self.direction != 'DOWN':
            self.direction = 'UP'
        if self.change_to == 'DOWN' and self.direction != 'UP':
            self.direction = 'DOWN'
        if self.change_to == 'LEFT' and self.direction != 'RIGHT':
            self.direction = 'LEFT'
        if self.change_to == 'RIGHT' and self.direction != 'LEFT':
            self.direction = 'RIGHT'
        
    def update_position(self):
        """Uses direction and current position to update the position of the snake"""
        if self.direction == 'UP':
            self.position[1] -= 10
        if self.direction == 'DOWN':
            self.position[1] += 10
        if self.direction == 'LEFT':
            self.position[0] -= 10
        if self.direction == 'RIGHT':
            self.position[0] += 10
        
    def reset(self):
        self.position = copy.copy(self.starting_position)
        self.body = []
        for i in range(0,4):
            self.body.append([self.position[0] - i * 10, self.position[1]])
        self.direction = 'RIGHT'
        self.change_to = self.direction
    

class Fruit(BoardObject):
    def __init__(self):
        self.position = [random.randrange(1, (WINDOW_X//10)) * 10,
                        random.randrange(1, (WINDOW_Y//10)) * 10]
        self.exists = True
    
    def reset(self):
        """Reset our position"""
        self.position = [random.randrange(1, (WINDOW_X//10)) * 10,
                        random.randrange(1, (WINDOW_Y//10)) * 10]
        self.exists = True


class Game:
    def __init__(self, snake: Snake, fruit: Fruit):
        self.snake = snake
        self.fruit = fruit
        self.score = 0 
        self.font = pygame.font.SysFont('times new roman', 50)
    
    def step(self):
        """move through a single game step"""
        # handling key events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                self.snake.set_direction(event)

        self.snake.update_position()
        
        # move the self.snake by adding new entry to the front of it
        self.snake.body.insert(0, list(self.snake.position))

        if self.snake.position[0] == self.fruit.position[0] and self.snake.position[1] == self.fruit.position[1]:
            self.score += 10
            self.fruit.exists = False
        else:
            self.snake.body.pop() # remove the last entry in the self.snake. Movement!
            
        if not self.fruit.exists:
            self.fruit.position = [random.randrange(1, (WINDOW_X//10)) * 10,
                            random.randrange(1, (WINDOW_Y//10)) * 10]
            
        self.fruit.exists = True
    
    def draw_snakeboard(self):
        """Draw graphics on the screen"""
        game_window.fill(black)
            
        # Draw the self.snake
        for pos in self.snake.body:
            pygame.draw.rect(game_window, green, pygame.Rect(
            pos[0], pos[1], 10, 10))
        
        # Draw the self.fruit
        pygame.draw.rect(game_window, white, pygame.Rect(
        self.fruit.position[0], self.fruit.position[1], 10, 10))
    
    def start(self):
        while True:
            # Move through a single gameplay step 
            self.step()
            self.draw_snakeboard()
            self.check_gameover()
            
            # displaying score countinuously
            self.show_score(1, white, 'times new roman', 20)
            
            # Refresh game screen
            pygame.display.update()

            # Frame Per Second /Refresh Rate
            fps.tick(SNAKE_SPEED)
    
    def restart(self):
        """init all state and restart the game"""
        self.snake.reset()
        self.fruit.reset()
        self.score = 0
        self.start()

    # displaying Score function
    def show_score(self, choice, color, font, size):

        # creating font object score_font
        score_font = pygame.font.SysFont(font, size)
        
        # create the display surface object
        score_surface = score_font.render('Score : ' + str(self.score), True, color)
        
        # create a rectangular object for the
        # text surface object
        score_rect = score_surface.get_rect()
        
        # displaying text
        game_window.blit(score_surface, score_rect)
    
    def check_gameover(self):
        # Game Over conditions, should be moved into its own check probably
        if self.snake.position[0] < 0 or self.snake.position[0] > WINDOW_X-10:
            self.game_over()
        if self.snake.position[1] < 0 or self.snake.position[1] > WINDOW_Y-10:
            self.game_over()
        
        # Touching the self.snake body
        for block in self.snake.body[1:]:
            if self.snake.position[0] == block[0] and self.snake.position[1] == block[1]:
                self.game_over()
                
    def game_over(self):
        # creating a text surface on which text will be drawn
        game_over_surface = self.font.render('Your Score is : ' + str(self.score), True, red)
        
        # create a rectangular object for the text
        game_over_rect = game_over_surface.get_rect()
        
        # text pos
        game_over_rect.midtop = (WINDOW_X/2, WINDOW_Y/4)
        
        # draw the text on the screen with blit
        game_window.blit(game_over_surface, game_over_rect)
        pygame.display.flip()
        time.sleep(2)

        #TODO Throw some text up asking for a quit or restart

        
        # deactivating pygame library
        self.restart()
    
    def quit(self):
        # deactivate pygame library
        pygame.quit()
        # quit the program
        quit()


def main():
    # init snake and self.fruit objects
    snake = Snake([100, 50])
    fruit = Fruit()
    game = Game(snake, fruit)

    game.start()


if __name__ == "__main__":
    main()
