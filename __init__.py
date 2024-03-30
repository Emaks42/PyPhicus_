import math
from numba import njit, prange
import numpy as np
from pyphicus.classes import *
from pyphicus.functions import *

class Simulation:
    def __init__(self):
        self.map = []
        self.raden = []
        self.waves = []
        self.custom_energies = []
        self.energies = []
        self.materials = []
        self.formuls = []
        self.time = 0
        self.ensum = 0

    def add_object(self,object,add_base_time_vec=1):
        self.map.append([object.x, object.y, Object(object.x, object.y, object.material, object.hp,self, z = object.z), 1])
        if add_base_time_vec:
            self.map[-1][2].vectors.append([vector_4D(0, 0, 0, 1), -1])

    def load_settings(self,filename):
        file = open(filename, encoding="utf-8")

        line = file.readline()[:-1]
        num_of_form = int(line)
        for i in range(num_of_form):
            line = file.readline()[:-1]
            self.add_formul(line)
        line = file.readline()[:-1]
        num_of_en = int(line)
        for i in range(num_of_en):
            line = file.readline()[:-1]
            num_of_rul = int(line)
            rules = []
            for j in range(num_of_rul):
                line = file.readline()[:-1]
                rules.append(line)
            line = file.readline()
            num_of_gen = int(line)
            gen = []
            for j in range(num_of_gen):
                line = file.readline()[:-1]
                num = int(line)
                gen.append(num)

            color = []
            line = file.readline()[:-1]
            num = int(line)
            color.append(num)
            line = file.readline()[:-1]
            num = int(line)
            color.append(num)
            line = file.readline()[:-1]
            num = int(line)
            color.append(num)

            self.energies.append(Energy(color, rules, gen, 5))

        line = file.readline()[:-1]
        num_of_mat = int(line)
        for i in range(num_of_mat):
            line = file.readline()[:-1]
            num_of_rul = int(line)
            rules = []
            for j in range(num_of_rul):
                line = file.readline()[:-1]
                rules.append(line)
            epsl = []
            for j in range(num_of_en):
                line = file.readline()[:-1]
                num = float(line)
                epsl.append(num)
            color = []
            line = file.readline()[:-1]
            num = int(line)
            color.append(num)
            line = file.readline()[:-1]
            num = int(line)
            color.append(num)
            line = file.readline()[:-1]
            num = int(line)
            color.append(num)

            self.materials.append(Material(color, epsl, rules))

        file.close()

    def cadr(self):
        mtr = []
        self.ensum = 0
        for h in numba.prange(len(self.map)):
            self.map[h] = use_vec(self.map[h])
            xch, ych = self.map[h][2].use_energy(self)
            if self.map[h][2].hp <= 0:
                mtr.append(self.map[h])
                for k in range(len(self.map[h][2].energy)):
                    self.raden.append(
                        Radial_Energy(random.randint(5, 15), self.map[h][0], self.map[h][2].z,
                                      self.map[h][1], k,
                                      self.map[h][2].energy[k],
                                      random.randint(1, 5), 1))
            self.map[h][0] += xch
            self.map[h][1] += ych
            if self.time == self.map[h][2].t:
                qwerty = 0
            self.map[h][2].egv = [vector_3D(0, 0, 0), vector_3D(0, 0, 0), vector_3D(0, 0, 0), vector_3D(0, 0, 0),
                                  vector_3D(0, 0, 0), vector_3D(0, 0, 0)]
            self.map[h][2].rv = [vector_3D(0, 0, 0), vector_3D(0, 0, 0), vector_3D(0, 0, 0), vector_3D(0, 0, 0),
                                 vector_3D(0, 0, 0), vector_3D(0, 0, 0)]
            ul = 2
            for k in range(len(self.energies)):
                self.ensum += self.map[h][2].energy[k]
                ul += len(str(self.map[h][2].energy[k]))
            if abs(self.map[h][2].x) + abs(self.map[h][2].y) + abs(self.map[h][2].z) > 30000:
                mtr.append(self.map[h])
        for h in mtr:
            self.map.remove(h)

        radentorem = []
        for h in numba.prange(len(self.raden)):
            self.ensum += self.raden[h].count
            for k in numba.prange(len(self.map)):
                if distance(self.map[k][0], self.map[k][1], self.raden[h].x, self.raden[h].z) <= \
                        self.raden[h].r:
                    epsdis = self.materials[self.map[k][2].material].epslist[self.raden[h].energy]
                    if self.raden[h].count <= self.raden[h].eps * epsdis:
                        self.map[k][2].energy[self.raden[h].energy] += self.raden[h].count
                        self.map[k][2].egv[self.raden[h].energy].sum(
                            vector_3D(get_dist_to_sph(self.raden[h].r, self.map[k][0], self.raden[h].x),
                                      get_dist_to_sph(self.raden[h].r, self.map[k][1],
                                                      self.raden[h].y),
                                      get_dist_to_sph(self.raden[h].r, self.map[k][2].z,
                                                      self.raden[h].z)))
                        self.map[k][2].egv[self.raden[h].energy].umn(self.raden[h].direction)
                        self.map[k][2].rv[self.raden[h].energy].sum(
                            vector_3D(self.map[k][0] - self.raden[h].x,
                                      self.map[k][1] - self.raden[h].y,
                                      self.map[k][2].z - self.raden[h].z))
                        self.map[k][2].rv[self.raden[h].energy].norm()
                        self.map[k][2].rv[self.raden[h].energy].umn(self.raden[h].direction)
                        radentorem.append(self.raden[h])
                        break
                    self.map[k][2].energy[self.raden[h].energy] += self.raden[h].eps * epsdis
                    self.raden[h].count -= self.raden[h].eps * epsdis
                    self.map[k][2].egv[self.raden[h].energy].sum(
                    vector_3D(get_dist_to_sph(self.raden[h].r, self.map[k][0], self.raden[h].x),
                              get_dist_to_sph(self.raden[h].r, self.map[k][1],
                                              self.raden[h].y),
                              get_dist_to_sph(self.raden[h].r, self.map[k][2].z, self.raden[h].z)))
                    self.map[k][2].egv[self.raden[h].energy].umn(self.raden[h].direction)
                    self.map[k][2].rv[self.raden[h].energy].sum(
                    vector_3D(self.map[k][0] - self.raden[h].x,
                              self.map[k][1] - self.raden[h].y,
                              self.map[k][2].z - self.raden[h].z))
                    self.map[k][2].rv[self.raden[h].energy].norm()
                    self.map[k][2].rv[self.raden[h].energy].umn(self.raden[h].direction)
        for h in numba.prange(len(radentorem)):
            self.raden.remove(radentorem[h])

        c_e_to_rem = []
        for h in numba.prange(len(self.custom_energies)):
            self.ensum += self.custom_energies[h].count
            for k in numba.prange(len(self.map)):
                if self.custom_energies[h].get_dist(self.map[k][2].x,self.map[k][2].y,self.map[k][2].z) <= 0:
                    epsdis = self.materials[self.map[k][2].material].epslist[self.custom_energies[h].energy]
                    if self.custom_energies[h].count <= self.custom_energies[h].eps * epsdis:
                        self.map[k][2].energy[self.custom_energies[h].energy] += self.custom_energies[h].count
                        self.map[k][2].egv[self.custom_energies[h].energy].sum(self.custom_energies[h].get_direction(
                            self.map[k][2],self))
                        self.map[k][2].egv[self.custom_energies[h].energy].norm()
                        self.map[k][2].rv[self.custom_energies[h].energy].sum(self.custom_energies[h].get_direction(
                            self.map[k][2],self))
                        self.map[k][2].rv[self.custom_energies[h].energy].norm()
                        c_e_to_rem.append(self.custom_energies[h])
                        break
                    self.map[k][2].energy[self.custom_energies[h].energy] += self.custom_energies[h].eps * epsdis
                    self.custom_energies[h].count -= self.custom_energies[h].eps * epsdis
                    self.map[k][2].egv[self.custom_energies[h].energy].sum(self.custom_energies[h].get_direction(
                        self.map[k][2], self))
                    self.map[k][2].egv[self.custom_energies[h].energy].norm()
                    self.map[k][2].rv[self.custom_energies[h].energy].sum(self.custom_energies[h].get_direction(
                        self.map[k][2], self))
                    self.map[k][2].rv[self.custom_energies[h].energy].norm()
        for h in numba.prange(len(c_e_to_rem)):
            self.custom_energies.remove(c_e_to_rem[h])

        wavestorem = []
        for h in numba.prange(len(self.waves)):
            self.waves[h].move()
            self.ensum += self.waves[h].count
            for k in numba.prange(len(self.map)):
                if distance(self.map[k][0], self.map[k][1], self.waves[h].x, self.waves[h].z) <= 5:
                    epsdis = self.materials[self.map[k][2].material].epslist[self.waves[h].energy]
                    if self.waves[h].count <= self.waves[h].eps * epsdis:
                        self.map[k][2].energy[self.waves[h].energy] += self.waves[h].count
                        self.map[k][2].egv[self.waves[h].energy].sum(self.waves[h].direction)
                        self.map[k][2].rv[self.waves[h].energy].sum(self.waves[h].direction)
                        self.map[k][2].rv[self.waves[h].energy].norm()
                        wavestorem.append(self.waves[h])
                        break
                    self.map[k][2].energy[self.waves[h].energy] += self.waves[h].eps * epsdis
                    self.waves[h].count -= self.waves[h].eps * epsdis
                    self.map[k][2].egv[self.waves[h].energy].sum(self.waves[h].direction)
                    self.map[k][2].rv[self.waves[h].energy].sum(self.waves[h].direction)
                    self.map[k][2].rv[self.waves[h].energy].norm()
            if self.waves[h].count <= 0:
                wavestorem.append(self.waves[h])

        for h in numba.prange(len(wavestorem)):
            self.waves.remove(wavestorem[h])

        self.time += 1

    def add_formul(self,s):
        ans = ""
        while len(s) != 0:
            if s[0] == "(":
                stgnf = ""
                s = s[1:]
                cou = 1
                pos = 0
                # print(s, "102")
                # print(pos)
                while cou != 0:
                    if s[pos] == "(":
                        cou += 1
                    elif s[pos] == ")":
                        cou -= 1
                    pos += 1
                    # print(s[pos])
                stgnf = s[:pos]
                s = s[pos:]
                stgnf = stgnf[:-1]
                # print(stgnf)
                self.add_formul(stgnf)
                ans = ans + "f" + str(len(self.formuls) - 1) + "a"
            elif s[0] == ")":
                s = s[1:]
            elif s[0] == " ":
                s = s[1:]
            else:
                ans = ans + s[0]
                s = s[1:]
        self.formuls.append(ans)

    def use_formul(self, f, count, mass, hp, x, y, z, t, mvx, mvy, mvz, mvt, mvl):
        ans = 0
        num = 0
        # print(f)

        if f[0] == "f":
            f = f[1:]
            n, f = get_num(f)
            num = self.use_formul(self.formuls[n], count, mass, hp, x, y, z, t, mvx, mvy, mvz, mvt, mvl)
        elif f[0] == "c":
            if f[1] != "o":
                num = count
                f = f[1:]
            elif f[1] == "o" and f[2] == "s": # cos
                f = f[4:]
                n, f = get_num(f)
                num = np.cos(self.use_formul(self.formuls[n], count, mass, hp, x, y, z, t, mvx, mvy, mvz, mvt, mvl))
            elif f[1] == "t" and f[2] == "g": # ctg
                f = f[4:]
                n, f = get_num(f)
                num = self.use_formul(self.formuls[n], count, mass, hp, x, y, z, t, mvx, mvy, mvz, mvt, mvl)
                num = np.cos(num) / np.sin(num)
        elif f[0] == "s" and f[1] == "i" and f[2] == "n":
            f = f[4:]
            n, f = get_num(f)
            num = np.sin(self.use_formul(self.formuls[n], count, mass, hp, x, y, z, t, mvx, mvy, mvz, mvt, mvl))
        elif f[0] == "t" and f[1] == "a" and f[2] == "n":
            f = f[4:]
            n, f = get_num(f)
            num = np.tan(self.use_formul(self.formuls[n], count, mass, hp, x, y, z, t, mvx, mvy, mvz, mvt, mvl))
        elif f[0] == "a" and f[1] == "b" and f[2] == "s":
            f = f[4:]
            n, f = get_num(f)
            num = np.abs(self.use_formul(self.formuls[n], count, mass, hp, x, y, z, t, mvx, mvy, mvz, mvt, mvl))
        elif f[0] == "m":
            num = mass
            f = f[1:]
        elif f[0] == "h":
            num = hp
            f = f[1:]
        elif f[0] == "x":
            num = x
            f = f[1:]
        elif f[0] == "y":
            num = y
            f = f[1:]
        elif f[0] == "z":
            num = z
            f = f[1:]
        elif f[0] == "t":
            num = t
            f = f[1:]
        elif f[0] == "r":
            f = f[1:]
            aa, f = get_num(f)
            bb, f = get_num(f)
            num = random.randint(aa, bb)
            # print(num)
        elif f[0] == "v":
            f = f[1:]
            if f[0] == "x":
                num = mvx
            elif f[0] == "y":
                num = mvy
            elif f[0] == "z":
                num = mvz
            elif f[0] == "t":
                num = mvt
            elif f[0] == "l":
                num = mvl
            f = f[1:]
        elif ord(f[0]) >= ord('0') and ord(f[0]) <= ord('9'):
            num, f = get_num(f)
        ans = num
        while len(f) != 0:
            sign = f[0]
            # print(f)
            f = f[1:]
            if f[0] == "/":
                sign = "//"
                f = f[1:]
            if f[0] == "*":
                sign = "**"
                f = f[1:]
            num = 0
            if f[0] == "f":
                f = f[1:]
                n, f = get_num(f)
                num = self.use_formul(self.formuls[n], count, mass, hp, x, y, z, t, mvx, mvy, mvz, mvt, mvl)
            elif f[0] == "c":
                if f[1] != "o":
                    num = count
                    f = f[1:]
                elif f[1] == "o" and f[2] == "s":  # cos
                    f = f[4:]
                    n, f = get_num(f)
                    num = np.cos(self.use_formul(self.formuls[n], count, mass, hp, x, y, z, t, mvx, mvy, mvz, mvt, mvl))
                elif f[1] == "t" and f[2] == "g":  # ctg
                    f = f[4:]
                    n, f = get_num(f)
                    num = self.use_formul(self.formuls[n], count, mass, hp, x, y, z, t, mvx, mvy, mvz, mvt, mvl)
                    num = np.cos(num) / np.sin(num)
            elif f[0] == "s" and f[1] == "i" and f[2] == "n":
                f = f[4:]
                n, f = get_num(f)
                num = np.sin(self.use_formul(self.formuls[n], count, mass, hp, x, y, z, t, mvx, mvy, mvz, mvt, mvl))
            elif f[0] == "a" and f[1] == "b" and f[2] == "s":
                f = f[4:]
                n, f = get_num(f)
                num = np.abs(self.use_formul(self.formuls[n], count, mass, hp, x, y, z, t, mvx, mvy, mvz, mvt, mvl))
            elif f[0] == "m":
                num = mass
                f = f[1:]
            elif f[0] == "h":
                num = hp
                f = f[1:]
            elif f[0] == "x":
                num = x
                f = f[1:]
            elif f[0] == "y":
                num = y
                f = f[1:]
            elif f[0] == "z":
                num = z
                f = f[1:]
            elif f[0] == "t":
                if f[1] != "a":
                    num = t
                    f = f[1:]
                elif f[1] == "a" and f[2] == "n":
                    f = f[4:]
                    n, f = get_num(f)
                    num = np.tan(self.use_formul(self.formuls[n], count, mass, hp, x, y, z, t, mvx, mvy, mvz, mvt, mvl))
            elif f[0] == "r":
                f = f[1:]
                aa, f = get_num(f)
                bb, f = get_num(f)
                num = random.randint(aa, bb)
                # print(num)
            elif f[0] == "v":
                f = f[1:]
                if f[0] == "x":
                    num = mvx
                elif f[0] == "y":
                    num = mvy
                elif f[0] == "z":
                    num = mvz
                elif f[0] == "t":
                    num = mvt
                elif f[0] == "l":
                    num = mvl
                f = f[1:]
            else:
                num, f = get_num(f)
            if sign == "+":
                ans += num
            elif sign == "-":
                ans -= num
            elif sign == "*":
                ans *= num
            elif sign == "/":
                ans /= num
            elif sign == "//":
                if ans < int(num):
                    ans = 0
                ans = ans // int(num)
            elif sign == "**":
                ans = ans ** num
            elif sign == "%":
                ans = ans % int(num)
        # print(ans)
        return ans

    def update_sim(self):
        for h in self.map:
            h[2].update(self)
