#!/.venv/bin/python3
import os
import sys
import time
import numpy as np
import numpy.linalg as lin
import matplotlib.pyplot as plt
import matplotlib.animation as anim
from pyquaternion import Quaternion

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from parcial1.clases import Punto, Subspace

sys.setrecursionlimit(100)

# from ..parcial1.clases import Punto, Subspace

# parametros bici (longitud en metros, angulos en grados,
# tiempo en segundos, velocidad angular en deg/s)
# (variable - seleccionar) angulo de inclinacion / roll
rho = 20  # [-45, 45]
# (variable - seleccionar) angulo manuvrio
phi = 10  # [-40, 40]
# (variable - seleccionar) velocidad angular rueda trasera
omega = 100  # [0.1, 100]
# (constante) longitud entre ruedas
l = 1  #
# (constante) radio ruedas
r = 0.5  # [0.25, 0.75]
# (constante) angulo de tenedor
beta = 20  # [0, 45]
# (variable - calculado) angulo pitch
psi = 0
# (variable - calculado) angulo visto desde arriba de rotacion
# de bici (b.az)
theta = 0
# (constante) tolerancia para decidir si rueda esta tocando piso
tolerancia = 0.001  # 0.001 (1mm)
# (constante - seleccionar) delta t, intervalo de tiempo entre escenas
dt = 1


piso = Subspace(0, 0, 0, 0, 0, 0, None, "piso")
# posiciones y angulo en y depende de posicion de la bici
b = Subspace(0, 0, 0, 0, 0, theta, piso, "b")
# posiciones de marco ab no cambian
# angulo cambia dependiendo de angulo de manuvrio (rueda delantera debe tocar piso)
ab = Subspace(0, 0, 0, 0, -psi, 0, b, "ab")
# posiciones de marco f no cambian
# angulo decidido por beta (angulo tenedor)
f = Subspace(l, 0, r, 0, -beta, 0, ab, "f")
# posiciones de marco af no cambian
# cambia dependiendo de rotacion manuvrio
af = Subspace(0, 0, 0, 0, 0, phi, f, "af")


def encontrarPuntoRuedaDelantera():
    """
    encuentra vector que va de centro_rueda delantera
    hasta el punto mas bajo de la rueda delantera con
    respecto al plano bx-by
    """
    Subspace.definirContexto(b)
    # coordenadas centro de rueda
    # un vector unitario en cordenada z negativo (hacia abajo)
    z_dn = np.array([0, 0, -1])
    # vectores para definir plano afx-afz en espacio base (v1 y v2)
    v1 = np.subtract(
        Punto(1, 0, 0, af).puntoAbs().p(), Punto(0, 0, 0, af).puntoAbs().p()
    )
    v2 = np.subtract(
        Punto(0, 0, 1, af).puntoAbs().p(), Punto(0, 0, 0, af).puntoAbs().p()
    )
    # time.sleep(1)
    # print("encontrarPuntoRuedaDelantera(), v1: {}".format(v1))
    # proyectar z_dn a plano v1-v2. Esta proyeccion se utiliza para encontrar el
    # punto mas bajo de la rueda (donde tocaria el piso)
    proy = v1 * (np.dot(v1, z_dn)) + v2 * (np.dot(v2, z_dn))
    # normalizar
    proy = proy / lin.norm(proy)
    # la linea que toca el piso en la rueda (spoke en rueda de bici)
    v3 = proy * r
    # v3 va de centro_rueda delantera
    return np.array(v3, float)


def ajustarPsi():
    """
    ajusta posicion para que rueda delantera toque el piso
    se corre cada vez que se modifica el manuvrio
    """
    Subspace.definirContexto(b)
    n = 0
    # cada vez angulo_rotacion /= 2, cada vez ajuste es menor
    angulo_rotacion = 20
    # correr maximo 10 veces
    while n < 20:
        # punto en centro de af (centro de rueda delantera)
        centro_rueda = Punto(0, 0, 0, f).puntoAbs().p()
        v3 = encontrarPuntoRuedaDelantera()
        # vector de origen a punto que deberia tocar piso (dentro de plano afx-afz)
        v4 = centro_rueda + v3
        # if n == 0:
        #     vectoar = v3
        #     print(
        #         "v2: [{}, {}, {}]".format(
        #             np.round(vectoar[0], 5),
        #             np.round(vectoar[1], 5),
        #             np.round(vectoar[2], 5),
        #         )
        #     )
        #     frame = b
        #     print(
        #         "b: [{}, {}, {}]".format(
        #             np.round(frame.x, 5),
        #             np.round(frame.y, 5),
        #             np.round(frame.z, 5),
        #         )
        #     )
        # si rueda de bici esta dentro de rango, no hay
        # necesidad de rotar bici, terminar de ajustar
        if np.abs(v4[2]) <= tolerancia:
            print("ajustarPsi(), v3: {}, centro rueda: {}".format(v3, centro_rueda))
            break
        # interseccion entre planos abz-abx y el plano formado por by-v4
        # el eje y del plano ab es ortogonal a abz-abx
        ort1 = np.subtract(
            Punto(0, 1, 0, ab).puntoAbs().p(), Punto(0, 0, 0, ab).puntoAbs().p()
        )
        b_y = np.subtract(
            Punto(0, 1, 0, b).puntoAbs().p(), Punto(0, 0, 0, b).puntoAbs().p()
        )
        ort2 = np.cross(b_y, v4)
        # v5 es interseccion de planos
        v5 = np.cross(ort1, ort2)
        v5 = v5 / lin.norm(v5)
        # v5 debe estar en direccion positiva respecto al eje x de b
        if v5[0] < 0:
            v5 = v5 * (-1)
        # # v6 -> proyeccion de v4 en v5
        # v6 = ((np.dot(v4, v5)) / lin.norm(v5) ** 2) * v5
        # # encontrar angulo entre v6 y eje x de ab
        # ab_x = Punto(1, 0, 0, ab).puntoAbs()[1].p()
        # angulo_rotacion = np.arccos(
        #     np.dot(ab_x, v6) / (lin.norm(ab_x) * lin.norm(v6)),
        # )
        # equis = np.array([1, 0, 0])
        # print(
        #     "angle between x and v6: "
        #     + str(
        #         np.arccos(
        #             np.dot(equis, v6) / (lin.norm(equis) * lin.norm(v6)),
        #         )
        #     )
        # )
        # coordenada z de v4 determina si toca rotar hacia
        # arriba o hacia abajo
        diff = v4[2]
        # rotar ab por angulo
        # angulo_rotacion += 5
        if diff < 0:
            ab.ay += angulo_rotacion
        elif diff > 0:
            ab.ay -= angulo_rotacion
        n += 1
        angulo_rotacion /= 2


