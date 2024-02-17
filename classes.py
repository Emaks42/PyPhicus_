from pyphicus.functions import *

class vector_3D():
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
    def getlen(self):
        return getlenv(self.x,self.y,self.z)
    def scal_proi(self,vec2):
        return scal_pr(self.x,self.y,self.z,vec2.x,vec2.y,vec2.z)
    def umn(self,num):
        self.x, self.y, self.z = umv(self.x,self.y,self.z,num)
    def sum(self,vec2):
        self.x,self.y,self.z = sumv(self.x,self.y,self.z,vec2.x,vec2.y,vec2.z)
    def norm(self):
        self.x, self.y, self.z = normv(self.x, self.y, self.z)

class vector_4D():
    def __init__(self,x,y,z,t):
        self.x = x
        self.y = y
        self.z = z
        self.t = t
    def getlen_4D(self):
        return getlenv_4D(self.x,self.y,self.z,self.t)
    def getlen(self):
        return getlenv(self.x,self.y,self.z)
    def scal_proi_4D(self,vec2):
        return scal_pr_4D(self.x,self.y,self.z,self.t,vec2.x,vec2.y,vec2.z,vec2.t)
    def scal_proi(self,vec2):
        return scal_pr(self.x,self.y,self.z,vec2.x,vec2.y,vec2.z)
    def umn_4D(self,num):
        self.x, self.y, self.z, self.t = umv_4D(self.x,self.y,self.z,self.t,num)
    def umn(self, num):
        self.x, self.y, self.z = umv(self.x, self.y, self.z, num)
    def sum(self,vec2):
        self.x,self.y,self.z, self.t = sumv_4D(self.x,self.y,self.z,self.t,vec2.x,vec2.y,vec2.z,vec2.t)
    def norm_4D(self):
        self.x, self.y, self.z, self.t = normv_4D(self.x, self.y, self.z,self.t)
    def norm(self):
        self.x, self.y, self.z = normv(self.x, self.y, self.z)

class Energy():
    def __init__(self,color,effects,generations,touch_formula):
        self.color = color
        self.effects = effects
        self.generations = generations
        self.touch_formula = touch_formula

class Radial_Energy():
    def __init__(self,r,x,y,z,energy,count,eps,direction):
        self.r = r
        self.x = x
        self.y = y
        self.z = z
        self.energy = energy
        self.count = count
        self.eps = eps
        self.direction = direction

class Static_Energy():
    def __init__(self,energy,count,eps,direction,sdf_formula,obj,sim):
        self.energy = energy
        self.count = count
        self.eps = eps
        self.direction = direction
        self.sdf_formula = read_sdf(obj.convert_formul(sdf_formula,sim))

    def get_dist(self,x,y,z):
        dist = read_get_dist(x,y,z,self.sdf_formula,0)
        return dist

    def get_direction(self,obj,sim):
        return vector_3D(sim.use_formul(self.direction[0],obj.energy[self.energy],
                              x=obj.x,y=obj.y,z=obj.z,t=obj.t,
                              mass=obj.mass,hp=obj.hp,mvx=obj.vectors[0].x,
                              mvy=obj.vectors[0].y,mvz=obj.vectors[0].z,
                              mvt=obj.vectors[0].t,mvl=obj.vectors[0].getlen_4D()),
                         sim.use_formul(self.direction[1], obj.energy[self.energy],
                                        x=obj.x, y=obj.y, z=obj.z, t=obj.t,
                                        mass=obj.mass, hp=obj.hp, mvx=obj.vectors[0].x,
                                        mvy=obj.vectors[0].y, mvz=obj.vectors[0].z,
                                        mvt=obj.vectors[0].t, mvl=obj.vectors[0].getlen_4D()),
                         sim.use_formul(self.direction[2], obj.energy[self.energy],
                                        x=obj.x, y=obj.y, z=obj.z, t=obj.t,
                                        mass=obj.mass, hp=obj.hp, mvx=obj.vectors[0].x,
                                        mvy=obj.vectors[0].y, mvz=obj.vectors[0].z,
                                        mvt=obj.vectors[0].t, mvl=obj.vectors[0].getlen_4D()))

def read_sdf(formul):
    ans = []
    while len(formul) != 0:
        if formul[0] == "(":
            stgnf = ""
            formul = formul[1:]
            cou = 1
            pos = 0
            while cou != 0:
                if formul[pos] == "(":
                    cou += 1
                elif formul[pos] == ")":
                    cou -= 1
                pos += 1
            stgnf = formul[:pos]
            formul = formul[pos:]
            stgnf = stgnf[:-1]
            ans.append(read_sdf(stgnf))
        elif formul[0] == ")":
            formul = formul[1:]
        elif formul[0] == " ":
            formul = formul[1:]
        elif ord(formul[0]) >= ord('0') and ord(formul[0]) <= ord('9'):
            n, formul = get_num(formul)
            ans.append(n)
            formul = formul[1:]
        else:
            pos = 0
            while formul[pos] != " ":
                pos += 1
            stgnf = formul[:pos]
            formul = formul[pos:]
            ans.append(stgnf)
    return ans

