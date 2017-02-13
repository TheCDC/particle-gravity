#!/usr/bin/env python3
import newtonian
import pygame
import pygame.gfxdraw
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
            # x1, y1 = tuple(map(int, self.pos))
            # x2, y2 = tuple(map(int, pos))
            # pygame.gfxdraw.line(self.surf, x1, y1, x2, y2, self.color)
        self.pos = pos[:]

    def getpos(self):
        return self.pos[:]

    def penup(self):
        self.pen = False

    def pendown(self):
        self.pen = True


class GraphicalSimulation:

    def __init__(self, surface, N=None, bg_color=(0, 0, 0)):
        self.bg_color = tuple(bg_color[:])
        self.surf = surface
        self.bottom_layer = pygame.Surface(
            (self.surf.get_width(), self.surf.get_height()),
            flags=pygame.HWSURFACE,
            depth=32)
        self.top_layer = pygame.Surface(
            (self.bottom_layer.get_width(), self.bottom_layer.get_height()),
            # pygame.HWSURFACE puts the surface in video memory
            # pygame.SRCALPHA initializes the surface with per-pixel alpha
            flags=pygame.HWSURFACE | pygame.SRCALPHA,
            depth=32).convert_alpha()

        self.bottom_layer.fill(self.bg_color)
        self.size = (self.bottom_layer.get_width(),
                     self.bottom_layer.get_height())
        if N is None:
            n = 12
        else:
            n = N
        # self.bottom_layer.fill(self.bg_color)
        mass_range_exponents = (8, 12)
        self.particles = [newtonian.Particle(mass=random.randint(*[10**i for i in mass_range_exponents]), position=[
            random.randint(0, a) for a in self.size], velocity=[(random.random() - 0.5) * 24 for i in range(2)]) for i in range(n)]
        # big mass in the center
        self.particles.append(newtonian.Particle(
            mass=10**(max(mass_range_exponents)),
            position=[(random.random() - 0.5) * a /
                      4 + a / 2 for a in self.size],
            velocity=(0, 0)))

        self.field = newtonian.ParticleField(self.particles)
        self.turtles = [Turtle(self.bottom_layer, randcolor())
                        for _ in self.particles]
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
                # pygame.draw.circle(self.bottom_layer, t.color,
                # tuple(map(int, t.getpos())), int((math.log(p.mass**2))**(1 /
                # 2)))
                x, y = tuple(map(int, t.getpos()))
                pygame.gfxdraw.aacircle(self.bottom_layer,
                                        x, y, int((math.log(p.mass**2))**(1 / 2)), t.color)
        self.frames += 1
        # self.top_layer.fill(self.bg_color)
        self.top_layer.fill((0, 0, 0, 0))
        # self.surf.fill(self.bg_color)
        for t, p in zip(self.turtles, self.field.get_particles()):
            t.setpos(p.getpos())
            # pygame.draw.circle(self.top_layer, t.color,
            # tuple(map(int, t.getpos())), int((math.log(p.mass**2))**(1 / 2)))
            x, y = tuple(map(int, t.getpos()))
            pygame.gfxdraw.filled_circle(self.top_layer,
                                         x, y, int((math.log(p.mass**2))**(1 / 2)), t.color)
        self.surf.blit(self.bottom_layer, (0, 0),
                       # special_flags=pygame.BLEND_RGBA_MULT
                       special_flags=0
                       )
        self.surf.blit(self.top_layer, (0, 0),
                       # special_flags=pygame.BLEND_RGB_MAX
                       special_flags=0
                       )


def default_simulation():
    infoObj = pygame.display.Info()
    WIDTH = int(infoObj.current_w)
    HEIGHT = int(infoObj.current_h)
    size = (WIDTH, HEIGHT)

    trail_surface = pygame.Surface(size)
    trail_surface.fill((255, 255, 255))
    sim = GraphicalSimulation(
        trail_surface, random.randint(3, 15), bg_color=(0, 0, 0))
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
        size, pygame.FULLSCREEN | pygame.DOUBLEBUF)
    sim = default_simulation()
    ti = time.time()
    total_time = 0

    def wipe():
        for i in range(0, 255, 255 // 60):
            DISPLAYSURF.fill((i, i, i))
            pygame.display.update()
            CLOCK.tick(60)
        for i in range(255, 0, -255 // 60):
            DISPLAYSURF.fill((i, i, i))
            pygame.display.update()
            CLOCK.tick(60)
        DISPLAYSURF.fill((1, 1, 1))

    def save():
        pygame.image.save(DISPLAYSURF, os.path.join(
            "screenshots", time.strftime("%Y-%m-%d %H-%M-%S") + ".png"))

    do_reset = False
    while True:
        tf = time.time()
        if tf - ti >= 60:
            do_reset = True
            save()
        if do_reset:
            wipe()
            sim = default_simulation()
            ti = time.time()
            do_reset = False

        for event in pygame.event.get():
            #~ print(event)
            if event.type == pygame.QUIT or pygame.mouse.get_pressed()[0] == 1:
                save()
                pygame.mixer.quit()
                pygame.quit()
                sys.exit()
            if pygame.mouse.get_pressed()[2] == 1:
                do_reset = True

        granularity = 10
        step = 0.25
        for _ in range(granularity):
            sim.update(step / granularity)
        try:
            sim.draw()
        except OverflowError:
            save()
            do_reset = True
        CLOCK.tick(60)
        # time.sleep(1/60)
        DISPLAYSURF.blit(sim.surf, (0, 0), special_flags=0)
        pygame.display.update()
        # print("yes")
if __name__ == '__main__':
    main()
