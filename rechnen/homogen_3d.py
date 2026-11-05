#!/usr/bin/env python3
"""
Homogene Koordinaten in 3D und Drehung um ein beliebiges Zentrum (SW 7).

Die 2D-Bausteine (`homogen`, `verschiebung`, `zusammensetzen`) stehen in
abbildung.py. Hier kommen die 4×4-Matrizen der Folien 25 und 26 dazu und die
Übung von Folie 23: erst das Zentrum in den Ursprung schieben, dann drehen,
dann zurückschieben, also M = T(c) · R(φ) · T(−c).

Winkel im Gradmass, positiv gegen den Uhrzeigersinn (Rechte-Hand-Regel um die
jeweilige Achse). Bei Vielfachen von 90° bleiben die Einträge exakt.
"""

from __future__ import annotations

from .abbildung import (BUCHSTABE_F_FOLIEN, ZusammensetzungResult, drehung, homogen,
                        homogen_punkte, punkte, verschiebung, zusammensetzen)
from .core import Matrix, parse_number
from .render import Step

#: Drehzentrum der Übung auf Folie 23.
ZENTRUM_FOLIE_23 = (2, 3)


def drehung_3d(achse: str, winkel_grad) -> Matrix:
    """
    4×4-Matrix der Drehung um die x-, y- oder z-Achse in homogenen Koordinaten
    (Folie 25). `achse` ist "x", "y" oder "z".

    Rot_y hat das Vorzeichen anders als Rot_x und Rot_z: [[c, 0, s], [0, 1, 0], [−s, 0, c]].
    """
    d = drehung(winkel_grad)
    c, s = d[0, 0], d[1, 0]
    if achse == "x":
        zeilen = [[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]]
    elif achse == "y":
        zeilen = [[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]]
    elif achse == "z":
        zeilen = [[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    else:
        raise ValueError("achse ist 'x', 'y' oder 'z'")
    return Matrix(zeilen)


def verschiebung_3d(u, v, w) -> Matrix:
    """4×4-Matrix der Verschiebung um (u, v, w) in homogenen Koordinaten (Folie 26)."""
    u, v, w = parse_number(u), parse_number(v), parse_number(w)
    return Matrix([[1, 0, 0, u], [0, 1, 0, v], [0, 0, 1, w], [0, 0, 0, 1]])


def abbildung_um_zentrum(A, zentrum=ZENTRUM_FOLIE_23, P=None, namen=("T(-c)", "A", "T(c)"),
                         decimal: bool = False) -> ZusammensetzungResult:
    """
    Eine 2×2-Abbildung A (Drehung, Spiegelung, Skalierung, …) um das Zentrum c
    statt um den Ursprung: M = T(c)·A·T(−c), wie in der Übung von Folie 23.

    Rechenweg: T(−c) schiebt c in den Ursprung, A wirkt, T(c) schiebt zurück;
    das Zentrum bleibt fest. P sind die Punkte spaltenweise (Standard: der
    Buchstabe F von Folie 23; die Zeile mit den Einsen wird ergänzt).
    `.matrix` ist die 3×3-Matrix in homogenen Koordinaten.
    """
    cx, cy = parse_number(zentrum[0]), parse_number(zentrum[1])
    P = BUCHSTABE_F_FOLIEN if P is None else punkte(P)
    P = homogen_punkte(P) if P.m == 2 else P
    out = zusammensetzen(verschiebung(-cx, -cy), homogen(A), verschiebung(cx, cy),
                         namen=namen, P=P, decimal=decimal)
    out.title = "Abbildung um ein beliebiges Zentrum"
    out.summary = ("M = T(c)·A·T(−c): erst das Zentrum in den Ursprung, dann "
                   "abbilden, dann zurückschieben.")
    out.zentrum = (cx, cy)
    out.steps.append(Step(
        "Das Zentrum bleibt fest",
        detail=r"M \cdot (c_x, c_y, 1)^T = (c_x, c_y, 1)^T",
        items=[("M\\,c", out.matrix @ Matrix([[cx], [cy], [1]]))],
        note="Probe: der Fixpunkt ist das Zentrum."))
    return out


def drehung_um_zentrum(winkel_grad, zentrum=ZENTRUM_FOLIE_23, P=None,
                       decimal: bool = False) -> ZusammensetzungResult:
    """
    Drehung um das Zentrum c statt um den Ursprung (Übung Folie 23):
    M = T(c)·Rot(φ)·T(−c). P wie bei `abbildung_um_zentrum`.
    """
    out = abbildung_um_zentrum(drehung(winkel_grad), zentrum, P,
                               namen=("T(-c)", "R", "T(c)"), decimal=decimal)
    out.title = "Drehung um ein beliebiges Zentrum"
    out.summary = ("M = T(c)·R·T(−c): erst das Zentrum in den Ursprung, dann "
                   "drehen, dann zurückschieben.")
    return out
