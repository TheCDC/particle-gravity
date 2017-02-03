#!/usr/bin/env python3
import newtonian
import pygame
import random
import time
import sys
import math
import os


def randcolor():
    return tuple([int(random.random() * 255) for i in range(3)])


class Turtle:

    def __init__(self, surf, color):
        self.surf = surf
        self.pos = (0, 0)
        self.pen = True
        self.color = color

    def setpos(self, pos):
        if self.pen:
            pygame.draw.aaline(self.surf, self.color, self.pos, pos, 1)
        self.pos = pos[:]

    def getpos(self):
        return self.pos[:]

    def penup(self):
        self.pen = False

    def pendown(self):
        self.pen = True


class GraphicalSimulation:

    def __init__(self, surface, N=None):
        self.surf = surface
        self.bottom_layer = pygame.Surface(
            (self.surf.get_width(), self.surf.get_height()))
        self.size = (self.bottom_layer.get_width(),
                     self.bottom_layer.get_height())
        if not (N == None):
            n = 12
        else:
            n = N

        mass_range_exponents = (8, 12)
        self.particles = [newtonian.Particle(mass=random.randint(*[10**i for i in mass_range_exponents]), position=[
                                             random.randint(0, a) for a in self.size], velocity=[(random.random() - 0.5) * 24 for i in range(2)]) for i in range(n)]
        # big mass in the center
        self.particles.append(newtonian.Particle(
            mass=10**(max(mass_range_exponents)), position=[(random.random() - 0.5) * a / 4 + a / 2 for a in self.size], velocity=(0, 0)))

        self.field = newtonian.ParticleField(self.particles)
        self.turtles = [Turtle(self.bottom_layer, randcolor())
                        for _ in self.particles]
        self.top_layer = pygame.Surface(
            (self.bottom_layer.get_width(), self.bottom_layer.get_height()))
        for t, p in zip(self.turtles, self.field.get_particles()):
            t.penup()
            t.setpos(p.getpos())
            t.pendown()
        self.frames = 0

    def update(self, step=1 / 100):
        self.field.time_step(step)

    def draw(self):
        if self.frames == 0:
            for t, p in zip(self.turtles, self.field.get_particles()):
                t.setpos(p.getpos())
                pygame.draw.circle(self.bottom_layer, t.color,
                                   tuple(map(int, t.getpos())), int((math.log(p.mass**2))**(1 / 2)))
        self.frames += 1
        self.top_layer.fill((0, 0, 0))
        self.surf.fill((0, 0, 0))
        for t, p in zip(self.turtles, self.field.get_particles()):
            t.setpos(p.getpos())
            pygame.draw.circle(self.top_layer, t.color,
                               tuple(map(int, t.getpos())), int((math.log(p.mass**2))**(1 / 2)))
        self.surf.blit(self.bottom_layer, (0, 0),
                       special_flags=pygame.BLEND_MAX)
        self.surf.blit(self.top_layer, (0, 0),
                       special_flags=pygame.BLEND_RGBA_ADD)


def default_simulation():
    infoObj = pygame.display.Info()
    WIDTH = int(infoObj.current_w)
    HEIGHT = int(infoObj.current_h)
    size = (WIDTH, HEIGHT)

    trail_surface = pygame.Surface(size)
    sim = GraphicalSimulation(trail_surface, random.randint(3, 12))
    return sim


def main():
    pygame.init()
    infoObj = pygame.display.Info()
    WIDTH = int(infoObj.current_w)
    HEIGHT = int(infoObj.current_h)
    size = (WIDTH, HEIGHT)
    CLOCK = pygame.time.Clock()
    # WIDTH = 600
    # HEIGHT = 600
    DISPLAYSURF = pygame.display.set_mode(
        size, pygame.DOUBLEBUF | pygame.FULLSCREEN)
    sim = default_simulation()
    ti = time.time()

    def wipe():
        for i in range(0, 255, 255 // 60):
            DISPLAYSURF.fill((i, i, i))
            pygame.display.update()
            CLOCK.tick(60)
        for i in range(255, 0, -255 // 60):
            DISPLAYSURF.fill((i, i, i))
            pygame.display.update()
            CLOCK.tick(60)
        DISPLAYSURF.fill((0, 0, 0))

    do_reset = False
    while True:
        tf = time.time()
        if tf - ti >= 60:
            pygame.image.save(DISPLAYSURF, os.path.join(
                "screenshots", time.strftime("%Y-%m-%d %H-%M-%S") + ".png"))
            do_reset = True

        if do_reset:
            wipe()
            sim = default_simulation()
            ti = time.time()
            do_reset = False

        for event in pygame.event.get():
            #~ print(event)
            if event.type == pygame.QUIT or pygame.mouse.get_pressed()[0] == 1:
                pygame.mixer.quit()
                pygame.quit()
                sys.exit()
            if pygame.mouse.get_pressed()[2] == 1:
                do_reset = True

        granularity = 20
        step = 0.25
        for _ in range(granularity):
            sim.update(step / granularity)
        sim.draw()
        CLOCK.tick(60)
        # time.sleep(1/60)
        DISPLAYSURF.blit(sim.surf, (0, 0))
        pygame.display.update()
        # print("yes")
if __name__ == '__main__':
    main()
