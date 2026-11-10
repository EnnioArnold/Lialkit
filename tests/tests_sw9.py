#!/usr/bin/env python3
"""Tests für SW 9 (multiple lineare Regression). Aufruf: python3 tests/tests_sw9.py"""
import os
import sys
import tempfile
from fractions import Fraction

os.environ.setdefault("MPLBACKEND", "Agg")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

import lialkit as lk
from lialkit.aufgaben.exercises import aufgabe, liste, loese
from lialkit.grafik.plots_projektion import plot_mehrfachregression
from lialkit.rechnen.core import Matrix, Vector
from lialkit.rechnen.multiple_regression import (GEWICHTHEBER_X, GEWICHTHEBER_Y, mehrfachregression,
                                                 residualmatrix, zentriermatrix)
from lialkit.rechnen.regression import regression

FAILS = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)
        print("  FEHLER:", msg)


def nah(a, b, tol=1e-6):
    return abs(float(a) - b) < tol


F = Fraction
print("Folien 14, 15, 21: Gewichtheber")
r = mehrfachregression(GEWICHTHEBER_X, GEWICHTHEBER_Y)
check(r.X.shape == (5, 3), "X ist 5×3 mit Einserspalte")
check(all(nah(a, b) for a, b in zip(r.yhat, [96.38188976, 112.03543307, 134.07874016, 134.33858268, 166.16535433])), "ŷ = Py (Folie 14)")
check(all(nah(a, b) for a, b in zip(r.e, [-3.38188976, -6.03543307, 11.92125984, 5.66141732, -8.16535433])), "e = Qy (Folie 15)")
check(nah(r.P[0][0], 0.76946632) and nah(r.P[4][4], 0.71259843) and nah(r.Q[2][2], 0.64566929), "Einträge P und Q")
check(nah(r.sqt, 3075.2) and r.sqt == F(15376, 5), "SQT = 3075.2 exakt")
check(nah(r.sqr, 288.7047244094689) and nah(r.r2, 0.9061183908658075), "SQR und R² (Folie 21)")
check(r.sqt == r.sqe + r.sqr, "SQT = SQE + SQR")
check(r.P @ r.P == r.P and r.P.T == r.P and r.Q @ r.Q == r.Q and r.Q.T == r.Q, "P, Q symmetrisch und idempotent")
check(r.P + r.Q == Matrix.identity(5), "P + Q = I")
check((r.X.T @ r.e.as_matrix()).column(0).is_zero(), "Xᵀe = 0")
check((r.X @ r.b.as_matrix()).column(0) == r.yhat, "Xb̂ = ŷ")
check(r.vorhersage([2, "1.1"]) == r.yhat[0], "vorhersage an einer Beobachtung")

print("Zentrierende Matrix M (Folie 21)")
M = zentriermatrix(5)
check(M[0][0] == F(4, 5) and M[0][1] == F(-1, 5), "M: 0.8 und −0.2")
check(M @ M == M and (M @ Vector([1] * 5).as_matrix()).column(0).is_zero(), "M idempotent, M·1 = 0")
check(residualmatrix(r.X) == r.Q, "residualmatrix = Q")

print("Spezialfall: eine Einflussgrösse ist die Gerade aus SW 8")
g = mehrfachregression([[0], [1], [2]], [6, 0, 0])
check(list(g.b) == [5, -3] and g.sqr == 6 and g.sqt == 24, "b̂ = (5, −3), SQR = 6, SQT = 24")
check(g.r2 == F(3, 4), "R² = 1 − 6/24")
check(g.b == Vector([regression([(0, 6), (1, 0), (2, 0)]).C, -3]), "wie regression()")
check(mehrfachregression([[1], [2], [3]], [2, 4, 6]).r2 == 1, "exakt linear: R² = 1")

print("Fehlerfälle (Folie 22)")
for X, y, was in (([[1, 2], [2, 4], [3, 6], [4, 8]], [1, 2, 3, 5], "korrelierte Spalten"),
                  ([[1], [2]], [1, 2, 3], "Länge"), ([[1], [2], [3]], [5, 5, 5], "SQT = 0")):
    try:
        mehrfachregression(X, y)
        check(False, f"{was}: kein ValueError")
    except ValueError:
        pass

print("Aufgabe, Zeichnung, Export")
check(liste("SW9") == ["SW9.F5"] and "keine Musterlösung" in aufgabe("SW9.F5").note, "Aufgabe gekennzeichnet")
check(nah(loese("SW9.F5").r2, 0.9061183908658075), "loese(SW9.F5)")
with tempfile.TemporaryDirectory() as tmp:
    fig = plot_mehrfachregression(GEWICHTHEBER_X, GEWICHTHEBER_Y)
    path = os.path.join(tmp, "m.png")
    fig.savefig(path, dpi=50)
    check(os.path.getsize(path) > 2000 and len(fig.axes) == 2, "PNG mit zwei Achsen")
check(lk.mehrfachregression is mehrfachregression and "mehrfachregression" in lk.info(), "Export und info()")

print()
if FAILS:
    print(f"{len(FAILS)} FEHLER")
    sys.exit(1)
print("Alle Tests bestanden.")
