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

base = Subspace(0, 0, 0, 0, 0, 0, None, "base")
sub1 = Subspace(1, 1, 0, 0, 0, 45, base, "sub1")
sub2 = Subspace(1, 1, 0, 0, 0, -45, sub1, "sub2")

Subspace.definirContexto(sub1)

p1 = Punto(1, 1, 0, sub1)

print(
    "\n\np1, subspace {} context {}: {}\n\n".format(
        p1.parentSpace.nombre if p1.parentSpace else None,
        Subspace.getNombreContexto(),
        p1.puntoAbs().p(),
    )
)

Subspace.definirContexto(base)

p2 = Punto(1, 1, 0, sub2)

print(
    "\n\np1, subspace {}, context {}: {}\n\n".format(
        p1.parentSpace.nombre if p1.parentSpace else None,
        Subspace.getNombreContexto(),
        p1.puntoAbs().p(),
    )
)

print(
    "\n\np2, subspace {}, context {}: {}\n\n".format(
        p2.parentSpace.nombre if p2.parentSpace else None,
        Subspace.getNombreContexto(),
        p2.puntoAbs().p(),
    )
)
