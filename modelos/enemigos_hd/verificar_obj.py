"""Verifica los .obj exportados (lo que realmente se importa en Roblox), sin confiar en el generador.

Por cada archivo: lee vértices y caras, separa cada objeto en piezas conectadas y revisa que
cada pieza sea cerrada y manifold, que sus normales apunten hacia afuera (volumen > 0), que no
haya triángulos degenerados ni caras coplanares superpuestas entre piezas, y que el total no
pase de 20.000 triángulos ni 20.000 vértices.

Uso: python verificar_obj.py            (revisa las 5 carpetas *_hd)
"""
import glob
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from malla import Shell, revisar  # noqa: E402


def leer_obj(path):
    V, objetos, actual = [], {}, None
    for line in open(path):
        if line.startswith("v "):
            V.append([float(x) for x in line.split()[1:4]])
        elif line.startswith("o "):
            actual = line.split(maxsplit=1)[1].strip()
            objetos[actual] = []
        elif line.startswith("f "):
            idx = [int(t.split("/")[0]) - 1 for t in line.split()[1:]]
            for i in range(1, len(idx) - 1):                     # por si hubiera polígonos: abanico
                objetos[actual].append([idx[0], idx[i], idx[i + 1]])
    return np.array(V), {k: np.array(v) for k, v in objetos.items()}


def piezas(F):
    """Componentes conectadas por vértices compartidos (union-find)."""
    parent = {}

    def find(a):
        while parent.setdefault(a, a) != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for a, b, c in F:
        ra, rb, rc = find(a), find(b), find(c)
        parent[rb] = ra
        parent[find(rc)] = ra
    roots = np.array([find(a) for a in F[:, 0]])
    return [F[roots == r] for r in np.unique(roots)]


def verificar(path):
    V, objetos = leer_obj(path)
    shells, por_obj = [], {}
    for nombre, F in objetos.items():
        comps = piezas(F)
        por_obj[nombre] = (len(F), len(comps))
        shells += [Shell(V, c, nombre) for c in comps]
    ok, info = revisar(shells)
    info["vertices"] = len(V)                                   # vértices reales del archivo
    if info["vertices"] > 20000:
        ok = False
        info["problemas"].append(f"{len(V)} vértices en el archivo")
    return ok, info, por_obj


if __name__ == "__main__":
    todo_ok = True
    for path in sorted(glob.glob(os.path.join(HERE, "*_hd", "*_hd.obj"))):
        ok, info, por_obj = verificar(path)
        todo_ok &= ok
        print(f"{'OK ' if ok else 'MAL'} {os.path.basename(path):26s} {info['triangulos']:6d} tri  {info['vertices']:6d} vért  "
              f"{info['piezas']:4d} piezas cerradas  " + " ".join(f"{k}:{v[0]}" for k, v in por_obj.items()))
        for p in info["problemas"]:
            print("      ", p)
    sys.exit(0 if todo_ok else 1)
