import math
import sys
import random
import time
import pygame
import neat
import config
import os
import pickle

from GameObjects.Bird import Bird
from GameObjects.Floor import Floor
from GameObjects.Pipe import Pipe
from GameObjects.Background import Background


NAMES = ["Violette", "Alexey", "Daulet", "Shmyak", "Alpa", "Mahmud", "Iska", "IslamK"]

pygame.init()
FONT__NAMES = pygame.font.SysFont("Roboto Condensed", 25)
FONT__SCORE = pygame.font.SysFont("Roboto Condensed Bold", 40)
FONT__HEADING = pygame.font.SysFont("Roboto Condensed Semibold Italic", 40)

gen = 0


def draw_all(screen, birds, pipes, floor, background, score):
    background.draw(screen)
    for pipe in pipes:
        pipe.move()
        pipe.draw(screen)
    for bird in birds:
        bird.draw(screen)
        bird.draw_name(screen, FONT__NAMES)
    floor.draw(screen)

    score_label = FONT__SCORE.render("Score: " + str(math.floor(score)), True, (50, 50, 50))
    score_label_rect = score_label.get_rect()
    score_label_rect.center = (config.WINDOW_SIZE[0] - 100, 50)
    screen.blit(score_label, score_label_rect)

    label = FONT__HEADING.render("Genereation: " + str(gen), True, (0, 72, 186))
    label_rect = label.get_rect()
    label_rect.center = (config.WINDOW_SIZE[0] / 2, 25)
    screen.blit(label, label_rect)

    pygame.display.update()


def run_game(genomes, neat_config):
    global gen
    gen += 1
    screen = pygame.display.set_mode((config.WINDOW_SIZE[0], config.WINDOW_SIZE[1]))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Flappy Bird")

    background = Background()
    birds = []
    pipes = [Pipe(600), ]
    score = 0
    floor = Floor(config.WINDOW_SIZE[1])
    nets = []
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, neat_config)
        nets.append(net)
        g.fitness = 0
        birds.append(Bird(random.choice(NAMES),"random", 70, random.randrange(0, 300)))
    while True:
        clock.tick(config.FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # detect the closest pipe
        cpipe = 0
        if len(birds):
            if len(pipes) > 1 and birds[0].x >= pipes[0].x:
                cpipe = 1
        # move birds
        # user_input = pygame.key.get_pressed()
        for bi, bird in enumerate(birds):
            genomes[bi][1].fitness += 1
            bird.move()
            output = nets[bi].activate(
                (round(bird.velocity, 1), round(bird.y, 1), round(pipes[cpipe].height, 1), round(pipes[cpipe].bottom, 1), (pipes[cpipe].x - bird.x)))
            if output[0] > 0.5:
                bird.jump()
            #if user_input[pygame.K_SPACE]:
            #    bird.jump()

        # pipes
        tbd_pipes = []
        add_new_pipe = False
        for pipe in pipes:
            # collision
            for bi, bird in enumerate(birds):
                if pipe.collide(bird, screen):
                    # print(f"Bird {bird.name} is downm ... PIPE GOT HER!")
                    genomes[bi][1].fitness -= 100
                    nets.pop(bi)
                    genomes.pop(bi)
                    birds.pop(bi)
            if pipe.x + pipe.UPPER_PIPE.get_width() < 0:
                tbd_pipes.append(pipe)
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_new_pipe = True
        if add_new_pipe:
            if birds:
                score += 1
            pipes.append(Pipe(pipes[-1].x + config.PIPE_SPAWN_DISTANCE))
            for g in genomes:
                g[1].fitness += 10
        for dp in tbd_pipes:
            pipes.remove(dp)

        # remove fallen birds
        for bi, bird in enumerate(birds):
            if bird.y + bird.cframe.get_height() >= floor.y or bird.y <= 0:
                genomes[bi][1].fitness -= 150
                nets.pop(bi)
                genomes.pop(bi)
                birds.pop(bi)
        draw_all(screen, birds, pipes, floor, background, score)
        if not birds:
            time.sleep(2)
            break


def save(best_genome, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(best_genome, f)


def load(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    return None


if __name__ == '__main__':
    neat_config_path = "./config-feedforward.txt"
    neat_cfg = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, neat_config_path)

    model = 'model.pkl'
    best = load('model')

    if best is None:
        p = neat.Population(neat_cfg)
        best = p.run(run_game, 1000)
        save(best, 'model')
    else:
        # Create a network from the loaded genome and run the game with it
        net = neat.nn.FeedForwardNetwork.create(best, neat_cfg)
        run_game([(None, best)], neat_cfg)
    print('\nWINNER (chicken dinner) IS - \n{!s}'.format(best))
