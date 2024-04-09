import random
import pygame
import math
from numba import njit, prange
import numba
import pygame.gfxdraw
import numpy as np
import datetime


@njit(fastmath=True)
def n_angle(ang):
    if ang > 360:
        ang -= 360
    elif ang < 0:
        ang += 360
    return ang


@njit(fastmath=True)
def is_in_triangle(x1, y1, x2, y2, x3, y3, x0, y0):
    n1 = (x1 - x0) * (y2 - y1) - (x2 - x1) * (y1 - y0)
    n2 = (x2 - x0) * (y3 - y2) - (x3 - x2) * (y2 - y0)
    n3 = (x3 - x0) * (y1 - y3) - (x1 - x3) * (y3 - y0)
    if n1 > 0 and n2 > 0 and n3 > 0:
        return True
    return False


@njit(fastmath=True)
def get_defenitor3(a11,a12,a13,a21,a22,a23,a31,a32,a33):
    return a11 * a22 * a33 + a12 * a23 * a31 + a21 * a32 * a13 - \
        a13 * a22 * a31 - a12 * a21 * a33 - a23 * a32 * a11


@njit(fastmath=True)
def calc_3d(x, y, z, x0, y0, z0, cosb, sinb, sina, cosb_, sinb_, sina_):
    cx = x - x0
    cy = y - y0
    cz = z - z0
    delta = get_defenitor3(cosb_, cosb, cosb, sinb_, sinb, sinb, sina, sina, sina_)
    delta_s = get_defenitor3(cx, cosb, cosb, cy, sinb, sinb, cz, sina, sina_)
    delta_d = get_defenitor3(cosb_, cx, cosb, sinb_, cy, sinb, sina, cz, sina_)
    delta_s_ = get_defenitor3(cosb_, cosb, cx, sinb_, sinb, cy, sina, sina, cz)
    return delta_s / delta, delta_d / delta, delta_s_ / delta


def render(map,x,y,z,a,b,a1,b1,angle_a,angle_b):
    sa = np.sin(angle_a / 57.3)
    sa_ = np.sin((angle_a + 90) / 57.3)
    cb = np.cos(angle_b / 57.3)
    cb_ = np.cos((angle_b + 90) / 57.3)
    sb = np.sin(angle_b / 57.3)
    sb_ = np.sin((angle_b + 90) / 57.3)
    dist_mean = 2500

    for polygon in map:
        h1 = is_in_triangle(x, y, a, b, a1, b1, polygon[0], polygon[1])
        h2 = is_in_triangle(x, y, a, b, a1, b1, polygon[3], polygon[4])
        h3 = is_in_triangle(x, y, a, b, a1, b1, polygon[6], polygon[7])
        if h1 and h2 and h3:
            shift_x1, dist1, shift_y1 = calc_3d(polygon[0], polygon[1], polygon[2], x, y, z,
                                             cb, sb, sa, cb_, sb_, sa_)
            shift_x2, dist2, shift_y2 = calc_3d(polygon[3], polygon[4], polygon[5], x, y, z,
                                             cb, sb, sa, cb_, sb_, sa_)
            shift_x3, dist3, shift_y3 = calc_3d(polygon[6], polygon[7], polygon[8], x, y, z,
                                             cb, sb, sa, cb_, sb_, sa_)
            p1_x, p1_y = shift_x1 * (dist_mean / dist1), shift_y1 * (dist_mean / dist1)
            p2_x, p2_y = shift_x2 * (dist_mean / dist2), shift_y2 * (dist_mean / dist2)
            p3_x, p3_y = shift_x3 * (dist_mean / dist3), shift_y3 * (dist_mean / dist3)
            #print([p1_x, p1_y], [p2_x, p2_y], [p3_x, p3_y])
            pygame.gfxdraw.filled_polygon(screen,[[500 + p1_x, 300 + p1_y], [500 + p2_x, 300 + p2_y], [500 + p3_x, 300 + p3_y]],[250,60,200])



pygame.font.init()

my_font = pygame.font.SysFont("arial", 15)

rot_x = 135
rot_y = 0

lesser_hypo_of_va = 2160 * 10


a = 1658  # координата x левой вершины поля зрения
b = 300  # координата y левой вершины поля зрения

a1 = 300  # координата x правой вершины поля зрения
b1 = 1658  # координата y правой вершины поля зрения

rot_left = 90  # угол поворота левой границы поля зрения
rot_right = 180  # угол поворота правой границы поля зрения

x = 1500
y = 1500
z = 50

