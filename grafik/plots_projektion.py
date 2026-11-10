#!/usr/bin/env python3
"""
Zeichnungen zu SW 7 und 8: Skalarprodukt mit Projektion, Regressionsgerade
mit Fehlern und die Projektion auf den Spaltenraum.

Gestaltung wie in plots.py (Swiss Style): Schwarz/Weiss, rot für das
Gegebene, schwarz für das Ergebnis, grau gestrichelt für Hilfslinien.
"""

from __future__ import annotations

from ..rechnen.core import Vector
from ..rechnen.multiple_regression import mehrfachregression
from ..rechnen.regression import regression
from .plots import INK, RED, _finish, _style_2d, _style_3d, _swiss
from .plots_abbildung import _figur, _grenzen, _pfeil

GRAU = "#86868b"


@_swiss
def plot_skalarprodukt(a, b, titel: str = "", groesse: float = 5.5):
    """
    Folie 8/9: a (rot) und b (schwarz) in der Ebene, dazu die Projektion von
    b auf a (grau gestrichelt, mit dem Lot) und der Winkel φ in der Überschrift.
    """
    import matplotlib.pyplot as plt

    a, b = Vector(a), Vector(b)
    if len(a) != 2 or len(b) != 2:
        raise ValueError("Gezeichnet werden Vektoren der Ebene")
    af, bf = [float(v) for v in a], [float(v) for v in b]
    na2 = af[0] ** 2 + af[1] ** 2
    if na2 == 0:
        raise ValueError("Auf den Nullvektor lässt sich nicht projizieren")
    k = (af[0] * bf[0] + af[1] * bf[1]) / na2
    p = (k * af[0], k * af[1])
    wert = a.dot(b)
    kopf = titel or (f"a·b = {float(wert):g}" + ("" if a.is_zero() or b.is_zero()
                                                 else f",  φ = {a.angle(b):.1f}°"))
    xs, ys = [0, af[0], bf[0], p[0]], [0, af[1], bf[1], p[1]]
    fig, ax = _figur(plt, 1, xs, ys, groesse)
    _style_2d(ax, kopf)
    ax.plot([bf[0], p[0]], [bf[1], p[1]], color=GRAU, lw=1.2, ls="--", zorder=2)
    ax.plot([0, p[0]], [0, p[1]], color=GRAU, lw=3, alpha=0.6, zorder=2,
            label="Projektion von b auf a")
    _pfeil(ax, tuple(af), RED, "a")
    _pfeil(ax, tuple(bf), INK, "b")
    _grenzen(ax, xs, ys)
    ax.legend(loc="best", fontsize=10)
    fig.tight_layout()
    return _finish(fig)


@_swiss
def plot_regression(t, b=None, titel: str = "", groesse: float = 5.0):
    """
    Folie 9 und 21: links die Datenpunkte (rot), die Regressionsgerade
    (schwarz) und die Fehler (grau gestrichelt); bei genau drei Punkten rechts
    dasselbe im Raum: b, die Ebene C(A), die Projektion p = Ax̂ und der Fehler e.
    """
    import matplotlib.pyplot as plt
    import numpy as np

    r = regression(t, b)
    ts, ys = [float(v) for v in r.t], [float(v) for v in r.y]
    C, D = float(r.C), float(r.D)
    raum = len(ts) == 3
    fig = plt.figure(figsize=(groesse * (2 if raum else 1), groesse))
    ax = fig.add_subplot(1, 2 if raum else 1, 1)
    _style_2d(ax, titel or f"b = {float(r.C):.4g} + {float(r.D):.4g}·t,  SQR = {float(r.sqr):.4g}")
    t0, t1 = min(ts + [0]), max(ts)
    ax.plot([t0, t1], [C + D * t0, C + D * t1], color=INK, lw=1.8, label="Regressionsgerade", zorder=3)
    for x, y in zip(ts, ys):
        ax.plot([x, x], [y, C + D * x], color=GRAU, lw=1.2, ls="--", zorder=2)
    ax.plot(ts, ys, "o", color=RED, ms=7, label="Daten", zorder=4)
    ax.set_aspect("auto")
    _grenzen(ax, ts, ys + [C + D * t0, C + D * t1], schritt=None)
    ax.set_xlabel("t")
    ax.set_ylabel("b")
    ax.legend(loc="best", fontsize=10)

    if raum:
        a3 = fig.add_subplot(1, 2, 2, projection="3d")
        _style_3d(a3, "Spaltenraum C(A)")
        a1, a2 = np.ones(3), np.array(ts)
        bb, pp = np.array(ys), np.array([float(v) for v in r.p])
        s, u = np.meshgrid(np.linspace(-1, 2.5, 8), np.linspace(-1, 1.5, 8))
        flaeche = [s * a1[i] + u * a2[i] for i in range(3)]
        a3.plot_surface(*flaeche, color=RED, alpha=0.15, linewidth=0)
        a3.plot([0, bb[0]], [0, bb[1]], [0, bb[2]], color=RED, lw=2)
        a3.plot([0, pp[0]], [0, pp[1]], [0, pp[2]], color=INK, lw=2)
        a3.plot([pp[0], bb[0]], [pp[1], bb[1]], [pp[2], bb[2]], color=GRAU, lw=1.5, ls="--")
        for v, name, farbe in ((bb, "b", RED), (pp, "p = Ax̂", INK)):
            a3.text(*v, " " + name, color=farbe, fontsize=11, fontweight="bold")
    fig.tight_layout()
    return _finish(fig)


@_swiss
def plot_mehrfachregression(X, y, titel: str = "", groesse: float = 5.0):
    """
    Folien 12 und 18 bis 21: links beobachtetes y (rot) gegen vorhergesagtes ŷ
    (liegt die Wolke auf der Diagonalen, ist R² nahe 1; Fehler e grau gestrichelt),
    rechts SQT, SQE und SQR als Balken (SQT = SQE + SQR).
    """
    import matplotlib.pyplot as plt

    r = mehrfachregression(X, y)
    ys, yh = [float(v) for v in r.y], [float(v) for v in r.yhat]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(groesse * 2, groesse))
    _style_2d(ax, titel or f"R² = {float(r.r2):.4f}")
    lo, hi = min(ys + yh), max(ys + yh)
    ax.plot([lo, hi], [lo, hi], color=INK, lw=1.8, label="ŷ = y (exaktes Modell)", zorder=3)
    for a, b in zip(yh, ys):
        ax.plot([a, a], [a, b], color=GRAU, lw=1.2, ls="--", zorder=2)
    ax.plot(yh, ys, "o", color=RED, ms=7, label="Samples (ŷᵢ, yᵢ)", zorder=4)
    ax.set_aspect("auto")
    ax.set_xlabel("ŷ (Modell)")
    ax.set_ylabel("y (gemessen)")
    ax.legend(loc="best", fontsize=10)
    _style_2d(bx, "Fehlerquadrate")
    bx.bar(["SQT", "SQE", "SQR"], [float(r.sqt), float(r.sqe), float(r.sqr)],
           color=[INK, GRAU, RED], zorder=3)
    bx.set_aspect("auto")
    fig.tight_layout()
    return _finish(fig)
