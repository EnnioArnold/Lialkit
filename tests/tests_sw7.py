#!/usr/bin/env python3
"""Tests für SW 7 (Skalarprodukt, orthogonale Abbildungen, homogene Koordinaten). Aufruf: python3 tests/tests_sw7.py"""
import os
import random
import sys
from fractions import Fraction

os.environ.setdefault("MPLBACKEND", "Agg")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

import lialkit as lk
from lialkit.aufgaben.exercises import aufgabe, liste, loese
from lialkit.grafik.plots_projektion import plot_skalarprodukt
from lialkit.rechnen.abbildung import (BUCHSTABE_F_FOLIEN, drehung, homogen, scherung,
                                       skalierung, spiegelung_x, verschiebung, zusammensetzen)
from lialkit.rechnen.core import Matrix, Vector
from lialkit.rechnen.homogen_3d import drehung_3d, abbildung_um_zentrum, drehung_um_zentrum, verschiebung_3d
from lialkit.rechnen.skalarprodukt import (laenge, normieren, pruefe_orthogonal,
                                           senkrechter_vektor, skalarprodukt)

FAILS = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)
        print("  FEHLER:", msg)


def vec(rows):
    return [int(r[0]) for r in rows]


print("Länge, Normieren (Folien 5, 6)")
check(laenge([4, 3]).laenge == 5, "|(4,3)| = 5")
check(laenge([4, 3]).quadrat == 25, "|a|² = 25")
check(abs(laenge([1, 1]).laenge - 2 ** 0.5) < 1e-12, "|(1,1)| = √2")
n = normieren([4, 3])
check(n.a0 == Vector([Fraction(4, 5), Fraction(3, 5)]), "a⁰ = (4/5, 3/5)")
check(n.a0.norm() == 1, "|a⁰| = 1")
check(abs(float(normieren([1, 1]).a0.norm()) - 1) < 1e-8, "irrational normiert")
try:
    normieren([0, 0])
    check(False, "Nullvektor normieren")
except ValueError:
    pass
check(repr(n) and n.latex() and laenge([4, 3])._repr_html_(), "Anzeige")

print("Senkrechter Vektor (Folie 15)")
s1, s2 = senkrechter_vektor([4, 3])
check(s1 == Vector([-3, 4]) and s2 == Vector([3, -4]), "(−a₂, a₁), (a₂, −a₁)")
check(s1.dot(Vector([4, 3])) == 0 and s2.dot(Vector([4, 3])) == 0, "senkrecht")

print("Skalarprodukt (Folien 7–15)")
sp = skalarprodukt([1, 2], [3, -1])
check(sp.wert == 1 and "kleiner als 90" in sp.art, "(1,2)·(3,−1) = 1")
check(abs(sp.proj_a_auf_b - 1 / 10 ** 0.5) < 1e-12, "a_b = a·b/|b|")
check(abs(sp.winkel - 81.8699) < 1e-3, "Winkel")
check("senkrecht" in skalarprodukt([1, 2], [-2, 1]).art, "a·b = 0 senkrecht")
check("gleiche Richtung" in skalarprodukt([1, 2], [2, 4]).art, "parallel")
check("entgegengesetzte" in skalarprodukt([1, 2], [-2, -4]).art, "antiparallel")
check("grösser als 90" in skalarprodukt([1, 0], [-1, 1]).art, "stumpf")
check(skalarprodukt([0, 0], [1, 2]).winkel is None, "Nullvektor: kein Winkel")
check(skalarprodukt([1, 2, 3], [4, 5, 6]).wert == 32, "Rⁿ: 4 + 10 + 18")
# Folie 12: Kommutativ-, Distributiv- und gemischtes Assoziativgesetz, Folie 15: a·a = |a|²
rnd = random.Random(7)
for _ in range(20):
    a, b, c = (Vector([rnd.randint(-9, 9) for _ in range(3)]) for _ in range(3))
    k = rnd.randint(-5, 5)
    ok = (a.dot(b) == b.dot(a) and (a + b).dot(c) == a.dot(c) + b.dot(c)
          and (a * k).dot(b) == k * a.dot(b) and a.dot(a) == laenge(a).quadrat)
    check(ok, f"Rechenregeln {a} {b} {c}")
    check(skalarprodukt(a, b).wert == a.dot(b), "skalarprodukt = dot")

print("Orthogonale Abbildungen (Folie 17)")
for name, M, det_ in (("Drehung 90°", drehung(90), 1), ("Drehung 30°", drehung(30), 1),
                      ("Spiegelung x", spiegelung_x(), -1), ("Spiegelung 30°", lk.spiegelung_achse(30), -1)):
    r = pruefe_orthogonal(M)
    check(bool(r) and round(float(r.det)) == det_, f"{name} orthogonal, det {det_}")
    check(r.A.T @ r.A is not None and ("Drehung" in r.art) == (det_ == 1), f"{name}: Einordnung")
check(not pruefe_orthogonal(skalierung(2)), "Skalierung nicht orthogonal")
check("nicht normiert" in pruefe_orthogonal(skalierung(2)).art, "Begründung: Länge")
check(not pruefe_orthogonal(scherung(1)), "Scherung nicht orthogonal")
check("Drehspiegelung" in pruefe_orthogonal(Matrix([[1, 0, 0], [0, 1, 0], [0, 0, -1]])).art, "3D det −1")
x, y = Vector([3, -1]), Vector([2, 5])
Q = drehung(90)
check((Q @ x.as_matrix()).column(0).dot((Q @ y.as_matrix()).column(0)) == x.dot(y), "Skalarprodukt bleibt erhalten")
check(Q.T @ Q == Matrix.identity(2), "A⁻¹ = Aᵀ")
check(pruefe_orthogonal(Q).latex() and repr(pruefe_orthogonal(Q)), "Anzeige")
try:
    pruefe_orthogonal([[1, 2, 3], [4, 5, 6]])
    check(False, "nicht quadratisch")
