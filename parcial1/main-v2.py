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
rho = 40  # [-45, 45]
# (variable - seleccionar) angulo manuvrio
phi = 2  # [-40, 40]
# (variable - seleccionar) velocidad angular rueda trasera
omega = 100  # [0.1, 100]
# (constante) longitud entre ruedas
l = 1  #
# (constante) radio ruedas
r = 0.5  # [0.25, 0.75]
# (constante) angulo de tenedor
beta = 0  # [0, 45]
# (variable - calculado) angulo pitch
psi = 0
# (variable - calculado) angulo visto desde arriba de rotacion
# de bici (b.az)
theta = 0
# (constante) tolerancia para decidir si rueda esta tocando piso
tolerancia = 0.0001  # 0.001 (1mm)
# (constante - seleccionar) delta t, intervalo de tiempo entre escenas
dt = 1


piso = Subspace(0, 0, 0, 0, 0, 0, None, "piso")
# posiciones y angulo en y depende de posicion de la bici
b = Subspace(0, 0, 0, 0, 0, theta, piso, "b")
# posiciones de marco ab no cambian
# angulo cambia dependiendo de angulo de manuvrio (rueda delantera debe tocar piso)
ab = Subspace(0, 0, 0, rho, -psi, 0, b, "ab")
# posiciones de marco f no cambian
# angulo decidido por beta (angulo tenedor)
f = Subspace(l, 0, r, 0, beta, 0, ab, "f")
# posiciones de marco af no cambian
# cambia dependiendo de rotacion manuvrio
af = Subspace(0, 0, 0, 0, 0, -phi, f, "af")


def encontrarPuntoRuedaDelantera():
    """
    encuentra vector que va de centro_rueda delantera
    hasta el punto mas bajo de la rueda delantera con
    respecto al plano bx-by
    """
    Subspace.definirContexto(b)
    # coordenadas centro de rueda
    # un vector unitario en cordenada z negativo (hacia abajo)
    dn = np.array([0, 0, -1])
    # vectores para definir plano afx-afz en espacio base (v1 y v2)
    v1 = np.subtract(
        Punto(1, 0, 0, af).puntoAbs().p(), Punto(0, 0, 0, af).puntoAbs().p()
    )
    v2 = np.subtract(
        Punto(0, 0, 1, af).puntoAbs().p(), Punto(0, 0, 0, af).puntoAbs().p()
    )
    # proyectar dn a plano v1-v2. Esta proyeccion se utiliza para encontrar el
    # punto mas bajo de la rueda (donde tocaria el piso)
    proy = np.array(v1 * (np.dot(v1, dn)) + v2 * (np.dot(v2, dn)))
    # normalizar
    proy = proy / lin.norm(proy)
    # v3 es el punto donde la rueda deberia tocar el piso
    v3 = Punto(0, 0, 0, f).puntoAbs().p() + proy * r
    # print("v3: {}".format(v3))

    return v3


def ajustarPsi():
    """
    ajusta posicion para que rueda delantera toque el piso
    se corre cada vez que se modifica el manuvrio
    """
    n = 0
    # cada vez angulo_rotacion /= 2, cada vez ajuste es menor
    angulo_rotacion = 20
    # correr maximo 10 veces
    while n < 20:
        # punto en centro de af (centro de rueda delantera)
        Subspace.definirContexto(b)
        centro_rueda = Punto(0, 0, 0, f).puntoAbs().p()
        # print("centro rueda: {}".format(centro_rueda))
        v3 = encontrarPuntoRuedaDelantera()
        # si rueda de bici esta dentro de rango, no hay
        # necesidad de rotar bici, terminar de ajustar
        if np.abs(v3[2]) <= tolerancia:
            # print("v3: {}".format(v3))
            break

        # rotar ab por angulo
        # angulo_rotacion += 5
        if v3[2] < 0:
            ab.ay += angulo_rotacion
        elif v3[2] > 0:
            ab.ay -= angulo_rotacion
        n += 1
        angulo_rotacion /= 2


