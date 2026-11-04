#!/usr/bin/env python3
"""Tests für SW 8 (Regression, orthogonale Projektion). Aufruf: python3 tests/tests_sw8.py"""
import os
import random
import sys
import tempfile
from fractions import Fraction

os.environ.setdefault("MPLBACKEND", "Agg")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

import lialkit as lk
from lialkit.aufgaben.exercises import aufgabe, liste, loese
from lialkit.grafik.plots_projektion import plot_regression
from lialkit.rechnen.core import Matrix, Vector
from lialkit.rechnen.regression import kleinste_quadrate, projektionsmatrix, regression

FAILS = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)
        print("  FEHLER:", msg)


F = Fraction
print("Folie 9, 18, 19, 21: Punkte (0,6), (1,0), (2,0)")
r = regression([(0, 6), (1, 0), (2, 0)])
check(r.C == 5 and r.D == -3, "x̂ = (5, −3), also b = 5 − 3t")
check(r.p == Vector([5, 2, -1]) and r.e == Vector([1, -2, 1]), "p = (5, 2, −1), e = (1, −2, 1)")
check(r.sqr == 6, "SQR = 6")
check(r.A.rows == [[1, 0], [1, 1], [1, 2]] and r.b == Vector([6, 0, 0]), "A und b wie Folie 9")
check(r.vorhersage(3) == -4, "Vorhersage bei t = 3")
check(regression([0, 1, 2], [6, 0, 0]).D == -3, "Aufruf mit t und b getrennt")
sechstel = [[5, 2, -1], [2, 2, 2], [-1, 2, 5]]
check(r.P.rows == [[F(v, 6) for v in row] for row in sechstel], "Folie 19: P = 1/6·(5 2 −1; 2 2 2; −1 2 5)")
check(projektionsmatrix([[1, 0], [1, 1], [1, 2]]).P == r.P, "projektionsmatrix = P")
check(r.A.T @ r.e.as_matrix() == Matrix([[0], [0]]), "Aᵀe = 0 (Folie 17)")
check(r.P @ r.b.as_matrix() == r.p.as_matrix(), "p = P·b")
check(r.summary and r.latex() and repr(r) and r._repr_html_(), "Anzeige")

print("Folie 14, 15: Projektion auf einen Vektor")
b = Vector([1, 2, 3])
for i, e in enumerate(([1, 0, 0], [0, 1, 0], [0, 0, 1])):
    p = kleinste_quadrate(e, b).p
    check(p == Vector([b[j] if j == i else 0 for j in range(3)]), f"Projektion auf e{i + 1}")
Pa = projektionsmatrix([1, 2, 2]).P
check(Pa.rows == [[F(v, 9) for v in row] for row in ([1, 2, 2], [2, 4, 4], [2, 4, 4])], "P = aaᵀ/aᵀa für a = (1,2,2)")
check(kleinste_quadrate([1, 2, 2], [9, 0, 0]).x[0] == 1, "x̂ = aᵀb/aᵀa")

print("Folie 20: Pb = b im Spaltenraum, Pb = 0 senkrecht dazu")
A = Matrix([[1, 0], [1, 1], [1, 2]])
P = projektionsmatrix(A).P
for s in ((2, -1), (0, 3), (1, 1)):
    inC = (A @ Matrix([[s[0]], [s[1]]]))
    check(P @ inC == inC, f"P·b = b für b = A{s}")
senkrecht = Matrix([[1], [-2], [1]])                 # Aᵀ·senkrecht = 0
check(A.T @ senkrecht == Matrix([[0], [0]]) and P @ senkrecht == Matrix([[0], [0], [0]]), "P·b = 0 für b ⟂ C(A)")
check(P @ P == P and P.T == P, "P² = P, Pᵀ = P")

print("Folie 22: AᵀA invertierbar nur bei linear unabhängigen Spalten")
for schlecht in ([[1, 2], [2, 4], [3, 6]], [[1, 1], [1, 1], [1, 1]]):
    try:
        projektionsmatrix(schlecht)
        check(False, "abhängige Spalten müssten scheitern")
    except ValueError as exc:
        check("linear abhängig" in str(exc), "Begründung")
try:
    regression([(1, 2), (1, 5)])
    check(False, "gleiche t")
except ValueError:
    pass
try:
    regression([(1, 2)])
    check(False, "ein Punkt")
except ValueError:
    pass

print("Weitere Regression")
ex = regression([(0, 1), (1, 3), (2, 5)])
check(ex.C == 1 and ex.D == 2 and ex.sqr == 0 and ex.exakt_loesbar, "Punkte auf einer Geraden: SQR = 0")
v = regression([(0, 1), (1, 3), (2, 4), (3, 8)])      # von Hand: D = 11/5, C = 7/10, SQR = 9/5
check(v.D == F(11, 5) and v.C == F(7, 10) and v.sqr == F(9, 5), "vier Punkte von Hand nachgerechnet")
rnd = random.Random(3)
for _ in range(10):                                   # Normalgleichung und Minimalität
    ts = rnd.sample(range(-9, 10), 5)
    ys = [rnd.randint(-9, 9) for _ in ts]
    g = regression(ts, ys)
    check((g.A.T @ g.e.as_matrix()).rows == [[0], [0]], "Aᵀe = 0")
    for dc, dd in ((F(1, 10), 0), (0, F(1, 10)), (F(-1, 5), F(1, 5))):
        e2 = Vector([y - (g.C + dc + (g.D + dd) * t) for t, y in zip(ts, ys)])
        check(e2.norm_squared() > g.sqr, "jede andere Gerade hat grösseren Fehler")

print("Aufgaben aus den Folien (ohne Musterlösung)")
check(liste("SW8") == ["SW8.F14", "SW8.F18", "SW8.F19"], f"liste: {liste('SW8')}")
for k in liste("SW8"):
    check("keine Musterlösung" in aufgabe(k).note and repr(aufgabe(k)) and aufgabe(k)._repr_html_(), f"{k}: gekennzeichnet")
check([h[1] for h in loese("SW8.F14").highlights] == [Vector([1, 0, 0]), Vector([0, 2, 0]), Vector([0, 0, 3])],
      "F14: Projektionen auf e₁, e₂, e₃")
check(loese("SW8.F18").x == Vector([5, -3]), "F18: x̂ = (5, −3)")
check(loese("SW8.F19").P.rows == [[F(v, 6) for v in row] for row in sechstel], "F19: P")

print("Zeichnung und Export")
with tempfile.TemporaryDirectory() as tmp:
    for name, daten in (("drei", [(0, 6), (1, 0), (2, 0)]), ("vier", [(0, 1), (1, 3), (2, 4), (3, 8)])):
        fig = plot_regression(daten)
        path = os.path.join(tmp, name + ".png")
        fig.savefig(path, dpi=50)
        check(os.path.getsize(path) > 2000, f"PNG {name} leer")
        check(len(fig.axes) == (2 if name == "drei" else 1), f"{name}: Achsen")
check(lk.regression is regression and "regression" in lk.info(), "Export und info()")

print()
if FAILS:
    print(f"{len(FAILS)} FEHLER")
    sys.exit(1)
print("Alle Tests bestanden.")