except ValueError:
    pass

print("Homogene Koordinaten 2D (Folien 20–22)")
R, T = homogen(drehung(90)), verschiebung(2, 3)
check((T @ R).rows == [[0, -1, 2], [1, 0, 3], [0, 0, 1]], "Folie 22: T·R")
check((R @ T).rows == [[0, -1, -3], [1, 0, 2], [0, 0, 1]], "Folie 22: R·T")
check((T @ R) != (R @ T), "nicht kommutativ")
z = zusammensetzen(R, T)                        # erst R, dann T = T·R
check(z.matrix.rows == (T @ R).rows, "zusammensetzen(R, T) = T·R")

print("Drehung um ein beliebiges Zentrum (Folie 23)")
d = drehung_um_zentrum(90, (2, 3))
check(d.matrix.rows == [[0, -1, 5], [1, 0, 1], [0, 0, 1]], "M = T(c)·R·T(−c)")
check((d.matrix @ Matrix([[2], [3], [1]])).rows == [[2], [3], [1]], "Zentrum bleibt fest")
check(vec((d.matrix @ Matrix([[1], [1], [1]])).rows) == [4, 2, 1], "(1,1) -> (4,2)")
check(vec((d.matrix @ Matrix([[4], [5], [1]])).rows) == [0, 5, 1], "(4,5) -> (0,5)")
check(drehung_um_zentrum(360, (2, 3)).matrix.rows == Matrix.identity(3).rows, "360° = Identität")
dp = drehung_um_zentrum(30, (2, 3), BUCHSTABE_F_FOLIEN)
check(abs(float(dp.matrix[0, 2]) - (2 - (2 * 3 ** 0.5 / 2 - 3 * 0.5))) < 1e-6, "30°: Verschiebungsanteil")
check("Probe" in dp.steps[-3].title or dp.latex(), "Rechenweg")
sx = abbildung_um_zentrum(spiegelung_x(), (2, 3))      # Spiegelung an der Geraden y = 3
check(vec((sx.matrix @ Matrix([[2], [5], [1]])).rows) == [2, 1, 1], "Spiegelung an y = 3: (2,5) -> (2,1)")
check(abbildung_um_zentrum(drehung(90), (2, 3)).matrix.rows == d.matrix.rows, "A = Drehung gibt dasselbe")
check(len(d.steps) >= 5 and "Zentrum" in d.steps[-1].title, "Schritte")

print("Homogene Koordinaten 3D (Folien 25, 26)")
P = Matrix([[1], [2], [3], [1]])
check(vec((verschiebung_3d(1, 2, 3) @ Matrix([[0], [0], [0], [1]])).rows) == [1, 2, 3, 1], "Translation")
check(vec((drehung_3d("x", 90) @ Matrix([[0], [1], [0], [1]])).rows) == [0, 0, 1, 1], "Rot_x(90°): e₂ → e₃")
check(vec((drehung_3d("y", 90) @ Matrix([[1], [0], [0], [1]])).rows) == [0, 0, -1, 1], "Rot_y(90°): e₁ → −e₃")
check(vec((drehung_3d("z", 90) @ Matrix([[1], [0], [0], [1]])).rows) == [0, 1, 0, 1], "Rot_z(90°): e₁ → e₂")
check(drehung_3d("z", 90).rows[:2][0][:2] == homogen(drehung(90)).rows[0][:2], "Rot_z = 2D-Drehung")
for ax in "xyz":
    M3 = drehung_3d(ax, 30)
    core3 = Matrix([r[:3] for r in M3.rows[:3]])
    check(bool(pruefe_orthogonal(core3)) and round(float(pruefe_orthogonal(core3).det)) == 1,
          f"Rot_{ax}(30°) orthogonal, det 1")
check(drehung_3d("x", 0) == Matrix.identity(4), "0° = Identität")
try:
    drehung_3d("w", 10)
    check(False, "falsche Achse")
except ValueError:
    pass

print("Aufgabe SW7.F23 (Folie 23, ohne Musterlösung)")
check(liste("SW7") == ["SW7.F23"], f"liste: {liste('SW7')}")
a = aufgabe("SW7.F23")
check("keine Musterlösung" in a.note and repr(a) and a._repr_html_(), "gekennzeichnet")
check(loese("SW7.F23").matrix.rows == [[0, -1, 5], [1, 0, 1], [0, 0, 1]], "loese: 90° um (2,3)")

print("Zeichnung")
check(plot_skalarprodukt([4, 3], [1, 5]) is not None, "plot_skalarprodukt")
check(lk.plot_abbildung(d.matrix, BUCHSTABE_F_FOLIEN) is not None, "Drehung um Zentrum zeichnen")
check("skalarprodukt" in lk.info() and lk.skalarprodukt is skalarprodukt, "Export und info()")

if FAILS:
    print(f"\n{len(FAILS)} Fehler")
    sys.exit(1)
print("\nAlle Tests bestanden.")