valores_tiempo = []
valores_velocidad_x = []
valores_velocidad_y = []
valores_x = []
valores_y = []
valores_theta = []
t = 0
# definir velocidades angulares simples
# luego se pueden sumar y determinar la velocidad angular de cualquier punto

# volver a mirar el jueves


def actualizarPosicion():
    """
    la bici se puede trasladar en el plano x-y
    y puede rotar en el eje z como eje
    """
    global theta

    if np.abs(phi) <= 0.00001:
        # si manuvrio esta recto, se esta hiendo en linea recta
        pass

    Subspace.definirContexto(b)
    # v1 es afy proyectado en el plano bx-by
    v1 = Punto(0, 1, 0, af).puntoAbs().p() - Punto(0, 0, 0, af).puntoAbs().p()
    bx = Punto(1, 0, 0, b).puntoAbs().p()
    by = Punto(0, 1, 0, b).puntoAbs().p()
    v1 = bx * (np.dot(bx, v1)) + by * (np.dot(by, v1))
    # angulo entre v1 y by, rads
    a_between = np.abs(np.arccos(by.dot(v1) / (lin.norm(by) * lin.norm(v1))))
    # v2 es el centro de la rueda delantera proyectado en bx-by
    v2 = Punto(0, 0, 0, af).puntoAbs().p()
    v2 = bx * (np.dot(bx, v2)) + by * (np.dot(by, v2))
    # d es distancia entre centros de ruedas
    d = np.abs(lin.norm(v2))
    # con a_between y d se resuelve el radio de centro instantaneo - law of sines
    # (d es base de triangulo isoceles y a_between es angulo opuesto)
    r_centro_instantaneo = d * np.sin((np.pi - a_between) / 2) / np.sin(a_between)
    print("r_centro_instantaneo: {}".format(r_centro_instantaneo))

    # FIXME: si esta bien??? no creo que se pueda asumir que
    # es triangulo isoceles
    ##

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
    # print("dtheta: {}, radio: {}, v3: {}, proy: {}".format(dtheta, radio, v3, proy))
    # print("v3: {}, proy: {}".format(v3, proy))

    zQuat = Quaternion(axis=[0, 0, 1], degrees=dtheta)
    rotado = np.array(zQuat.rotate([0, v6[0] + radio, 0]))
    rotado = np.abs(rotado)
    dx = rotado[0]
    dy = rotado[1]

    # vector de velocidad
    v7 = Punto(1, 0, 0, b).puntoAbs().p()
    v7 = v7 / lin.norm(v7)
    v7 = np.multiply(v7, v_rueda_trasera)
    # vector de velocidad en mitad de bicicleta
    v8 = Punto(1, 0, 0, b).puntoAbs().p()
    v8 = v8 / lin.norm(v8)
    rot = Quaternion(axis=[0, 0, 1], degrees=dtheta)
    v8 = rot.rotate(v8)
    v8 = None

    theta += dtheta
    valores_theta.append(theta)
    valores_velocidad_x.append(v_rueda_trasera * np.cos(np.deg2rad(theta)))
    valores_velocidad_y.append(v_rueda_trasera * np.sin(np.deg2rad(theta)))
    if abs(theta) > 360:
        theta %= 360
    b.x += 10 * np.cos(np.deg2rad(b.az))
    b.y += 10 * np.sin(np.deg2rad(b.az))
    b.az = theta
    valores_x.append(b.x)
    valores_y.append(b.y)
    Subspace.definirContexto(piso)
    global valores_tiempo