def actualizarPosicion():
    """
    la bici se puede trasladar en el plano x-y
    y puede rotar en el eje z como eje
    """
    global theta

    Subspace.definirContexto(b)
    # la linea perpendicular a la rueda proyectada al plano
    # abx-aby siempre sera el mismo eje y en este plano
    # se encuentra entonces la proyeccion del vector perpendicular
    # a la rueda delantera en este mismo plano, el punto de
    # interseccion co el eje y en este plano, y asi el centro
    # instantaneo y la velocidad de este vector
    v3 = encontrarPuntoRuedaDelantera()
    Subspace.definirContexto(b)
    # representar plano bx-by
    v4 = Punto(1, 0, 0, b).puntoAbs().p()
    v5 = Punto(0, 1, 0, b).puntoAbs().p()
    # proyectar v3 a plano v4-v5
    proy = v4 * (np.dot(v4, v3)) + v5 * (np.dot(v5, v3))
    # angulo entre eje y de b y proy
    b_y = Punto(0, 1, 0, b).puntoAbs().p()
    centro_rueda = Punto(0, 0, 0, f).puntoAbs().p()
    v6 = centro_rueda + v3
    x1 = v6[0]
    y1 = v6[1]
    t = -x1 / proy[0]
    # radio del centro instantaneo de rotacion
    radio = x1 + proy[1] * t
    # angle_between = np.arccos(
    #     np.dot(direccion, [1, 0, 0]) / (lin.norm(direccion) * lin.norm([1, 0, 0])),
    # )
    # encontrar cantidad que se movera la bici
    # velocidad rueda trasera
    v_rueda_trasera = omega * r
    # velocidad angular de bicicleta vista desde arriba
    omega_centro_instantaneo = radio * v_rueda_trasera
    # cambio de angulo en dt
    dtheta = omega_centro_instantaneo * dt
    zQuat = Quaternion(axis=[0, 0, 1], degrees=dtheta)
    rotado = np.array(zQuat.rotate([0, v6[0] + radio, 0]))
    rotado = np.abs(rotado)
    dx = rotado[0]
    dy = -rotado[1] if phi < 0 else rotado[1]

    theta += dtheta
    if theta > 360:
        theta -= 360
    # b.x += 1
    # b.y += 1
    b.az += 95
    time.sleep(1)
    Subspace.definirContexto(f)
    # print(
    #     "YEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE"
    # )
    # print(
    #     "actualizarPosicion(), b: {}, b.angulos: {}, b->piso (start): {}, b->piso (vec): {}".format(
    #         b.vecOrigen(),
    #         [b.ax, b.ay, b.az],
    #         Punto(0, 0, 0, f).puntoAbs()[0].p(),
    #         Punto(0, 0, 0, f).puntoAbs()[1].p(),
    #     )
    # )
    # print(
    #     "ZZZZZZZZZZZYEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE"
    # )
    # exit()


# fig = plt.figure()
# ax = fig.add_subplot(1, 1, 1)
# x_data = []
# y_data = []
# (line,) = plt.plot(x_data, y_data)
# t = 0


# def update(frame):
#     actualizarPosicion()
#     ajustarPsi()
#     Subspace.definirContexto(b)
#     o_b = ab.vecOrigen()
#     # Subspace.definirContexto(ab)
#     pos2 = ab.vecOrigen()
#     # print("theta: {}".format(theta))
#     global x_data, y_data, t
#     t += dt
#     x_data.append(t)
#     y_data.append(theta)
#     x_data = x_data[-20:]
#     y_data = y_data[-20:]
#     # ax.clear()
#     # ax.plot(x_data, y_data)
#     plt.title("yeet")
#     plt.ylabel("FUCK")
#     plt.xlabel("tiempo [s]")
#     line.set_data(x_data, y_data)
#     fig.gca().relim()
#     fig.gca().autoscale_view()
#     return line


# animation = anim.FuncAnimation(fig, update, interval=50, cache_frame_data=False)  # type: ignore
# plt.show()

while True:
    ajustarPsi()
    actualizarPosicion()
    time.sleep(1)
    Subspace.definirContexto(None)
    pos = b.vecOrigen()
    # Subspace.definirContexto(ab)
    pos2 = ab.vecOrigen()
    time.sleep(1)
    # print("------------------------------")
    # print("b.x: {}, b.y: {}, b.z: {}".format(pos[0], pos[1], pos[2]))
    # print("ab.x: {}, ab.y: {}, ab.z: {}".format(pos2[0], pos2[1], pos2[2]))
