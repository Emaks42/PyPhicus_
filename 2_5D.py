import random

import pygame
import math
from numba import njit, prange


@njit(fastmath=True)
def distance(x1, y1, x2, y2):
    dist = pow((pow(x2-x1,2)+pow(y2-y1,2)),0.5)
    return dist


@njit(fastmath=True)
def sign(n):
    return -1 if n < 0 else 1 if n > 0 else 0


@njit(fastmath=True)
def is_in_triangle(x1, y1, x2, y2, x3, y3, x0, y0):
    n1 = (x1 - x0) * (y2 - y1) - (x2 - x1) * (y1 - y0)
    n2 = (x2 - x0) * (y3 - y2) - (x3 - x2) * (y2 - y0)
    n3 = (x3 - x0) * (y1 - y3) - (x1 - x3) * (y3 - y0)
    if n1 > 0 and n2 > 0 and n3 > 0:
        return True
    return False

@njit(fastmath=True)
def calculate(x,y,px,py,tga,ctga,shrx,shry):
    delta = tga + ctga
    delta_x = x * ctga + y + px * tga - py
    delta_y = -px + py * ctga + x + y * tga
    col_x = delta_x / delta
    col_y = delta_y / delta
    dist = distance(px, py, col_x, col_y)
    scp = sign((col_x - x) * shrx + (col_y - y) * shry)
    # print(col_x,col_y,delta_x,delta_y,delta,dist,scp)
    screen_shift = distance(x, y, col_x, col_y) * scp * (540 / dist)
    return screen_shift, dist


@njit(fastmath=True)
def calc2(x,y,px,py,cosa,sina,cosa_,sina_):
    cx = px - x
    cy = py - y
    delta = cosa * sina_ - sina * cosa_
    delta_y = cx * sina_ - cy * cosa_
    delta_x = cy * cosa - cx * sina
    return delta_x / delta * (540 / (delta_y / delta)), delta_y / delta


@njit(fastmath=True)
def get_intersection(x,y,tga,x1,y1,x2,y2):
    if x2 - x1 == 0:
        x1 += 0.0001
    tgb = (y2 - y1) / (x2 - x1)
    delta = -tgb + tga
    delta_x = -tgb*x1 + y1 + tga * x - y
    delta_y = tgb * (tga * x - y) - tga * (tgb * x1 - y1)
    if delta == 0:
        return 0, 0
    return delta_x / delta, delta_y / delta


@njit(fastmath=True)
def is_point_on_otr(x,y,x1,y1,x2,y2):
    return sign((x1-x)*(x2-x) + (y1-y) * (y2-y)) < 0


def render(map,x,y,a,b,a1,b1,rot):
    tga = math.tan(rot / 57.3)
    if tga == 0:
        tga = 0.00000001
    ctga = 1 / tga
    shrx = math.cos((rot+90) / 57.3)
    shry = math.sin((rot + 90) / 57.3)

    for point in map:
        h1 = is_in_triangle(x,y,a,b,a1,b1,point[0],point[1])
        h2 = is_in_triangle(x,y,a,b,a1,b1,point[2],point[3])
        if h1 and h2:
            screen_shift, dist = calculate(x,y,point[0],point[1],tga,ctga,shrx,shry)
            screen_shift1, dist1 = calculate(x, y, point[2], point[3], tga, ctga, shrx, shry)
            pygame.draw.polygon(screen,[255,2,200],[[540 + screen_shift,dist / 14],[540 + screen_shift1,dist1 / 14],
                                                    [540 + screen_shift1,600 - dist1 / 14],[540 + screen_shift,600 - dist / 14]])


