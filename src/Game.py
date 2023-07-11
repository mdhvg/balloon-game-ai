import random
import pygame
import os
import math

from Balloon import Balloon
from Bubbles import Bubbles
from Spikes import Spikes, SpikeArray

# Initialize pygame
pygame.init()
pygame.font.init()
CascadiaCode = pygame.font.SysFont("Cascadia Code", 30)

# Globals
BUBBLE_WIDTH, BUBBLE_HEIGHT = 15, 15
BALLOON_WIDTH, BALLOON_HEIGHT = 60, 60
SPIKE_WIDTH, SPIKE_HEIGHT = 15, 30

# Import image assets
BALLOON_IMAGE = pygame.image.load(os.path.join("../Images", "Balloon.png"))
BALLOON_IMAGE = pygame.transform.scale(BALLOON_IMAGE, (BALLOON_WIDTH, BALLOON_HEIGHT))
BUBBLE_IMAGE = pygame.image.load(os.path.join("../Images", "Bubble.png"))
BUBBLE_IMAGE = pygame.transform.scale(BUBBLE_IMAGE, (BUBBLE_WIDTH, BUBBLE_HEIGHT))
SPIKE_IMAGE = pygame.image.load(os.path.join("../Images", "Spike.png"))
SPIKE_IMAGE = pygame.transform.scale(SPIKE_IMAGE, (SPIKE_WIDTH, SPIKE_HEIGHT))

# Define Basic Colors
COLOR_WHITE = (255, 255, 255)

# Collision function
def collide(object1, object2):
    offset_x = object2.x - object1.x
    offset_y = object2.y - object1.y
    return object1.mask.overlap(object2.mask, (offset_x, offset_y)) != None

def selfCollision(self, object):
    return collide(self, object)

Spikes.collision = selfCollision
Bubbles.collision = selfCollision

