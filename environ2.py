import numba
import pygame, math
import pygame.gfxdraw
from pygame.locals import *
import ctypes
import os
from numba import njit, prange
import random
import numpy as np
import pyphicus
pygame.init()
dir = os.path.abspath(os.curdir)

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()

display_width = user32.GetSystemMetrics(0)
display_heidth = user32.GetSystemMetrics(1)

if display_width > 1920:
    scaling_w = 1920 / display_width
else:
    scaling_w = display_width / 1920

if display_heidth > 1080:
    scaling_h = 1080 / display_heidth
else:
    scaling_h = display_heidth / 1080

print("DW -", display_width)
print("DH -", display_heidth)
print(" ")
print("SW -", scaling_w)
print("SH -", scaling_h)
print(" ")
uolid = 0
display_width = 1920
display_heidth = 1080


@njit(fastmath=True, cache=True, parallel=True)
def getlen(x,y,z):
    return math.sqrt(x*x + y*y + z*z)

@njit(fastmath=True, cache=True, parallel=True)
def scal_pr(x,y,z,x1,y1,z1):
    return x * x1 + y * y1 + z * z1

@njit(fastmath=True, cache=True, parallel=True)
def umv(x,y,z,n):
    return x * n, y * n, z * n

@njit(fastmath=True, cache=True, parallel=True)
def sumv(x,y,z,x1,y1,z1):
    return x + x1, y + y1, z + z1
class vector_3D():
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
    def getlen(self):
        return getlen(self.x,self.y,self.z)
    def scal_proi(self,vec2):
        return scal_pr(self.x,self.y,self.z,vec2.x,vec2.y,vec2.z)
    def umn(self,num):
        self.x, self.y, self.z = umv(self.x,self.y,self.z,num)
    def sum(self,vec2):
        self.x,self.y,self.z = sumv(self.x,self.y,self.z,vec2.x,vec2.y,vec2.z)

@njit(fastmath=True, cache=True, parallel=True)
def sort_optt(len,list,cryt1,cryt2,pred,si):
    i = si
    steps = 0
    while i < len - 1 and steps < pred:
        steps += 1
        ch = False
        if cryt1[i] < cryt1[i + 1]:
            sav = cryt1[i]
            cryt1[i] = cryt1[i + 1]
            cryt1[i + 1] = sav
            sav = cryt2[i]
            cryt2[i] = cryt2[i + 1]
            cryt2[i + 1] = sav
            sav = list[i]
            list[i] = list[i + 1]
            list[i + 1] = sav
            ch = False
        elif cryt1[i] == cryt1[i + 1]:
            ch = True
        elif cryt1[i] == cryt1[i + 1] and cryt2[i] < cryt2[i + 1]:
            sav = cryt1[i]
            cryt1[i] = cryt1[i + 1]
            cryt1[i + 1] = sav
            sav = cryt2[i]
            cryt2[i] = cryt2[i + 1]
            cryt2[i + 1] = sav
            sav = list[i]
            list[i] = list[i + 1]
            list[i + 1] = sav
            ch = False
        elif cryt1[i] > cryt1[i + 1]:
            ch = True
        #print(len, i, cryt1[i], cryt1[i + 1])
        #print(":")
        if not(ch) and i == 0:
            ch = True
        if ch:
            i = i + 1
        else:
            i = i - 1
    return list,cryt1,cryt2,i

class Light():
    def __init__(self,dir,color):
        self.direction = dir
        self.color = color

class Light_object():
    def __init__(self,x,y,color,light_power):
        self.x = x
        self.y = y
        self.color = color
        self.light_power = light_power

class Point:
    def __init__(self, rp, rot_xp, y):
        self.rp = rp
        self.rot_xp = rot_xp
        self.y = y
        self.x = math.cos(self.rot_xp / 57.3) * self.rp
        self.z = math.fabs((math.sin(self.rot_xp / 57.3) * self.rp) / 200)
        if self.z == 0:
            self.z += 0.000000000001
        self.x1 = self.x / self.z
        self.y1 = (self.y - 500) / self.z
        self.x1 = 500 + self.x1 * 2
        self.y1 = 500 + self.y1 * 2
        self.it_coo = [self.x1,self.y1]

    def build(self,rot_x,cxx,zz,yyy):
        n = build_opt(self.rot_xp,self.y,self.rp,rot_x,cxx,zz,yyy)
        if n[0] < display_width * -0.1:
            n[0] = 0
        if n[0] > display_width * 1.1:
            n[0] = display_width * 1.1
        if n[1] < display_heidth * -0.1:
            n[1] = 0
        if n[1] > display_heidth * 1.1:
            n[1] = display_heidth * 1.1
        self.it_coo[0] = int(n[0])
        self.it_coo[1] = int(n[1])
        self.z = n[2]

class Polygon():
    def __init__(self,points,color,texture):
        self.points = points
        self.color = color
        self.texture = texture
        self.min_z = 0
        self.min_z_id = 0
        self.sum_z = 0
        self.light_pol1 = 255
        self.light_pol2 = 255
        self.mid_rot_x = 0
        self.mid_rot_y = 0
        self.mpdxp1 = 0
        self.mpdxp2 = 0
        self.mpdyp1 = 0
        self.mpdyp2 = 0

class Bullet():
    def __init__(self,x,y,speed, angle, lp,lip2):
        self.speed = speed
        self.x = x
        self.y = y
        self.xch = math.cos(angle / 57.3) * speed
        self.ych = math.sin(angle / 57.3) * speed
        self.lp = lp
        self.lip2 = lip2
    def move(self):
        self.x += self.xch
        self.y += self.ych
        if self.y == 0:
            self.y += 0.000000000001
        if self.x == 0:
            self.x += 0.000000000001

class Object():
    def __init__(self,x,y,poly,pol,zzzz,scailing,uolid,name="no name"):
        self.x = x
        self.y = y
        self.pol = pol
        self.poly = poly
        self.z_pos = zzzz
        self.scail = scailing
        self.name = name
        for nf in self.pol:
            #print(nf.y)
            nf.y *= scailing
            nf.rp *= scailing
        self.lighting = []
        self.id = uolid
        cr1 = []
        cr2 = []
        listt = []
        for i in numba.prange(len(self.poly)):
            cr1.append(self.poly[i].min_z)
            cr2.append(self.poly[i].sum_z)
            listt.append(i)
    def draw_obj(self,rot_x,yy,cx,czz,arot,screen,lights):
        for i in self.pol:
            i.build(rot_x, cx, czz, yy + self.z_pos)
        for i in self.poly:
            min = 0
            i.sum_z = 0
            i.mid_rot_x = 0
            for j in numba.prange(len(i.points)):
                i.sum_z += self.pol[i.points[j]].z
                i.mid_rot_x += self.pol[i.points[j]].rot_xp
                if self.pol[i.points[j]].z > min:
                    min = self.pol[i.points[j]].z
                    i.min_z_id = j
            i.min_z = min
            i.mid_rot_x = i.mid_rot_x / len(i.points)
            if i.mid_rot_x > 359:
                i.mid_rot_x -= 360
            elif i.mid_rot_x < 0:
                i.mid_rot_x += 360
        cr1 = []
        cr2 = []
        listt = []
        for i in numba.prange(len(self.poly)):
            cr1.append(self.poly[i].min_z)
            cr2.append(self.poly[i].sum_z)
            listt.append(i)
        answ = sort_opt(len(self.poly),listt,cr1,cr2)
        ans_poly = []
        for i in numba.prange(len(self.poly)):
            ans_poly.append(self.poly[answ[i]])
        self.lighting = []
        for j in lights:
            new_light_dir = getdir(self.x,self.y,j.x,j.y)
            new_light_power = 1 - distance(self.x,self.y,j.x,j.y) / (1000 * j.light_power)
            if new_light_power >= 0:
                new_light_color = [j.color[0] * new_light_power,j.color[1] * new_light_power,j.color[2] * new_light_power]
            else:
                new_light_color = [0,0,0]
            self.lighting.append(Light(new_light_dir, new_light_color))
        n = (((czz * self.scail) * (czz * self.scail)) / 10000 * (len(ans_poly) / 5000)) // 1
        if n > len(ans_poly) / 1.8:
            n = len(ans_poly) // 1.8
        ans_poly = ans_poly[int(n):]
        for i in ans_poly:
            for j in self.lighting:
                i.light_pol1 = get_light(i.mid_rot_x,i.mid_rot_y,j.direction,arot)
            it_color = []
            it_color.append(i.color[0])
            it_color.append(i.color[1])
            it_color.append(i.color[2])
            m = len(self.lighting)
            for j in self.lighting:
                it_color[0] += (i.light_pol1 * j.color[0]) #/ m
                it_color[1] += (i.light_pol1 * j.color[1]) #/ m
                it_color[2] += (i.light_pol1 * j.color[2]) #/ m
            for j in range(len(it_color)):
                if it_color[j] > 255:
                    it_color[j] = 255
                if it_color[j] < 0:
                    it_color[j] = 0
            pygame.gfxdraw.filled_trigon(screen, self.pol[i.points[0]].it_coo[0],self.pol[i.points[0]].it_coo[1],
                                    self.pol[i.points[1]].it_coo[0],self.pol[i.points[1]].it_coo[1],
                                    self.pol[i.points[2]].it_coo[0],self.pol[i.points[2]].it_coo[1], it_color)
            pygame.gfxdraw.aatrigon(screen, self.pol[i.points[0]].it_coo[0], self.pol[i.points[0]].it_coo[1],
                                         self.pol[i.points[1]].it_coo[0], self.pol[i.points[1]].it_coo[1],
                                         self.pol[i.points[2]].it_coo[0], self.pol[i.points[2]].it_coo[1], it_color)

