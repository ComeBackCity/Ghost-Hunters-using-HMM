import math
import numpy as np
import pygame as pg
import random

pg.init()

np.set_printoptions(precision=3)
size = 9
t_size = pow(size, 2)
time = 0
uniform_distribution = float(1.00 / (size * size))
initial_distribution = np.empty((1, t_size))
evidence_array = np.zeros((1, t_size), dtype=np.float)
initial_distribution.fill(uniform_distribution)
transition_matrix = np.zeros((t_size, t_size), dtype=np.float)
color_matrix = np.zeros((size, size))
ghost_pos = random.randint(0, 8)
color = False
last_selected = -1

# initial screen size
screen_size = (1100, 900)

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
BackgroundColor = (10, 135, 140)

gameDisplay = pg.display.set_mode(screen_size)
pg.display.set_caption('Ghostbusters')
grid_font = pg.font.SysFont('Comic Sans MS', 15)
button_font = pg.font.SysFont('Comic Sans MS', 30)

gameExit = False

base = 900 / size
w_base = 32
h_base = 37


def valid(x, y):
    if x < 0 or x >= size or y < 0 or y >= size:
        return False
    return True


def printmatrix(matrix):
    for row in matrix:
        print(row)


directions_small = ((0, 0), (1, 1), (1, -1), (-1, 1), (-1, -1))
directions_large = ((0, 1), (0, -1), (1, 0), (-1, 0))
large_prob = 0.96
small_prob = 0.04

for i in range(t_size):
    row = int(i / size)
    column = i % size
    large = 0
    small = 0
    my_large_directions = []
    my_small_directions = []
    for direction in directions_large:
        if valid(row + direction[0], column + direction[1]):
            large += 1
            my_large_directions.append(direction)

    for direction in directions_small:
        if valid(row + direction[0], column + direction[1]):
            small += 1
            my_small_directions.append(direction)

    large_div = large_prob / large
    small_div = small_prob / small

    for j in range(t_size):
        j_row = int(j / size)
        j_col = j % size
        if directions_small.__contains__((row - j_row, column - j_col)):
            transition_matrix[i][j] = small_div
        elif directions_large.__contains__((row - j_row, column - j_col)):
            transition_matrix[i][j] = large_div


def update_ghost_position():
    global ghost_pos
    r = random.random()
    start = 0.0
    for k in range(t_size):
        if r <= transition_matrix[ghost_pos, k] + start:
            ghost_pos = k
            break
        else:
            start += transition_matrix[ghost_pos, k]


def manhattan_distance(p1, p2):
    row1 = int(p1 / size)
    col1 = p1 % size
    row2 = int(p2 / size)
    col2 = p2 % size
    return abs(row1 - row2) + abs(col1 - col2)


while not gameExit:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            gameExit = True
        elif event.type == pg.MOUSEBUTTONUP:
            mouse_pos = pg.mouse.get_pos()
            if 925 < mouse_pos[0] < 1075 and 600 < mouse_pos[1] < 700:
                initial_distribution = np.dot(initial_distribution, transition_matrix)
                update_ghost_position()
                if color:
                    color_matrix = np.zeros((size, size))
                    color = False
                    last_selected = -1
            elif 925 < mouse_pos[0] < 1075 and 725 < mouse_pos[1] < 825:
                if ghost_pos == last_selected:
                    print('SUCCESS!')
                else:
                    print('FAILED :(')
                gameExit = True
            elif 0 < mouse_pos[0] < 900 and 0 < mouse_pos[1] < 900:
                affected = 0
                evidence_array = np.zeros((1, t_size), dtype=np.float)
                x = int(mouse_pos[1] / base)
                y = int(mouse_pos[0] / base)
                position = x * size + y
                distance = manhattan_distance(ghost_pos, position)
                if distance <= 1:
                    color_matrix[x, y] = 1
                    for i in range(t_size):
                        if manhattan_distance(i, position) <= 1:
                            affected += 1
                    prob = 1 / affected
                    for i in range(t_size):
                        if manhattan_distance(i, position) <= 1:
                            evidence_array[0, i] = prob
                elif distance == 2:
                    color_matrix[x, y] = 2
                    for i in range(t_size):
                        if manhattan_distance(i, position) == 2:
                            affected += 1
                    prob = 1 / affected
                    for i in range(t_size):
                        if manhattan_distance(i, position) == 2:
                            evidence_array[0, i] = prob
                else:
                    color_matrix[x, y] = 3
                    for i in range(t_size):
                        if manhattan_distance(i, position) > 2:
                            affected += 1
                    prob = 1 / affected
                    for i in range(t_size):
                        if manhattan_distance(i, position) > 2:
                            evidence_array[0, i] = prob
                color = True
                product = np.multiply(initial_distribution, evidence_array)
                Sum = np.sum(product)
                initial_distribution = product / Sum
                last_selected = position

    gameDisplay.fill(BackgroundColor)
    for i in range(size):
        y = i * base
        for j in range(size):
            x = j * base
            if color_matrix[i, j] == 1:
                color = RED
                font_color = BLACK
            elif color_matrix[i, j] == 2:
                color = ORANGE
                font_color = BLACK
            elif color_matrix[i, j] == 3:
                color = GREEN
                font_color = BLACK
            elif (i + j) % 2 == 0:
                color = WHITE
                font_color = BLACK
            else:
                color = BLACK
                font_color = WHITE

            if last_selected == i * size + j:
                pg.draw.rect(gameDisplay, BLUE, [x, y, base, base])
                pg.draw.rect(gameDisplay, color, [x+10, y+10, base-20, base-20])
            else:
                pg.draw.rect(gameDisplay, color, [x, y, base, base])
            img = grid_font.render(str(round(initial_distribution[0, i * size + j], 3)), True, font_color)
            gameDisplay.blit(img, (x + w_base, y + h_base))

    # positioning 2 buttons
    pg.draw.rect(gameDisplay, BLACK, [925, 600, 150, 100])
    img = button_font.render('Advance', True, WHITE)
    gameDisplay.blit(img, (940, 625))
    pg.draw.rect(gameDisplay, BLACK, [925, 725, 150, 100])
    img = button_font.render('Catch', True, WHITE)
    gameDisplay.blit(img, (960, 750))
    pg.display.update()

pg.quit()
quit()

# a = np.array([0.2, 0.2, 0.3, 0.3])
# b = np.array([[0.1, 0.5, 0.3, 0.1], [0.1, 0.5, 0.4, 0.0], [0.2, 0.2, 0.3, 0.3], [0.1, 0.2, 0.3, 0.4]])
# c = np.dot(a, b)
# print(c)