def read_get_dist(x,y,z,n, dist):
    if n[0] == "imp":
        md = read_get_dist(x,y,z,n[2], dist)
        h = n[1]
        for l in range(1, h):
            md1 = read_get_dist(x,y,z,n[2 + l], dist)
            md = int(not(md)) | int(md1)
        if md >= 0:
            dist += md
        else:
            dist = -1
            return dist
    if n[0] == "impxor":
        md = read_get_dist(x,y,z,n[2], dist)
        h = n[1]
        for l in range(1, h):
            md1 = read_get_dist(x,y,z,n[2 + l], dist)
            md = int(-md) ^ int(md1)
        if md >= 0:
            dist += md
        else:
            dist = -1
            return dist
    if n[0] == "or":
        md = read_get_dist(x,y,z,n[2], dist)
        h = n[1]
        for l in range(1, h):
            md1 = read_get_dist(x,y,z,n[2 + l], dist)
            md = int(md) | int(md1)
        if md >= 0:
            dist += md
        else:
            dist = -1
            return dist
    if n[0] == "and":
        md = read_get_dist(x,y,z,n[2], dist)
        h = n[1]
        for l in range(1, h):
            md1 = read_get_dist(x,y,z,n[2 + l], dist)
            md = int(md) & int(md1)
        if md >= 0:
            dist += md
        else:
            dist = 1
            return dist
    if n[0] == "xor":
        md = read_get_dist(x,y,z,n[2], dist)
        h = n[1]
        for l in range(1, h):
            md1 = read_get_dist(x,y,z,n[2 + l], dist)
            md = int(md) ^ int(md1)
        if md >= 0:
            dist += md
        else:
            dist = -1
            return dist
    if n[0] == "min":
        md = read_get_dist(x,y,z,n[2], dist)
        h = n[1]
        for l in range(1, h):
            md1 = read_get_dist(x,y,z,n[2 + l], dist)
            md = min(md,md1)
        if md >= 0:
            dist += md
        else:
            dist = -1
            return dist
    if n[0] == "max":
        md = read_get_dist(x,y,z,n[2], dist)
        h = n[1]
        for l in range(1, h):
            md1 = read_get_dist(x,y,z,n[2 + l], dist)
            md = max(md,md1)
        if md >= 0:
            dist += md
        else:
            dist = -1
            return dist
    if n[0] == "sm":
        md = read_get_dist(x,y,z,n[2], dist)
        h = n[1]
        for l in range(1, h):
            md1 = read_get_dist(x,y,z,n[2 + l], dist)
            md = softmin(md,md1)
        if md >= 0:
            dist += md
        else:
            dist = -1
            return dist
    if n[0] == "s":
        if get_dist_sph(x,y,z, n[1], n[2], n[3], n[4]) >= 0:
            dist += get_dist_sph(x,y,z, n[1], n[2], n[3], n[4])
        else:
            dist = -1
            return dist
    if n[0] == "r":
        if get_dist_rect(x,y,z, n[1], n[2], n[3], n[4], n[5], n[6]) >= 0:
            dist += get_dist_rect(x,y,z, n[1], n[2], n[3], n[4], n[5], n[6])
        else:
            dist = -1
            return dist
    if n[0] == "rhx":
        if get_dist_rect_h_x(x,y,z, n[1], n[2], n[3], n[4], n[5], n[6], n[7]) >= 0:
            dist += get_dist_rect_h_x(x,y,z, n[1], n[2], n[3], n[4], n[5], n[6], n[7])
        else:
            dist = -1
            return dist
    if n[0] == "rhy":
        if get_dist_rect_h_y(x,y,z, n[1], n[2], n[3], n[4], n[5], n[6], n[7]) >= 0:
            dist += get_dist_rect_h_y(x,y,z, n[1], n[2], n[3], n[4], n[5], n[6], n[7])
        else:
            dist = -1
            return dist
    if n[0] == "rhz":
        if get_dist_rect_h_z(x,y,z, n[1], n[2], n[3], n[4], n[5], n[6], n[7]) >= 0:
            dist += get_dist_rect_h_z(x,y,z, n[1], n[2], n[3], n[4], n[5], n[6], n[7])
        else:
            dist = -1
            return dist
    if n[0] == "cx":
        if get_dist_cyl_x(x,y,z, n[1], n[2], n[3], n[4], n[5]) >= 0:
            dist += get_dist_cyl_x(x,y,z, n[1], n[2], n[3], n[4], n[5])
        else:
            dist = -1
            return dist
    if n[0] == "cy":
        if get_dist_cyl_y(x,y,z, n[1], n[2], n[3], n[4], n[5]) >= 0:
            dist += get_dist_cyl_y(x,y,z, n[1], n[2], n[3], n[4], n[5])
        else:
            dist = -1
            return dist
    if n[0] == "cz":
        if get_dist_cyl_z(x,y,z, n[1], n[2], n[3], n[4], n[5]) >= 0:
            dist += get_dist_cyl_z(x,y,z, n[1], n[2], n[3], n[4], n[5])
        else:
            dist = -1
            return dist
    if n[0] == "torx":
        if get_dist_tor_x(x,y,z, n[1], n[2], n[3], n[4],n[5],n[6]) >= 0:
            dist += get_dist_tor_x(x,y,z, n[1], n[2], n[3], n[4],n[5],n[6])
        else:
            dist = -1
            return dist
    if n[0] == "tory":
        if get_dist_tor_y(x,y,z, n[1], n[2], n[3], n[4],n[5],n[6]) >= 0:
            dist += get_dist_tor_y(x,y,z, n[1], n[2], n[3], n[4],n[5],n[6])
        else:
            dist = -1
            return dist
    if n[0] == "torz":
        if get_dist_tor_z(x,y,z, n[1], n[2], n[3], n[4],n[5],n[6]) >= 0:
            dist += get_dist_tor_z(x,y,z, n[1], n[2], n[3], n[4],n[5],n[6])
        else:
            dist = -1
            return dist
    return dist

