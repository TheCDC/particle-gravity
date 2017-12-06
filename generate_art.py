from graphical import headless_generate_art
import time
c = 0
while c < 200:
    try:
        headless_generate_art()
        c += 1
        print(c, time.ctime())
    except RuntimeError:
        pass