map = [[0,0,0,200,200,0,200,200,150],[200,200,150,0,0,0,0,0,150],[0,0,150,200,200,150,100,400,150],
       [200,200,0,200,200,150,100,400,150],[100,400,150,100,400,0,200,200,0],[100,400,0,0,0,0,0,0,150],
       [0,0,150,100,400,150,100,400,0],[0,0,0,200,200,0,100,400,0]]

for i in range(0):
    map.append([random.randint(30,100) * 10, random.randint(30,100) * 10, random.randint(30,100) * 10,
                random.randint(30,100) * 10, random.randint(30,100) * 10, random.randint(30,100) * 10,
                random.randint(30,100) * 10, random.randint(30,100) * 10, random.randint(30,100) * 10])

fieldx = 1000
fieldy = 600

screen = pygame.display.set_mode((fieldx,fieldy))
screen.set_alpha(None)
pygame.display.set_caption("3D Engine")

clock = pygame.time.Clock()
FPS = 60  # кадры  в секунду

speed = 10
speed_rotation = 1  # скорость поворота игрока

running = True  # значение работы программы
move_forward = False
move_backward = False
move_right = False
move_left = False
move_up = False
move_down = False

camera_left = False
camera_right = False

#pygame.mouse.set_visible(False)


while running:  # начало основного цикла

    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                move_forward = True
            if event.key == pygame.K_s:
                move_backward = True
            if event.key == pygame.K_d:
                move_right = True
            if event.key == pygame.K_a:
                move_left = True
            if event.key == pygame.K_SPACE:
                move_up = True
            if event.key == pygame.K_LSHIFT:
                move_down = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                move_forward = False
            if event.key == pygame.K_s:
                move_backward = False
            if event.key == pygame.K_d:
                move_right = False
            if event.key == pygame.K_a:
                move_left = False
            if event.key == pygame.K_SPACE:
                move_up = False
            if event.key == pygame.K_LSHIFT:
                move_down = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                camera_left = True
            if event.button == 3:
                camera_right = True
            if event.button == 4:
                rot_y += speed_rotation
                rot_y = n_angle(rot_y)
            if event.button == 5:
                rot_y -= speed_rotation
                rot_y = n_angle(rot_y)
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                camera_left = False
            if event.button == 3:
                camera_right = False

    if move_forward:
        x += math.cos(rot_x / 57.3) * speed
        y += math.sin(rot_x / 57.3) * speed
    if move_backward:
        x -= math.cos(rot_x / 57.3) * speed
        y -= math.sin(rot_x / 57.3) * speed
    if move_left:
        x += math.cos((rot_x - 90) / 57.3) * speed
        y += math.sin((rot_x - 90) / 57.3) * speed
    if move_right:
        x += math.cos((rot_x + 90) / 57.3) * speed
        y += math.sin((rot_x + 90) / 57.3) * speed
    if move_up:
        z -= speed
    if move_down:
        z += speed

    if camera_left:
        rot_left -= speed_rotation
        rot_right -= speed_rotation
        rot_x -= speed_rotation
        rot_x = n_angle(rot_x)
        rot_left = n_angle(rot_left)
        rot_right = n_angle(rot_right)

    if camera_right:
        rot_left += speed_rotation
        rot_right += speed_rotation
        rot_x += speed_rotation
        rot_x = n_angle(rot_x)
        rot_left = n_angle(rot_left)
        rot_right = n_angle(rot_right)

    angle = rot_left * 3.14 / 180
    a = (lesser_hypo_of_va * math.cos(angle)) + x
    b = (lesser_hypo_of_va * math.sin(angle)) + y

    angle1 = rot_right * 3.14 / 180
    a1 = (lesser_hypo_of_va * math.cos(angle1)) + x
    b1 = (lesser_hypo_of_va * math.sin(angle1)) + y

    screen.fill((0,0,0))

    render(map,x,y,z,a,b,a1,b1,rot_y,rot_x)

    '''mp = pygame.mouse.get_pos()
    rot_y += (mp[1] - fieldy // 2) // 6
    rot_y = n_angle(rot_y)
    if rot_y > 90 and rot_y <= 270:
        rot_y = 90
    elif rot_y < 270 and rot_y >= 90:
        rot_y = 270
    rot_x += (mp[0] - fieldx // 2) // 6
    rot_x = n_angle(rot_x)
    rot_left += (mp[0] - fieldx // 2) // 6
    rot_left = n_angle(rot_left)
    rot_right += (mp[0] - fieldx // 2) // 6
    rot_right = n_angle(rot_right)'''

    #pygame.mouse.set_pos(fieldx // 2, fieldy // 2)


    print(round(clock.get_fps()))

    pygame.display.flip()
