#!/usr/bin/env python3
import turtle
import random
import math
import numpy
import time
# G = 2.071e-43
G = 6.67300e-11

# G = 6.67300e-9


def distance(p1, p2):
    return sum((p1.getpos() - p2.getpos())**2)**(1 / 2)


def angle(p1, p2):
    return math.atan2(*((p2.getpos() - p1.getpos())[2::-1]))


def accel_vector(p1, p2):
    F = G * p1.mass * p2.mass / distance(p1, p2)
    a = F / p1.mass
    theta = angle(p1, p2)
    return numpy.array([math.cos(theta), math.sin(theta)]) * a


class Particle:
    def __init__(self,
                 mass: float,
                 position: numpy.array,
                 velocity=None,
                 anchored=False):
        self.mass = mass
        self.pos = numpy.array(position, dtype=float)
        if velocity:
            self.velocity = numpy.array(list(map(float, velocity)))
        else:
            self.velocity = numpy.zeros(len(position), dtype=float)
        self.acceleration = numpy.zeros(len(position), dtype=float)
        self.anchored = anchored

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, np_array: numpy.array):
        self._velocity = numpy.array(np_array)

    def __add__(self, other):
        if not isinstance(other, Particle):
            raise ValueError("Can only add Particle to Particle not {}".format(
                repr(other)))
        else:
            if len(self.pos) != len(other.pos):
                raise ValueError(
                    "Can not add particles with different dimensionalities.")
            ms = numpy.array([self.mass, other.mass])
            sm = sum(ms)
            p = Particle(
                self.mass + other.mass,
                (self.pos * self.mass / sm + other.pos * other.mass / sm) / 2)
            return p

    def getpos(self):
        return numpy.array(self.pos)

    def be_pulled(self, other):
        self.acceleration = accel_vector(self, other)
        # print(self.acceleration)

    def add_pull(self, other):
        self.acceleration += accel_vector(self, other)

    def simulate(self, time_step):
        if not self.anchored:
            time_step = float(time_step)
            self._velocity += self.acceleration * time_step
            # if any(abs(i) > 0 for i in self._velocity):
            #     print(self._velocity)
            self.pos += self._velocity * time_step

    def __str__(self):
        return "Particle({},{})".format(self.mass, self.pos)

    def __eq__(self, other):
        return self.mass == other.mass and all(self.pos == other.pos)


class ParticleField:
    def __init__(self, particles):
        self.ps = particles

    def get_particles(self):
        return self.ps[:]

    def combined(self):
        avg_mass = sum(self.ps[1:], self.ps[0])
        return avg_mass

    def time_step(self, step):
        for p in self.ps:
            p.acceleration *= 0
        for index, p in enumerate(self.ps):
            for otherindex, other in list(enumerate(self.ps))[index + 1:]:
                p.add_pull(other)
                other.add_pull(p)
        for p in self.ps:
            p.simulate(step)


def test_Particle():
    p1 = Particle(1, (0, 0))
    p2 = Particle(2, (1, 1))
    print(p1 + p2)
    ps = []
    for _ in range(10):
        ps.append(
            Particle(random.random(), (random.random(), random.random())))
    print(sum(ps[1:], ps[0]))
    p1.be_pulled(p2)
    p1.simulate(1)
    assert p1.getpos()[0] != 0


def test_distance():
    assert distance(Particle(0, (0, 0)), Particle(0, (0, 1))) == 1
    assert angle(Particle(0, (0, 0)), Particle(0,
                                               (0, 1))) * 180 / math.pi == 90


def test_ParticleField():
    ps = [
        Particle(
            random.randint(10, 200),
            [float(random.randint(0, 1)) for i in range(2)]) for i in range(10)
    ]
    pf = ParticleField(ps)
    # for i in range(5):
    #     print([str(i) for i in pf.get_particles()])
    #     pf.time_step(10)
    p1i = Particle(10000000000, (0, 0))
    p1f = Particle(10000000000, (0, 0))
    p2 = Particle(2, (1, 1))
    for i in range(100):
        p1f.be_pulled(p2)
        p1f.simulate(100000)
    assert all(p1i.getpos() != p1f.getpos())
    print(p1f.getpos())


def randcolor():
    return tuple([random.random() for i in range(3)])


WIDTH, HEIGHT = 1920, 1080


def main():
    turtle.setup(WIDTH, HEIGHT)
    # screen.colormode(255)
    ps = [
        Particle(
            random.randint(1e8, 1e12),
            [random.randint(-a // 2, a // 2) for a in (WIDTH, HEIGHT)],
            velocity=[(random.random() - 0.5) * 8 for i in range(2)])
        for i in range(12)
    ]
    # ps.append(Particle(1e10, [0, 0], anchored=True))
    ts = [turtle.Turtle() for i in ps]
    pf = ParticleField(ps)
    for t, p in zip(ts, ps):
        # make each turtle unique by color
        # also set them to max speed
        # and make them go to the initial positions of their particles.
        t.pencolor(randcolor())
        t.speed(0)
        t.hideturtle()
        t.goto(p.getpos())
        t.clear()
        t.dot((math.log(p.mass) / math.log(10)))
    granularity = 100
    time_step = 1
    try:
        going = True
        while going:
            parts = pf.get_particles()
            # print(list(map(str, parts)))
            if all(
                    abs(p.pos[0]) > WIDTH / 2 or abs(p.pos[1]) > HEIGHT / 2
                    for p in parts):
                going = False
            for index, p in enumerate(parts):
                t = ts[index]
                # t.clear()
                # t.penup()
                pos = p.getpos()
                t.goto(pos)
                # t.setx(pos[0])
                # t.sety(pos[1])
                # t.dot(math.log(p.mass))
            # time.sleep(1)
            for _ in range(granularity):
                pf.time_step(time_step / granularity)
        print("DONE")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(list(p.velocity for p in ps))


if __name__ == '__main__':
    main()