class Game():
    def __init__(self, WIN, CLOCK, SCREEN_WIDTH = 480, SCREEN_HEIGHT = 640, RISING_SPEED = 2, FPS = 60):
        pygame.display.set_caption("Rising Balloon")
        self.WIN = WIN
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.RISING_SPEED = RISING_SPEED
        self.CLOCK = CLOCK
        self.FPS = FPS
    
    def reset(self):
        self.DEAD = False

        # Set tracking lines
        self.next_bubble_line = Line()
        self.next_spike_start_line = Line()
        self.next_spike_end_line = Line()
        self.prev_spike_start_line = Line()
        self.prev_spike_end_line = Line()

        # Set balloon parameters
        self.balloon = Balloon(self.SCREEN_WIDTH//2-(BALLOON_WIDTH//2) ,self.SCREEN_HEIGHT-200, BALLOON_WIDTH, BALLOON_HEIGHT, BALLOON_IMAGE)

        # Set bubble parameters
        self.bubbles_visible = 20
        self.bubbles = []
        
        # Set spike parameters
        self.max_spike_arrays = 7
        self.max_spikes = self.SCREEN_WIDTH//SPIKE_WIDTH
        self.spikes = []

        # Set Zero Score
        self.score = 0

        # Set time
        self.now = pygame.time.get_ticks()
    
    def render_window(self):

        # Clear screen
        self.WIN.fill(COLOR_WHITE)

        # Draw tracking lines
        if self.next_bubble_line != None:
            pygame.draw.line(self.WIN, self.next_bubble_line.color, self.next_bubble_line.start, self.next_bubble_line.end, 2)
            pygame.draw.line(self.WIN, self.next_spike_start_line.color, self.next_spike_start_line.start, self.next_spike_start_line.end, 2)
            pygame.draw.line(self.WIN, self.next_spike_end_line.color, self.next_spike_end_line.start, self.next_spike_end_line.end, 2)
            pygame.draw.line(self.WIN, self.prev_spike_start_line.color, self.prev_spike_start_line.start, self.prev_spike_start_line.end, 2)
            pygame.draw.line(self.WIN, self.prev_spike_end_line.color, self.prev_spike_end_line.start, self.prev_spike_end_line.end, 2)
        

        # Draw bubbles
        for bubble in self.bubbles:
            bubble.draw(self.WIN)

        # Draw spikes
        for spike_array in self.spikes:
            spike_array.draw(self.WIN)
        
        # Write score
        score_text = CascadiaCode.render("Score: " + str(self.score), True, (0,0,0))
        self.WIN.blit(score_text, (10,10))

        # Draw balloon
        self.balloon.draw(self.WIN)

        # Update display
        # pygame.display.update()
    
    def step(self, direction):

        # Move balloon in direction [left, none, right]
        if direction == 0:
            self.balloon.moveIncrement(-self.SCREEN_WIDTH/self.FPS, self.SCREEN_WIDTH, BALLOON_WIDTH)
        if direction == 2:
            self.balloon.moveIncrement(self.SCREEN_WIDTH/self.FPS, self.SCREEN_WIDTH, BALLOON_WIDTH)

    def get_state(self):

        # Create bubbles if there are less than bubbles_visible
        while len(self.bubbles) < self.bubbles_visible:
            self.bubbles.append(Bubbles(random.randint(0,self.SCREEN_WIDTH-BUBBLE_WIDTH),random.randint(-self.SCREEN_HEIGHT,0),30,30,BUBBLE_IMAGE))

        # Create spikes
        if len(self.spikes) < self.max_spike_arrays:
            time_difference = pygame.time.get_ticks() - self.now
            if time_difference >= random.randint(1500, 3000):
                gap_index = random.randint(0,self.max_spikes-((2*BALLOON_WIDTH)//SPIKE_WIDTH))
                gap_length = random.randint(8, self.max_spikes-gap_index)
                self.spikes.append(SpikeArray(-SPIKE_HEIGHT, SPIKE_WIDTH, SPIKE_HEIGHT, SPIKE_IMAGE, self.max_spikes, gap_index, gap_length))
                self.now = pygame.time.get_ticks()
        
        # Remove bubbles which collide with spikes
        for bubble in self.bubbles:
            for spike_array in self.spikes:
                if spike_array.collision(bubble):
                    self.bubbles.remove(bubble)
                    break
        
        # Increase score on collision between balloon and bubble and remove bubble
        for bubble in self.bubbles:
            if bubble.collision(self.balloon) and self.score > 0:
                self.score += 0.01*self.score
                self.bubbles.remove(bubble)

        # Check if balloon collides with spikes
        for spike_array in self.spikes:
            if spike_array.collision(self.balloon):

                # Give negative reward
                self.score -= 10

                # Kill balloon
                self.DEAD = True

        # Remove Spikes if they are off screen
        for spike_array in self.spikes[:]:
            spike_array.moveWithVelocity(0,self.RISING_SPEED)
            if spike_array.y > self.SCREEN_HEIGHT:
                self.spikes.remove(spike_array)
        
        # Remove Bubbles if they are off screen
        for bubble in self.bubbles[:]:
            bubble.moveWithVelocity(0,self.RISING_SPEED)
            if bubble.y > self.SCREEN_HEIGHT:
                self.bubbles.remove(bubble)

        # Create state array
        state_array = [1,1,1,1,1,1,1,1]

        # Find next bubble
        min_distance = 1000
        for bubble in self.bubbles:
            if bubble.y < self.balloon.y:
                x_distance = self.balloon.x - bubble.x
                y_distance = self.balloon.y - bubble.y
                if y_distance < min_distance:
                    state_array[0] = x_distance
                    state_array[5] = y_distance
                    min_distance = y_distance
                    self.next_bubble_line = Line((0,255,0), (self.balloon.x, self.balloon.y), (bubble.x, bubble.y))
        
        # Find next spike
        min_distance = 1000
        for spike_array in self.spikes:
            # Next spike array
            if spike_array.y < self.balloon.y:
                x_distance = self.balloon.x - spike_array.gap_index*SPIKE_WIDTH
                y_distance = (self.balloon.y - spike_array.y) - SPIKE_HEIGHT
                x_end_distance = self.balloon.x+BALLOON_WIDTH - (spike_array.gap_index+spike_array.gap_length)*SPIKE_WIDTH
                if y_distance < min_distance:
                    state_array[1] = x_distance
                    state_array[2] = x_end_distance
                    state_array[6] = y_distance
                    self.next_spike_start_line = Line((255,0,0), (self.balloon.x, self.balloon.y), (spike_array.gap_index*SPIKE_WIDTH, spike_array.y+SPIKE_HEIGHT))
                    self.next_spike_end_line = Line((255,0,0), (self.balloon.x + BALLOON_WIDTH, self.balloon.y), ((spike_array.gap_index+spike_array.gap_length)*SPIKE_WIDTH, spike_array.y+SPIKE_HEIGHT))
                    min_distance = y_distance
        
        # Find previous spike
        min_distance = -1000
        for spike_array in self.spikes:
            # Previous spike array
            if spike_array.y > self.balloon.y:
                x_distance = self.balloon.x - spike_array.gap_index*SPIKE_WIDTH
                y_distance = self.balloon.y - spike_array.y + BALLOON_HEIGHT
                x_end_distance = self.balloon.x+BALLOON_WIDTH - (spike_array.gap_index+spike_array.gap_length)*SPIKE_WIDTH
                if y_distance > min_distance:
                    state_array[3] = x_distance
                    state_array[4] = x_end_distance
                    state_array[7] = y_distance
                    self.prev_spike_start_line = Line((255,255,0), (self.balloon.x, self.balloon.y + BALLOON_HEIGHT), (spike_array.gap_index*SPIKE_WIDTH, spike_array.y))
                    self.prev_spike_end_line = Line((255,255,0), (self.balloon.x+BALLOON_WIDTH, self.balloon.y+BALLOON_HEIGHT), ((spike_array.gap_index+spike_array.gap_length)*SPIKE_WIDTH, spike_array.y))
                    min_distance = y_distance

        if state_array[7] < 0:
            state_array[3] = 1
            state_array[4] = 1
            state_array[7] = 1

        if state_array[1] != 1:
            if state_array[1] < 0 or state_array[2] > 0:
                self.score -= 0.1
        if state_array[3] != 1:
            print(state_array[3], state_array[4])
            if state_array[3] < 0 or state_array[4] > 0:
                self.score -= 0.1

        for state in state_array[:5]:
            state/=self.SCREEN_WIDTH
        for state in state_array[5:]:
            state/=self.SCREEN_HEIGHT

        return state_array

class Line():
    def __init__(self, color = (255,255,255), start = (0,0), end = (0,0)) -> None:
        self.color = color
        self.start = start
        self.end = end
        pass


if __name__ == "__main__":
    WIN = pygame.display.set_mode((480, 640))
    CLOCK = pygame.time.Clock()
    game = Game(WIN, CLOCK)
    for i in range(3):
        game.reset()
        while not game.DEAD:
            CLOCK.tick(60)
            game.step((random.random()*2)-1)
            game.get_state()
            game.render_window()
            pygame.display.update()
        print("ded")
    pygame.quit()