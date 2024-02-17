import random
import math
from numba import njit, prange
import numba

@njit(fastmath=True, cache=True)
def get_dist_sph(x,y,z,r,x1,y1,z1):
    return ((x - x1) ** 2 + (y - y1) ** 2 + (z - z1) ** 2) ** 0.5 - r

@njit(fastmath=True, cache=True)
def get_dist_rect(x,y,z,xcr,ycr,zcr,hsx,hsy,hsz):
    return max(max(abs(ycr - y) - hsy,abs(xcr - x) - hsx),abs(zcr - z) - hsz)

@njit(fastmath=True, cache=True)
def get_dist_rect_h_z(x,y,z,xcr,ycr,zcr,hsx,hsy,hsz, r):
    return max(get_dist_rect(x,y,z,xcr,ycr,zcr,hsx,hsy,hsz),-get_dist_rect(x,y,z,xcr,ycr,zcr,hsx-r,hsy-r,hsz+12))

@njit(fastmath=True, cache=True)
def get_dist_rect_h_y(x,y,z,xcr,ycr,zcr,hsx,hsy,hsz, r):
    return max(get_dist_rect(x,y,z,xcr,ycr,zcr,hsx,hsy,hsz),-get_dist_rect(x,y,z,xcr,ycr,zcr,hsx-r,hsy+12,hsz-r))

@njit(fastmath=True, cache=True)
def get_dist_rect_h_x(x,y,z,xcr,ycr,zcr,hsx,hsy,hsz, r):
    return max(get_dist_rect(x,y,z,xcr,ycr,zcr,hsx,hsy,hsz),-get_dist_rect(x,y,z,xcr,ycr,zcr,hsx+12,hsy-r,hsz-r))

@njit(fastmath=True, cache=True)
def get_dist_tor_z(x,y,z,xt,yt,zt,r,hs,ri):
    return max(get_dist_cyl_z(x,y,z,xt,yt,zt,r,hs),-get_dist_cyl_z(x,y,z,xt,yt,zt,ri,hs+12))

@njit(fastmath=True, cache=True)
def get_dist_tor_x(x,y,z,xt,yt,zt,r,hs,ri):
    return max(get_dist_cyl_x(x,y,z,xt,yt,zt,r,hs),-get_dist_cyl_x(x,y,z,xt,yt,zt,ri,hs+12))

@njit(fastmath=True, cache=True)
def get_dist_tor_y(x,y,z,xt,yt,zt,r,hs,ri):
    return max(get_dist_cyl_y(x,y,z,xt,yt,zt,r,hs),-get_dist_cyl_y(x,y,z,xt,yt,zt,ri,hs+12))

@njit(fastmath=True, cache=True)
def get_dist_cyl_z(x,y,z,xt,yt,zt,r,hs):
    return max(((x - xt) ** 2 + (y - yt) ** 2) ** 0.5 - r,abs(zt - z) - hs)

@njit(fastmath=True, cache=True)
def get_dist_cyl_y(x,y,z,xt,yt,zt,r,hs):
    return max(((x - xt) ** 2 + (z - zt) ** 2) ** 0.5 - r,abs(yt - y) - hs)

@njit(fastmath=True, cache=True)
def get_dist_cyl_x(x,y,z,xt,yt,zt,r,hs):
    return max(((z - zt) ** 2 + (y - yt) ** 2) ** 0.5 - r,abs(xt - x) - hs)

@njit(fastmath=True, cache=True)
def get_dist_triangle(x,y,x1,y1,x2,y2,x3,y3):
    return max(max(((x - x1) ** 2 + (y - y1) ** 2) ** 0.5,((x - x2) ** 2 + (y - y2) ** 2) ** 0.5),((x - x3) ** 2 + (y - y3) ** 2) ** 0.5)

@njit(fastmath=True, cache=True)
def softmin(a,b,k = 4):
    return -math.log(max(0.0001,math.exp(-k * a) + math.exp(-k * b))) / k

@njit(fastmath=True, cache=True)
def getlenv(x,y,z):
    return math.sqrt(x*x + y*y + z*z)

@njit(fastmath=True, cache=True)
def scal_pr(x,y,z,x1,y1,z1):
    return x * x1 + y * y1 + z * z1

@njit(fastmath=True, cache=True)
def umv(x,y,z,n):
    return x * n, y * n, z * n

@njit(fastmath=True, cache=True)
def sumv(x,y,z,x1,y1,z1):
    return x + x1, y + y1, z + z1