# fig = plt.figure()
# # set the spacing between subplots
# plt.subplots_adjust(
#     left=0.1,
#     bottom=0.1,
#     right=0.9,
#     top=0.9,
#     wspace=0.4,
#     hspace=0.4,
# )
# g1 = fig.add_subplot(2, 3, 1)
# g2 = fig.add_subplot(2, 3, 4)
# g3 = fig.add_subplot(2, 3, 2)
# g4 = fig.add_subplot(2, 3, 5)
# g5 = fig.add_subplot(2, 3, 3)
# g6 = fig.add_subplot(2, 3, 6)
# (line,) = plt.plot(valores_tiempo, valores_velocidad_x)
# (l1,) = g1.plot(valores_tiempo, valores_x)
# (l2,) = g2.plot(valores_tiempo, valores_x)
# (l3,) = g3.plot(valores_tiempo, valores_velocidad_x)
# (l4,) = g4.plot(valores_tiempo, valores_velocidad_y)
# (l5,) = g5.plot(valores_x, valores_y)
# (l6,) = g6.plot(valores_tiempo, valores_velocidad_y)


# def update(frame):
#     time.sleep(0.1)
#     # ajustar psi y posicion
#     ajustarPsi()
#     actualizarPosicion()

#     global t, valores_tiempo, valores_velocidad_x, valores_velocidad_y, valores_x, valores_y, valores_theta
#     t += dt
#     valores_tiempo.append(t)

#     n_elementos = 20
#     valores_tiempo = valores_tiempo[-n_elementos:]
#     valores_velocidad_x = valores_velocidad_x[-n_elementos:]
#     valores_velocidad_y = valores_velocidad_y[-n_elementos:]
#     valores_x = valores_x[-n_elementos:]
#     valores_y = valores_y[-n_elementos:]
#     valores_theta = valores_theta[-n_elementos:]
#     # ax.clear()
#     # ax.plot(x_data, y_data)
#     # plt.title("valores")
#     # plt.ylabel("velocidad en y [m/s]")
#     # plt.xlabel("tiempo [s]")
#     # fig.gca().relim()
#     # fig.gca().autoscale_view()
#     # line.set_data(valores_tiempo, valores_velocidad_x)
#     # vel x
#     g1.set_xlabel("tiempo [s]")
#     g1.set_ylabel("pos en x [m]")
#     g1.set_title("pos en x")
#     l1.set_data(valores_tiempo, valores_x)
#     g1.relim()
#     g1.autoscale_view()
#     # vel x
#     g2.set_xlabel("tiempo [s]")
#     g2.set_ylabel("pos en y [m]")
#     g2.set_title("pos en y")
#     l2.set_data(valores_tiempo, valores_y)
#     g2.relim()
#     g2.autoscale_view()
#     # vel x
#     g3.set_xlabel("tiempo [s]")
#     g3.set_ylabel("velocidad en x [m/s]")
#     g3.set_title("velocidad en x")
#     l3.set_data(valores_tiempo, valores_velocidad_x)
#     g3.relim()
#     g3.autoscale_view()
#     # vel x
#     g4.set_xlabel("tiempo [s]")
#     g4.set_ylabel("velocidad en y [m/s]")
#     g4.set_title("velocidad en y")
#     l4.set_data(valores_tiempo, valores_velocidad_y)
#     g4.relim()
#     g4.autoscale_view()
#     # vel x
#     g5.set_xlabel("pos x [m]")
#     g5.set_ylabel("pos y [m]")
#     g5.set_title("trayectoria")
#     l5.set_data(valores_x, valores_y)
#     g5.relim()
#     g5.autoscale_view()
#     # vel x
#     g6.set_xlabel("tiempo [s]")
#     g6.set_ylabel("velocidad en y [m/s]")
#     g6.set_title("velocidad en y")
#     l6.set_data(valores_tiempo, valores_velocidad_y)
#     g6.relim()
#     g6.autoscale_view()

#     return line


# animation = anim.FuncAnimation(fig, update, interval=50, cache_frame_data=False)  # type: ignore
# plt.show()

while True:
    # ajustar psi y posicion
    ajustarPsi()
    actualizarPosicion()
    time.sleep(1)