class Energy_Wave():
    def __init__(self,direction,energy,count,x,y,z,eps):
        self.direction = direction
        self.energy = energy
        self.count = count
        self.x = x
        self.y = y
        self.z = z
        self.eps = eps
    def move(self):
        self.x += self.direction.x
        self.y += self.direction.y
        self.z += self.direction.z

class Material():
    def __init__(self,color,epslist,rul):
        self.color = color
        self.epslist = epslist
        self.rul = rul

class Object():
    def __init__(self,x,y,m,hp,sim,points=0,z=0, mass=1):
        self.x = x
        self.y = y
        self.z = z
        self.vectors = []
        self.points = points
        self.egv = [vector_3D(0,0,0),vector_3D(0,0,0),vector_3D(0,0,0),
                    vector_3D(0,0,0),vector_3D(0,0,0),vector_3D(0,0,0)]
        self.rv = [vector_3D(0,0,0),vector_3D(0,0,0),vector_3D(0,0,0),
                   vector_3D(0,0,0),vector_3D(0,0,0),vector_3D(0,0,0)]
        self.material = m
        self.mass = mass
        self.hp = hp
        self.energy = []
        for h in numba.prange(len(sim.energies)):
            qq = 0
            for k in numba.prange(len(sim.energies[h].generations)):
                qq += sim.use_formul(sim.formuls[sim.energies[h].generations[k]],
                                     sim.materials[self.material].epslist[h], self.mass,
                                     self.hp, self.x, self.z, self.y, 0, 0, 0, 0, 0, 0)
            self.energy.append(qq)
        self.t = 0

    def update(self,sim):
        self.energy = []
        for h in numba.prange(len(sim.energies)):
            qq = 0
            for k in numba.prange(len(sim.energies[h].generations)):
                qq += sim.use_formul(sim.formuls[sim.energies[h].generations[k]],
                                     sim.materials[self.material].epslist[h], self.mass,
                                     self.hp, self.x, self.z, self.y, 0, self.vectors[0][0].x,
                                                self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                self.vectors[0][0].getlen())
            self.energy.append(qq)

    def use_energy(self,sim):
        xch = 0
        ych = 0
        enred = 0
        for h in range(len(sim.materials[self.material].rul)):
            s = sim.materials[self.material].rul[h]
            numm, s = get_num(s)
            n, s = get_num(s)
            g, s = get_num(s)
            if int(n - g) <= int(self.energy[numm]) and int(n + g) >= int(self.energy[numm]):
                n = ord(s[0]) - ord('0')
                s = s[1:]
                for l in range(n):
                    t = ord(s[0]) - ord('0')
                    s = s[1:]
                    if t == 0:
                        c1 = s[0]
                        isn = 0
                        if c1 == "d":
                            c1 = self.egv[numm].x
                        elif c1 == "b":
                            c1 = -self.egv[numm].x
                        elif c1 == "p":
                            c1 = self.rv[numm].x
                        elif c1 == "q":
                            c1 = -self.rv[numm].x
                        elif c1 == "r":
                            c1 = random.randint(-10, 10)
                        elif c1 == "f":
                            s = s[1:]
                            nn, s = get_num(s)
                            c1 = sim.use_formul(sim.formuls[nn], int(self.energy[numm]), self.mass, self.hp,
                                                self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                self.vectors[0][0].getlen())
                            isn = 1
                        else:
                            c1, s = get_num(s)
                            isn = 1
                        self.x += c1
                        xch += c1
                        if not (isn):
                            s = s[1:]
                    if t == 1:
                        c1 = s[0]
                        isn = 0
                        if c1 == "d":
                            c1 = self.egv[numm].y
                        elif c1 == "b":
                            c1 = -self.egv[numm].y
                        elif c1 == "p":
                            c1 = self.rv[numm].y
                        elif c1 == "q":
                            c1 = -self.rv[numm].y
                        elif c1 == "r":
                            c1 = random.randint(-10, 10)
                        elif c1 == "f":
                            s = s[1:]
                            nn, s = get_num(s)
                            c1 = sim.use_formul(sim.formuls[nn], int(self.energy[numm]), self.mass, self.hp,
                                                self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                self.vectors[0][0].getlen())
                            isn = 1
                        else:
                            c1, s = get_num(s)
                            isn = 1
                        self.z += c1
                        if not (isn):
                            s = s[1:]
                    if t == 2:
                        c1 = s[0]
                        isn = 0
                        if c1 == "d":
                            c1 = self.egv[numm].z
                        elif c1 == "b":
                            c1 = -self.egv[numm].z
                        elif c1 == "p":
                            c1 = self.rv[numm].z
                        elif c1 == "q":
                            c1 = -self.rv[numm].z
                        elif c1 == "r":
                            c1 = random.randint(-10, 10)
                        elif c1 == "f":
                            s = s[1:]
                            nn, s = get_num(s)
                            c1 = sim.use_formul(sim.formuls[nn], int(self.energy[numm]), self.mass, self.hp,
                                                self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                self.vectors[0][0].getlen())
                            isn = 1
                        else:
                            c1, s = get_num(s)
                            isn = 1
                        self.y += c1
                        ych += c1
                        if not (isn):
                            s = s[1:]
                    if t == 3:
                        c1 = s[0]
                        isn = 0

                        if c1 == "d":
                            c1 = self.egv[numm].x
                        elif c1 == "b":
                            c1 = -self.egv[numm].x
                        elif c1 == "p":
                            c1 = self.rv[numm].x
                        elif c1 == "q":
                            c1 = -self.rv[numm].x
                        elif c1 == "r":
                            c1 = random.randint(-10, 10)
                        elif c1 == "f":
                            s = s[1:]
                            nn, s = get_num(s)
                            c1 = sim.use_formul(sim.formuls[nn], int(self.energy[numm]), self.mass, self.hp,
                                                self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                self.vectors[0][0].getlen())
                            isn = 1
                        else:
                            c1, s = get_num(s)
                            isn = 1
                        if not (isn):
                            s = s[1:]

                        c2 = s[0]
                        isn = 0
                        if c2 == "d":
                            c2 = self.egv[numm].y
                        elif c2 == "b":
                            c2 = -self.egv[numm].y
                        elif c2 == "p":
                            c2 = self.rv[numm].y
                        elif c2 == "q":
                            c2 = -self.rv[numm].y
                        elif c2 == "r":
                            c2 = random.randint(-10, 10)
                        elif c2 == "f":
                            s = s[1:]
                            nn, s = get_num(s)
                            c2 = sim.use_formul(sim.formuls[nn], int(self.energy[numm]), self.mass, self.hp,
                                                self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                self.vectors[0][0].getlen())
                            isn = 1
                        else:
                            c2, s = get_num(s)
                            isn = 1
                        if not (isn):
                            s = s[1:]

                        c3 = s[0]
                        isn = 0
                        if c3 == "d":
                            c3 = self.egv[numm].z
                        elif c3 == "b":
                            c3 = -self.egv[numm].z
                        elif c3 == "p":
                            c3 = self.rv[numm].z
                        elif c3 == "q":
                            c3 = -self.rv[numm].z
                        elif c3 == "r":
                            c3 = random.randint(-10, 10)
                        elif c3 == "f":
                            s = s[1:]
                            nn, s = get_num(s)
                            c3 = sim.use_formul(sim.formuls[nn], int(self.energy[numm]), self.mass, self.hp,
                                                self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                self.vectors[0][0].getlen())
                            isn = 1
                        else:
                            c3, s = get_num(s)
                            isn = 1
                        if not (isn):
                            s = s[1:]

                        c4 = s[0]
                        isn = 0
                        if c4 == "d":
                            c4 = self.egv[numm].z
                        elif c4 == "b":
                            c4 = -self.egv[numm].z
                        elif c4 == "p":
                            c4 = self.rv[numm].z
                        elif c4 == "q":
                            c4 = -self.rv[numm].z
                        elif c4 == "r":
                            c4 = random.randint(-10, 10)
                        elif c4 == "f":
                            s = s[1:]
                            nn, s = get_num(s)
                            c4 = sim.use_formul(sim.formuls[nn], int(self.energy[numm]), self.mass, self.hp,
                                                self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                self.vectors[0][0].getlen())
                            isn = 1
                        else:
                            c4, s = get_num(s)
                            isn = 1
                        if not (isn):
                            s = s[1:]

                        vec = vector_4D(c1, c2, c3, c4)
                        g = 0
                        if s[0] == "o":
                            g = -1
                        else:
                            g, s = get_num(s)
                        self.vectors.append([vec, g])
                    if t == 4:
                        n = 0
                        if s[0] == "f":
                            s = s[1:]
                            nn, s = get_num(s)
                            n = sim.use_formul(sim.formuls[nn], int(self.energy[numm]), self.mass, self.hp,
                                               self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                               self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                               self.vectors[0][0].getlen())
                        else:
                            n, s = get_num(s)
                        self.hp += n
                        # print(self.hp)
                    if t == 6:
                        num = ord(s[0]) - ord('0')
                        s = s[1:]
                        cou, s = get_num(s)
                        self.energy[num] -= cou
                        typ = ord(s[0]) - ord('0')
                        s = s[1:]
                        if typ == 1:  # typ == 1
                            c1 = s[0]
                            isn = 0

                            if c1 == "d":
                                c1 = self.egv[numm].x
                            elif c1 == "b":
                                c1 = -self.egv[numm].x
                            elif c1 == "p":
                                c1 = self.rv[numm].x
                            elif c1 == "q":
                                c1 = -self.rv[numm].x
                            elif c1 == "r":
                                c1 = random.randint(-10, 10)
                            elif c1 == "f":
                                s = s[1:]
                                nn, s = get_num(s)
                                c1 = sim.use_formul(sim.formuls[nn], int(self.energy[numm]), self.mass, self.hp,
                                                    self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                    self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                    self.vectors[0][0].getlen())
                                isn = 1
                            else:
                                c1, s = get_num(s)
                                isn = 1
                            if not (isn):
                                s = s[1:]

                            c2 = s[0]
                            isn = 0
                            if c2 == "d":
                                c2 = self.egv[numm].y
                            elif c2 == "b":
                                c2 = -self.egv[numm].y
                            elif c2 == "p":
                                c2 = self.rv[numm].y
                            elif c2 == "q":
                                c2 = -self.rv[numm].y
                            elif c2 == "r":
                                c2 = random.randint(-10, 10)
                            elif c2 == "f":
                                s = s[1:]
                                nn, s = get_num(s)
                                c2 = sim.use_formul(sim.formuls[nn], int(self.energy[numm]), self.mass, self.hp,
                                                    self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                    self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                    self.vectors[0][0].getlen())
                                isn = 1
                            else:
                                c2, s = get_num(s)
                                isn = 1
                            if not (isn):
                                s = s[1:]

                            c3 = s[0]
                            isn = 0
                            if c3 == "d":
                                c3 = self.egv[numm].z
                            elif c3 == "b":
                                c3 = -self.egv[numm].z
                            elif c3 == "p":
                                c3 = self.rv[numm].z
                            elif c3 == "q":
                                c3 = -self.rv[numm].z
                            elif c3 == "r":
                                c3 = random.randint(-10, 10)
                            elif c3 == "f":
                                s = s[1:]
                                nn, s = get_num(s)
                                c3 = sim.use_formul(sim.formuls[nn], int(self.energy[numm]), self.mass, self.hp,
                                                    self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                    self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                    self.vectors[0][0].getlen())
                                isn = 1
                            else:
                                c3, s = get_num(s)
                                isn = 1
                            if not (isn):
                                s = s[1:]

                            vec = vector_3D(c1, c2, c3)
                            epp, s = get_num(s)
                            if sim.materials[self.material].epslist[numm] != 0:
                                epp *= 1 / sim.materials[self.material].epslist[numm]  # тестовое, надо обдумать
                            else:
                                epp = 0
                            sim.waves.append(Energy_Wave(vec, num, cou, self.x, self.z, self.y, epp))
                        else:  # typ == 0
                            r = 0
                            if s[0] == "f":
                                s = s[1:]
                                nn, s = get_num(s)
                                r = sim.use_formul(sim.formuls[nn], int(self.energy[numm]), self.mass, self.hp,
                                                   self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                   self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                   self.vectors[0][0].getlen())
                                if r <= 0:
                                    r = 1
                                r = int(r)
                            else:
                                r, s = get_num(s)
                            epp = 0
                            if s[0] == "f":
                                s = s[1:]
                                nn, s = get_num(s)
                                epp = sim.use_formul(sim.formuls[nn], int(self.energy[numm]), self.mass, self.hp,
                                                     self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                     self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                     self.vectors[0][0].getlen())
                            else:
                                epp, s = get_num(s)
                            if sim.materials[self.material].epslist[numm] != 0:
                                epp *= 1 / sim.materials[self.material].epslist[numm]  # тестовое, надо обдумать
                            else:
                                epp = 0
                            dir = ord(s[0]) - ord('0')
                            if dir == 0:
                                dir = -1
                            s = s[1:]
                            sim.raden.append(Radial_Energy(r, self.x, self.z, self.y, num, cou, epp, dir))
                    if t == 7:
                        c1 = s[0]
                        isn = 0
                        if c1 == "d":
                            c1 = self.egv[numm].z
                        elif c1 == "b":
                            c1 = -self.egv[numm].z
                        elif c1 == "p":
                            c1 = self.rv[numm].z
                        elif c1 == "q":
                            c1 = -self.rv[numm].z
                        elif c1 == "r":
                            c1 = random.randint(-10, 10)
                        elif c1 == "f":
                            s = s[1:]
                            nn, s = get_num(s)
                            c1 = sim.use_formul(sim.formuls[nn], int(self.energy[numm]), self.mass, self.hp,
                                                self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                self.vectors[0][0].getlen())
                            isn = 1
                        else:
                            c1, s = get_num(s)
                            isn = 1
                        self.t += c1
                        if not (isn):
                            s = s[1:]
                    if t == 8:
                        e1 = ord(s[0]) - ord('0')
                        s = s[1:]
                        e2 = ord(s[0]) - ord('0')
                        s = s[1:]
                        c1 = s[0]
                        if c1 == "f":
                            s = s[1:]
                            nn, s = get_num(s)
                            c1 = sim.use_formul(sim.formuls[nn], int(self.energy[numm]), self.mass, self.hp,
                                                self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                self.vectors[0][0].getlen())
                            isn = 1
                        else:
                            c1, s = get_num(s)
                            isn = 1
                        self.energy[e1] -= c1
                        self.energy[e2] += c1
        for h in range(len(self.energy)):
            for k in sim.energies[h].effects:
                n, s = get_num(k)
                g, s = get_num(s)
                if int(n - g) <= int(self.energy[h]) and int(n + g) >= int(self.energy[h]):
                    n = ord(s[0]) - ord('0')
                    s = s[1:]
                    for l in range(n):
                        t = ord(s[0]) - ord('0')
                        s = s[1:]
                        if t == 0:
                            c1 = s[0]
                            isn = 0
                            if c1 == "d":
                                c1 = self.egv[h].x
                            elif c1 == "b":
                                c1 = -self.egv[h].x
                            elif c1 == "p":
                                c1 = self.rv[h].x
                            elif c1 == "q":
                                c1 = -self.rv[h].x
                            elif c1 == "r":
                                c1 = random.randint(-10, 10)
                            elif c1 == "f":
                                s = s[1:]
                                nn, s = get_num(s)
                                c1 = sim.use_formul(sim.formuls[nn], int(self.energy[h]), self.mass, self.hp,
                                                    self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                    self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                    self.vectors[0][0].getlen())
                                isn = 1
                            else:
                                c1, s = get_num(s)
                                isn = 1
                            self.x += c1
                            xch += c1
                            if not (isn):
                                s = s[1:]
                        if t == 1:
                            c1 = s[0]
                            isn = 0
                            if c1 == "d":
                                c1 = self.egv[h].y
                            elif c1 == "b":
                                c1 = -self.egv[h].y
                            elif c1 == "p":
                                c1 = self.rv[h].y
                            elif c1 == "q":
                                c1 = -self.rv[h].y
                            elif c1 == "r":
                                c1 = random.randint(-10, 10)
                            elif c1 == "f":
                                s = s[1:]
                                nn, s = get_num(s)
                                c1 = sim.use_formul(sim.formuls[nn], int(self.energy[h]), self.mass, self.hp,
                                                    self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                    self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                    self.vectors[0][0].getlen())
                                isn = 1
                            else:
                                c1, s = get_num(s)
                                isn = 1
                            self.z += c1
                            if not (isn):
                                s = s[1:]
                        if t == 2:
                            c1 = s[0]
                            isn = 0
                            if c1 == "d":
                                c1 = self.egv[h].z
                            elif c1 == "b":
                                c1 = -self.egv[h].z
                            elif c1 == "p":
                                c1 = self.rv[h].z
                            elif c1 == "q":
                                c1 = -self.rv[h].z
                            elif c1 == "r":
                                c1 = random.randint(-10, 10)
                            elif c1 == "f":
                                s = s[1:]
                                nn, s = get_num(s)
                                c1 = sim.use_formul(sim.formuls[nn], int(self.energy[h]), self.mass, self.hp,
                                                    self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                    self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                    self.vectors[0][0].getlen())
                                isn = 1
                            else:
                                c1, s = get_num(s)
                                isn = 1
                            self.y += c1
                            ych += c1
                            if not (isn):
                                s = s[1:]
                        if t == 3:
                            c1 = s[0]
                            isn = 0
                            if c1 == "d":
                                c1 = self.egv[h].x
                            elif c1 == "b":
                                c1 = -self.egv[h].x
                            elif c1 == "p":
                                c1 = self.rv[h].x
                            elif c1 == "q":
                                c1 = -self.rv[h].x
                            elif c1 == "r":
                                c1 = random.randint(-10, 10)
                            elif c1 == "f":
                                s = s[1:]
                                nn, s = get_num(s)
                                c1 = sim.use_formul(sim.formuls[nn], int(self.energy[h]), self.mass, self.hp,
                                                    self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                    self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                    self.vectors[0][0].getlen())
                                isn = 1
                            else:
                                c1, s = get_num(s)
                                isn = 1
                            if not (isn):
                                s = s[1:]

                            c2 = s[0]
                            isn = 0
                            if c2 == "d":
                                c2 = self.egv[h].y
                            elif c2 == "b":
                                c2 = -self.egv[h].y
                            elif c2 == "p":
                                c2 = self.rv[h].y
                            elif c2 == "q":
                                c2 = -self.rv[h].y
                            elif c2 == "r":
                                c2 = random.randint(-10, 10)
                            elif c2 == "f":
                                s = s[1:]
                                nn, s = get_num(s)
                                c2 = sim.use_formul(sim.formuls[nn], int(self.energy[h]), self.mass, self.hp,
                                                    self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                    self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                    self.vectors[0][0].getlen())
                                isn = 1
                            else:
                                c2, s = get_num(s)
                                isn = 1
                            if not (isn):
                                s = s[1:]

                            c3 = s[0]
                            isn = 0
                            if c3 == "d":
                                c3 = self.egv[h].z
                            elif c3 == "b":
                                c3 = -self.egv[h].z
                            elif c3 == "p":
                                c3 = self.rv[h].z
                            elif c3 == "q":
                                c3 = -self.rv[h].z
                            elif c3 == "r":
                                c3 = random.randint(-10, 10)
                            elif c3 == "f":
                                s = s[1:]
                                nn, s = get_num(s)
                                c3 = sim.use_formul(sim.formuls[nn], int(self.energy[h]), self.mass, self.hp,
                                                    self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                    self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                    self.vectors[0][0].getlen())
                                isn = 1
                            else:
                                c3, s = get_num(s)
                                isn = 1
                            if not (isn):
                                s = s[1:]

                            c4 = s[0]
                            isn = 0
                            if c4 == "d":
                                c4 = self.egv[h].z
                            elif c4 == "b":
                                c4 = -self.egv[h].z
                            elif c4 == "p":
                                c4 = self.rv[h].z
                            elif c4 == "q":
                                c4 = -self.rv[h].z
                            elif c4 == "r":
                                c4 = random.randint(-10, 10)
                            elif c4 == "f":
                                s = s[1:]
                                nn, s = get_num(s)
                                c4 = sim.use_formul(sim.formuls[nn], int(self.energy[h]), self.mass, self.hp,
                                                    self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                    self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                    self.vectors[0][0].getlen())
                                isn = 1
                            else:
                                c4, s = get_num(s)
                                isn = 1
                            if not (isn):
                                s = s[1:]

                            vec = vector_4D(c1, c2, c3, c4)
                            g = 0
                            if s[0] == "o":
                                g = -1
                            else:
                                g, s = get_num(s)
                            self.vectors.append([vec, g])
                        if t == 4:
                            n = 0
                            if s[0] == "f":
                                s = s[1:]
                                nn, s = get_num(s)
                                n = sim.use_formul(sim.formuls[nn], int(self.energy[h]), self.mass, self.hp,
                                                   self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                   self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                   self.vectors[0][0].getlen())
                            else:
                                n, s = get_num(s)
                            self.hp += n
                            # print(self.hp)
                        if t == 6:
                            num = ord(s[0]) - ord('0')
                            s = s[1:]
                            cou, s = get_num(s)
                            self.energy[h] -= cou
                            typ = ord(s[0]) - ord('0')
                            s = s[1:]
                            if typ == 1:  # typ == 1
                                c1 = s[0]
                                isn = 0
                                if c1 == "d":
                                    c1 = self.egv[h].x
                                elif c1 == "b":
                                    c1 = -self.egv[h].x
                                elif c1 == "p":
                                    c1 = self.rv[h].x
                                elif c1 == "q":
                                    c1 = -self.rv[h].x
                                elif c1 == "r":
                                    c1 = random.randint(-10, 10)
                                elif c1 == "f":
                                    s = s[1:]
                                    nn, s = get_num(s)
                                    c1 = sim.use_formul(sim.formuls[nn], int(self.energy[h]), self.mass, self.hp,
                                                        self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                        self.vectors[0][0].y, self.vectors[0][0].z,
                                                        self.vectors[0][0].t,
                                                        self.vectors[0][0].getlen())
                                    isn = 1
                                else:
                                    c1, s = get_num(s)
                                    isn = 1
                                if not (isn):
                                    s = s[1:]

                                c2 = s[0]
                                isn = 0
                                if c2 == "d":
                                    c2 = self.egv[h].y
                                elif c2 == "b":
                                    c2 = -self.egv[h].y
                                elif c2 == "p":
                                    c2 = self.rv[h].y
                                elif c2 == "q":
                                    c2 = -self.rv[h].y
                                elif c2 == "r":
                                    c2 = random.randint(-10, 10)
                                elif c2 == "f":
                                    s = s[1:]
                                    nn, s = get_num(s)
                                    c2 = sim.use_formul(sim.formuls[nn], int(self.energy[h]), self.mass, self.hp,
                                                        self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                        self.vectors[0][0].y, self.vectors[0][0].z,
                                                        self.vectors[0][0].t,
                                                        self.vectors[0][0].getlen())
                                    isn = 1
                                else:
                                    c2, s = get_num(s)
                                    isn = 1
                                if not (isn):
                                    s = s[1:]

                                c3 = s[0]
                                isn = 0
                                if c3 == "d":
                                    c3 = self.egv[h].z
                                elif c3 == "b":
                                    c3 = -self.egv[h].z
                                elif c3 == "p":
                                    c3 = self.rv[h].z
                                elif c3 == "q":
                                    c3 = -self.rv[h].z
                                elif c3 == "r":
                                    c3 = random.randint(-10, 10)
                                elif c3 == "f":
                                    s = s[1:]
                                    nn, s = get_num(s)
                                    c3 = sim.use_formul(sim.formuls[nn], int(self.energy[h]), self.mass, self.hp,
                                                        self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                        self.vectors[0][0].y, self.vectors[0][0].z,
                                                        self.vectors[0][0].t,
                                                        self.vectors[0][0].getlen())
                                    isn = 1
                                else:
                                    c3, s = get_num(s)
                                    isn = 1
                                if not (isn):
                                    s = s[1:]

                                vec = vector_3D(c1, c2, c3)
                                epp, s = get_num(s)
                                if sim.materials[self.material].epslist[h] != 0:
                                    epp *= 1 / sim.materials[self.material].epslist[h]  # тестовое, надо обдумать
                                else:
                                    epp = 0
                                sim.waves.append(Energy_Wave(vec, num, cou, self.x, self.z, self.y, epp))
                            else:  # typ == 0
                                r = 0
                                if s[0] == "f":
                                    s = s[1:]
                                    nn, s = get_num(s)
                                    r = sim.use_formul(sim.formuls[nn], int(self.energy[h]), self.mass, self.hp,
                                                       self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                       self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                       self.vectors[0][0].getlen())
                                    if r <= 0:
                                        r = 1
                                    r = int(r)
                                    # print(self.energy[h])
                                else:
                                    r, s = get_num(s)
                                epp = 0
                                if s[0] == "f":
                                    s = s[1:]
                                    nn, s = get_num(s)
                                    epp = sim.use_formul(sim.formuls[nn], int(self.energy[h]), self.mass, self.hp,
                                                         self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                         self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                         self.vectors[0][0].getlen())
                                else:
                                    epp, s = get_num(s)
                                if sim.materials[self.material].epslist[h] != 0:
                                    epp *= 1 / sim.materials[self.material].epslist[h]  # тестовое, надо обдумать
                                else:
                                    epp = 0
                                dir = ord(s[0]) - ord('0')
                                if dir == 0:
                                    dir = -1
                                s = s[1:]
                                sim.raden.append(
                                    Radial_Energy(r, self.x, self.z, self.y, num, cou, epp, dir))
                        if t == 7:
                            c1 = s[0]
                            isn = 0
                            if c1 == "d":
                                c1 = self.egv[h].z
                            elif c1 == "b":
                                c1 = -self.egv[h].z
                            elif c1 == "p":
                                c1 = self.rv[h].z
                            elif c1 == "q":
                                c1 = -self.rv[h].z
                            elif c1 == "r":
                                c1 = random.randint(-10, 10)
                            elif c1 == "f":
                                s = s[1:]
                                nn, s = get_num(s)
                                c1 = sim.use_formul(sim.formuls[nn], int(self.energy[h]), self.mass, self.hp,
                                                    self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                    self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                    self.vectors[0][0].getlen())
                                isn = 1
                            else:
                                c1, s = get_num(s)
                                isn = 1
                            self.t += c1
                            if not (isn):
                                s = s[1:]
                        if t == 8:
                            e1 = ord(s[0]) - ord('0')
                            s = s[1:]
                            e2 = ord(s[0]) - ord('0')
                            s = s[1:]
                            c1 = s[0]
                            if c1 == "f":
                                s = s[1:]
                                nn, s = get_num(s)
                                c1 = sim.use_formul(sim.formuls[nn], int(self.energy[h]), self.mass, self.hp,
                                                    self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                                    self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                                    self.vectors[0][0].getlen())
                                isn = 1
                            else:
                                c1, s = get_num(s)
                                isn = 1
                            self.energy[e1] -= c1
                            self.energy[e2] += c1
        return xch,ych

    def convert_formul(self,s,sim):
        ans = ""
        while len(s) != 0:
            if s[0] == "f":
                s = s[1:]
                form_num, s = get_num(s)
                num = sim.use_formul(sim.formuls[form_num], 0, self.mass, self.hp,
                                     self.x, self.z, self.y, self.t, self.vectors[0][0].x,
                                     self.vectors[0][0].y, self.vectors[0][0].z, self.vectors[0][0].t,
                                     self.vectors[0][0].getlen())
                ans = ans + str(num) + 'a'
            else:
                ans = ans + s[0]
                s = s[1:]
        return ans

def use_vec(l):
    x = l[0]
    y = l[1]
    ob = l[2]
    #print(x, y)
    nvectors = []
    new_vec = vector_4D(0,0,0,0)
    if len(ob.vectors) > 1:
        for h in ob.vectors:
            if h[1] == -1:
                new_vec.sum(h[0])
            else:
                nvectors.append(h)
    elif len(ob.vectors) == 1 and ob.vectors[0][1] == -1:
        new_vec = ob.vectors[0][0]
    elif len(ob.vectors) == 1:
        nvectors.append(ob.vectors[0])
    for h in nvectors:
        ob.pol[h[1]].add_x(h[0].x)
        ob.pol[h[1]].add_y(-h[0].y)
        ob.pol[h[1]].add_z(h[0].z * 200)
        #print(ob.pol[h[1]].x)
    x += new_vec.x
    ob.x += new_vec.x
    y += new_vec.z
    ob.y += new_vec.z
    ob.z += new_vec.y
    ob.t += new_vec.t
    nvectors.append([new_vec,-1])
    ob.vectors = nvectors
    #print(x,y)
    return [x,y,ob,1]