@njit(fastmath=True,parallel=True, cache=True)
def get_light(mid_rot_x,mid_rot_y,direction,arot):
    sumcol = 255
    rxa = mid_rot_x - direction - arot
    if rxa > 359:
        rxa -= 360
    elif rxa < 0:
        rxa += 360
    rxa -= 180
    sumcol -= 255 * (np.fabs(rxa) / 180) + 255 * (mid_rot_y / 180)
    sumcol = int(sumcol)
    if sumcol < 0:
        sumcol = 0
    elif sumcol > 255:
        sumcol = 255
    return sumcol

@njit(fastmath=True,parallel=True, cache=True)
def build_opt(rot_xp,y,rp,rot_x,cxx,zz,yyy):
    rot_x += rot_xp
    x = np.cos(rot_x / 57.3) * rp
    z = np.fabs((zz * 10 + (np.sin(rot_x / 57.3) * rp)) / 200)
    if z == 0:
        z += 0.000000000001
    x1 = x / (z / 5)
    y1 = (y - 500 + yyy) / (z / 5)
    x1 = cxx + x1 * 2
    y1 = 500 + y1 * 2
    it_coo = [x1, y1]
    ans = [int(it_coo[0]),int(it_coo[1]),z]
    return ans


@njit(fastmath=True, cache=True, parallel=True)
def sort_opt(len,list,cryt1,cryt2):
    i = 0
    while i < len - 1:
        ch = False
        if cryt1[i] < cryt1[i + 1]:
            sav = cryt1[i]
            cryt1[i] = cryt1[i + 1]
            cryt1[i + 1] = sav
            sav = cryt2[i]
            cryt2[i] = cryt2[i + 1]
            cryt2[i + 1] = sav
            sav = list[i]
            list[i] = list[i + 1]
            list[i + 1] = sav
            ch = False
        elif cryt1[i] == cryt1[i + 1]:
            ch = True
        elif cryt1[i] == cryt1[i + 1] and cryt2[i] < cryt2[i + 1]:
            sav = cryt1[i]
            cryt1[i] = cryt1[i + 1]
            cryt1[i + 1] = sav
            sav = cryt2[i]
            cryt2[i] = cryt2[i + 1]
            cryt2[i + 1] = sav
            sav = list[i]
            list[i] = list[i + 1]
            list[i + 1] = sav
            ch = False
        elif cryt1[i] > cryt1[i + 1]:
            ch = True
        if not(ch) and i == 0:
            ch = True
        if ch:
            i = i + 1
        else:
            i = i - 1
    return list

@njit(fastmath=True)
def is_in_triangle(x1, y1, x2, y2, x3, y3, x0, y0):
    n1 = (x1 - x0) * (y2 - y1) - (x2 - x1) * (y1 - y0)
    n2 = (x2 - x0) * (y3 - y2) - (x3 - x2) * (y2 - y0)
    n3 = (x3 - x0) * (y1 - y3) - (x1 - x3) * (y3 - y0)
    if n1 > 0 and n2 > 0 and n3 > 0:
        return True
    else:
        return False

@njit(fastmath=True,parallel=True, cache=True)
def getdir(x1,y1,x2,y2):
    x_dist = x1 - x2
    y_dist = y1 - y2
    xy_dist = distance(x1,y1,x2,y2)
    return int(math.acos(x_dist / xy_dist) * 57.3 * 2)

@njit(fastmath=True,parallel=True, cache=True)
def distance(x1, y1, x2, y2):
    dist = pow((pow(x2-x1,2)+pow(y2-y1,2)),0.5)
    return dist

@njit(fastmath=True,parallel=True, cache=True)
def distXY_func(x, x1, y, y1):  # функция расстояний x и y между двумя оюъектами
    if x < x1:
        distX = x1 - x
    else:
        distX = x - x1
    if y < y1:
        distY = y1 - y
    else:
        distY = y - y1

    return distX, distY

@njit(fastmath=True,parallel=True, cache=True)
def Pifogor_func(x, y):  # функция вычисления теоремы Пифагора

    Pifogor = np.sqrt(x * x + y * y)

    return Pifogor

@njit(fastmath=True,parallel=True, cache=True)
def Perim_half_func_ver2(Pifogor, Pifogor1):

    Perim = (Pifogor + Pifogor1 + 1080 * 10) / 2

    return Perim

@njit(fastmath=True,parallel=True, cache=True)
def Arithmetical_Mean_func(a, b):  # функция среднего арифметического

    return (a + b) / 2

def distribution_buffer_func(map,x,y):

    distance_arr = []

    for buffer_cicle in prange(len(map)):
        distance_arr.append(distance(map[buffer_cicle][0],map[buffer_cicle][1],x,y))

    ar = []
    arr = []
    for i in prange(len(map)):
        ar.append(i)
        arr.append(0)
    answ = sort_opt(len(map),ar,distance_arr,arr)
    new_map = []
    for i in prange(len(map)):
        new_map.append(map[answ[i]])

    return new_map


def get_random_name(l):
    gl = ["а","у","о","э","ы","я","ё","е","и","ю"]
    sogl = ["б","в","г","д","з","й","к","л",
            "м","н","п","р","с","т","ф","х",
            "ц","ч","ш","щ","ж"]
    ad = ["ь","ъ"]
    t = random.randint(0,1)
    ans = ""
    kep_let = 0
    for i in range(l):
        if t == 1:
            ans += gl[random.randint(0,len(gl) - 1)]
        elif t == 0:
            ans += sogl[random.randint(0,len(sogl) - 1)]
        if random.randint(1 + kep_let,2) == 2:
            t = not(t)
            kep_let = 0
        else:
            kep_let += 1
    return ans