@njit(fastmath=True, cache=True)
def normv(x,y,z):
    l = getlenv(x,y,z)
    if l != 0:
        return x / l, y / l, z / l
    return 0, 0, 0

@njit(fastmath=True, cache=True)
def getlenv_4D(x,y,z,t):
    return math.sqrt(x*x + y*y + z*z + t*t)

@njit(fastmath=True, cache=True)
def scal_pr_4D(x,y,z,t,x1,y1,z1,t1):
    return x * x1 + y * y1 + z * z1 + t * t1

@njit(fastmath=True, cache=True)
def umv_4D(x,y,z,t,n):
    return x * n, y * n, z * n, t * n

@njit(fastmath=True, cache=True)
def sumv_4D(x,y,z,t,x1,y1,z1,t1):
    return x + x1, y + y1, z + z1, t + t1

@njit(fastmath=True, cache=True)
def normv_4D(x,y,z,t):
    l = getlenv_4D(x,y,z,t)
    if l != 0:
        return x / l, y / l, z / l, t / l
    return 0, 0, 0

@njit(fastmath=True, cache=True)
def get_num(s):
    num = ""
    n_r = 0
    d_r = 0
    l = 0
    ans = 0
    dr = 0
    sig = 1
    if s[0] == "-":
        sig *= -1
        s = s[1:]
    for h in s:
        if ord(h) - ord('0') > 9 or ord(h) - ord('0') < 0:
            n_r = 1
            num = num[::-1]
            ans = 0
            j = 0
            if d_r:
                num = num[::-1]
                for k in num:
                    ans += (ord(k) - ord('0')) * (0.1 ** j)
                    j += 1
            else:
                for k in num:
                    ans += (ord(k) - ord('0')) * (10 ** j)
                    j += 1
            #print(ans)
            break
        elif h == ".":
            d_r = 1
            num = num[::-1]
            ans = 0
            j = 0
            for k in num:
                ans += (ord(k) - ord('0')) * (10 ** j)
                j += 1
            num = ""
            #print(ans)
        if not(n_r) and h != ".":
            num = num + h
            l += 1
    return int(ans * sig),s[l + 1:]

@njit(fastmath=True, cache=True)
def distance(x1, y1, x2, y2):
    dist = pow((pow(x2-x1,2)+pow(y2-y1,2)),0.5)
    return dist

@njit(fastmath=True, cache=True)
def get_dist_to_sph(r,p,c):
    c3 = p - c
    if c3 != 0:
        cz = math.fabs(c3) / c3
    else:
        cz = 1
    c3 = r * math.sin((math.fabs(c3) / r * 90) / 57.3) - c3 * cz
    #print(c3)
    c3 *= cz
    return c3

def rot_coord(ob,n1,n2):
    if type(ob) == Object:
        num1 = 0
        if n1 == 0:
            num1 = ob.x
        elif n1 == 1:
            num1 = ob.z
        elif n1 == 2:
            num1 = ob.y
        else:
            num1 = ob.t

        num2 = 0
        if n2 == 0:
            num2 = ob.x
        elif n2 == 1:
            num2 = ob.z
        elif n2 == 2:
            num2 = ob.y
        else:
            num2 = ob.t

        sav = num2
        num2 = num1
        num1 = sav

        if n1 == 0:
            ob.x = num1
        elif n1 == 1:
            ob.z = num1
        elif n1 == 2:
            ob.y = num1
        else:
            ob.t = num1

        if n1 == 0:
            ob.x = num2
        elif n1 == 1:
            ob.z = num2
        elif n1 == 2:
            ob.y = num2
        else:
            ob.t = num2
    else:
        num1 = 0
        if n1 == 0:
            num1 = ob.x
        elif n1 == 1:
            num1 = ob.y
        elif n1 == 2:
            num1 = ob.z
        else:
            num1 = ob.t

        num2 = 0
        if n2 == 0:
            num2 = ob.x
        elif n2 == 1:
            num2 = ob.y
        elif n2 == 2:
            num2 = ob.z
        else:
            num2 = ob.t

        sav = num2
        num2 = num1
        num1 = sav

        if n1 == 0:
            ob.x = num1
        elif n1 == 1:
            ob.y = num1
        elif n1 == 2:
            ob.z = num1
        else:
            ob.t = num1

        if n1 == 0:
            ob.x = num2
        elif n1 == 1:
            ob.y = num2
        elif n1 == 2:
            ob.z = num2
        else:
            ob.t = num2

    return ob
