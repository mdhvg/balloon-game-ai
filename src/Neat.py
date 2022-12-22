import os
import neat
import pygame
from Game import Game

# Initialize pygame
pygame.init()
pygame.font.init()
CascadiaCode = pygame.font.SysFont("Cascadia Code", 30)

# Globals
SCREEN_WIDTH, SCREEN_HEIGHT = 480, 640
FPS = 60

class neat_trainer():
    def __init__(self):

        # Make main window
        self.WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Rising Balloon")
        self.clock = pygame.time.Clock()
        self.game = Game(self.WIN, self.clock, SCREEN_WIDTH, SCREEN_HEIGHT, 2, FPS)

        # Load config file
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, "config.txt")
        self.config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

        # Create population
        self.Population = neat.Population(self.config)
        self.Population.add_reporter(neat.StdOutReporter(True))
        self.Population.add_reporter(neat.StatisticsReporter())
        self.Population.add_reporter(neat.Checkpointer(1))

        # QUIT check
        self.QUIT = False

    def train(self):

        # Run NEAT
        self.winner = self.Population.run(self.eval_genomes, 10)

    def eval_genomes(self, genomes, config):

        # Loop over all genomes in population
        for genome_id, genome in genomes:
            if not self.QUIT:
                genome.fitness = self.eval_genome(genome, config)

    def eval_genome(self, genome, config):

        # Create neural network
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        # Reset game
        self.game.reset()

        # Run game while not dead
        while not self.game.DEAD and not self.QUIT:

            # Tick clock
            self.clock.tick()
            
            # Calculate appropriate action for current state
            action = net.activate(self.game.get_state())

            # Step game
            print(action.index(max(action)))
            self.game.step(action.index(max(action)))

            # Render window
            self.game.render_window()

            # Update display
            pygame.display.update()

            # Event listener
            for event in pygame.event.get():

                # Exit Condition
                if event.type == pygame.QUIT:
                    self.QUIT = True
                    pygame.quit()
        
        # Return fitness
        return self.game.score

if __name__ == "__main__":
    trainer = neat_trainer()
    trainer.train()