def gen_random_obj(mirors):
    pol = []
    poly = set()
    avgensp = 360 // mirors
    # 1 stage
    op_gc = random.randint(8,10) // mirors
    r_pre = random.randint(1,4) * 50
    r_min = random.randint(2,3) * 50
    y_pre = random.randint(5, 7) * 50
    y_min = random.randint(3, 8) * 50
    for h in range(op_gc):
        typee = random.randint(0, 1)
        if typee:
            pol.append(Point(r_min,0 + h * (avgensp // op_gc),y_min))
            pol.append(Point(r_min + r_pre, 0 + h * (avgensp // op_gc), y_min + y_pre))
        else:
            pol.append(Point(r_min + r_pre,0 + h * (avgensp // op_gc),y_min))
            pol.append(Point(r_min, 0 + h * (avgensp // op_gc), y_min + y_pre))
    for h in range(random.randint(15,20) // mirors):
        pol.append(Point(random.randint(r_pre + r_min,r_pre + r_min + 50), random.randint(1,avgensp), random.randint(y_min,y_pre + y_min + 50)))
    mirp = []
    for h in pol:
        np = 360 - h.rot_xp
        for j in range(mirors - 1):
            mirp.append(Point(h.rp,np,h.y))
            np -= h.rot_xp
    pol += mirp
    for a11 in range(len(pol)):
        for b11 in range(len(pol)):
            if pol[a11].rot_xp < pol[b11].rot_xp:
                sav = pol[b11]
                pol[b11] = pol[a11]
                pol[a11] = sav
    #ares = []
    #for h in range(mirors):
        #mirpol = pol
        #for j in range(len(mirpol)):
            #mirpol[j].rot_xp = mirpol[j].rot_xp * (h + 1)
        #ares = ares + mirpol
    #pol = pol + ares
    for ty in range(len(pol) - 2):
        poly.add(Polygon([ty,ty + 1,ty + 2],[40,40,40],0))
    poly.add(Polygon([0, 1, -2], [40, 40, 40], 0))
    tpoly = []
    for ty in range(len(pol)):
        tpoly.append([])
        for ty2 in range(len(pol) - ty - 3):
            if abs(pol[ty2 + ty + 2].rot_xp - pol[ty].rot_xp) < 51 and abs(pol[ty2 + ty + 2].y - pol[ty].y) < 250:
                tpoly[ty].append(ty2 + ty + 2)
    for ty in range(len(tpoly)):
        if len(tpoly[ty]) > 1:
            for h in range(len(tpoly[ty]) - 1):
                poly.add(Polygon([ty, tpoly[ty][h], tpoly[ty][h + 1]], [40, 40, 40], 0))
            poly.add(Polygon([ty, tpoly[ty][0], tpoly[ty][1]], [40, 40, 40], 0))
    poly.add(Polygon([len(pol) - 1, len(pol) - 2, 0], [40, 40, 40], 0))
    poly.add(Polygon([len(pol) - 1, 1, 0], [40, 40, 40], 0))
    avcon = []
    for ty in range(len(tpoly)):
        if len(tpoly[ty]) > 3 and random.randint(1,len(avcon) + 2) == 1:
            avcon.append(tpoly[ty][:random.randint(4,5)])
    for con in range(len(avcon)):
        rrr = 0
        for j in range(len(avcon[con])):
            rrr += pol[avcon[con][j]].rp
        rrr /= len(avcon[con])
        length = random.randint(2,4)
        #print("shup")
        for step in range(length):
            rrr += random.randint(1,5) * 25
            rot_dir = random.randint(-2,2) / rrr
            y_dir = random.randint(-5,5) * 40
            #print("seg")
            for j in range(len(avcon[con]) - 1):
                poi1 = avcon[con][j]
                poi2 = avcon[con][j + 1]
                if j > 0:
                    poi3 = len(pol) - 1
                else:
                    poi3 = len(pol)
                    pol.append(Point(rrr, pol[poi1].rot_xp + rot_dir, pol[poi1].y + y_dir))
                poi4 = len(pol)
                #print(poi1,poi2,poi3,poi4)
                pol.append(Point(rrr, pol[poi2].rot_xp + rot_dir, pol[poi2].y + y_dir))
                poly.add(Polygon([poi1,poi2,poi3],[40,40,40],0))
                poly.add(Polygon([poi2, poi4, poi3], [40, 40, 40], 0))
            poi1 = avcon[con][len(avcon[con]) - 1]
            poi2 = avcon[con][0]
            poi3 = len(pol) - 1
            poi4 = len(pol) - len(avcon[con])
            #print(poi1, poi2, poi3, poi4)
            poly.add(Polygon([poi1, poi2, poi3], [40, 40, 40], 0))
            poly.add(Polygon([poi2, poi4, poi3], [40, 40, 40], 0))
            acl = len(avcon[con])
            avcon[con] = []
            for k in range(acl):
                avcon[con].append(len(pol) - acl + k)
        rott = 0
        yy = 0
        for j in range(len(avcon[con])):
            rott += pol[avcon[con][j]].rot_xp
            yy += pol[avcon[con][j]].y
        yy /= len(avcon[con])
        rott /= len(avcon[con])
        rrr += random.randint(10,20) * 10
        poii = len(pol)
        pol.append(Point(rrr,rott,yy))
        for j in range(len(avcon[con]) - 1):
            poly.add(Polygon([poii, avcon[con][j], avcon[con][j + 1]], [40, 40, 40], 0))
        poly.add(Polygon([poii, avcon[con][0], avcon[con][-1]], [40, 40, 40], 0))
    rpoly = []
    for h in poly:
        rpoly.append(h)
    print("do itogo:")
    print(len(rpoly))
    for h in rpoly:
        for h2 in rpoly:
            if h != h2:
                if h.points == h2.points:
                    rpoly.remove(h2)
    print("itogo:")
    print(len(rpoly))
    return Object(400,400,rpoly,pol,-300,1,-1,get_random_name(random.randint(4,10)))

def main():
    screen = pygame.display.set_mode((1920, 1080), pygame.NOFRAME, pygame.SCALED)
    screen.set_alpha(None)
    pygame.display.set_caption("3D Engine")

    pygame.mouse.set_visible(False)

    screen.fill([0, 0, 0])
    pygame.display.flip()
    print(get_random_name(random.randint(4, 10)))

    my_font = pygame.font.SysFont("arial", 25)

    clock = pygame.time.Clock()
    FPS = 60  # кадры  в секунду

    x = 3200  # координата x игрока
    y = 3200  # координата y игрока

    speed = 10  # скорость игрока
    speed_rotation = 1  # скорость поворота игрока

    lesser_hypo_of_va = 2160 * 10
    semi_hypo_of_va = 1080 * 10
    hypo_of_va = 3741.22 * 10

    a = 1658  # координата x левой вершины поля зрения
    b = 300  # координата y левой вершины поля зрения

    a1 = 300  # координата x правой вершины поля зрения
    b1 = 1658  # координата y правой вершины поля зрения

    i = 180  # угол поворота левой границы поля зрения
    i1 = 300  # угол поворота правой границы поля зрения
    rotation_midle = 225  # угол поворота камеры (то что ты просил)
    ll = 45
    pp = 225
    xch = [0, 0, 0]
    ych = [0, 0, 0]
    vision_r = 1400

    a_projection = 0
    b_projection = 0
    h_fe = 0

    map = []
    tpol = [
        Point(250, 0, 500),
        Point(250, 214.00000000000026, 500),
        Point(250, 125.00000000000034, 500),
        Point(1, 125.00000000000034, 230),
    ]
    tpoly = [
        Polygon([1, 3, 0], [180, 0, 0], 0),
        Polygon([2, 0, 3], [180, 0, 0], 0),
        Polygon([3, 2, 1], [180, 0, 0], 0),
    ]
    spol = [
        Point(165, 0, 500),
        Point(165, 316.10000000000025, 500),
        Point(165, 226.8000000000001, 500),
        Point(165, 179.5, 500),
        Point(165, 133.5000000000002, 500),
        Point(165, 43.40000000000018, 500),
        Point(165, 43.40000000000018, 540),
        Point(165, 0.6, 540),
        Point(165, 315.69999999999976, 540),
        Point(165, 225.4999999999998, 540),
        Point(165, 179.29999999999978, 540),
        Point(165, 133.29999999999987, 540),
        Point(85, 315.79999999999995, 545),
        Point(85, 225.79999999999936, 545),
        Point(85, 131.59999999999934, 545),
        Point(85, 41.59999999999934, 545),
        Point(85, 317.30000000000024, 690),
        Point(85, 226.3999999999998, 690),
        Point(85, 133.9999999999998, 690),
        Point(85, 40.69999999999983, 690),
    ]
    spolly = [
        Polygon([2, 9, 8], [115, 55, 0], 0),
        Polygon([8, 2, 1], [115, 55, 0], 0),
        Polygon([9, 2, 3], [115, 55, 0], 0),
        Polygon([2, 4, 1], [115, 55, 0], 0),
        Polygon([3, 4, 2], [115, 55, 0], 0),
        Polygon([3, 10, 9], [115, 55, 0], 0),
        Polygon([6, 8, 9], [115, 55, 0], 0),
        Polygon([11, 10, 9], [115, 55, 0], 0),
        Polygon([9, 6, 11], [115, 55, 0], 0),
        Polygon([1, 8, 7], [115, 55, 0], 0),
        Polygon([8, 7, 6], [115, 55, 0], 0),
        Polygon([0, 1, 7], [115, 55, 0], 0),
        Polygon([1, 0, 5], [115, 55, 0], 0),
        Polygon([1, 5, 4], [115, 55, 0], 0),
        Polygon([13, 17, 16], [115, 55, 0], 0),
        Polygon([18, 17, 13], [115, 55, 0], 0),
        Polygon([16, 12, 13], [115, 55, 0], 0),
        Polygon([13, 14, 18], [115, 55, 0], 0),
        Polygon([16, 19, 12], [115, 55, 0], 0),
        Polygon([12, 19, 15], [115, 55, 0], 0),
        Polygon([10, 3, 4], [115, 55, 0], 0),
        Polygon([4, 11, 10], [115, 55, 0], 0),
        Polygon([7, 0, 6], [115, 55, 0], 0),
        Polygon([6, 0, 5], [115, 55, 0], 0),
        Polygon([15, 19, 18], [115, 55, 0], 0),
        Polygon([18, 14, 15], [115, 55, 0], 0),
        Polygon([11, 4, 5], [115, 55, 0], 0),
        Polygon([5, 6, 11], [115, 55, 0], 0),
    ]
    pol3 = [
        Point(170, 179.69999999999996, 620),
        Point(170, 89.39999999999992, 620),
        Point(170, 0.6999999999999986, 620),
        Point(170, 270.50000000000017, 620),
        Point(170, 223.99999999999991, 380),
        Point(170, 133.7999999999996, 380),
        Point(170, 46.199999999999584, 380),
        Point(170, 315.3000000000001, 380),
    ]
    poly3 = [
        Polygon([3, 2, 7], [170, 25, 140], 0),
        Polygon([2, 6, 7], [170, 25, 140], 0),
        Polygon([3, 7, 4], [170, 25, 140], 0),
        Polygon([2, 3, 0], [170, 25, 140], 0),
        Polygon([2, 1, 6], [170, 25, 140], 0),
        Polygon([0, 1, 2], [170, 25, 140], 0),
        Polygon([0, 4, 3], [170, 25, 140], 0),
        Polygon([1, 5, 6], [170, 25, 140], 0),
        Polygon([0, 5, 4], [170, 25, 140], 0),
        Polygon([1, 0, 5], [170, 25, 140], 0),
    ]
    poll = [
        Point(70, 318.29999999999893, 970),
        Point(70, 270.1999999999987, 970),
        Point(70, 223.1999999999989, 970),
        Point(70, 178.99999999999912, 970),
        Point(70, 130.699999999999, 970),
        Point(70, 89.99999999999908, 970),
        Point(70, 1.6999999999990836, 970),
        Point(70, 44.59999999999927, 970),
        Point(70, 3.299999999999268, 340),
        Point(70, 271.99999999999983, 340),
        Point(70, 317.59999999999997, 340),
        Point(70, 223.80000000000015, 340),
        Point(70, 178.30000000000004, 340),
        Point(70, 131.10000000000002, 340),
        Point(70, 88.70000000000006, 340),
        Point(70, 44.40000000000003, 340),
        Point(140, 37.10000000000001, 440),
        Point(140, 197.69999999999987, 440),
        Point(140, 151.49999999999991, 415),
        Point(140, 90.99999999999991, 415),
        Point(140, 329.6, 415),
        Point(140, 256.9000000000001, 415),
        Point(190, 231.30000000000004, 365),
        Point(190, 176.9000000000001, 365),
        Point(190, 88.60000000000007, 365),
        Point(190, 359.5, 365),
        Point(190, 312.1, 315),
        Point(265, 189.69999999999993, 285),
        Point(265, 120.09999999999994, 285),
        Point(265, 76.69999999999996, 285),
        Point(265, 22.899999999999967, 285),
        Point(265, 320.09999999999997, 285),
        Point(265, 272.2999999999999, 285),
        Point(265, 226.49999999999991, 285),
        Point(265, 226.49999999999991, 190),
        Point(265, 201.69999999999996, 190),
        Point(265, 155.59999999999994, 190),
        Point(265, 104.69999999999995, 190),
        Point(265, 40.099999999999966, 190),
        Point(265, 337.3, 190),
        Point(265, 300.20000000000016, 190),
        Point(240, 290.20000000000005, 135),
        Point(240, 250.60000000000014, 135),
        Point(240, 197.20000000000007, 135),
        Point(240, 140.60000000000005, 135),
        Point(240, 78.00000000000004, 135),
        Point(240, 13.200000000000053, 135),
        Point(210, 13.200000000000053, 65),
        Point(210, 302.40000000000003, 65),
        Point(210, 243.3000000000002, 65),
        Point(210, 182.70000000000016, 65),
        Point(210, 143.2000000000001, 65),
    ]
    polly = [
        Polygon([34, 27, 33, 39], [75, 140, 35], 0),
        Polygon([31, 40, 39], [75, 140, 35], 0),
        Polygon([31, 39, 46], [75, 140, 35], 0),
        Polygon([48, 39, 40], [75, 140, 35], 0),
        Polygon([46, 39, 48], [75, 140, 35], 0),
        Polygon([38, 46, 31], [75, 140, 35], 0),
        Polygon([25, 31, 20], [75, 140, 35], 0),
        Polygon([31, 32, 40], [75, 140, 35], 0),
        Polygon([26, 31, 20], [75, 140, 35], 0),
        Polygon([25, 38, 31], [75, 140, 35], 0),
        Polygon([32, 21, 31], [75, 140, 35], 0),
        Polygon([41, 48, 40], [75, 140, 35], 0),
        Polygon([41, 40, 32], [75, 140, 35], 0),
        Polygon([48, 47, 46], [75, 140, 35], 0),
        Polygon([46, 38, 47], [75, 140, 35], 0),
        Polygon([47, 45, 46], [75, 140, 35], 0),
        Polygon([45, 46, 29], [75, 140, 35], 0),
        Polygon([25, 30, 38], [75, 140, 35], 0),
        Polygon([25, 29, 30], [75, 140, 35], 0),
        Polygon([30, 38, 29], [75, 140, 35], 0),
        Polygon([20, 25, 16], [75, 140, 35], 0),
        Polygon([25, 29, 16], [75, 140, 35], 0),
        Polygon([38, 45, 47], [75, 140, 35], 0),
        Polygon([20, 21, 26], [75, 140, 35], 0),
        Polygon([42, 48, 41], [75, 140, 35], 0),
        Polygon([49, 42, 48], [75, 140, 35], 0),
        Polygon([36, 48, 43], [75, 140, 35], 0),
        Polygon([42, 41, 32], [75, 140, 35], 0),
        Polygon([21, 20, 16], [75, 140, 35], 0),
        Polygon([45, 38, 29], [75, 140, 35], 0),
        Polygon([21, 32, 22], [75, 140, 35], 0),
        Polygon([42, 32, 34], [75, 140, 35], 0),
        Polygon([33, 22, 32], [75, 140, 35], 0),
        Polygon([34, 32, 33], [75, 140, 35], 0),
        Polygon([17, 16, 21], [75, 140, 35], 0),
        Polygon([29, 16, 24], [75, 140, 35], 0),
        Polygon([19, 24, 16], [75, 140, 35], 0),
        Polygon([16, 19, 18], [75, 140, 35], 0),
        Polygon([18, 17, 16], [75, 140, 35], 0),
        Polygon([8, 10, 0], [105, 50, 0], 0),
        Polygon([0, 6, 8], [105, 50, 0], 0),
        Polygon([1, 0, 10], [105, 50, 0], 0),
        Polygon([10, 9, 1], [105, 50, 0], 0),
        Polygon([15, 8, 6], [105, 50, 0], 0),
        Polygon([6, 7, 15], [105, 50, 0], 0),
        Polygon([14, 15, 7], [105, 50, 0], 0),
        Polygon([5, 7, 14], [105, 50, 0], 0),
        Polygon([1, 2, 9], [105, 50, 0], 0),
        Polygon([9, 11, 2], [105, 50, 0], 0),
        Polygon([22, 21, 17], [75, 140, 35], 0),
        Polygon([49, 42, 34], [75, 140, 35], 0),
        Polygon([49, 34, 43, 49], [75, 140, 35], 0),
        Polygon([50, 49, 43], [75, 140, 35], 0),
        Polygon([13, 14, 5], [105, 50, 0], 0),
        Polygon([5, 4, 13], [105, 50, 0], 0),
        Polygon([2, 3, 11], [105, 50, 0], 0),
        Polygon([11, 12, 3], [105, 50, 0], 0),
        Polygon([45, 29, 37], [75, 140, 35], 0),
        Polygon([29, 28, 24], [75, 140, 35], 0),
        Polygon([29, 28, 37], [75, 140, 35], 0),
        Polygon([51, 45, 37], [75, 140, 35], 0),
        Polygon([19, 24, 28], [75, 140, 35], 0),
        Polygon([19, 18, 28], [75, 140, 35], 0),
        Polygon([33, 23, 22], [75, 140, 35], 0),
        Polygon([17, 22, 23], [75, 140, 35], 0),
        Polygon([4, 12, 13], [105, 50, 0], 0),
        Polygon([4, 12, 3], [105, 50, 0], 0),
        Polygon([27, 34, 33], [75, 140, 35], 0),
        Polygon([43, 35, 34], [75, 140, 35], 0),
        Polygon([27, 23, 33], [75, 140, 35], 0),
        Polygon([34, 35, 27], [75, 140, 35], 0),
        Polygon([23, 17, 18], [75, 140, 35], 0),
        Polygon([18, 23, 28], [75, 140, 35], 0),
        Polygon([44, 28, 18], [75, 140, 35], 0),
        Polygon([51, 37, 44], [75, 140, 35], 0),
        Polygon([37, 28, 44], [75, 140, 35], 0),
        Polygon([35, 23, 27], [75, 140, 35], 0),
        Polygon([36, 23, 35], [75, 140, 35], 0),
        Polygon([28, 36, 23], [75, 140, 35], 0),
        Polygon([50, 43, 36], [75, 140, 35], 0),
        Polygon([36, 43, 35], [75, 140, 35], 0),
        Polygon([51, 50, 44], [75, 140, 35], 0),
        Polygon([44, 36, 50], [75, 140, 35], 0),
        Polygon([44, 36, 28], [75, 140, 35], 0),
    ]
    pol2 = [
        Point(300, 0, 700),
        Point(300, 270.6000000000003, 700),
        Point(300, 179.7000000000005, 700),
        Point(300, 89.50000000000044, 700),
        Point(300, 0.30000000000000004, 300),
        Point(300, 270.6999999999997, 300),
        Point(300, 179.49999999999963, 300),
        Point(300, 89.89999999999965, 300),
        Point(300, 134.49999999999983, 215),
        Point(300, 315.1000000000004, 215),
        Point(300, 145.50000000000034, 445),
        Point(300, 123.10000000000016, 445),
        Point(300, 123.10000000000016, 700),
        Point(300, 145.10000000000025, 700),
    ]
    poly2 = [
        Polygon([1, 5, 6], [115, 45, 0], 0),
        Polygon([2, 6, 1], [115, 45, 0], 0),
        Polygon([4, 1, 5], [110, 50, 0], 0),
        Polygon([0, 1, 4], [110, 50, 0], 0),
        Polygon([9, 5, 6], [230, 30, 0], 0),
        Polygon([9, 5, 4], [110, 50, 0], 0),
        Polygon([10, 6, 2], [110, 50, 0], 0),
        Polygon([13, 2, 10], [110, 50, 0], 0),
        Polygon([6, 8, 9], [230, 30, 0], 0),
        Polygon([6, 10, 11], [110, 50, 0], 0),
        Polygon([7, 8, 6], [110, 50, 0], 0),
        Polygon([7, 11, 6], [110, 50, 0], 0),
        Polygon([7, 8, 9], [230, 30, 0], 0),
        Polygon([9, 4, 7], [230, 30, 0], 0),
        Polygon([10, 13, 12], [115, 155, 0], 0),
        Polygon([12, 11, 10], [115, 155, 0], 0),
        Polygon([7, 4, 0], [110, 50, 0], 0),
        Polygon([3, 0, 7], [110, 50, 0], 0),
        Polygon([12, 3, 11], [110, 50, 0], 0),
        Polygon([11, 7, 3], [110, 50, 0], 0),
    ]
    polw = [
        Point(250, 173.6, 530),
        Point(250, 182.2, 530),
        Point(250, 182.2, 470),
        Point(250, 173.99999999999983, 470),
        Point(250, 6.3999999999998645, 470),
        Point(250, 353.79999999999967, 470),
        Point(250, 353.79999999999967, 595),
        Point(250, 5.099999999999997, 595),
        Point(105, 353.2000000000004, 530),
        Point(105, 7.20000000000001, 530),
        Point(105, 352.9999999999999, 400),
        Point(105, 6.399999999999997, 400),
        Point(105, 183.2999999999999, 400),
        Point(105, 172.6, 400),
        Point(105, 5.599999999999998, 420),
        Point(105, 354.49999999999983, 420),
        Point(105, 183.7999999999999, 420),
        Point(105, 172.60000000000002, 420),
        Point(70, 5.9, 420),
        Point(70, 351.60000000000036, 420),
        Point(70, 180.90000000000057, 420),
        Point(70, 172.90000000000057, 420),
        Point(70, 172.90000000000057, 470),
        Point(70, 183.20000000000053, 470),
        Point(70, 7.000000000000572, 470),
        Point(70, 350.4, 470),
        Point(5, 5.300000000000002, 470),
        Point(250, 352.9000000000001, 530),
        Point(250, 5.599999999999995, 530),
    ]
    polyw = [
        Polygon([1, 2, 27], [70, 70, 70], 0),
        Polygon([0, 1, 27], [70, 70, 70], 0),
        Polygon([3, 2, 5], [70, 70, 70], 0),
        Polygon([27, 5, 2], [70, 70, 70], 0),
        Polygon([3, 0, 28], [70, 70, 70], 0),
        Polygon([4, 5, 3], [70, 70, 70], 0),
        Polygon([28, 4, 3], [70, 70, 70], 0),
        Polygon([0, 28, 27], [70, 70, 70], 0),
        Polygon([12, 13, 16], [5, 30, 125], 0),
        Polygon([17, 13, 16], [5, 30, 125], 0),
        Polygon([16, 12, 15], [110, 70, 5], 0),
        Polygon([14, 17, 16], [110, 70, 5], 0),
        Polygon([15, 14, 16], [110, 70, 5], 0),
        Polygon([12, 13, 11], [110, 70, 5], 0),
        Polygon([10, 15, 12], [110, 70, 5], 0),
        Polygon([10, 11, 12], [110, 70, 5], 0),
        Polygon([13, 17, 14], [110, 70, 5], 0),
        Polygon([11, 14, 13], [110, 70, 5], 0),
        Polygon([20, 21, 23], [110, 70, 5], 0),
        Polygon([22, 23, 21], [110, 70, 5], 0),
        Polygon([19, 23, 20], [110, 70, 5], 0),
        Polygon([23, 25, 19], [110, 70, 5], 0),
        Polygon([18, 22, 21], [110, 70, 5], 0),
        Polygon([24, 22, 18], [110, 70, 5], 0),
        Polygon([18, 19, 25], [110, 70, 5], 0),
        Polygon([24, 25, 18], [110, 70, 5], 0),
        Polygon([10, 11, 15], [5, 30, 125], 0),
        Polygon([8, 6, 27], [110, 70, 5], 0),
        Polygon([7, 9, 8], [110, 70, 5], 0),
        Polygon([7, 6, 8], [110, 70, 5], 0),
        Polygon([11, 14, 15], [5, 30, 125], 0),
        Polygon([28, 7, 9], [110, 70, 5], 0),
        Polygon([5, 27, 28], [70, 70, 70], 0),
        Polygon([6, 27, 28], [110, 70, 5], 0),
        Polygon([7, 6, 28], [110, 70, 5], 0),
        Polygon([5, 4, 28], [70, 70, 70], 0),
    ]
    bpol = [
        Point(45, 0.30000000000000004, 500),
        Point(45, 315.9, 505),
        Point(45, 227.39999999999984, 515),
        Point(45, 132.39999999999984, 515),
        Point(45, 48.59999999999981, 515),
        Point(45, 315.2000000000003, 485),
        Point(45, 225.50000000000017, 485),
        Point(45, 128.90000000000015, 485),
        Point(45, 51.80000000000013, 485),
    ]
    bpolly = [
        Polygon([0, 4, 8], [125, 125, 125], 0),
        Polygon([4, 1, 0], [125, 125, 125], 0),
        Polygon([5, 8, 0], [125, 125, 125], 0),
        Polygon([0, 5, 1], [125, 125, 125], 0),
        Polygon([3, 4, 8], [125, 125, 125], 0),
        Polygon([2, 1, 4], [125, 125, 125], 0),
        Polygon([3, 4, 2], [125, 125, 125], 0),
        Polygon([6, 8, 5], [125, 125, 125], 0),
        Polygon([8, 7, 3], [125, 125, 125], 0),
        Polygon([6, 8, 7], [125, 125, 125], 0),
        Polygon([6, 5, 1], [125, 125, 125], 0),
        Polygon([1, 2, 6], [125, 125, 125], 0),
        Polygon([7, 3, 6], [125, 125, 125], 0),
        Polygon([6, 2, 3], [125, 125, 125], 0),
    ]

    # phis
    sim = pyphicus.Simulation()

    sim.load_settings("Phis_rul\\set_7")

    throw_pwr = 20
    # /phis

    hands = 0  # Object(x, y, polyw, polw, 0, 1, uolid)
    hands_x = 0
    hands_y = 0
    hands_id = None

    objects = []

    '''objects.append([1000, 1000, Object(1000, 1000, spolly, spol, -400, 1, uolid, "стол"), 1])
    sim.add_object(pyphicus.Object(1000,1000, 0, 100, sim))
    objects.append([500, 500, Object(500, 500, polyw, polw, -500, 1, uolid, "ружьё"), 1])
    sim.add_object(pyphicus.Object(1000, 1000, 0, 100, sim))'''
    for h in range(30):
        xc = random.randint(500, 2700)
        yc = random.randint(500, 2700)
        sim.add_object(pyphicus.Object(xc, yc, 0, 100, sim, z = -(random.randint(300,1500))))
        print(sim.map[-1][2].energy)
        objects.append([xc, yc, Object(xc, yc, tpoly, tpol, -800, 1, uolid, "треугольник"), 1])

    print(len(sim.map))

    print(len(polly))
    print(len(poll))

    print(len(map))

    wiggle_switch = True
    wiggle = 0

    map_size = 4
    l = 0
    l1 = 0

    #sim.update_sim()

    Pifogor_buffer_max = 0
    main_buffer_cicle = 0
    buffer_update = 0
    buffer_cicle = 0

    iteration_cicle = 0

    polygon_display = 0
    flat_polygon_output = [[0, 0, 0], [0, 0, 0]]
    pre_flat_polygon_color = [0, 0]

    texture_size_x = 0
    color = [0, 0, 0]
    yyyy = 100

    mini_map_display = False

    running = True  # значение работы программы
    move_forward = False
    move_backward = False
    move_right = False
    move_left = False
    move_up = False
    move_down = False
    camera_left = False
    camera_right = False

    hands_up = False
    hands_down = False
    hands_left = False
    hands_right = False
    hands_rot_left = False
    hands_rot_right = False

    shift = False
    ctrl = False

    uf = 0
    fs = 0
    add_y = 0
    add_y_dir = 3
    add_y_w = 0

    add_rot = 0

    moving = False
    lights = [Light_object(450, 450, [0.5, 0.5, 0], 1), Light_object(-15000, -15000, [0.1, 0.1, 0], 25000),
              Light_object(1050, 1050, [1, 0, 1], 1), Light_object(1050, 3050, [0, 0, 1], 1),
              Light_object(3050, 1050, [0, 1, 0], 1)]
    wey = 0
    tics = 0

    red_dir = -1
    green_dir = -1
    power_dir = -1

    while running:  # начало основного цикла

        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    move_down = True
                if event.key == pygame.K_SPACE:
                    move_up = True
                if event.key == pygame.K_LCTRL:
                    ctrl = True
                if event.key == pygame.K_w:
                    move_forward = True
                if event.key == pygame.K_s:
                    move_backward = True
                if event.key == pygame.K_d:
                    move_right = True
                if event.key == pygame.K_a:
                    move_left = True
                if event.key == pygame.K_UP:
                    hands_up = True
                if event.key == pygame.K_DOWN:
                    hands_down = True
                if event.key == pygame.K_LEFT:
                    if ctrl:
                        hands_rot_left = True
                    else:
                        hands_left = True
                if event.key == pygame.K_RIGHT:
                    if ctrl:
                        hands_rot_right = True
                    else:
                        hands_right = True
                if event.key == pygame.K_u:
                    if distance(x, y, 1000, 1000) < 500:
                        objects.append([1000, 1000, gen_random_obj(1), 1])
                        sim.add_object(pyphicus.Object(1000, 1000, 0, 100, sim))
                if event.key == pygame.K_e:
                    mini = -1
                    minn = 500
                    for obj in numba.prange(len(objects)):
                        if type(objects[obj]) == list:
                            if distance(objects[obj][0], objects[obj][1], x, y) < minn:
                                minn = distance(objects[obj][0], objects[obj][1], x, y)
                                mini = obj
                    if mini != -1:
                        if hands != 0:
                            objects[hands_id] = [x, y, hands, 1]
                            sim.map[hands_id][2].x = x
                            sim.map[hands_id][2].y = y
                            sim.map[hands_id] = [x, y, sim.map[hands_id][2], 1]
                            sim.map[hands_id][2].update(sim)
                        hands = objects[mini][2]
                        hands_id = mini
                        objects[mini] = 0
                if event.key == pygame.K_q:
                    if hands != 0:
                        objects[hands_id] = [x, y, hands, 1]
                        sim.map[hands_id][2].x = x
                        sim.map[hands_id][2].y = y
                        sim.map[hands_id][2].z = -yyyy + hands_y
                        sim.map[hands_id] = [x, y, sim.map[hands_id][2], 1]
                        sim.map[hands_id][2].update(sim)
                        sim.map[hands_id][2].vectors.append([pyphicus.vector_4D(math.cos(rotation_midle / 57.3) * throw_pwr,
                                                                                math.sin(rotation_midle / 57.3) * throw_pwr,0,0),-1])
                        hands = 0
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT:
                    move_down = False
                if event.key == pygame.K_SPACE:
                    move_up = False
                if event.key == pygame.K_LCTRL:
                    ctrl = False
                if event.key == pygame.K_w:
                    move_forward = False
                if event.key == pygame.K_s:
                    move_backward = False
                if event.key == pygame.K_d:
                    move_right = False
                if event.key == pygame.K_a:
                    move_left = False
                if event.key == pygame.K_UP:
                    hands_up = False
                if event.key == pygame.K_DOWN:
                    hands_down = False
                if event.key == pygame.K_LEFT:
                    hands_rot_left = False
                    hands_left = False
                if event.key == pygame.K_RIGHT:
                    hands_rot_right = False
                    hands_right = False
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

        if move_forward:
            x += math.cos(rotation_midle / 57.3) * speed
            y += math.sin(rotation_midle / 57.3) * speed
            moving = True
        if move_backward:
            x -= math.cos(rotation_midle / 57.3) * speed
            y -= math.sin(rotation_midle / 57.3) * speed
            moving = True
        if move_left:
            x += math.cos((rotation_midle - 90) / 57.3) * speed
            y += math.sin((rotation_midle - 90) / 57.3) * speed
            moving = True
        if move_right:
            x += math.cos((rotation_midle + 90) / 57.3) * speed
            y += math.sin((rotation_midle + 90) / 57.3) * speed
            moving = True
        if move_up:
            yyyy += speed
            moving = True
        if move_down:
            yyyy -= speed
            moving = True

        if hands_up:
            hands_y -= 10
        if hands_down:
            hands_y += 10
        if hands_left:
            hands_x -= 10
        if hands_right:
            hands_x += 10

        if hands_rot_left:
            add_rot -= 2
            if add_rot < 0:
                add_rot = 360

        if hands_rot_right:
            add_rot += 2
            if add_rot > 360:
                add_rot = 0

        if camera_right:
            i += speed_rotation
            i1 += speed_rotation
            rotation_midle += speed_rotation

        if camera_left:
            i -= speed_rotation
            i1 -= speed_rotation
            rotation_midle -= speed_rotation

        if moving:
            if math.fabs(add_y_w) > 25:
                add_y_dir *= -1
            add_y_w += add_y_dir
        # далее программа переводит градусы более 360 и менее нуля в стандартные

        if i >= 360:
            i -= 360

        if i < 0:
            i += 360

        if i1 >= 360:
            i1 -= 360

        if i1 < 0:
            i1 += 360

        if rotation_midle >= 360:
            rotation_midle -= 360

        if rotation_midle < 0:
            rotation_midle += 360

        angle = i * 3.14 / 180
        a = (lesser_hypo_of_va * math.cos(angle)) + x
        b = (lesser_hypo_of_va * math.sin(angle)) + y

        angle1 = i1 * 3.14 / 180
        a1 = (lesser_hypo_of_va * math.cos(angle1)) + x
        b1 = (lesser_hypo_of_va * math.sin(angle1)) + y

        averageX = Arithmetical_Mean_func(a=a, b=a1)
        averageY = Arithmetical_Mean_func(a=b, b=b1)

        Pifogor_buffer_max = 0
        main_buffer_cicle = 0
        buffer_update = 0
        buffer_cicle = 0

        if moving == True:
            if wiggle > 60:
                wiggle_switch = False
            if wiggle < 1:
                wiggle_switch = True

            if wiggle_switch == True:
                wiggle += 1.2
            else:
                wiggle -= 1.2

        moving = False

        sim.cadr()

        map = []

        for map_ob in range(len(sim.map)):
            if type(objects[map_ob]) != int:
                objects[map_ob][2].x = sim.map[map_ob][2].x
                objects[map_ob][0] = sim.map[map_ob][0]
                objects[map_ob][2].y = sim.map[map_ob][2].y
                objects[map_ob][1] = sim.map[map_ob][1]
                objects[map_ob][2].z_pos = sim.map[map_ob][2].z
                map.append(objects[map_ob])
                #print(sim.map[map_ob][2].vectors[0][0].z)

        map = distribution_buffer_func(map,x,y)

        screen.fill([0, 0, 0])
        color_wund = [60, 220, 60]

        # костёр
        if lights[0].color[0] >= 0.5:
            red_dir = -1
        if lights[0].color[1] >= 0.3:
            green_dir = -1
        if lights[0].color[0] <= 0.3:
            red_dir = 1
        if lights[0].color[1] <= 0.1:
            green_dir = 1
        if lights[0].light_power >= 1.5:
            power_dir = -1
        if lights[0].light_power <= 0.5:
            power_dir = 1
        lights[0].light_power += power_dir * random.randint(1, 3) * 0.01
        lights[0].color[0] += red_dir * random.randint(1, 3) * 0.01
        lights[0].color[1] += green_dir * random.randint(1, 2) * 0.01

        for cicle in numba.prange(len(map)):  # начало цикла вычесления проекции и вывода
            isoj = False
            if isoj:
                for flat_polygon_conclusion in range(2):

                    # далее программа определяет попадание вершины в поле зрения
                    pi1 = (x - map[cicle][0 + (flat_polygon_conclusion * 2)]) * (b - y) - (a - x) * (
                            y - map[cicle][1 + (flat_polygon_conclusion * 2)])
                    pi2 = (a - map[cicle][0 + (flat_polygon_conclusion * 2)]) * (b1 - b) - (a1 - a) * (
                            b - map[cicle][1 + (flat_polygon_conclusion * 2)])
                    pi3 = (a1 - map[cicle][0 + (flat_polygon_conclusion * 2)]) * (y - b1) - (x - a1) * (
                            b1 - map[cicle][1 + (flat_polygon_conclusion * 2)])

                    if pi1 > 0 and pi2 > 0 and pi3 > 0:  # условие вычисления проекции при попадании в поле зрения

                        distXX, distYY = distXY_func(x=x, x1=map[cicle][0 + (flat_polygon_conclusion * 2)], y=y,
                                                     y1=map[cicle][1 + (flat_polygon_conclusion * 2)])
                        dist_against_fisheye1, dist_against_fisheye2 = distXY_func(x=averageX, x1=map[cicle][
                            0 + (flat_polygon_conclusion * 2)], y=averageY, y1=map[cicle][
                            1 + (flat_polygon_conclusion * 2)])

                        Pifogor_dist = Pifogor_func(x=distXX, y=distYY)
                        Pifogor_against_fisheye = Pifogor_func(x=dist_against_fisheye1, y=dist_against_fisheye2)

                        Perim_against_fisheye = Perim_half_func_ver2(Pifogor=Pifogor_against_fisheye,
                                                                     Pifogor1=Pifogor_dist)

                        if Perim_against_fisheye * (Perim_against_fisheye - semi_hypo_of_va) * (
                                Perim_against_fisheye - Pifogor_dist) * (
                                Perim_against_fisheye - Pifogor_against_fisheye) >= 0:
                            h_fe = math.sqrt(Perim_against_fisheye * (Perim_against_fisheye - semi_hypo_of_va) * (
                                    Perim_against_fisheye - Pifogor_dist) * (
                                                     Perim_against_fisheye - Pifogor_against_fisheye)) * (
                                           2 / semi_hypo_of_va)
                        else:
                            h_fe = 0

                        if Pifogor_dist >= h_fe:
                            Pifogor_Answer_Fisheye = math.sqrt(Pifogor_dist * Pifogor_dist - h_fe * h_fe)
                        else:
                            Pifogor_Answer_Fisheye = math.sqrt(h_fe * h_fe - Pifogor_dist * Pifogor_dist)
                        length_lines_for_projection = Pifogor_func(x=Pifogor_Answer_Fisheye, y=Pifogor_Answer_Fisheye)
                        a_projection = (length_lines_for_projection * math.cos(angle + l)) + x
                        b_projection = (length_lines_for_projection * math.sin(angle + l)) + y
                        line_projection_x, line_projection_y = distXY_func(x=a_projection,
                                                                           x1=map[cicle][
                                                                               0 + (flat_polygon_conclusion * 2)],
                                                                           y=b_projection,
                                                                           y1=map[cicle][
                                                                               1 + (flat_polygon_conclusion * 2)])
                        final_length_line_for_projection = Pifogor_func(x=line_projection_x, y=line_projection_y)

                        if (Pifogor_Answer_Fisheye // 47) <= 220:
                            pre_flat_polygon_color[flat_polygon_conclusion] = 220 - (Pifogor_Answer_Fisheye // 47)

                        else:
                            pre_flat_polygon_color[flat_polygon_conclusion] = 0

                        x_display_output = (final_length_line_for_projection) * (960 / Pifogor_Answer_Fisheye)

                        flat_polygon_output[flat_polygon_conclusion][0] = x_display_output

                        wall_size = (1000000 // (Pifogor_Answer_Fisheye) - 0)

                        flat_polygon_output[flat_polygon_conclusion][1] = (1080 - wall_size) // 2
                        flat_polygon_output[flat_polygon_conclusion][2] = ((1080 - wall_size) // 2) + wall_size

                        polygon_display += 1
                flat_polygon_color = Arithmetical_Mean_func(a=pre_flat_polygon_color[0], b=pre_flat_polygon_color[1])

                if polygon_display == 2:
                    pygame.gfxdraw.filled_polygon(screen, [[flat_polygon_output[0][0], flat_polygon_output[0][1]],
                                                           [flat_polygon_output[1][0], flat_polygon_output[1][1]],
                                                           [flat_polygon_output[1][0], flat_polygon_output[1][2]],
                                                           [flat_polygon_output[0][0], flat_polygon_output[0][2]]],
                                                  [flat_polygon_color // 3, flat_polygon_color // 1.5,
                                                   flat_polygon_color // 1])
                    pygame.gfxdraw.aapolygon(screen, [[flat_polygon_output[0][0], flat_polygon_output[0][1]],
                                                      [flat_polygon_output[1][0], flat_polygon_output[1][1]],
                                                      [flat_polygon_output[1][0], flat_polygon_output[1][2]],
                                                      [flat_polygon_output[0][0], flat_polygon_output[0][2]]],
                                             [flat_polygon_color // 5, flat_polygon_color // 5,
                                              flat_polygon_color // 5])

                polygon_display = 0
            else:
                h = is_in_triangle(x, y, a, b, a1, b1, map[cicle][0], map[cicle][1])

                if h:  # условие вычисления проекции при попадании в поле зрения

                    distXX, distYY = distXY_func(x=x, x1=map[cicle][0], y=y, y1=map[cicle][1])
                    dist_against_fisheye1, dist_against_fisheye2 = distXY_func(x=averageX, x1=map[cicle][0], y=averageY,
                                                                               y1=map[cicle][1])

                    Pifogor_dist = Pifogor_func(x=distXX, y=distYY)
                    Pifogor_against_fisheye = Pifogor_func(x=dist_against_fisheye1, y=dist_against_fisheye2)

                    Perim_against_fisheye = Perim_half_func_ver2(Pifogor=Pifogor_against_fisheye, Pifogor1=Pifogor_dist)

                    if Perim_against_fisheye * (Perim_against_fisheye - semi_hypo_of_va) * (
                            Perim_against_fisheye - Pifogor_dist) * (
                            Perim_against_fisheye - Pifogor_against_fisheye) >= 0:
                        h_fe = math.sqrt(Perim_against_fisheye * (Perim_against_fisheye - semi_hypo_of_va) * (
                                Perim_against_fisheye - Pifogor_dist) * (
                                                 Perim_against_fisheye - Pifogor_against_fisheye)) * (
                                       2 / semi_hypo_of_va)
                    else:
                        h_fe = 0

                    Pifogor_Answer_Fisheye = math.sqrt((Pifogor_dist * Pifogor_dist) - (h_fe * h_fe))

                    a_projection = ((Pifogor_Answer_Fisheye * 2) * math.cos(angle)) + x
                    b_projection = ((Pifogor_Answer_Fisheye * 2) * math.sin(angle)) + y

                    line_projection_x, line_projection_y = distXY_func(x=a_projection, x1=map[cicle][0], y=b_projection,
                                                                       y1=map[cicle][1])
                    final_length_line_for_projection = Pifogor_func(x=line_projection_x, y=line_projection_y)

                    if (Pifogor_Answer_Fisheye // 37) <= 220:
                        pre_flat_polygon_color = 220 - (Pifogor_Answer_Fisheye // 37)

                    else:
                        pre_flat_polygon_color = 0

                    x_display_output = ((final_length_line_for_projection * (
                            960 / (Pifogor_Answer_Fisheye * 1.7321))) - 320) * 1.5

                    wall_size = (200000 // Pifogor_Answer_Fisheye)

                    flat_polygon_output = [0, 0, 0]

                    flat_polygon_output[0] = x_display_output

                    flat_polygon_output[1] = (1080 - wall_size) // 2
                    flat_polygon_output[2] = ((1080 - wall_size) // 2) + wall_size
                    map[cicle][2].draw_obj(rotation_midle + (x_display_output / display_width) * 45 - 22.5,
                                           yyyy + add_y * 2, x_display_output, Pifogor_Answer_Fisheye, 0, screen, lights)

        f3menu1 = my_font.render("X: " + str(x), True, [200, 200, 200])
        f3menu2 = my_font.render("Y: " + str(y), True, [200, 200, 200])
        f3menu3 = my_font.render("FPS: " + str(round(clock.get_fps())), True, [200, 200, 200])
        f3menu4 = my_font.render("ничего", True, [200, 200, 200])
        if hands != 0:
            f3menu4 = my_font.render(hands.name, True, [200, 200, 200])
        screen.blit(f3menu4, (350 * scaling_w, 10 * scaling_h))


        if mini_map_display == True:

            pygame.gfxdraw.aapolygon(screen, [[x // map_size, y // map_size, int(a) // map_size, int(b) // map_size],
                                              [int(a) // map_size, int(b) // map_size, int(a1) // map_size,
                                               int(b1) // map_size],
                                              [int(a1) // map_size, int(b1) // map_size, x, y]], [255, 28, 96])

            for minimap_cicle in prange(len(map)):
                pygame.gfxdraw.filled_circle(screen, round(map[minimap_cicle][0]) // map_size,
                                             round(map[minimap_cicle][1]) // map_size, round(2 * scaling_h),
                                             [220, 220, 220])

            pygame.gfxdraw.filled_circle(screen, round(x) // map_size, round(y) // map_size, round(8 * scaling_h),
                                         [220, 220, 220])
            pygame.gfxdraw.aacircle(screen, round(x) // map_size, round(y) // map_size, round(8 * scaling_h),
                                    [220, 220, 220])

            screen.blit(f3menu1, (x // map_size, (y) // map_size - 65 * scaling_h))
            screen.blit(f3menu2, (x // map_size, (y) // map_size - 35 * scaling_h))

        pygame.gfxdraw.box(screen, [[1833, 0], [1920, 33]], [0, 0, 0])
        screen.blit(f3menu3, (1750 * scaling_w, 10 * scaling_h))
        if hands != 0:
            hands.x = x
            hands.y = y
            mp = pygame.mouse.get_pos()
            wey = 0
            if add_y == 200:
                wey = mp[1]
            hands.draw_obj(275 + add_rot, display_heidth // 2 - 200 + add_y_w + wey + hands_y,
                           display_width // 2 + hands_x, 160, rotation_midle - add_rot,screen,lights)
        tics += 1

        pygame.display.flip()  # обновление экрана

    pygame.quit()

if __name__ == "__main__":
    main()
