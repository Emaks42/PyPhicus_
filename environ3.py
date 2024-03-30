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
    sph_pol = [
        Point(20.789660142870975, 0.0, 597.8150807960814),
        Point(20.789660142870975, 24.0, 597.8150807960814),
        Point(20.789660142870975, 48.0, 597.8150807960814),
        Point(20.789660142870975, 72.0, 597.8150807960814),
        Point(20.789660142870975, 96.0, 597.8150807960814),
        Point(20.789660142870975, 120.0, 597.8150807960814),
        Point(20.789660142870975, 144.0, 597.8150807960814),
        Point(20.789660142870975, 168.0, 597.8150807960814),
        Point(20.789660142870975, 192.0, 597.8150807960814),
        Point(20.789660142870975, 216.0, 597.8150807960814),
        Point(20.789660142870975, 240.0, 597.8150807960814),
        Point(20.789660142870975, 264.0, 597.8150807960814),
        Point(20.789660142870975, 288.0, 597.8150807960814),
        Point(20.789660142870975, 312.0, 597.8150807960814),
        Point(20.789660142870975, 336.0, 597.8150807960814),
        Point(40.67084573195993, 0.0, 591.3558006228784),
        Point(40.67084573195993, 24.0, 591.3558006228784),
        Point(40.67084573195993, 48.0, 591.3558006228784),
        Point(40.67084573195993, 72.0, 591.3558006228784),
        Point(40.67084573195993, 96.0, 591.3558006228784),
        Point(40.67084573195993, 120.0, 591.3558006228784),
        Point(40.67084573195993, 144.0, 591.3558006228784),
        Point(40.67084573195993, 168.0, 591.3558006228784),
        Point(40.67084573195993, 192.0, 591.3558006228784),
        Point(40.67084573195993, 216.0, 591.3558006228784),
        Point(40.67084573195993, 240.0, 591.3558006228784),
        Point(40.67084573195993, 264.0, 591.3558006228784),
        Point(40.67084573195993, 288.0, 591.3558006228784),
        Point(40.67084573195993, 312.0, 591.3558006228784),
        Point(40.67084573195993, 336.0, 591.3558006228784),
        Point(58.774781083461434, 0.0, 580.9044195862697),
        Point(58.774781083461434, 24.0, 580.9044195862697),
        Point(58.774781083461434, 48.0, 580.9044195862697),
        Point(58.774781083461434, 72.0, 580.9044195862697),
        Point(58.774781083461434, 96.0, 580.9044195862697),
        Point(58.774781083461434, 120.0, 580.9044195862697),
        Point(58.774781083461434, 144.0, 580.9044195862697),
        Point(58.774781083461434, 168.0, 580.9044195862697),
        Point(58.774781083461434, 192.0, 580.9044195862697),
        Point(58.774781083461434, 216.0, 580.9044195862697),
        Point(58.774781083461434, 240.0, 580.9044195862697),
        Point(58.774781083461434, 264.0, 580.9044195862697),
        Point(58.774781083461434, 288.0, 580.9044195862697),
        Point(58.774781083461434, 312.0, 580.9044195862697),
        Point(58.774781083461434, 336.0, 580.9044195862697),
        Point(74.31035347705556, 0.0, 566.9176461489424),
        Point(74.31035347705556, 24.0, 566.9176461489424),
        Point(74.31035347705556, 48.0, 566.9176461489424),
        Point(74.31035347705556, 72.0, 566.9176461489424),
        Point(74.31035347705556, 96.0, 566.9176461489424),
        Point(74.31035347705556, 120.0, 566.9176461489424),
        Point(74.31035347705556, 144.0, 566.9176461489424),
        Point(74.31035347705556, 168.0, 566.9176461489424),
        Point(74.31035347705556, 192.0, 566.9176461489424),
        Point(74.31035347705556, 216.0, 566.9176461489424),
        Point(74.31035347705556, 240.0, 566.9176461489424),
        Point(74.31035347705556, 264.0, 566.9176461489424),
        Point(74.31035347705556, 288.0, 566.9176461489424),
        Point(74.31035347705556, 312.0, 566.9176461489424),
        Point(74.31035347705556, 336.0, 566.9176461489424),
        Point(86.59868350340963, 0.0, 550.0066797085778),
        Point(86.59868350340963, 24.0, 550.0066797085778),
        Point(86.59868350340963, 48.0, 550.0066797085778),
        Point(86.59868350340963, 72.0, 550.0066797085778),
        Point(86.59868350340963, 96.0, 550.0066797085778),
        Point(86.59868350340963, 120.0, 550.0066797085778),
        Point(86.59868350340963, 144.0, 550.0066797085778),
        Point(86.59868350340963, 168.0, 550.0066797085778),
        Point(86.59868350340963, 192.0, 550.0066797085778),
        Point(86.59868350340963, 216.0, 550.0066797085778),
        Point(86.59868350340963, 240.0, 550.0066797085778),
        Point(86.59868350340963, 264.0, 550.0066797085778),
        Point(86.59868350340963, 288.0, 550.0066797085778),
        Point(86.59868350340963, 312.0, 550.0066797085778),
        Point(86.59868350340963, 336.0, 550.0066797085778),
        Point(95.10279099735025, 0.0, 530.9105021718236),
        Point(95.10279099735025, 24.0, 530.9105021718236),
        Point(95.10279099735025, 48.0, 530.9105021718236),
        Point(95.10279099735025, 72.0, 530.9105021718236),
        Point(95.10279099735025, 96.0, 530.9105021718236),
        Point(95.10279099735025, 120.0, 530.9105021718236),
        Point(95.10279099735025, 144.0, 530.9105021718236),
        Point(95.10279099735025, 168.0, 530.9105021718236),
        Point(95.10279099735025, 192.0, 530.9105021718236),
        Point(95.10279099735025, 216.0, 530.9105021718236),
        Point(95.10279099735025, 240.0, 530.9105021718236),
        Point(95.10279099735025, 264.0, 530.9105021718236),
        Point(95.10279099735025, 288.0, 530.9105021718236),
        Point(95.10279099735025, 312.0, 530.9105021718236),
        Point(95.10279099735025, 336.0, 530.9105021718236),
        Point(99.45106020336341, 0.0, 510.4635856391098),
        Point(99.45106020336341, 24.0, 510.4635856391098),
        Point(99.45106020336341, 48.0, 510.4635856391098),
        Point(99.45106020336341, 72.0, 510.4635856391098),
        Point(99.45106020336341, 96.0, 510.4635856391098),
        Point(99.45106020336341, 120.0, 510.4635856391098),
        Point(99.45106020336341, 144.0, 510.4635856391098),
        Point(99.45106020336341, 168.0, 510.4635856391098),
        Point(99.45106020336341, 192.0, 510.4635856391098),
        Point(99.45106020336341, 216.0, 510.4635856391098),
        Point(99.45106020336341, 240.0, 510.4635856391098),
        Point(99.45106020336341, 264.0, 510.4635856391098),
        Point(99.45106020336341, 288.0, 510.4635856391098),
        Point(99.45106020336341, 312.0, 510.4635856391098),
        Point(99.45106020336341, 336.0, 510.4635856391098),
        Point(99.4534787836086, 0.0, 489.55942732230113),
        Point(99.4534787836086, 24.0, 489.55942732230113),
        Point(99.4534787836086, 48.0, 489.55942732230113),
        Point(99.4534787836086, 72.0, 489.55942732230113),
        Point(99.4534787836086, 96.0, 489.55942732230113),
        Point(99.4534787836086, 120.0, 489.55942732230113),
        Point(99.4534787836086, 144.0, 489.55942732230113),
        Point(99.4534787836086, 168.0, 489.55942732230113),
        Point(99.4534787836086, 192.0, 489.55942732230113),
        Point(99.4534787836086, 216.0, 489.55942732230113),
        Point(99.4534787836086, 240.0, 489.55942732230113),
        Point(99.4534787836086, 264.0, 489.55942732230113),
        Point(99.4534787836086, 288.0, 489.55942732230113),
        Point(99.4534787836086, 312.0, 489.55942732230113),
        Point(99.4534787836086, 336.0, 489.55942732230113),
        Point(95.10994105003735, 0.0, 469.11150516036076),
        Point(95.10994105003735, 24.0, 469.11150516036076),
        Point(95.10994105003735, 48.0, 469.11150516036076),
        Point(95.10994105003735, 72.0, 469.11150516036076),
        Point(95.10994105003735, 96.0, 469.11150516036076),
        Point(95.10994105003735, 120.0, 469.11150516036076),
        Point(95.10994105003735, 144.0, 469.11150516036076),
        Point(95.10994105003735, 168.0, 469.11150516036076),
        Point(95.10994105003735, 192.0, 469.11150516036076),
        Point(95.10994105003735, 216.0, 469.11150516036076),
        Point(95.10994105003735, 240.0, 469.11150516036076),
        Point(95.10994105003735, 264.0, 469.11150516036076),
        Point(95.10994105003735, 288.0, 469.11150516036076),
        Point(95.10994105003735, 312.0, 469.11150516036076),
        Point(95.10994105003735, 336.0, 469.11150516036076),
        Point(86.61025258279014, 0.0, 450.01336030952575),
        Point(86.61025258279014, 24.0, 450.01336030952575),
        Point(86.61025258279014, 48.0, 450.01336030952575),
        Point(86.61025258279014, 72.0, 450.01336030952575),
        Point(86.61025258279014, 96.0, 450.01336030952575),
        Point(86.61025258279014, 120.0, 450.01336030952575),
        Point(86.61025258279014, 144.0, 450.01336030952575),
        Point(86.61025258279014, 168.0, 450.01336030952575),
        Point(86.61025258279014, 192.0, 450.01336030952575),
        Point(86.61025258279014, 216.0, 450.01336030952575),
        Point(86.61025258279014, 240.0, 450.01336030952575),
        Point(86.61025258279014, 264.0, 450.01336030952575),
        Point(86.61025258279014, 288.0, 450.01336030952575),
        Point(86.61025258279014, 312.0, 450.01336030952575),
        Point(86.61025258279014, 336.0, 450.01336030952575),
        Point(74.32583603305524, 0.0, 433.0995508386723),
        Point(74.32583603305524, 24.0, 433.0995508386723),
        Point(74.32583603305524, 48.0, 433.0995508386723),
        Point(74.32583603305524, 72.0, 433.0995508386723),
        Point(74.32583603305524, 96.0, 433.0995508386723),
        Point(74.32583603305524, 120.0, 433.0995508386723),
        Point(74.32583603305524, 144.0, 433.0995508386723),
        Point(74.32583603305524, 168.0, 433.0995508386723),
        Point(74.32583603305524, 192.0, 433.0995508386723),
        Point(74.32583603305524, 216.0, 433.0995508386723),
        Point(74.32583603305524, 240.0, 433.0995508386723),
        Point(74.32583603305524, 264.0, 433.0995508386723),
        Point(74.32583603305524, 288.0, 433.0995508386723),
        Point(74.32583603305524, 312.0, 433.0995508386723),
        Point(74.32583603305524, 336.0, 433.0995508386723),
        Point(58.79350055340174, 0.0, 419.1091828902863),
        Point(58.79350055340174, 24.0, 419.1091828902863),
        Point(58.79350055340174, 48.0, 419.1091828902863),
        Point(58.79350055340174, 72.0, 419.1091828902863),
        Point(58.79350055340174, 96.0, 419.1091828902863),
        Point(58.79350055340174, 120.0, 419.1091828902863),
        Point(58.79350055340174, 144.0, 419.1091828902863),
        Point(58.79350055340174, 168.0, 419.1091828902863),
        Point(58.79350055340174, 192.0, 419.1091828902863),
        Point(58.79350055340174, 216.0, 419.1091828902863),
        Point(58.79350055340174, 240.0, 419.1091828902863),
        Point(58.79350055340174, 264.0, 419.1091828902863),
        Point(58.79350055340174, 288.0, 419.1091828902863),
        Point(58.79350055340174, 312.0, 419.1091828902863),
        Point(58.79350055340174, 336.0, 419.1091828902863),
        Point(40.691984105253624, 0.0, 408.653612936374),
        Point(40.691984105253624, 24.0, 408.653612936374),
        Point(40.691984105253624, 48.0, 408.653612936374),
        Point(40.691984105253624, 72.0, 408.653612936374),
        Point(40.691984105253624, 96.0, 408.653612936374),
        Point(40.691984105253624, 120.0, 408.653612936374),
        Point(40.691984105253624, 144.0, 408.653612936374),
        Point(40.691984105253624, 168.0, 408.653612936374),
        Point(40.691984105253624, 192.0, 408.653612936374),
        Point(40.691984105253624, 216.0, 408.653612936374),
        Point(40.691984105253624, 240.0, 408.653612936374),
        Point(40.691984105253624, 264.0, 408.653612936374),
        Point(40.691984105253624, 288.0, 408.653612936374),
        Point(40.691984105253624, 312.0, 408.653612936374),
        Point(40.691984105253624, 336.0, 408.653612936374),
        Point(20.812293706763125, 0.0, 402.1897324885397),
        Point(20.812293706763125, 24.0, 402.1897324885397),
        Point(20.812293706763125, 48.0, 402.1897324885397),
        Point(20.812293706763125, 72.0, 402.1897324885397),
        Point(20.812293706763125, 96.0, 402.1897324885397),
        Point(20.812293706763125, 120.0, 402.1897324885397),
        Point(20.812293706763125, 144.0, 402.1897324885397),
        Point(20.812293706763125, 168.0, 402.1897324885397),
        Point(20.812293706763125, 192.0, 402.1897324885397),
        Point(20.812293706763125, 216.0, 402.1897324885397),
        Point(20.812293706763125, 240.0, 402.1897324885397),
        Point(20.812293706763125, 264.0, 402.1897324885397),
        Point(20.812293706763125, 288.0, 402.1897324885397),
        Point(20.812293706763125, 312.0, 402.1897324885397),
        Point(20.812293706763125, 336.0, 402.1897324885397),
        Point(0.023139704322540595, 0.0, 400.00000267722965),
        Point(0.023139704322540595, 24.0, 400.00000267722965),
        Point(0.023139704322540595, 48.0, 400.00000267722965),
        Point(0.023139704322540595, 72.0, 400.00000267722965),
        Point(0.023139704322540595, 96.0, 400.00000267722965),
        Point(0.023139704322540595, 120.0, 400.00000267722965),
        Point(0.023139704322540595, 144.0, 400.00000267722965),
        Point(0.023139704322540595, 168.0, 400.00000267722965),
        Point(0.023139704322540595, 192.0, 400.00000267722965),
        Point(0.023139704322540595, 216.0, 400.00000267722965),
        Point(0.023139704322540595, 240.0, 400.00000267722965),
        Point(0.023139704322540595, 264.0, 400.00000267722965),
        Point(0.023139704322540595, 288.0, 400.00000267722965),
        Point(0.023139704322540595, 312.0, 400.00000267722965),
        Point(0.023139704322540595, 336.0, 400.00000267722965),
    ]
    sph_poly = [
        Polygon([98, 114, 113], [200, 200, 200], 0),
        Polygon([97, 98, 113], [200, 200, 200], 0),
        Polygon([113, 129, 128], [200, 200, 200], 0),
        Polygon([113, 114, 129], [200, 200, 200], 0),
        Polygon([112, 113, 128], [200, 200, 200], 0),
        Polygon([97, 113, 112], [200, 200, 200], 0),
        Polygon([83, 99, 98], [200, 200, 200], 0),
        Polygon([98, 99, 114], [200, 200, 200], 0),
        Polygon([82, 83, 98], [200, 200, 200], 0),
        Polygon([82, 98, 97], [200, 200, 200], 0),
        Polygon([112, 128, 127], [200, 200, 200], 0),
        Polygon([128, 129, 144], [200, 200, 200], 0),
        Polygon([127, 128, 143], [200, 200, 200], 0),
        Polygon([128, 144, 143], [200, 200, 200], 0),
        Polygon([83, 84, 99], [200, 200, 200], 0),
        Polygon([68, 84, 83], [200, 200, 200], 0),
        Polygon([67, 68, 83], [200, 200, 200], 0),
        Polygon([67, 83, 82], [200, 200, 200], 0),
        Polygon([99, 115, 114], [200, 200, 200], 0),
        Polygon([114, 130, 129], [200, 200, 200], 0),
        Polygon([114, 115, 130], [200, 200, 200], 0),
        Polygon([84, 100, 99], [200, 200, 200], 0),
        Polygon([99, 100, 115], [200, 200, 200], 0),
        Polygon([129, 145, 144], [200, 200, 200], 0),
        Polygon([129, 130, 145], [200, 200, 200], 0),
        Polygon([68, 69, 84], [200, 200, 200], 0),
        Polygon([69, 85, 84], [200, 200, 200], 0),
        Polygon([84, 85, 100], [200, 200, 200], 0),
        Polygon([96, 97, 112], [200, 200, 200], 0),
        Polygon([111, 112, 127], [200, 200, 200], 0),
        Polygon([96, 112, 111], [200, 200, 200], 0),
        Polygon([81, 82, 97], [200, 200, 200], 0),
        Polygon([81, 97, 96], [200, 200, 200], 0),
        Polygon([127, 143, 142], [200, 200, 200], 0),
        Polygon([143, 144, 159], [200, 200, 200], 0),
        Polygon([142, 143, 158], [200, 200, 200], 0),
        Polygon([143, 159, 158], [200, 200, 200], 0),
        Polygon([53, 69, 68], [200, 200, 200], 0),
        Polygon([52, 68, 67], [200, 200, 200], 0),
        Polygon([52, 53, 68], [200, 200, 200], 0),
        Polygon([126, 127, 142], [200, 200, 200], 0),
        Polygon([111, 127, 126], [200, 200, 200], 0),
        Polygon([66, 67, 82], [200, 200, 200], 0),
        Polygon([66, 82, 81], [200, 200, 200], 0),
        Polygon([144, 160, 159], [200, 200, 200], 0),
        Polygon([144, 145, 160], [200, 200, 200], 0),
        Polygon([53, 54, 69], [200, 200, 200], 0),
        Polygon([54, 70, 69], [200, 200, 200], 0),
        Polygon([69, 70, 85], [200, 200, 200], 0),
        Polygon([142, 158, 157], [200, 200, 200], 0),
        Polygon([141, 142, 157], [200, 200, 200], 0),
        Polygon([126, 142, 141], [200, 200, 200], 0),
        Polygon([51, 52, 67], [200, 200, 200], 0),
        Polygon([51, 67, 66], [200, 200, 200], 0),
        Polygon([158, 159, 174], [200, 200, 200], 0),
        Polygon([157, 158, 173], [200, 200, 200], 0),
        Polygon([158, 174, 173], [200, 200, 200], 0),
        Polygon([38, 54, 53], [200, 200, 200], 0),
        Polygon([37, 53, 52], [200, 200, 200], 0),
        Polygon([37, 38, 53], [200, 200, 200], 0),
        Polygon([100, 116, 115], [200, 200, 200], 0),
        Polygon([115, 131, 130], [200, 200, 200], 0),
        Polygon([115, 116, 131], [200, 200, 200], 0),
        Polygon([85, 101, 100], [200, 200, 200], 0),
        Polygon([100, 101, 116], [200, 200, 200], 0),
        Polygon([159, 175, 174], [200, 200, 200], 0),
        Polygon([159, 160, 175], [200, 200, 200], 0),
        Polygon([54, 55, 70], [200, 200, 200], 0),
        Polygon([38, 39, 54], [200, 200, 200], 0),
        Polygon([39, 55, 54], [200, 200, 200], 0),
        Polygon([130, 146, 145], [200, 200, 200], 0),
        Polygon([130, 131, 146], [200, 200, 200], 0),
        Polygon([70, 86, 85], [200, 200, 200], 0),
        Polygon([85, 86, 101], [200, 200, 200], 0),
        Polygon([157, 173, 172], [200, 200, 200], 0),
        Polygon([141, 157, 156], [200, 200, 200], 0),
        Polygon([156, 157, 172], [200, 200, 200], 0),
        Polygon([36, 37, 52], [200, 200, 200], 0),
        Polygon([36, 52, 51], [200, 200, 200], 0),
        Polygon([145, 161, 160], [200, 200, 200], 0),
        Polygon([145, 146, 161], [200, 200, 200], 0),
        Polygon([55, 71, 70], [200, 200, 200], 0),
        Polygon([70, 71, 86], [200, 200, 200], 0),
        Polygon([95, 96, 111], [200, 200, 200], 0),
        Polygon([110, 111, 126], [200, 200, 200], 0),
        Polygon([95, 111, 110], [200, 200, 200], 0),
        Polygon([80, 81, 96], [200, 200, 200], 0),
        Polygon([80, 96, 95], [200, 200, 200], 0),
        Polygon([173, 174, 189], [200, 200, 200], 0),
        Polygon([172, 173, 188], [200, 200, 200], 0),
        Polygon([173, 189, 188], [200, 200, 200], 0),
        Polygon([23, 39, 38], [200, 200, 200], 0),
        Polygon([22, 38, 37], [200, 200, 200], 0),
        Polygon([22, 23, 38], [200, 200, 200], 0),
        Polygon([125, 126, 141], [200, 200, 200], 0),
        Polygon([110, 126, 125], [200, 200, 200], 0),
        Polygon([65, 66, 81], [200, 200, 200], 0),
        Polygon([65, 81, 80], [200, 200, 200], 0),
        Polygon([174, 175, 190], [200, 200, 200], 0),
        Polygon([174, 190, 189], [200, 200, 200], 0),
        Polygon([39, 40, 55], [200, 200, 200], 0),
        Polygon([24, 40, 39], [200, 200, 200], 0),
        Polygon([23, 24, 39], [200, 200, 200], 0),
        Polygon([160, 176, 175], [200, 200, 200], 0),
        Polygon([160, 161, 176], [200, 200, 200], 0),
        Polygon([40, 56, 55], [200, 200, 200], 0),
        Polygon([55, 56, 71], [200, 200, 200], 0),
        Polygon([140, 141, 156], [200, 200, 200], 0),
        Polygon([125, 141, 140], [200, 200, 200], 0),
        Polygon([50, 51, 66], [200, 200, 200], 0),
        Polygon([50, 66, 65], [200, 200, 200], 0),
        Polygon([156, 172, 171], [200, 200, 200], 0),
        Polygon([172, 188, 187], [200, 200, 200], 0),
        Polygon([171, 172, 187], [200, 200, 200], 0),
        Polygon([21, 37, 36], [200, 200, 200], 0),
        Polygon([21, 22, 37], [200, 200, 200], 0),
        Polygon([155, 156, 171], [200, 200, 200], 0),
        Polygon([140, 156, 155], [200, 200, 200], 0),
        Polygon([35, 36, 51], [200, 200, 200], 0),
        Polygon([35, 51, 50], [200, 200, 200], 0),
        Polygon([175, 191, 190], [200, 200, 200], 0),
        Polygon([175, 176, 191], [200, 200, 200], 0),
        Polygon([24, 25, 40], [200, 200, 200], 0),
        Polygon([25, 41, 40], [200, 200, 200], 0),
        Polygon([40, 41, 56], [200, 200, 200], 0),
        Polygon([188, 189, 204], [200, 200, 200], 0),
        Polygon([187, 188, 203], [200, 200, 200], 0),
        Polygon([188, 204, 203], [200, 200, 200], 0),
        Polygon([8, 24, 23], [200, 200, 200], 0),
        Polygon([7, 23, 22], [200, 200, 200], 0),
        Polygon([7, 8, 23], [200, 200, 200], 0),
        Polygon([189, 190, 205], [200, 200, 200], 0),
        Polygon([189, 205, 204], [200, 200, 200], 0),
        Polygon([9, 25, 24], [200, 200, 200], 0),
        Polygon([8, 9, 24], [200, 200, 200], 0),
        Polygon([101, 117, 116], [200, 200, 200], 0),
        Polygon([116, 132, 131], [200, 200, 200], 0),
        Polygon([116, 117, 132], [200, 200, 200], 0),
        Polygon([86, 102, 101], [200, 200, 200], 0),
        Polygon([101, 102, 117], [200, 200, 200], 0),
        Polygon([171, 187, 186], [200, 200, 200], 0),
        Polygon([170, 171, 186], [200, 200, 200], 0),
        Polygon([155, 171, 170], [200, 200, 200], 0),
        Polygon([20, 21, 36], [200, 200, 200], 0),
        Polygon([20, 36, 35], [200, 200, 200], 0),
        Polygon([186, 187, 202], [200, 200, 200], 0),
        Polygon([187, 203, 202], [200, 200, 200], 0),
        Polygon([6, 22, 21], [200, 200, 200], 0),
        Polygon([6, 7, 22], [200, 200, 200], 0),
        Polygon([131, 147, 146], [200, 200, 200], 0),
        Polygon([131, 132, 147], [200, 200, 200], 0),
        Polygon([71, 87, 86], [200, 200, 200], 0),
        Polygon([86, 87, 102], [200, 200, 200], 0),
        Polygon([146, 162, 161], [200, 200, 200], 0),
        Polygon([146, 147, 162], [200, 200, 200], 0),
        Polygon([56, 72, 71], [200, 200, 200], 0),
        Polygon([71, 72, 87], [200, 200, 200], 0),
        Polygon([190, 191, 206], [200, 200, 200], 0),
        Polygon([190, 206, 205], [200, 200, 200], 0),
        Polygon([25, 26, 41], [200, 200, 200], 0),
        Polygon([9, 10, 25], [200, 200, 200], 0),
        Polygon([10, 26, 25], [200, 200, 200], 0),
        Polygon([161, 177, 176], [200, 200, 200], 0),
        Polygon([161, 162, 177], [200, 200, 200], 0),
        Polygon([41, 57, 56], [200, 200, 200], 0),
        Polygon([56, 57, 72], [200, 200, 200], 0),
        Polygon([186, 202, 201], [200, 200, 200], 0),
        Polygon([170, 186, 185], [200, 200, 200], 0),
        Polygon([185, 186, 201], [200, 200, 200], 0),
        Polygon([5, 6, 21], [200, 200, 200], 0),
        Polygon([5, 21, 20], [200, 200, 200], 0),
        Polygon([94, 95, 110], [200, 200, 200], 0),
        Polygon([109, 110, 125], [200, 200, 200], 0),
        Polygon([94, 110, 109], [200, 200, 200], 0),
        Polygon([79, 80, 95], [200, 200, 200], 0),
        Polygon([79, 95, 94], [200, 200, 200], 0),
        Polygon([124, 125, 140], [200, 200, 200], 0),
        Polygon([109, 125, 124], [200, 200, 200], 0),
        Polygon([64, 65, 80], [200, 200, 200], 0),
        Polygon([64, 80, 79], [200, 200, 200], 0),
        Polygon([176, 192, 191], [200, 200, 200], 0),
        Polygon([176, 177, 192], [200, 200, 200], 0),
        Polygon([26, 42, 41], [200, 200, 200], 0),
        Polygon([41, 42, 57], [200, 200, 200], 0),
        Polygon([139, 140, 155], [200, 200, 200], 0),
        Polygon([124, 140, 139], [200, 200, 200], 0),
        Polygon([49, 50, 65], [200, 200, 200], 0),
        Polygon([49, 65, 64], [200, 200, 200], 0),
        Polygon([203, 204, 219], [200, 200, 200], 0),
        Polygon([202, 203, 218], [200, 200, 200], 0),
        Polygon([203, 219, 218], [200, 200, 200], 0),
        Polygon([204, 205, 220], [200, 200, 200], 0),
        Polygon([204, 220, 219], [200, 200, 200], 0),
        Polygon([201, 202, 217], [200, 200, 200], 0),
        Polygon([202, 218, 217], [200, 200, 200], 0),
        Polygon([154, 155, 170], [200, 200, 200], 0),
        Polygon([139, 155, 154], [200, 200, 200], 0),
        Polygon([34, 35, 50], [200, 200, 200], 0),
        Polygon([34, 50, 49], [200, 200, 200], 0),
        Polygon([191, 207, 206], [200, 200, 200], 0),
        Polygon([191, 192, 207], [200, 200, 200], 0),
        Polygon([10, 11, 26], [200, 200, 200], 0),
        Polygon([11, 27, 26], [200, 200, 200], 0),
        Polygon([26, 27, 42], [200, 200, 200], 0),
        Polygon([205, 206, 221], [200, 200, 200], 0),
        Polygon([205, 221, 220], [200, 200, 200], 0),
        Polygon([169, 170, 185], [200, 200, 200], 0),
        Polygon([154, 170, 169], [200, 200, 200], 0),
        Polygon([19, 20, 35], [200, 200, 200], 0),
        Polygon([19, 35, 34], [200, 200, 200], 0),
        Polygon([185, 201, 200], [200, 200, 200], 0),
        Polygon([200, 201, 216], [200, 200, 200], 0),
        Polygon([201, 217, 216], [200, 200, 200], 0),
        Polygon([184, 185, 200], [200, 200, 200], 0),
        Polygon([169, 185, 184], [200, 200, 200], 0),
        Polygon([4, 5, 20], [200, 200, 200], 0),
        Polygon([4, 20, 19], [200, 200, 200], 0),
        Polygon([206, 222, 221], [200, 200, 200], 0),
        Polygon([206, 207, 222], [200, 200, 200], 0),
        Polygon([11, 12, 27], [200, 200, 200], 0),
        Polygon([200, 216, 215], [200, 200, 200], 0),
        Polygon([199, 200, 215], [200, 200, 200], 0),
        Polygon([184, 200, 199], [200, 200, 200], 0),
        Polygon([199, 215, 214], [200, 200, 200], 0),
        Polygon([207, 223, 222], [200, 200, 200], 0),
        Polygon([198, 214, 213], [200, 200, 200], 0),
        Polygon([198, 199, 214], [200, 200, 200], 0),
        Polygon([208, 224, 223], [200, 200, 200], 0),
        Polygon([207, 208, 223], [200, 200, 200], 0),
        Polygon([197, 213, 212], [200, 200, 200], 0),
        Polygon([197, 198, 213], [200, 200, 200], 0),
        Polygon([195, 210, 224], [200, 200, 200], 0),
        Polygon([208, 209, 224], [200, 200, 200], 0),
        Polygon([195, 224, 209], [200, 200, 200], 0),
        Polygon([196, 212, 211], [200, 200, 200], 0),
        Polygon([196, 197, 212], [200, 200, 200], 0),
        Polygon([195, 211, 210], [200, 200, 200], 0),
        Polygon([195, 196, 211], [200, 200, 200], 0),
        Polygon([12, 28, 27], [200, 200, 200], 0),
        Polygon([12, 13, 28], [200, 200, 200], 0),
        Polygon([192, 208, 207], [200, 200, 200], 0),
        Polygon([27, 43, 42], [200, 200, 200], 0),
        Polygon([27, 28, 43], [200, 200, 200], 0),
        Polygon([177, 193, 192], [200, 200, 200], 0),
        Polygon([192, 193, 208], [200, 200, 200], 0),
        Polygon([42, 58, 57], [200, 200, 200], 0),
        Polygon([42, 43, 58], [200, 200, 200], 0),
        Polygon([162, 178, 177], [200, 200, 200], 0),
        Polygon([177, 178, 193], [200, 200, 200], 0),
        Polygon([57, 73, 72], [200, 200, 200], 0),
        Polygon([57, 58, 73], [200, 200, 200], 0),
        Polygon([147, 163, 162], [200, 200, 200], 0),
        Polygon([162, 163, 178], [200, 200, 200], 0),
        Polygon([72, 88, 87], [200, 200, 200], 0),
        Polygon([72, 73, 88], [200, 200, 200], 0),
        Polygon([132, 148, 147], [200, 200, 200], 0),
        Polygon([147, 148, 163], [200, 200, 200], 0),
        Polygon([87, 103, 102], [200, 200, 200], 0),
        Polygon([87, 88, 103], [200, 200, 200], 0),
        Polygon([117, 133, 132], [200, 200, 200], 0),
        Polygon([132, 133, 148], [200, 200, 200], 0),
        Polygon([102, 118, 117], [200, 200, 200], 0),
        Polygon([102, 103, 118], [200, 200, 200], 0),
        Polygon([117, 118, 133], [200, 200, 200], 0),
        Polygon([3, 4, 19], [200, 200, 200], 0),
        Polygon([183, 184, 199], [200, 200, 200], 0),
        Polygon([183, 199, 198], [200, 200, 200], 0),
        Polygon([18, 19, 34], [200, 200, 200], 0),
        Polygon([3, 19, 18], [200, 200, 200], 0),
        Polygon([168, 169, 184], [200, 200, 200], 0),
        Polygon([168, 184, 183], [200, 200, 200], 0),
        Polygon([13, 14, 29], [200, 200, 200], 0),
        Polygon([13, 29, 28], [200, 200, 200], 0),
        Polygon([193, 209, 208], [200, 200, 200], 0),
        Polygon([33, 34, 49], [200, 200, 200], 0),
        Polygon([18, 34, 33], [200, 200, 200], 0),
        Polygon([153, 154, 169], [200, 200, 200], 0),
        Polygon([153, 169, 168], [200, 200, 200], 0),
        Polygon([2, 3, 18], [200, 200, 200], 0),
        Polygon([182, 198, 197], [200, 200, 200], 0),
        Polygon([182, 183, 198], [200, 200, 200], 0),
        Polygon([48, 49, 64], [200, 200, 200], 0),
        Polygon([33, 49, 48], [200, 200, 200], 0),
        Polygon([138, 139, 154], [200, 200, 200], 0),
        Polygon([138, 154, 153], [200, 200, 200], 0),
        Polygon([63, 64, 79], [200, 200, 200], 0),
        Polygon([48, 64, 63], [200, 200, 200], 0),
        Polygon([123, 124, 139], [200, 200, 200], 0),
        Polygon([123, 139, 138], [200, 200, 200], 0),
        Polygon([0, 29, 14], [200, 200, 200], 0),
        Polygon([193, 194, 209], [200, 200, 200], 0),
        Polygon([180, 195, 209], [200, 200, 200], 0),
        Polygon([180, 209, 194], [200, 200, 200], 0),
        Polygon([78, 79, 94], [200, 200, 200], 0),
        Polygon([63, 79, 78], [200, 200, 200], 0),
        Polygon([108, 109, 124], [200, 200, 200], 0),
        Polygon([108, 124, 123], [200, 200, 200], 0),
        Polygon([93, 94, 109], [200, 200, 200], 0),
        Polygon([78, 94, 93], [200, 200, 200], 0),
        Polygon([93, 109, 108], [200, 200, 200], 0),
        Polygon([1, 2, 17], [200, 200, 200], 0),
        Polygon([2, 18, 17], [200, 200, 200], 0),
        Polygon([181, 197, 196], [200, 200, 200], 0),
        Polygon([181, 182, 197], [200, 200, 200], 0),
        Polygon([28, 44, 43], [200, 200, 200], 0),
        Polygon([28, 29, 44], [200, 200, 200], 0),
        Polygon([178, 194, 193], [200, 200, 200], 0),
        Polygon([0, 1, 16], [200, 200, 200], 0),
        Polygon([0, 15, 29], [200, 200, 200], 0),
        Polygon([0, 16, 15], [200, 200, 200], 0),
        Polygon([180, 196, 195], [200, 200, 200], 0),
        Polygon([1, 17, 16], [200, 200, 200], 0),
        Polygon([180, 181, 196], [200, 200, 200], 0),
        Polygon([17, 18, 33], [200, 200, 200], 0),
        Polygon([167, 168, 183], [200, 200, 200], 0),
        Polygon([167, 183, 182], [200, 200, 200], 0),
        Polygon([43, 59, 58], [200, 200, 200], 0),
        Polygon([43, 44, 59], [200, 200, 200], 0),
        Polygon([178, 179, 194], [200, 200, 200], 0),
        Polygon([163, 179, 178], [200, 200, 200], 0),
        Polygon([15, 44, 29], [200, 200, 200], 0),
        Polygon([165, 180, 194], [200, 200, 200], 0),
        Polygon([165, 194, 179], [200, 200, 200], 0),
        Polygon([58, 74, 73], [200, 200, 200], 0),
        Polygon([58, 59, 74], [200, 200, 200], 0),
        Polygon([148, 164, 163], [200, 200, 200], 0),
        Polygon([163, 164, 179], [200, 200, 200], 0),
        Polygon([17, 33, 32], [200, 200, 200], 0),
        Polygon([32, 33, 48], [200, 200, 200], 0),
        Polygon([152, 153, 168], [200, 200, 200], 0),
        Polygon([152, 168, 167], [200, 200, 200], 0),
        Polygon([16, 17, 32], [200, 200, 200], 0),
        Polygon([166, 182, 181], [200, 200, 200], 0),
        Polygon([166, 167, 182], [200, 200, 200], 0),
        Polygon([73, 89, 88], [200, 200, 200], 0),
        Polygon([73, 74, 89], [200, 200, 200], 0),
        Polygon([133, 149, 148], [200, 200, 200], 0),
        Polygon([148, 149, 164], [200, 200, 200], 0),
        Polygon([15, 16, 31], [200, 200, 200], 0),
        Polygon([15, 30, 44], [200, 200, 200], 0),
        Polygon([15, 31, 30], [200, 200, 200], 0),
        Polygon([165, 181, 180], [200, 200, 200], 0),
        Polygon([16, 32, 31], [200, 200, 200], 0),
        Polygon([165, 166, 181], [200, 200, 200], 0),
        Polygon([47, 48, 63], [200, 200, 200], 0),
        Polygon([32, 48, 47], [200, 200, 200], 0),
        Polygon([137, 138, 153], [200, 200, 200], 0),
        Polygon([137, 153, 152], [200, 200, 200], 0),
        Polygon([88, 104, 103], [200, 200, 200], 0),
        Polygon([88, 89, 104], [200, 200, 200], 0),
        Polygon([118, 134, 133], [200, 200, 200], 0),
        Polygon([133, 134, 149], [200, 200, 200], 0),
        Polygon([103, 119, 118], [200, 200, 200], 0),
        Polygon([103, 104, 119], [200, 200, 200], 0),
        Polygon([118, 119, 134], [200, 200, 200], 0),
        Polygon([30, 59, 44], [200, 200, 200], 0),
        Polygon([150, 165, 179], [200, 200, 200], 0),
        Polygon([150, 179, 164], [200, 200, 200], 0),
        Polygon([62, 63, 78], [200, 200, 200], 0),
        Polygon([47, 63, 62], [200, 200, 200], 0),
        Polygon([122, 123, 138], [200, 200, 200], 0),
        Polygon([122, 138, 137], [200, 200, 200], 0),
        Polygon([31, 32, 47], [200, 200, 200], 0),
        Polygon([151, 167, 166], [200, 200, 200], 0),
        Polygon([151, 152, 167], [200, 200, 200], 0),
        Polygon([77, 78, 93], [200, 200, 200], 0),
        Polygon([62, 78, 77], [200, 200, 200], 0),
        Polygon([107, 108, 123], [200, 200, 200], 0),
        Polygon([107, 123, 122], [200, 200, 200], 0),
        Polygon([92, 93, 108], [200, 200, 200], 0),
        Polygon([77, 93, 92], [200, 200, 200], 0),
        Polygon([92, 108, 107], [200, 200, 200], 0),
        Polygon([30, 45, 59], [200, 200, 200], 0),
        Polygon([30, 31, 46], [200, 200, 200], 0),
        Polygon([30, 46, 45], [200, 200, 200], 0),
        Polygon([150, 166, 165], [200, 200, 200], 0),
        Polygon([45, 74, 59], [200, 200, 200], 0),
        Polygon([135, 164, 149], [200, 200, 200], 0),
        Polygon([135, 150, 164], [200, 200, 200], 0),
        Polygon([31, 47, 46], [200, 200, 200], 0),
        Polygon([150, 151, 166], [200, 200, 200], 0),
        Polygon([46, 47, 62], [200, 200, 200], 0),
        Polygon([136, 137, 152], [200, 200, 200], 0),
        Polygon([136, 152, 151], [200, 200, 200], 0),
        Polygon([45, 60, 74], [200, 200, 200], 0),
        Polygon([60, 89, 74], [200, 200, 200], 0),
        Polygon([120, 149, 134], [200, 200, 200], 0),
        Polygon([120, 135, 149], [200, 200, 200], 0),
        Polygon([45, 46, 61], [200, 200, 200], 0),
        Polygon([45, 61, 60], [200, 200, 200], 0),
        Polygon([135, 151, 150], [200, 200, 200], 0),
        Polygon([75, 104, 89], [200, 200, 200], 0),
        Polygon([60, 75, 89], [200, 200, 200], 0),
        Polygon([105, 134, 119], [200, 200, 200], 0),
        Polygon([105, 120, 134], [200, 200, 200], 0),
        Polygon([46, 62, 61], [200, 200, 200], 0),
        Polygon([61, 62, 77], [200, 200, 200], 0),
        Polygon([121, 122, 137], [200, 200, 200], 0),
        Polygon([121, 137, 136], [200, 200, 200], 0),
        Polygon([135, 136, 151], [200, 200, 200], 0),
        Polygon([90, 119, 104], [200, 200, 200], 0),
        Polygon([75, 90, 104], [200, 200, 200], 0),
        Polygon([90, 105, 119], [200, 200, 200], 0),
        Polygon([76, 77, 92], [200, 200, 200], 0),
        Polygon([61, 77, 76], [200, 200, 200], 0),
        Polygon([106, 107, 122], [200, 200, 200], 0),
        Polygon([106, 122, 121], [200, 200, 200], 0),
        Polygon([60, 61, 76], [200, 200, 200], 0),
        Polygon([60, 76, 75], [200, 200, 200], 0),
        Polygon([120, 136, 135], [200, 200, 200], 0),
        Polygon([91, 92, 107], [200, 200, 200], 0),
        Polygon([76, 92, 91], [200, 200, 200], 0),
        Polygon([91, 107, 106], [200, 200, 200], 0),
        Polygon([120, 121, 136], [200, 200, 200], 0),
        Polygon([75, 76, 91], [200, 200, 200], 0),
        Polygon([75, 91, 90], [200, 200, 200], 0),
        Polygon([105, 121, 120], [200, 200, 200], 0),
        Polygon([105, 106, 121], [200, 200, 200], 0),
        Polygon([90, 106, 105], [200, 200, 200], 0),
        Polygon([90, 91, 106], [200, 200, 200], 0),
    ]
    sun_pol = [
Point( 207.89660142870974 , 0.0 , 1478.1508079608134 ),
Point( 207.89660142870974 , 24.0 , 1478.1508079608134 ),
Point( 207.89660142870974 , 48.0 , 1478.1508079608134 ),
Point( 207.89660142870974 , 72.0 , 1478.1508079608134 ),
Point( 207.89660142870974 , 96.0 , 1478.1508079608134 ),
Point( 207.89660142870974 , 120.0 , 1478.1508079608134 ),
Point( 207.89660142870974 , 144.0 , 1478.1508079608134 ),
Point( 207.89660142870974 , 168.0 , 1478.1508079608134 ),
Point( 207.89660142870974 , 192.0 , 1478.1508079608134 ),
Point( 207.89660142870974 , 216.0 , 1478.1508079608134 ),
Point( 207.89660142870974 , 240.0 , 1478.1508079608134 ),
Point( 207.89660142870974 , 264.0 , 1478.1508079608134 ),
Point( 207.89660142870974 , 288.0 , 1478.1508079608134 ),
Point( 207.89660142870974 , 312.0 , 1478.1508079608134 ),
Point( 207.89660142870974 , 336.0 , 1478.1508079608134 ),
Point( 406.7084573195993 , 0.0 , 1413.5580062287845 ),
Point( 406.7084573195993 , 24.0 , 1413.5580062287845 ),
Point( 406.7084573195993 , 48.0 , 1413.5580062287845 ),
Point( 406.7084573195993 , 72.0 , 1413.5580062287845 ),
Point( 406.7084573195993 , 96.0 , 1413.5580062287845 ),
Point( 406.7084573195993 , 120.0 , 1413.5580062287845 ),
Point( 406.7084573195993 , 144.0 , 1413.5580062287845 ),
Point( 406.7084573195993 , 168.0 , 1413.5580062287845 ),
Point( 406.7084573195993 , 192.0 , 1413.5580062287845 ),
Point( 406.7084573195993 , 216.0 , 1413.5580062287845 ),
Point( 406.7084573195993 , 240.0 , 1413.5580062287845 ),
Point( 406.7084573195993 , 264.0 , 1413.5580062287845 ),
Point( 406.7084573195993 , 288.0 , 1413.5580062287845 ),
Point( 406.7084573195993 , 312.0 , 1413.5580062287845 ),
Point( 406.7084573195993 , 336.0 , 1413.5580062287845 ),
Point( 587.7478108346144 , 0.0 , 1309.044195862697 ),
Point( 587.7478108346144 , 24.0 , 1309.044195862697 ),
Point( 587.7478108346144 , 48.0 , 1309.044195862697 ),
Point( 587.7478108346144 , 72.0 , 1309.044195862697 ),
Point( 587.7478108346144 , 96.0 , 1309.044195862697 ),
Point( 587.7478108346144 , 120.0 , 1309.044195862697 ),
Point( 587.7478108346144 , 144.0 , 1309.044195862697 ),
Point( 587.7478108346144 , 168.0 , 1309.044195862697 ),
Point( 587.7478108346144 , 192.0 , 1309.044195862697 ),
Point( 587.7478108346144 , 216.0 , 1309.044195862697 ),
Point( 587.7478108346144 , 240.0 , 1309.044195862697 ),
Point( 587.7478108346144 , 264.0 , 1309.044195862697 ),
Point( 587.7478108346144 , 288.0 , 1309.044195862697 ),
Point( 587.7478108346144 , 312.0 , 1309.044195862697 ),
Point( 587.7478108346144 , 336.0 , 1309.044195862697 ),
Point( 743.1035347705556 , 0.0 , 1169.1764614894232 ),
Point( 743.1035347705556 , 24.0 , 1169.1764614894232 ),
Point( 743.1035347705556 , 48.0 , 1169.1764614894232 ),
Point( 743.1035347705556 , 72.0 , 1169.1764614894232 ),
Point( 743.1035347705556 , 96.0 , 1169.1764614894232 ),
Point( 743.1035347705556 , 120.0 , 1169.1764614894232 ),
Point( 743.1035347705556 , 144.0 , 1169.1764614894232 ),
Point( 743.1035347705556 , 168.0 , 1169.1764614894232 ),
Point( 743.1035347705556 , 192.0 , 1169.1764614894232 ),
Point( 743.1035347705556 , 216.0 , 1169.1764614894232 ),
Point( 743.1035347705556 , 240.0 , 1169.1764614894232 ),
Point( 743.1035347705556 , 264.0 , 1169.1764614894232 ),
Point( 743.1035347705556 , 288.0 , 1169.1764614894232 ),
Point( 743.1035347705556 , 312.0 , 1169.1764614894232 ),
Point( 743.1035347705556 , 336.0 , 1169.1764614894232 ),
Point( 865.9868350340963 , 0.0 , 1000.066797085778 ),
Point( 865.9868350340963 , 24.0 , 1000.066797085778 ),
Point( 865.9868350340963 , 48.0 , 1000.066797085778 ),
Point( 865.9868350340963 , 72.0 , 1000.066797085778 ),
Point( 865.9868350340963 , 96.0 , 1000.066797085778 ),
Point( 865.9868350340963 , 120.0 , 1000.066797085778 ),
Point( 865.9868350340963 , 144.0 , 1000.066797085778 ),
Point( 865.9868350340963 , 168.0 , 1000.066797085778 ),
Point( 865.9868350340963 , 192.0 , 1000.066797085778 ),
Point( 865.9868350340963 , 216.0 , 1000.066797085778 ),
Point( 865.9868350340963 , 240.0 , 1000.066797085778 ),
Point( 865.9868350340963 , 264.0 , 1000.066797085778 ),
Point( 865.9868350340963 , 288.0 , 1000.066797085778 ),
Point( 865.9868350340963 , 312.0 , 1000.066797085778 ),
Point( 865.9868350340963 , 336.0 , 1000.066797085778 ),
Point( 951.0279099735025 , 0.0 , 809.1050217182367 ),
Point( 951.0279099735025 , 24.0 , 809.1050217182367 ),
Point( 951.0279099735025 , 48.0 , 809.1050217182367 ),
Point( 951.0279099735025 , 72.0 , 809.1050217182367 ),
Point( 951.0279099735025 , 96.0 , 809.1050217182367 ),
Point( 951.0279099735025 , 120.0 , 809.1050217182367 ),
Point( 951.0279099735025 , 144.0 , 809.1050217182367 ),
Point( 951.0279099735025 , 168.0 , 809.1050217182367 ),
Point( 951.0279099735025 , 192.0 , 809.1050217182367 ),
Point( 951.0279099735025 , 216.0 , 809.1050217182367 ),
Point( 951.0279099735025 , 240.0 , 809.1050217182367 ),
Point( 951.0279099735025 , 264.0 , 809.1050217182367 ),
Point( 951.0279099735025 , 288.0 , 809.1050217182367 ),
Point( 951.0279099735025 , 312.0 , 809.1050217182367 ),
Point( 951.0279099735025 , 336.0 , 809.1050217182367 ),
Point( 994.5106020336342 , 0.0 , 604.6358563910978 ),
Point( 994.5106020336342 , 24.0 , 604.6358563910978 ),
Point( 994.5106020336342 , 48.0 , 604.6358563910978 ),
Point( 994.5106020336342 , 72.0 , 604.6358563910978 ),
Point( 994.5106020336342 , 96.0 , 604.6358563910978 ),
Point( 994.5106020336342 , 120.0 , 604.6358563910978 ),
Point( 994.5106020336342 , 144.0 , 604.6358563910978 ),
Point( 994.5106020336342 , 168.0 , 604.6358563910978 ),
Point( 994.5106020336342 , 192.0 , 604.6358563910978 ),
Point( 994.5106020336342 , 216.0 , 604.6358563910978 ),
Point( 994.5106020336342 , 240.0 , 604.6358563910978 ),
Point( 994.5106020336342 , 264.0 , 604.6358563910978 ),
Point( 994.5106020336342 , 288.0 , 604.6358563910978 ),
Point( 994.5106020336342 , 312.0 , 604.6358563910978 ),
Point( 994.5106020336342 , 336.0 , 604.6358563910978 ),
Point( 994.534787836086 , 0.0 , 395.5942732230114 ),
Point( 994.534787836086 , 24.0 , 395.5942732230114 ),
Point( 994.534787836086 , 48.0 , 395.5942732230114 ),
Point( 994.534787836086 , 72.0 , 395.5942732230114 ),
Point( 994.534787836086 , 96.0 , 395.5942732230114 ),
Point( 994.534787836086 , 120.0 , 395.5942732230114 ),
Point( 994.534787836086 , 144.0 , 395.5942732230114 ),
Point( 994.534787836086 , 168.0 , 395.5942732230114 ),
Point( 994.534787836086 , 192.0 , 395.5942732230114 ),
Point( 994.534787836086 , 216.0 , 395.5942732230114 ),
Point( 994.534787836086 , 240.0 , 395.5942732230114 ),
Point( 994.534787836086 , 264.0 , 395.5942732230114 ),
Point( 994.534787836086 , 288.0 , 395.5942732230114 ),
Point( 994.534787836086 , 312.0 , 395.5942732230114 ),
Point( 994.534787836086 , 336.0 , 395.5942732230114 ),
Point( 951.0994105003736 , 0.0 , 191.11505160360747 ),
Point( 951.0994105003736 , 24.0 , 191.11505160360747 ),
Point( 951.0994105003736 , 48.0 , 191.11505160360747 ),
Point( 951.0994105003736 , 72.0 , 191.11505160360747 ),
Point( 951.0994105003736 , 96.0 , 191.11505160360747 ),
Point( 951.0994105003736 , 120.0 , 191.11505160360747 ),
Point( 951.0994105003736 , 144.0 , 191.11505160360747 ),
Point( 951.0994105003736 , 168.0 , 191.11505160360747 ),
Point( 951.0994105003736 , 192.0 , 191.11505160360747 ),
Point( 951.0994105003736 , 216.0 , 191.11505160360747 ),
Point( 951.0994105003736 , 240.0 , 191.11505160360747 ),
Point( 951.0994105003736 , 264.0 , 191.11505160360747 ),
Point( 951.0994105003736 , 288.0 , 191.11505160360747 ),
Point( 951.0994105003736 , 312.0 , 191.11505160360747 ),
Point( 951.0994105003736 , 336.0 , 191.11505160360747 ),
Point( 866.1025258279013 , 0.0 , 0.1336030952575129 ),
Point( 866.1025258279013 , 24.0 , 0.1336030952575129 ),
Point( 866.1025258279013 , 48.0 , 0.1336030952575129 ),
Point( 866.1025258279013 , 72.0 , 0.1336030952575129 ),
Point( 866.1025258279013 , 96.0 , 0.1336030952575129 ),
Point( 866.1025258279013 , 120.0 , 0.1336030952575129 ),
Point( 866.1025258279013 , 144.0 , 0.1336030952575129 ),
Point( 866.1025258279013 , 168.0 , 0.1336030952575129 ),
Point( 866.1025258279013 , 192.0 , 0.1336030952575129 ),
Point( 866.1025258279013 , 216.0 , 0.1336030952575129 ),
Point( 866.1025258279013 , 240.0 , 0.1336030952575129 ),
Point( 866.1025258279013 , 264.0 , 0.1336030952575129 ),
Point( 866.1025258279013 , 288.0 , 0.1336030952575129 ),
Point( 866.1025258279013 , 312.0 , 0.1336030952575129 ),
Point( 866.1025258279013 , 336.0 , 0.1336030952575129 ),
Point( 743.2583603305524 , 0.0 , -169.00449161327674 ),
Point( 743.2583603305524 , 24.0 , -169.00449161327674 ),
Point( 743.2583603305524 , 48.0 , -169.00449161327674 ),
Point( 743.2583603305524 , 72.0 , -169.00449161327674 ),
Point( 743.2583603305524 , 96.0 , -169.00449161327674 ),
Point( 743.2583603305524 , 120.0 , -169.00449161327674 ),
Point( 743.2583603305524 , 144.0 , -169.00449161327674 ),
Point( 743.2583603305524 , 168.0 , -169.00449161327674 ),
Point( 743.2583603305524 , 192.0 , -169.00449161327674 ),
Point( 743.2583603305524 , 216.0 , -169.00449161327674 ),
Point( 743.2583603305524 , 240.0 , -169.00449161327674 ),
Point( 743.2583603305524 , 264.0 , -169.00449161327674 ),
Point( 743.2583603305524 , 288.0 , -169.00449161327674 ),
Point( 743.2583603305524 , 312.0 , -169.00449161327674 ),
Point( 743.2583603305524 , 336.0 , -169.00449161327674 ),
Point( 587.9350055340175 , 0.0 , -308.9081710971369 ),
Point( 587.9350055340175 , 24.0 , -308.9081710971369 ),
Point( 587.9350055340175 , 48.0 , -308.9081710971369 ),
Point( 587.9350055340175 , 72.0 , -308.9081710971369 ),
Point( 587.9350055340175 , 96.0 , -308.9081710971369 ),
Point( 587.9350055340175 , 120.0 , -308.9081710971369 ),
Point( 587.9350055340175 , 144.0 , -308.9081710971369 ),
Point( 587.9350055340175 , 168.0 , -308.9081710971369 ),
Point( 587.9350055340175 , 192.0 , -308.9081710971369 ),
Point( 587.9350055340175 , 216.0 , -308.9081710971369 ),
Point( 587.9350055340175 , 240.0 , -308.9081710971369 ),
Point( 587.9350055340175 , 264.0 , -308.9081710971369 ),
Point( 587.9350055340175 , 288.0 , -308.9081710971369 ),
Point( 587.9350055340175 , 312.0 , -308.9081710971369 ),
Point( 587.9350055340175 , 336.0 , -308.9081710971369 ),
Point( 406.91984105253624 , 0.0 , -413.46387063626037 ),
Point( 406.91984105253624 , 24.0 , -413.46387063626037 ),
Point( 406.91984105253624 , 48.0 , -413.46387063626037 ),
Point( 406.91984105253624 , 72.0 , -413.46387063626037 ),
Point( 406.91984105253624 , 96.0 , -413.46387063626037 ),
Point( 406.91984105253624 , 120.0 , -413.46387063626037 ),
Point( 406.91984105253624 , 144.0 , -413.46387063626037 ),
Point( 406.91984105253624 , 168.0 , -413.46387063626037 ),
Point( 406.91984105253624 , 192.0 , -413.46387063626037 ),
Point( 406.91984105253624 , 216.0 , -413.46387063626037 ),
Point( 406.91984105253624 , 240.0 , -413.46387063626037 ),
Point( 406.91984105253624 , 264.0 , -413.46387063626037 ),
Point( 406.91984105253624 , 288.0 , -413.46387063626037 ),
Point( 406.91984105253624 , 312.0 , -413.46387063626037 ),
Point( 406.91984105253624 , 336.0 , -413.46387063626037 ),
Point( 208.12293706763126 , 0.0 , -478.10267511460313 ),
Point( 208.12293706763126 , 24.0 , -478.10267511460313 ),
Point( 208.12293706763126 , 48.0 , -478.10267511460313 ),
Point( 208.12293706763126 , 72.0 , -478.10267511460313 ),
Point( 208.12293706763126 , 96.0 , -478.10267511460313 ),
Point( 208.12293706763126 , 120.0 , -478.10267511460313 ),
Point( 208.12293706763126 , 144.0 , -478.10267511460313 ),
Point( 208.12293706763126 , 168.0 , -478.10267511460313 ),
Point( 208.12293706763126 , 192.0 , -478.10267511460313 ),
Point( 208.12293706763126 , 216.0 , -478.10267511460313 ),
Point( 208.12293706763126 , 240.0 , -478.10267511460313 ),
Point( 208.12293706763126 , 264.0 , -478.10267511460313 ),
Point( 208.12293706763126 , 288.0 , -478.10267511460313 ),
Point( 208.12293706763126 , 312.0 , -478.10267511460313 ),
Point( 208.12293706763126 , 336.0 , -478.10267511460313 ),
Point( 0.23139704322540597 , 0.0 , -499.9999732277039 ),
Point( 0.23139704322540597 , 24.0 , -499.9999732277039 ),
Point( 0.23139704322540597 , 48.0 , -499.9999732277039 ),
Point( 0.23139704322540597 , 72.0 , -499.9999732277039 ),
Point( 0.23139704322540597 , 96.0 , -499.9999732277039 ),
Point( 0.23139704322540597 , 120.0 , -499.9999732277039 ),
Point( 0.23139704322540597 , 144.0 , -499.9999732277039 ),
Point( 0.23139704322540597 , 168.0 , -499.9999732277039 ),
Point( 0.23139704322540597 , 192.0 , -499.9999732277039 ),
Point( 0.23139704322540597 , 216.0 , -499.9999732277039 ),
Point( 0.23139704322540597 , 240.0 , -499.9999732277039 ),
Point( 0.23139704322540597 , 264.0 , -499.9999732277039 ),
Point( 0.23139704322540597 , 288.0 , -499.9999732277039 ),
Point( 0.23139704322540597 , 312.0 , -499.9999732277039 ),
Point( 0.23139704322540597 , 336.0 , -499.9999732277039 ),
]
    sun_poly = [
        Polygon([98, 114, 113], [200, 200, 0], 0),
        Polygon([97, 98, 113], [200, 200, 0], 0),
        Polygon([113, 129, 128], [200, 200, 0], 0),
        Polygon([113, 114, 129], [200, 200, 0], 0),
        Polygon([112, 113, 128], [200, 200, 0], 0),
        Polygon([97, 113, 112], [200, 200, 0], 0),
        Polygon([83, 99, 98], [200, 200, 0], 0),
        Polygon([98, 99, 114], [200, 200, 0], 0),
        Polygon([82, 83, 98], [200, 200, 0], 0),
        Polygon([82, 98, 97], [200, 200, 0], 0),
        Polygon([112, 128, 127], [200, 200, 0], 0),
        Polygon([128, 129, 144], [200, 200, 0], 0),
        Polygon([127, 128, 143], [200, 200, 0], 0),
        Polygon([128, 144, 143], [200, 200, 0], 0),
        Polygon([83, 84, 99], [200, 200, 0], 0),
        Polygon([68, 84, 83], [200, 200, 0], 0),
        Polygon([67, 68, 83], [200, 200, 0], 0),
        Polygon([67, 83, 82], [200, 200, 0], 0),
        Polygon([99, 115, 114], [200, 200, 0], 0),
        Polygon([114, 130, 129], [200, 200, 0], 0),
        Polygon([114, 115, 130], [200, 200, 0], 0),
        Polygon([84, 100, 99], [200, 200, 0], 0),
        Polygon([99, 100, 115], [200, 200, 0], 0),
        Polygon([129, 145, 144], [200, 200, 0], 0),
        Polygon([129, 130, 145], [200, 200, 0], 0),
        Polygon([68, 69, 84], [200, 200, 0], 0),
        Polygon([69, 85, 84], [200, 200, 0], 0),
        Polygon([84, 85, 100], [200, 200, 0], 0),
        Polygon([96, 97, 112], [200, 200, 0], 0),
        Polygon([111, 112, 127], [200, 200, 0], 0),
        Polygon([96, 112, 111], [200, 200, 0], 0),
        Polygon([81, 82, 97], [200, 200, 0], 0),
        Polygon([81, 97, 96], [200, 200, 0], 0),
        Polygon([127, 143, 142], [200, 200, 0], 0),
        Polygon([143, 144, 159], [200, 200, 0], 0),
        Polygon([142, 143, 158], [200, 200, 0], 0),
        Polygon([143, 159, 158], [200, 200, 0], 0),
        Polygon([53, 69, 68], [200, 200, 0], 0),
        Polygon([52, 68, 67], [200, 200, 0], 0),
        Polygon([52, 53, 68], [200, 200, 0], 0),
        Polygon([126, 127, 142], [200, 200, 0], 0),
        Polygon([111, 127, 126], [200, 200, 0], 0),
        Polygon([66, 67, 82], [200, 200, 0], 0),
        Polygon([66, 82, 81], [200, 200, 0], 0),
        Polygon([144, 160, 159], [200, 200, 0], 0),
        Polygon([144, 145, 160], [200, 200, 0], 0),
        Polygon([53, 54, 69], [200, 200, 0], 0),
        Polygon([54, 70, 69], [200, 200, 0], 0),
        Polygon([69, 70, 85], [200, 200, 0], 0),
        Polygon([142, 158, 157], [200, 200, 0], 0),
        Polygon([141, 142, 157], [200, 200, 0], 0),
        Polygon([126, 142, 141], [200, 200, 0], 0),
        Polygon([51, 52, 67], [200, 200, 0], 0),
        Polygon([51, 67, 66], [200, 200, 0], 0),
        Polygon([158, 159, 174], [200, 200, 0], 0),
        Polygon([157, 158, 173], [200, 200, 0], 0),
        Polygon([158, 174, 173], [200, 200, 0], 0),
        Polygon([38, 54, 53], [200, 200, 0], 0),
        Polygon([37, 53, 52], [200, 200, 0], 0),
        Polygon([37, 38, 53], [200, 200, 0], 0),
        Polygon([100, 116, 115], [200, 200, 0], 0),
        Polygon([115, 131, 130], [200, 200, 0], 0),
        Polygon([115, 116, 131], [200, 200, 0], 0),
        Polygon([85, 101, 100], [200, 200, 0], 0),
        Polygon([100, 101, 116], [200, 200, 0], 0),
        Polygon([159, 175, 174], [200, 200, 0], 0),
        Polygon([159, 160, 175], [200, 200, 0], 0),
        Polygon([54, 55, 70], [200, 200, 0], 0),
        Polygon([38, 39, 54], [200, 200, 0], 0),
        Polygon([39, 55, 54], [200, 200, 0], 0),
        Polygon([130, 146, 145], [200, 200, 0], 0),
        Polygon([130, 131, 146], [200, 200, 0], 0),
        Polygon([70, 86, 85], [200, 200, 0], 0),
        Polygon([85, 86, 101], [200, 200, 0], 0),
        Polygon([157, 173, 172], [200, 200, 0], 0),
        Polygon([141, 157, 156], [200, 200, 0], 0),
        Polygon([156, 157, 172], [200, 200, 0], 0),
        Polygon([36, 37, 52], [200, 200, 0], 0),
        Polygon([36, 52, 51], [200, 200, 0], 0),
        Polygon([145, 161, 160], [200, 200, 0], 0),
        Polygon([145, 146, 161], [200, 200, 0], 0),
        Polygon([55, 71, 70], [200, 200, 0], 0),
        Polygon([70, 71, 86], [200, 200, 0], 0),
        Polygon([95, 96, 111], [200, 200, 0], 0),
        Polygon([110, 111, 126], [200, 200, 0], 0),
        Polygon([95, 111, 110], [200, 200, 0], 0),
        Polygon([80, 81, 96], [200, 200, 0], 0),
        Polygon([80, 96, 95], [200, 200, 0], 0),
        Polygon([173, 174, 189], [200, 200, 0], 0),
        Polygon([172, 173, 188], [200, 200, 0], 0),
        Polygon([173, 189, 188], [200, 200, 0], 0),
        Polygon([23, 39, 38], [200, 200, 0], 0),
        Polygon([22, 38, 37], [200, 200, 0], 0),
        Polygon([22, 23, 38], [200, 200, 0], 0),
        Polygon([125, 126, 141], [200, 200, 0], 0),
        Polygon([110, 126, 125], [200, 200, 0], 0),
        Polygon([65, 66, 81], [200, 200, 0], 0),
        Polygon([65, 81, 80], [200, 200, 0], 0),
        Polygon([174, 175, 190], [200, 200, 0], 0),
        Polygon([174, 190, 189], [200, 200, 0], 0),
        Polygon([39, 40, 55], [200, 200, 0], 0),
        Polygon([24, 40, 39], [200, 200, 0], 0),
        Polygon([23, 24, 39], [200, 200, 0], 0),
        Polygon([160, 176, 175], [200, 200, 0], 0),
        Polygon([160, 161, 176], [200, 200, 0], 0),
        Polygon([40, 56, 55], [200, 200, 0], 0),
        Polygon([55, 56, 71], [200, 200, 0], 0),
        Polygon([140, 141, 156], [200, 200, 0], 0),
        Polygon([125, 141, 140], [200, 200, 0], 0),
        Polygon([50, 51, 66], [200, 200, 0], 0),
        Polygon([50, 66, 65], [200, 200, 0], 0),
        Polygon([156, 172, 171], [200, 200, 0], 0),
        Polygon([172, 188, 187], [200, 200, 0], 0),
        Polygon([171, 172, 187], [200, 200, 0], 0),
        Polygon([21, 37, 36], [200, 200, 0], 0),
        Polygon([21, 22, 37], [200, 200, 0], 0),
        Polygon([155, 156, 171], [200, 200, 0], 0),
        Polygon([140, 156, 155], [200, 200, 0], 0),
        Polygon([35, 36, 51], [200, 200, 0], 0),
        Polygon([35, 51, 50], [200, 200, 0], 0),
        Polygon([175, 191, 190], [200, 200, 0], 0),
        Polygon([175, 176, 191], [200, 200, 0], 0),
        Polygon([24, 25, 40], [200, 200, 0], 0),
        Polygon([25, 41, 40], [200, 200, 0], 0),
        Polygon([40, 41, 56], [200, 200, 0], 0),
        Polygon([188, 189, 204], [200, 200, 0], 0),
        Polygon([187, 188, 203], [200, 200, 0], 0),
        Polygon([188, 204, 203], [200, 200, 0], 0),
        Polygon([8, 24, 23], [200, 200, 0], 0),
        Polygon([7, 23, 22], [200, 200, 0], 0),
        Polygon([7, 8, 23], [200, 200, 0], 0),
        Polygon([189, 190, 205], [200, 200, 0], 0),
        Polygon([189, 205, 204], [200, 200, 0], 0),
        Polygon([9, 25, 24], [200, 200, 0], 0),
        Polygon([8, 9, 24], [200, 200, 0], 0),
        Polygon([101, 117, 116], [200, 200, 0], 0),
        Polygon([116, 132, 131], [200, 200, 0], 0),
        Polygon([116, 117, 132], [200, 200, 0], 0),
        Polygon([86, 102, 101], [200, 200, 0], 0),
        Polygon([101, 102, 117], [200, 200, 0], 0),
        Polygon([171, 187, 186], [200, 200, 0], 0),
        Polygon([170, 171, 186], [200, 200, 0], 0),
        Polygon([155, 171, 170], [200, 200, 0], 0),
        Polygon([20, 21, 36], [200, 200, 0], 0),
        Polygon([20, 36, 35], [200, 200, 0], 0),
        Polygon([186, 187, 202], [200, 200, 0], 0),
        Polygon([187, 203, 202], [200, 200, 0], 0),
        Polygon([6, 22, 21], [200, 200, 0], 0),
        Polygon([6, 7, 22], [200, 200, 0], 0),
        Polygon([131, 147, 146], [200, 200, 0], 0),
        Polygon([131, 132, 147], [200, 200, 0], 0),
        Polygon([71, 87, 86], [200, 200, 0], 0),
        Polygon([86, 87, 102], [200, 200, 0], 0),
        Polygon([146, 162, 161], [200, 200, 0], 0),
        Polygon([146, 147, 162], [200, 200, 0], 0),
        Polygon([56, 72, 71], [200, 200, 0], 0),
        Polygon([71, 72, 87], [200, 200, 0], 0),
        Polygon([190, 191, 206], [200, 200, 0], 0),
        Polygon([190, 206, 205], [200, 200, 0], 0),
        Polygon([25, 26, 41], [200, 200, 0], 0),
        Polygon([9, 10, 25], [200, 200, 0], 0),
        Polygon([10, 26, 25], [200, 200, 0], 0),
        Polygon([161, 177, 176], [200, 200, 0], 0),
        Polygon([161, 162, 177], [200, 200, 0], 0),
        Polygon([41, 57, 56], [200, 200, 0], 0),
        Polygon([56, 57, 72], [200, 200, 0], 0),
        Polygon([186, 202, 201], [200, 200, 0], 0),
        Polygon([170, 186, 185], [200, 200, 0], 0),
        Polygon([185, 186, 201], [200, 200, 0], 0),
        Polygon([5, 6, 21], [200, 200, 0], 0),
        Polygon([5, 21, 20], [200, 200, 0], 0),
        Polygon([94, 95, 110], [200, 200, 0], 0),
        Polygon([109, 110, 125], [200, 200, 0], 0),
        Polygon([94, 110, 109], [200, 200, 0], 0),
        Polygon([79, 80, 95], [200, 200, 0], 0),
        Polygon([79, 95, 94], [200, 200, 0], 0),
        Polygon([124, 125, 140], [200, 200, 0], 0),
        Polygon([109, 125, 124], [200, 200, 0], 0),
        Polygon([64, 65, 80], [200, 200, 0], 0),
        Polygon([64, 80, 79], [200, 200, 0], 0),
        Polygon([176, 192, 191], [200, 200, 0], 0),
        Polygon([176, 177, 192], [200, 200, 0], 0),
        Polygon([26, 42, 41], [200, 200, 0], 0),
        Polygon([41, 42, 57], [200, 200, 0], 0),
        Polygon([139, 140, 155], [200, 200, 0], 0),
        Polygon([124, 140, 139], [200, 200, 0], 0),
        Polygon([49, 50, 65], [200, 200, 0], 0),
        Polygon([49, 65, 64], [200, 200, 0], 0),
        Polygon([203, 204, 219], [200, 200, 0], 0),
        Polygon([202, 203, 218], [200, 200, 0], 0),
        Polygon([203, 219, 218], [200, 200, 0], 0),
        Polygon([204, 205, 220], [200, 200, 0], 0),
        Polygon([204, 220, 219], [200, 200, 0], 0),
        Polygon([201, 202, 217], [200, 200, 0], 0),
        Polygon([202, 218, 217], [200, 200, 0], 0),
        Polygon([154, 155, 170], [200, 200, 0], 0),
        Polygon([139, 155, 154], [200, 200, 0], 0),
        Polygon([34, 35, 50], [200, 200, 0], 0),
        Polygon([34, 50, 49], [200, 200, 0], 0),
        Polygon([191, 207, 206], [200, 200, 0], 0),
        Polygon([191, 192, 207], [200, 200, 0], 0),
        Polygon([10, 11, 26], [200, 200, 0], 0),
        Polygon([11, 27, 26], [200, 200, 0], 0),
        Polygon([26, 27, 42], [200, 200, 0], 0),
        Polygon([205, 206, 221], [200, 200, 0], 0),
        Polygon([205, 221, 220], [200, 200, 0], 0),
        Polygon([169, 170, 185], [200, 200, 0], 0),
        Polygon([154, 170, 169], [200, 200, 0], 0),
        Polygon([19, 20, 35], [200, 200, 0], 0),
        Polygon([19, 35, 34], [200, 200, 0], 0),
        Polygon([185, 201, 200], [200, 200, 0], 0),
        Polygon([200, 201, 216], [200, 200, 0], 0),
        Polygon([201, 217, 216], [200, 200, 0], 0),
        Polygon([184, 185, 200], [200, 200, 0], 0),
        Polygon([169, 185, 184], [200, 200, 0], 0),
        Polygon([4, 5, 20], [200, 200, 0], 0),
        Polygon([4, 20, 19], [200, 200, 0], 0),
        Polygon([206, 222, 221], [200, 200, 0], 0),
        Polygon([206, 207, 222], [200, 200, 0], 0),
        Polygon([11, 12, 27], [200, 200, 0], 0),
        Polygon([200, 216, 215], [200, 200, 0], 0),
        Polygon([199, 200, 215], [200, 200, 0], 0),
        Polygon([184, 200, 199], [200, 200, 0], 0),
        Polygon([199, 215, 214], [200, 200, 0], 0),
        Polygon([207, 223, 222], [200, 200, 0], 0),
        Polygon([198, 214, 213], [200, 200, 0], 0),
        Polygon([198, 199, 214], [200, 200, 0], 0),
        Polygon([208, 224, 223], [200, 200, 0], 0),
        Polygon([207, 208, 223], [200, 200, 0], 0),
        Polygon([197, 213, 212], [200, 200, 0], 0),
        Polygon([197, 198, 213], [200, 200, 0], 0),
        Polygon([195, 210, 224], [200, 200, 0], 0),
        Polygon([208, 209, 224], [200, 200, 0], 0),
        Polygon([195, 224, 209], [200, 200, 0], 0),
        Polygon([196, 212, 211], [200, 200, 0], 0),
        Polygon([196, 197, 212], [200, 200, 0], 0),
        Polygon([195, 211, 210], [200, 200, 0], 0),
        Polygon([195, 196, 211], [200, 200, 0], 0),
        Polygon([12, 28, 27], [200, 200, 0], 0),
        Polygon([12, 13, 28], [200, 200, 0], 0),
        Polygon([192, 208, 207], [200, 200, 0], 0),
        Polygon([27, 43, 42], [200, 200, 0], 0),
        Polygon([27, 28, 43], [200, 200, 0], 0),
        Polygon([177, 193, 192], [200, 200, 0], 0),
        Polygon([192, 193, 208], [200, 200, 0], 0),
        Polygon([42, 58, 57], [200, 200, 0], 0),
        Polygon([42, 43, 58], [200, 200, 0], 0),
        Polygon([162, 178, 177], [200, 200, 0], 0),
        Polygon([177, 178, 193], [200, 200, 0], 0),
        Polygon([57, 73, 72], [200, 200, 0], 0),
        Polygon([57, 58, 73], [200, 200, 0], 0),
        Polygon([147, 163, 162], [200, 200, 0], 0),
        Polygon([162, 163, 178], [200, 200, 0], 0),
        Polygon([72, 88, 87], [200, 200, 0], 0),
        Polygon([72, 73, 88], [200, 200, 0], 0),
        Polygon([132, 148, 147], [200, 200, 0], 0),
        Polygon([147, 148, 163], [200, 200, 0], 0),
        Polygon([87, 103, 102], [200, 200, 0], 0),
        Polygon([87, 88, 103], [200, 200, 0], 0),
        Polygon([117, 133, 132], [200, 200, 0], 0),
        Polygon([132, 133, 148], [200, 200, 0], 0),
        Polygon([102, 118, 117], [200, 200, 0], 0),
        Polygon([102, 103, 118], [200, 200, 0], 0),
        Polygon([117, 118, 133], [200, 200, 0], 0),
        Polygon([3, 4, 19], [200, 200, 0], 0),
        Polygon([183, 184, 199], [200, 200, 0], 0),
        Polygon([183, 199, 198], [200, 200, 0], 0),
        Polygon([18, 19, 34], [200, 200, 0], 0),
        Polygon([3, 19, 18], [200, 200, 0], 0),
        Polygon([168, 169, 184], [200, 200, 0], 0),
        Polygon([168, 184, 183], [200, 200, 0], 0),
        Polygon([13, 14, 29], [200, 200, 0], 0),
        Polygon([13, 29, 28], [200, 200, 0], 0),
        Polygon([193, 209, 208], [200, 200, 0], 0),
        Polygon([33, 34, 49], [200, 200, 0], 0),
        Polygon([18, 34, 33], [200, 200, 0], 0),
        Polygon([153, 154, 169], [200, 200, 0], 0),
        Polygon([153, 169, 168], [200, 200, 0], 0),
        Polygon([2, 3, 18], [200, 200, 0], 0),
        Polygon([182, 198, 197], [200, 200, 0], 0),
        Polygon([182, 183, 198], [200, 200, 0], 0),
        Polygon([48, 49, 64], [200, 200, 0], 0),
        Polygon([33, 49, 48], [200, 200, 0], 0),
        Polygon([138, 139, 154], [200, 200, 0], 0),
        Polygon([138, 154, 153], [200, 200, 0], 0),
        Polygon([63, 64, 79], [200, 200, 0], 0),
        Polygon([48, 64, 63], [200, 200, 0], 0),
        Polygon([123, 124, 139], [200, 200, 0], 0),
        Polygon([123, 139, 138], [200, 200, 0], 0),
        Polygon([0, 29, 14], [200, 200, 0], 0),
        Polygon([193, 194, 209], [200, 200, 0], 0),
        Polygon([180, 195, 209], [200, 200, 0], 0),
        Polygon([180, 209, 194], [200, 200, 0], 0),
        Polygon([78, 79, 94], [200, 200, 0], 0),
        Polygon([63, 79, 78], [200, 200, 0], 0),
        Polygon([108, 109, 124], [200, 200, 0], 0),
        Polygon([108, 124, 123], [200, 200, 0], 0),
        Polygon([93, 94, 109], [200, 200, 0], 0),
        Polygon([78, 94, 93], [200, 200, 0], 0),
        Polygon([93, 109, 108], [200, 200, 0], 0),
        Polygon([1, 2, 17], [200, 200, 0], 0),
        Polygon([2, 18, 17], [200, 200, 0], 0),
        Polygon([181, 197, 196], [200, 200, 0], 0),
        Polygon([181, 182, 197], [200, 200, 0], 0),
        Polygon([28, 44, 43], [200, 200, 0], 0),
        Polygon([28, 29, 44], [200, 200, 0], 0),
        Polygon([178, 194, 193], [200, 200, 0], 0),
        Polygon([0, 1, 16], [200, 200, 0], 0),
        Polygon([0, 15, 29], [200, 200, 0], 0),
        Polygon([0, 16, 15], [200, 200, 0], 0),
        Polygon([180, 196, 195], [200, 200, 0], 0),
        Polygon([1, 17, 16], [200, 200, 0], 0),
        Polygon([180, 181, 196], [200, 200, 0], 0),
        Polygon([17, 18, 33], [200, 200, 0], 0),
        Polygon([167, 168, 183], [200, 200, 0], 0),
        Polygon([167, 183, 182], [200, 200, 0], 0),
        Polygon([43, 59, 58], [200, 200, 0], 0),
        Polygon([43, 44, 59], [200, 200, 0], 0),
        Polygon([178, 179, 194], [200, 200, 0], 0),
        Polygon([163, 179, 178], [200, 200, 0], 0),
        Polygon([15, 44, 29], [200, 200, 0], 0),
        Polygon([165, 180, 194], [200, 200, 0], 0),
        Polygon([165, 194, 179], [200, 200, 0], 0),
        Polygon([58, 74, 73], [200, 200, 0], 0),
        Polygon([58, 59, 74], [200, 200, 0], 0),
        Polygon([148, 164, 163], [200, 200, 0], 0),
        Polygon([163, 164, 179], [200, 200, 0], 0),
        Polygon([17, 33, 32], [200, 200, 0], 0),
        Polygon([32, 33, 48], [200, 200, 0], 0),
        Polygon([152, 153, 168], [200, 200, 0], 0),
        Polygon([152, 168, 167], [200, 200, 0], 0),
        Polygon([16, 17, 32], [200, 200, 0], 0),
        Polygon([166, 182, 181], [200, 200, 0], 0),
        Polygon([166, 167, 182], [200, 200, 0], 0),
        Polygon([73, 89, 88], [200, 200, 0], 0),
        Polygon([73, 74, 89], [200, 200, 0], 0),
        Polygon([133, 149, 148], [200, 200, 0], 0),
        Polygon([148, 149, 164], [200, 200, 0], 0),
        Polygon([15, 16, 31], [200, 200, 0], 0),
        Polygon([15, 30, 44], [200, 200, 0], 0),
        Polygon([15, 31, 30], [200, 200, 0], 0),
        Polygon([165, 181, 180], [200, 200, 0], 0),
        Polygon([16, 32, 31], [200, 200, 0], 0),
        Polygon([165, 166, 181], [200, 200, 0], 0),
        Polygon([47, 48, 63], [200, 200, 0], 0),
        Polygon([32, 48, 47], [200, 200, 0], 0),
        Polygon([137, 138, 153], [200, 200, 0], 0),
        Polygon([137, 153, 152], [200, 200, 0], 0),
        Polygon([88, 104, 103], [200, 200, 0], 0),
        Polygon([88, 89, 104], [200, 200, 0], 0),
        Polygon([118, 134, 133], [200, 200, 0], 0),
        Polygon([133, 134, 149], [200, 200, 0], 0),
        Polygon([103, 119, 118], [200, 200, 0], 0),
        Polygon([103, 104, 119], [200, 200, 0], 0),
        Polygon([118, 119, 134], [200, 200, 0], 0),
        Polygon([30, 59, 44], [200, 200, 0], 0),
        Polygon([150, 165, 179], [200, 200, 0], 0),
        Polygon([150, 179, 164], [200, 200, 0], 0),
        Polygon([62, 63, 78], [200, 200, 0], 0),
        Polygon([47, 63, 62], [200, 200, 0], 0),
        Polygon([122, 123, 138], [200, 200, 0], 0),
        Polygon([122, 138, 137], [200, 200, 0], 0),
        Polygon([31, 32, 47], [200, 200, 0], 0),
        Polygon([151, 167, 166], [200, 200, 0], 0),
        Polygon([151, 152, 167], [200, 200, 0], 0),
        Polygon([77, 78, 93], [200, 200, 0], 0),
        Polygon([62, 78, 77], [200, 200, 0], 0),
        Polygon([107, 108, 123], [200, 200, 0], 0),
        Polygon([107, 123, 122], [200, 200, 0], 0),
        Polygon([92, 93, 108], [200, 200, 0], 0),
        Polygon([77, 93, 92], [200, 200, 0], 0),
        Polygon([92, 108, 107], [200, 200, 0], 0),
        Polygon([30, 45, 59], [200, 200, 0], 0),
        Polygon([30, 31, 46], [200, 200, 0], 0),
        Polygon([30, 46, 45], [200, 200, 0], 0),
        Polygon([150, 166, 165], [200, 200, 0], 0),
        Polygon([45, 74, 59], [200, 200, 0], 0),
        Polygon([135, 164, 149], [200, 200, 0], 0),
        Polygon([135, 150, 164], [200, 200, 0], 0),
        Polygon([31, 47, 46], [200, 200, 0], 0),
        Polygon([150, 151, 166], [200, 200, 0], 0),
        Polygon([46, 47, 62], [200, 200, 0], 0),
        Polygon([136, 137, 152], [200, 200, 0], 0),
        Polygon([136, 152, 151], [200, 200, 0], 0),
        Polygon([45, 60, 74], [200, 200, 0], 0),
        Polygon([60, 89, 74], [200, 200, 0], 0),
        Polygon([120, 149, 134], [200, 200, 0], 0),
        Polygon([120, 135, 149], [200, 200, 0], 0),
        Polygon([45, 46, 61], [200, 200, 0], 0),
        Polygon([45, 61, 60], [200, 200, 0], 0),
        Polygon([135, 151, 150], [200, 200, 0], 0),
        Polygon([75, 104, 89], [200, 200, 0], 0),
        Polygon([60, 75, 89], [200, 200, 0], 0),
        Polygon([105, 134, 119], [200, 200, 0], 0),
        Polygon([105, 120, 134], [200, 200, 0], 0),
        Polygon([46, 62, 61], [200, 200, 0], 0),
        Polygon([61, 62, 77], [200, 200, 0], 0),
        Polygon([121, 122, 137], [200, 200, 0], 0),
        Polygon([121, 137, 136], [200, 200, 0], 0),
        Polygon([135, 136, 151], [200, 200, 0], 0),
        Polygon([90, 119, 104], [200, 200, 0], 0),
        Polygon([75, 90, 104], [200, 200, 0], 0),
        Polygon([90, 105, 119], [200, 200, 0], 0),
        Polygon([76, 77, 92], [200, 200, 0], 0),
        Polygon([61, 77, 76], [200, 200, 0], 0),
        Polygon([106, 107, 122], [200, 200, 0], 0),
        Polygon([106, 122, 121], [200, 200, 0], 0),
        Polygon([60, 61, 76], [200, 200, 0], 0),
        Polygon([60, 76, 75], [200, 200, 0], 0),
        Polygon([120, 136, 135], [200, 200, 0], 0),
        Polygon([91, 92, 107], [200, 200, 0], 0),
        Polygon([76, 92, 91], [200, 200, 0], 0),
        Polygon([91, 107, 106], [200, 200, 0], 0),
        Polygon([120, 121, 136], [200, 200, 0], 0),
        Polygon([75, 76, 91], [200, 200, 0], 0),
        Polygon([75, 91, 90], [200, 200, 0], 0),
        Polygon([105, 121, 120], [200, 200, 0], 0),
        Polygon([105, 106, 121], [200, 200, 0], 0),
        Polygon([90, 106, 105], [200, 200, 0], 0),
        Polygon([90, 91, 106], [200, 200, 0], 0),
    ]

    # phis
    sim = pyphicus.Simulation()

    sim.load_settings("Phis_rul\\set_6")

    throw_pwr = 20
    # /phis

    hands = 0  # Object(x, y, polyw, polw, 0, 1, uolid)
    hands_x = 0
    hands_y = 0
    hands_id = None

    objects = []

    xc = 0
    yc = 0
    sim.add_object(pyphicus.Object(xc, yc, 2, 100, sim, z=0))
    print(sim.map[-1][2].energy)
    objects.append([xc, yc, Object(xc, yc, sun_poly, sun_pol, -800, 1, uolid, "солнце"), 1])

    for h in range(3):
        xc = random.randint(500, 2700)
        yc = random.randint(500, 2700)
        sim.add_object(pyphicus.Object(xc, yc, 1, 100, sim, z = -(random.randint(0,400))))
        print(sim.map[-1][2].energy)
        objects.append([xc, yc, Object(xc, yc, sph_poly, sph_pol, -800, 1, uolid, "шарик"), 1])

    print(len(sim.map))

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
    lights = [Light_object(1, 1, [0.5, 0.5, 0], 10)]
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

        try:
            map = distribution_buffer_func(map,x,y)
        except:
            pass

        screen.fill([0, 0, 0])
        color_wund = [60, 220, 60]

        # костёр
        '''if lights[0].color[0] >= 0.5:
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
        lights[0].color[1] += green_dir * random.randint(1, 2) * 0.01'''

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