def render2(map,x,y,a,b,a1,b1,rot):
    ca = math.cos(rot / 57.3)
    sa = math.sin(rot / 57.3)
    ca_ = math.cos((rot + 90) / 57.3)
    sa_ = math.sin((rot + 90) / 57.3)
    tga1 = math.tan((rot - 45) / 57.3)
    tga2 = math.tan((rot + 45) / 57.3)
    decr = 14
    heist = 10

    for point in map:
        h1 = is_in_triangle(x, y, a, b, a1, b1, point[0], point[1])
        h2 = is_in_triangle(x, y, a, b, a1, b1, point[2], point[3])
        if h1 and h2:
            screen_shift, dist = calc2(x, y, point[0], point[1], ca, sa, ca_, sa_)
            screen_shift1, dist1 = calc2(x, y, point[2], point[3], ca, sa, ca_, sa_)
            pygame.draw.polygon(screen, [255, 2, 200],
                                [[540 + screen_shift, min(300 - heist,dist / decr)],
                                 [540 + screen_shift1, min(300 - heist,dist1 / decr)],
                                 [540 + screen_shift1, max(300 + heist,600 - dist1 / decr)],
                                 [540 + screen_shift, max(300 + heist,600 - dist / decr)]])
        elif h1:
            screen_shift, dist = calc2(x, y, point[0], point[1], ca, sa, ca_, sa_)
            ix, iy = get_intersection(x,y,tga1,point[0], point[1],point[2], point[3])
            if is_point_on_otr(ix,iy,point[0], point[1],point[2], point[3]) and not(ix == 0 and iy == 0):
                screen_shift1, dist1 = calc2(x, y, ix, iy, ca, sa, ca_, sa_)
            else:
                ix, iy = get_intersection(x, y, tga2, point[0], point[1], point[2], point[3])
                screen_shift1, dist1 = calc2(x, y, ix, iy, ca, sa, ca_, sa_)
            pygame.draw.polygon(screen, [255, 2, 200],
                                [[540 + screen_shift, min(300 - heist, dist / decr)],
                                 [540 + screen_shift1, min(300 - heist, dist1 / decr)],
                                 [540 + screen_shift1, max(300 + heist, 600 - dist1 / decr)],
                                 [540 + screen_shift, max(300 + heist, 600 - dist / decr)]])
        elif h2:
            ix, iy = get_intersection(x, y, tga1, point[0], point[1], point[2], point[3])
            if is_point_on_otr(ix, iy, point[0], point[1], point[2], point[3]) and not(ix == 0 and iy == 0):
                screen_shift, dist = calc2(x, y, ix, iy, ca, sa, ca_, sa_)
            else:
                ix, iy = get_intersection(x, y, tga2, point[0], point[1], point[2], point[3])
                screen_shift, dist = calc2(x, y, ix, iy, ca, sa, ca_, sa_)
            screen_shift1, dist1 = calc2(x, y, point[2], point[3], ca, sa, ca_, sa_)
            pygame.draw.polygon(screen, [255, 2, 200],
                                [[540 + screen_shift, min(300 - heist, dist / decr)],
                                 [540 + screen_shift1, min(300 - heist, dist1 / decr)],
                                 [540 + screen_shift1, max(300 + heist, 600 - dist1 / decr)],
                                 [540 + screen_shift, max(300 + heist, 600 - dist / decr)]])
        else:
            ix, iy = get_intersection(x, y, tga1, point[0], point[1], point[2], point[3])
            ix1, iy1 = get_intersection(x, y, tga2, point[0], point[1], point[2], point[3])
            if is_point_on_otr(ix, iy, point[0], point[1], point[2], point[3]) and \
                is_point_on_otr(ix1, iy1, point[0], point[1], point[2], point[3]):
                screen_shift, dist = calc2(x, y, ix, iy, ca, sa, ca_, sa_)
                screen_shift1, dist1 = calc2(x, y, ix1, iy1, ca, sa, ca_, sa_)
                pygame.draw.polygon(screen, [255, 2, 200],
                                    [[540 + screen_shift, min(300 - heist, dist / decr)],
                                     [540 + screen_shift1, min(300 - heist, dist1 / decr)],
                                     [540 + screen_shift1, max(300 + heist, 600 - dist1 / decr)],
                                     [540 + screen_shift, max(300 + heist, 600 - dist / decr)]])



screen = pygame.display.set_mode((1080, 600))
screen.set_alpha(None)
pygame.display.set_caption("3D Engine")

pygame.mouse.set_visible(False)

screen.fill([0, 0, 0])
pygame.display.flip()

clock = pygame.time.Clock()
FPS = 60 # кадры  в секунду

