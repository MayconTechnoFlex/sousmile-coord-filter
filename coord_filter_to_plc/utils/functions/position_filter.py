"""

Modulo de fórmula para filtrar pontos

"""

from utils.data.comm_plc import read_tags
from utils.functions.calc_functions import *


def pos_filter(in_data, lx, ly, lz, lc, ld, l_pos, l_info, tag_cut_depth, tag_enable_log):
    print('- Iniciando filtro de posições')
    n1, n2, n3 = 0, 0, 0

    limit_D = read_tags('ConfigPontos.Diff_AngleD')
    limit_C = read_tags('ConfigPontos.Diff_AngleC')
    limit_XYZ = read_tags('ConfigPontos.Dist_XYZ')
    limit_h = read_tags('ConfigPontos.Dist_H')
    p = read_tags(tag_cut_depth)

    #  Linha de limites com valores fixos para teste
    '''limit_D = 25
    limit_C = 15
    limit_XYZ = 4
    limit_h = 0.05
    p = 1.0'''

    print(f'''
    - Ajustes para filtro de posição:
    - Diferença do ângulo D: {limit_D};
    - Diferença do ângulo C: {limit_C};
    - Distância entre pontos: {limit_XYZ};
    - Profundidade entre os 3 pontos: {round(limit_h, 3)};
    - Profundidade de corte: {round(p, 3)};
            ''')

    for i in range(len(in_data.index)):

        if i + 2 < len(in_data.index):
            if i == 0:
                dist_XYZ = dist_between_points(in_data, i, i + 1)  # Calculates distance between points
                D1 = calc_attack_angle(in_data, i)  # Calculates attack angle
                D2 = calc_attack_angle(in_data, i + 1)  # Calculates attack angle of the next point
                difference_D = D2 - D1  # Calculates the attack angle difference between the points
                difference_C = calc_diff_c_angle(in_data, i, i + 1)  # Calc the difference between two angles C
                a = dist_between_points(in_data, i, i + 1)  # Side "a" of the triangle
                b = dist_between_points(in_data, i, i + 2)  # Side "b" of the triangle
                c = dist_between_points(in_data, i + 1, i + 2)  # Side "c" of the triangle

                # Clear the lists
                lx.clear()
                ly.clear()
                lz.clear()
                lc.clear()
                ld.clear()
                l_pos.clear()
                l_info.clear()

                # Start to save data into the lists
                lx.append(round(cut_depth_x(in_data, i, p), 1))
                ly.append(round(cut_depth_y(in_data, i, p), 1))
                lz.append(round(cut_depth_z(in_data, i, p), 1))
                ld.append(round(D1, 1))

                # Check if the limits of "C" are between 180 and -180
                if round(float(in_data.values[i][5].replace('C=', ''))) > 180:
                    lc.append(180)
                elif round(float(in_data.values[i][5].replace('C=', ''))) < -180:
                    lc.append(-180)
                else:
                    lc.append(round(float(in_data.values[i][5].replace('C=', ''))))

                l_pos.append(i)

                l_info.append(f'Ponto adicionado por ser o primeiro da lista')

            else:
                dist_XYZ = dist_between_points(in_data, n1, n2)  # Calc distance between points
                D1 = calc_attack_angle(in_data, n1)  # Calculates attack angle
                D2 = calc_attack_angle(in_data, n2)  # Calculates attack angle of the next point
                difference_D = D2 - D1  # Calculates the attack angle difference between the points
                difference_C = calc_diff_c_angle(in_data, n1, n2)  # Calc the difference between two angles C
                a = dist_between_points(in_data, n1, n2)  # Side "a" of the triangle
                b = dist_between_points(in_data, n1, n3)  # Side "b" of the triangle
                c = dist_between_points(in_data, n2, n3)  # Side "c" of the triangle

            #  Triangle height - Triângulo criado por três pontos para criar um filtro da profundidade do corte
            h = triangle_height(a, b, c)

            if abs(difference_D) <= limit_D and abs(difference_C) <= limit_C and h <= limit_h and dist_XYZ <= limit_XYZ:

                n1 = n1
                n2 = (i + 2)
                n3 = (i + 3)

            # Difference filter
            else:
                if abs(difference_D) > limit_D and abs(difference_C) < limit_C and h < limit_h and dist_XYZ < limit_XYZ:
                    l_info.append(f'Limite D: {round(difference_D, 1)}')
                elif abs(difference_D) < limit_D and abs(
                        difference_C) > limit_C and h < limit_h and dist_XYZ < limit_XYZ:
                    l_info.append(f'Limite C: {round(difference_C, 1)}')
                elif abs(difference_D) < limit_D and abs(
                        difference_C) < limit_C and h > limit_h and dist_XYZ < limit_XYZ:
                    l_info.append(f'Limite H: {round(h, 3)}')
                elif abs(difference_D) < limit_D and abs(
                        difference_C) > limit_C and h > limit_h and dist_XYZ < limit_XYZ:
                    l_info.append(
                        f'Limite H e C: {round(h, 3)}/ {round(difference_C, 1)})')
                elif abs(difference_D) > limit_D and abs(
                        difference_C) < limit_C and h > limit_h and dist_XYZ < limit_XYZ:
                    l_info.append(
                        f'Limite H e D: {round(h, 3)}/ {round(difference_D, 1)}')
                elif abs(difference_D) > limit_D and abs(
                        difference_C) > limit_C and h < limit_h and dist_XYZ < limit_XYZ:
                    l_info.append(
                        f'Limite C e D: {round(difference_C, 1)}/ {round(difference_D, 1)}')
                elif abs(difference_D) > limit_D and abs(
                        difference_C) > limit_C and h < limit_h and dist_XYZ < limit_XYZ:
                    l_info.append(
                        f'Limite C e D: {round(difference_C, 1)}/ {round(difference_D, 1)}')
                elif abs(difference_D) < limit_D and abs(
                        difference_C) < limit_C and h < limit_h and dist_XYZ > limit_XYZ:
                    l_info.append(
                        f'Limite XYZ: {round(dist_XYZ, 1)}')
                elif abs(difference_D) > limit_D and abs(
                        difference_C) < limit_C and h < limit_h and dist_XYZ > limit_XYZ:
                    l_info.append(
                        f'Limite XYZ e D: {round(dist_XYZ, 1)}/ {round(difference_D, 1)}')
                elif abs(difference_D) < limit_D and abs(
                        difference_C) > limit_C and h < limit_h and dist_XYZ > limit_XYZ:
                    l_info.append(
                        f'Limite XYZ e C: {round(dist_XYZ, 1)}/ {round(difference_C, 1)}')
                elif abs(difference_D) < limit_D and abs(
                        difference_C) < limit_C and h > limit_h and dist_XYZ > limit_XYZ:
                    l_info.append(
                        f'Limite XYZ e C: {round(dist_XYZ, 1)}/ {round(h, 3)}')
                else:
                    l_info.append(
                        f'''
                             Todos os limites: H:{round(h, 3)}/ C:{round(difference_C, 1)}/
                             D:{round(difference_D, 1)}/ XYZ:{round(dist_XYZ, 1)}''')

                lx.append(round(cut_depth_x(in_data, i + 1, p), 1))
                ly.append(round(cut_depth_y(in_data, i + 1, p), 1))
                lz.append(round(cut_depth_z(in_data, i + 1, p), 1))
                ld.append(round(calc_attack_angle(in_data, (i + 1)), 1))

                # Check if the limits of "C" are between 180 and -180
                if round(float(in_data.values[i + 1][5].replace('C=', '')), 1) > 180:
                    lc.append(180)
                elif round(float(in_data.values[i + 1][5].replace('C=', '')), 1) < -180:
                    lc.append(-180)
                else:
                    lc.append(round(float(in_data.values[i + 1][5].replace('C=', '')), 1))

                n1 = i + 1
                n2 = n1 + 1
                n3 = n1 + 2

                l_pos.append(i + 1)

        else:
            print('- Terminando de filtrar posições')

            for _ in range(5):
                lx.append(round(cut_depth_x(in_data, l_pos[_], p), 1))
                ly.append(round(cut_depth_y(in_data, l_pos[_], p), 1))
                lz.append(round(cut_depth_z(in_data, l_pos[_], p), 1))
                ld.append(round(calc_attack_angle(in_data, l_pos[_]), 1))

                # Check if the limits of "C" are between 180 and -180
                if round(float(in_data.values[l_pos[_]][5].replace('C=', '')), 1) > 180:
                    lc.append(180)
                elif round(float(in_data.values[l_pos[_]][5].replace('C=', '')), 1) < -180:
                    lc.append(-180)
                else:
                    lc.append(round(float(in_data.values[l_pos[_]][5].replace('C=', '')), 1))

                l_pos.append(l_pos[_])
                l_info.append(f'Ponto adicionado para terminar o ciclo')

            break
