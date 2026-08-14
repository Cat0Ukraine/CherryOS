from CherryAPI import CherryAPI
import time
import random

volume = 8192


def run():
    player_x = 60
    blocks = []  # each block: [x, y]
    score = 0
    speed = 1.5
    alive = True
    spawn_timer = 0

    CherryAPI.fill(0)
    CherryAPI.text("Dodger", 0, 0, 1)
    CherryAPI.text("Next/Prev = move", 0, 20, 1)
    CherryAPI.text("Black = start", 0, 32, 1)
    CherryAPI.show()
    while CherryAPI.pressed(2):
        pass
    while not CherryAPI.pressed(2):
        pass

    while alive:
        if CherryAPI.pressed(1) and player_x < 118:
            player_x += 4
        if CherryAPI.pressed(3) and player_x > 0:
            player_x -= 4

        spawn_timer += 1
        if spawn_timer > max(10, 30 - int(score / 5)):
            spawn_timer = 0
            blocks.append([random.randint(0, 118), 0])

        for b in blocks:
            b[1] += speed

        for b in blocks:
            if b[1] > 58 and player_x < b[0] + 8 and player_x + 8 > b[0]:
                alive = False

        blocks = [b for b in blocks if b[1] < 64]
        score += 1

        CherryAPI.fill(0)
        CherryAPI.text(str(score // 10), 0, 0, 1)
        CherryAPI.fill_rect(player_x, 58, 8, 6, 1)
        for b in blocks:
            CherryAPI.fill_rect(b[0], int(b[1]), 8, 4, 1)
        CherryAPI.show()
        time.sleep(0.03)

    CherryAPI.fill(0)
    CherryAPI.text("Game over!", 0, 0, 1)
    CherryAPI.text(f"Score: {score // 10}", 0, 12, 1)
    CherryAPI.text("Black - exit", 0, 40, 1)
    CherryAPI.sound(300, 0.3, volume)
    CherryAPI.show()
    while not CherryAPI.pressed(2):
        pass
    while CherryAPI.pressed(2):
        pass


run()
