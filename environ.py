import pyphicus
import pygame.gfxdraw
import random
import numpy
import numba

def main():
    pygame.font.init()

    fieldx = 500
    fieldy = 500

    screen = pygame.display.set_mode((fieldx, fieldy), pygame.SCALED)
    screen.set_alpha(None)
    pygame.display.set_caption("Physics Engine")

    my_font = pygame.font.SysFont("arial", 15)

    screen.fill([0, 0, 0])
    pygame.display.flip()

    simul = pyphicus.Simulation()

    simul.load_settings("Phis_rul\\set_3")

    paused = False


    clock = pygame.time.Clock()
    FPS = 60  # кадры  в секунду
    running = True  # значение работы программы
    move_up = False
    move_down = False
    move_right = False
    move_left = False
    shift = False
    ctrl = False

    mappos = 0
    cur_mat = 0
    cur_en = 0
    r_s = 10
    start_en = 100
    start_eps = 10
    start_dir = 1
    list_of_act_pos = 0

    ensum = 0

    simul.update_sim()

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
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_RIGHT:
                    list_of_act_pos += 1
                    if list_of_act_pos > 5:
                        list_of_act_pos = 0
                if event.key == pygame.K_LEFT:
                    list_of_act_pos -= 1
                    if list_of_act_pos < 0:
                        list_of_act_pos = 5
                if event.key == pygame.K_UP:
                    if list_of_act_pos == 0:
                        cur_mat += 1
                        if cur_mat > len(simul.materials) - 1:
                            cur_mat = 0
                    elif list_of_act_pos == 1:
                        cur_en += 1
                        if cur_en > len(simul.energies) - 1:
                            cur_en = 0
                    elif list_of_act_pos == 2:
                        start_en += 1
                    elif list_of_act_pos == 3:
                        start_eps += 1
                    elif list_of_act_pos == 4:
                        start_dir *= -1
                    elif list_of_act_pos == 5:
                        r_s += 1
                if event.key == pygame.K_DOWN:
                    if list_of_act_pos == 0:
                        cur_mat -= 1
                        if cur_mat < 0:
                            cur_mat = len(simul.materials) - 1
                    elif list_of_act_pos == 1:
                        cur_en -= 1
                        if cur_en < 0:
                            cur_en = len(simul.energies) - 1
                    elif list_of_act_pos == 2:
                        start_en -= 1
                    elif list_of_act_pos == 3:
                        start_eps -= 1
                    elif list_of_act_pos == 4:
                        start_dir *= -1
                    elif list_of_act_pos == 5:
                        r_s -= 1
                if event.key == pygame.K_LSHIFT:
                    shift = True
                if event.key == pygame.K_LCTRL:
                    ctrl = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    move_up = False
                if event.key == pygame.K_s:
                    move_down = False
                if event.key == pygame.K_d:
                    move_right = False
                if event.key == pygame.K_a:
                    move_left = False
                if event.key == pygame.K_LSHIFT:
                    shift = False
                if event.key == pygame.K_LCTRL:
                    ctrl = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                m_p = pygame.mouse.get_pos()
                if event.button == 1:
                    if shift:
                        simul.raden.append(pyphicus.Radial_Energy(r_s,m_p[0],0,m_p[1],cur_en,start_en,start_eps,start_dir))
                    elif ctrl:
                        simul.waves.append(
                            pyphicus.Energy_Wave(pyphicus.vector_3D(0,0,0),cur_en,start_en,m_p[0],0,m_p[1],start_eps))
                    else:
                        simul.add_object(pyphicus.Object(m_p[0], m_p[1], cur_mat, 100, simul))
                        simul.map[-1][2].t = simul.time

                if event.button == 4:
                    mappos += 1
                    if mappos > len(simul.map) - 1:
                        mappos = 0

        if move_up:
            simul.map[mappos][1] -= 2
            simul.map[mappos][2].y -= 2
        if move_down:
            simul.map[mappos][1] += 2
            simul.map[mappos][2].y += 2
        if move_left:
            simul.map[mappos][0] -= 2
            simul.map[mappos][2].x -= 2
        if move_right:
            simul.map[mappos][0] += 2
            simul.map[mappos][2].x += 2

        screen.fill([255, 255, 255])

        if not paused:
            simul.cadr()

        if len(simul.map) > 0:
            pygame.gfxdraw.circle(screen, int(simul.map[mappos][2].x), int(simul.map[mappos][2].y), 5, [255, 0, 0])

        for h in numba.prange(len(simul.waves)):
            pygame.gfxdraw.circle(screen, int(simul.waves[h].x), int(simul.waves[h].z), 5, simul.energies[simul.waves[h].energy].color)
            #f3menu3 = my_font.render(str(simul.waves[h].count), True, simul.energies[simul.waves[h].energy].color)
            #screen.blit(f3menu3, (simul.waves[h].x, simul.waves[h].z - 10))

        for h in numba.prange(len(simul.raden)):
            pygame.gfxdraw.circle(screen, int(simul.raden[h].x), int(simul.raden[h].z), simul.raden[h].r, simul.energies[simul.raden[h].energy].color)
            '''f3menu3 = my_font.render(str(simul.raden[h].count), True, simul.energies[simul.raden[h].energy].color)
            screen.blit(f3menu3, (simul.raden[h].x, simul.raden[h].z - 10))'''

        for h in numba.prange(len(simul.map)):
            if simul.time == simul.map[h][2].t:
                pygame.draw.circle(screen, simul.materials[simul.map[h][2].material].color, (simul.map[h][0], simul.map[h][1]), 5)
                ul = 0
                '''for k in range(len(simul.energies)):
                    f3menu3 = my_font.render(str(simul.map[h][2].energy[k]), True, simul.energies[k].color)
                    screen.blit(f3menu3, (simul.map[h][0] + ul * 15, simul.map[h][1] - 10))
                    ensum += simul.map[h][2].energy[k]
                    ul += len(str(simul.map[h][2].energy[k]))'''

        pygame.draw.rect(screen,simul.materials[cur_mat].color,(fieldx - 30,10,20,20))
        pygame.draw.rect(screen, simul.energies[cur_en].color, (fieldx - 30, 40, 20, 20))
        f3menu3 = my_font.render(str(start_en), True, [0,0,0])
        screen.blit(f3menu3, (fieldx - 30, 60))
        f3menu3 = my_font.render(str(start_eps), True, [0, 0, 0])
        screen.blit(f3menu3, (fieldx - 30, 80))
        f3menu3 = my_font.render(str(start_dir), True, [0, 0, 0])
        screen.blit(f3menu3, (fieldx - 30, 100))
        f3menu3 = my_font.render(str(r_s), True, [0, 0, 0])
        screen.blit(f3menu3, (fieldx - 30, 120))

        f3menu3 = my_font.render("FPS - " + str(round(clock.get_fps())), True, [0, 0, 0])
        screen.blit(f3menu3, (10, 30))
        f3menu3 = my_font.render("energysum - " + str(simul.ensum), True, [0, 0, 0])
        screen.blit(f3menu3, (10, 10))
        ensum = 0

        pygame.display.flip()

if __name__ == '__main__':
    main()