x = 0  # координата x игрока
y = 5  # координата y игрока

speed = 10  # скорость игрока
speed_rotation = 1  # скорость поворота игрока


lesser_hypo_of_va = 2160 * 10


a = 1658  # координата x левой вершины поля зрения
b = 300  # координата y левой вершины поля зрения

a1 = 300  # координата x правой вершины поля зрения
b1 = 1658  # координата y правой вершины поля зрения

rot_left = 90  # угол поворота левой границы поля зрения
rot_right = 180  # угол поворота правой границы поля зрения
rotation_midle = 135  # угол поворота камеры (то что ты просил)
vision_r = 1400

a_projection = 0
b_projection = 0
h_fe = 0

map = [[-3,-3,-3,20000],[-3,20000,20000,20000], [2000,-3,20000,20000], [20000,-3,-3,-3]]
'''bx = 0
by = 0
pbx = 0
pby = 0
for k in range(7):
    bx += 60
    by += -90
    map.append([bx,by,pbx,pby])
    pbx = bx
    pby = by
    bx += -60
    by += 20
    map.append([bx, by, pbx, pby])
    pbx = bx
    pby = by
    bx += 120
    by += 30
    map.append([bx, by, pbx, pby])
    pbx = bx
    pby = by'''
print(map)


running = True  # значение работы программы
move_up = False
move_down = False
move_right = False
move_left = False
camera_left = False
camera_right = False

mini_map_shift_x = 100
mini_map_shift_y = 300

while running:  # начало основного цикла

    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                move_up = True
            if event.key == pygame.K_s:
                move_down = True
            if event.key == pygame.K_d:
                move_right = True
            if event.key == pygame.K_a:
                move_left = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                move_up = False
            if event.key == pygame.K_s:
                move_down = False
            if event.key == pygame.K_d:
                move_right = False
            if event.key == pygame.K_a:
                move_left = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                camera_left = True
            if event.button == 3:
                camera_right = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                camera_left = False
            if event.button == 3:
                camera_right = False

    if move_up:
        x += math.cos(rotation_midle / 57.3) * speed
        y += math.sin(rotation_midle / 57.3) * speed
    if move_down:
        x -= math.cos(rotation_midle / 57.3) * speed
        y -= math.sin(rotation_midle / 57.3) * speed
    if move_left:
        x += math.cos((rotation_midle - 90) / 57.3) * speed
        y += math.sin((rotation_midle - 90) / 57.3) * speed
    if move_right:
        x += math.cos((rotation_midle + 90) / 57.3) * speed
        y += math.sin((rotation_midle + 90) / 57.3) * speed

    if camera_left:
        rot_left -= speed_rotation
        rot_right -= speed_rotation
        rotation_midle -= speed_rotation

    if camera_right:
        rot_left += speed_rotation
        rot_right += speed_rotation
        rotation_midle += speed_rotation

    if rot_left >= 360:
        rot_left -= 360

    if rot_left < 0:
        rot_left += 360

    if rot_right >= 360:
        rot_right -= 360

    if rot_right < 0:
        rot_right += 360

    if rotation_midle >= 360:
        rotation_midle -= 360

    if rotation_midle < 0:
        rotation_midle += 360

    angle = rot_left * 3.14 / 180
    a = (lesser_hypo_of_va * math.cos(angle)) + x
    b = (lesser_hypo_of_va * math.sin(angle)) + y

    angle1 = rot_right * 3.14 / 180
    a1 = (lesser_hypo_of_va * math.cos(angle1)) + x
    b1 = (lesser_hypo_of_va * math.sin(angle1)) + y

    screen.fill((0, 0, 0))

    render2(map,x,y,a,b,a1,b1,rotation_midle)

    pygame.draw.circle(screen, [255, 0, 0], [x + mini_map_shift_x, y + mini_map_shift_y], 4)
    for poi in map:
        pygame.draw.line(screen, [255,2,200], [poi[0] + mini_map_shift_x,poi[1] + mini_map_shift_y],
                         [poi[2] + mini_map_shift_x,poi[3] + mini_map_shift_y],2)

    pygame.display.flip()

    print("FPS -", round(clock.get_fps()))
    print("--------")
