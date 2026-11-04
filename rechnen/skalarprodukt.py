#!/usr/bin/env python3
"""
Skalarprodukt, Länge und orthogonale Abbildungen (SW 7).

`dot`, `angle` und `projection` stehen schon in vectors.py. Hier kommt dazu,
was die Folien von SW 7 zusammen zeigen: Länge (Norm), Normieren, den
senkrechten Vektor in der Ebene, das Skalarprodukt in allen Formen auf
einmal (Folie 15) und die Prüfung, ob eine Matrix eine orthogonale
Abbildung ist (Folie 17).

Längen sind im Allgemeinen irrational (√2, √5, …); sie werden dann als
Näherung auf vier Stellen gezeigt, die Rechnung davor bleibt exakt.
"""

from __future__ import annotations

import math
from fractions import Fraction

from .abbildung import _nah
from .core import Matrix, Num, Vector, fmt, is_exact
from .determinant import det
from .render import Result, Step, tex_number


def _vec(v) -> Vector:
    return v if isinstance(v, Vector) else Vector(v)


def _zahl(x, decimal: bool = False) -> str:
    return tex_number(x, decimal or isinstance(x, float))


# ==========================================================================
# Länge, Normieren, senkrechter Vektor (Folien 4–6, 15)
# ==========================================================================

class LaengeResult(Result):
    title = "Länge (Norm) eines Vektors"

    def __init__(self, a: Vector, quadrat: Num, laenge, decimal: bool = False):
        super().__init__(decimal)
        self.a, self.quadrat, self.laenge = a, quadrat, laenge
        self.summary = ("|a|² = a·a = aᵀa, also |a| = √(a·a) "
                        "(Pythagoras, Folie 5).")
        self.highlights = [("|a|", laenge)]


def laenge(a, decimal: bool = False) -> LaengeResult:
    """
    Länge (Norm) |a| = √(a₁² + … + aₙ²) mit Rechenweg (Folie 5: (4, 3) hat die Länge 5).
    """
    a = _vec(a)
    q = a.norm_squared()
    l = a.norm()
    out = LaengeResult(a, q, l, decimal)
    out.steps = [
        Step("Quadrate addieren", detail=f"|a|^2 = {_quadrat_text(a)} = {tex_number(q)}",
             items=[("a", a)]),
        Step("Wurzel ziehen",
             detail=f"|a| = \\sqrt{{{tex_number(q)}}} = {_zahl(l, decimal)}",
             note="" if is_exact(l) else
             "Die Wurzel ist irrational, hier auf vier Stellen gerundet."),
    ]
    return out


def _quadrat_text(a: Vector) -> str:
    return " + ".join(f"{tex_number(x)}^2" if x >= 0 else f"({tex_number(x)})^2"
                      for x in a.values)


class NormierenResult(Result):
    title = "Vektor normieren"

    def __init__(self, a: Vector, a0: Vector, l, decimal: bool = False):
        super().__init__(decimal or not isinstance(l, Fraction))
        self.a, self.a0, self.laenge = a, a0, l
        self.summary = ("Durch die eigene Länge geteilt hat der Vektor die Länge 1; "
                        "seine Spitze liegt auf dem Einheitskreis (Folie 6).")
        self.highlights = [("a^0", a0)]


def normieren(a, decimal: bool = False) -> NormierenResult:
    """
    Normierter Vektor a⁰ = a / |a| (Folie 6: aus (4, 3) wird (4/5, 3/5) = (0.8, 0.6)).
    Der Nullvektor lässt sich nicht normieren (ValueError).
    """
    a = _vec(a)
    l = a.norm()
    a0 = a.normalized()
    out = NormierenResult(a, a0, l, decimal)
    proben = a0.norm()
    out.steps = [
        Step("Länge bestimmen", detail=f"|a| = {_zahl(l, decimal)}",
             items=[("a", a)]),
        Step("Durch die Länge teilen", detail=r"a^0 = \frac{a}{|a|}",
             items=[("a^0", a0)]),
        Step("Probe", detail=f"|a^0| = {_zahl(proben, decimal or not is_exact(proben))}",
             note="Länge 1: die Spitze liegt auf dem Einheitskreis."
             if abs(float(proben) - 1) < 1e-9 else "ACHTUNG: weicht von 1 ab."),
    ]
    return out


def senkrechter_vektor(a) -> tuple[Vector, Vector]:
    """
    Die beiden Vektoren in der Ebene, die auf a senkrecht stehen (Folie 15):
    (−a₂, a₁) und (a₂, −a₁). Nur für Vektoren mit zwei Einträgen.
    """
    a = _vec(a)
    if len(a) != 2:
        raise ValueError("Einen senkrechten Vektor so einfach gibt es nur in der Ebene")
    return Vector([-a[1], a[0]]), Vector([a[1], -a[0]])


# ==========================================================================
# Das Skalarprodukt in allen Formen (Folien 7–15)
# ==========================================================================

class SkalarproduktResult(Result):
    title = "Skalarprodukt: geometrisch und arithmetisch"

    def __init__(self, a: Vector, b: Vector, wert: Num, la, lb, proj_a_auf_b,
                 proj_b_auf_a, grad, art: str, decimal: bool = False):
        super().__init__(decimal)
        self.a, self.b, self.wert = a, b, wert
        self.laenge_a, self.laenge_b = la, lb
        self.proj_a_auf_b, self.proj_b_auf_a = proj_a_auf_b, proj_b_auf_a
        self.winkel, self.art = grad, art
        self.summary = art
        self.highlights = [(r"a \cdot b", wert)]
        if grad is not None:
            self.highlights.append((r"\varphi", f"{grad:.4f}^\\circ"))


def skalarprodukt(a, b, decimal: bool = False) -> SkalarproduktResult:
    """
    Skalarprodukt a·b = aᵀb = |a|·|b|·cos φ mit allem, was Folie 15 daraus macht:
    Längen, Winkel, Projektionslängen a_b und b_a (Zahlen, keine Vektoren),
    parallel (a·b = |a||b|) oder senkrecht (a·b = 0).

    Ist ein Vektor der Nullvektor, gibt es keinen Winkel (winkel ist None).
    """
    a, b = _vec(a), _vec(b)
    a._check(b)
    wert = a.dot(b)
    la, lb = a.norm(), b.norm()
    nullvektor = a.is_zero() or b.is_zero()
    # Projektionslänge von a auf b: a_b = a·b / |b| (Folie 8), mit Vorzeichen
    pab = None if b.is_zero() else wert / lb
    pba = None if a.is_zero() else wert / la
    grad = None if nullvektor else a.angle(b)
    voll = 0.0 if nullvektor else float(la) * float(lb)
    if wert == 0:
        art = "a·b = 0: a und b stehen senkrecht aufeinander."
    elif not nullvektor and abs(float(wert) - voll) < 1e-9:
        art = "a·b = |a|·|b|: a und b sind parallel (gleiche Richtung)."
    elif not nullvektor and abs(float(wert) + voll) < 1e-9:
        art = "a·b = −|a|·|b|: a und b sind parallel (entgegengesetzte Richtung)."
    elif wert > 0:
        art = "a·b > 0: der Winkel ist kleiner als 90°."
    else:
        art = "a·b < 0: der Winkel ist grösser als 90°."
    out = SkalarproduktResult(a, b, wert, la, lb, pab, pba, grad, art, decimal)
    summe = " + ".join(f"{tex_number(x)} \\cdot {tex_number(y)}"
                       for x, y in zip(a.values, b.values))
    out.steps = [
        Step("Arithmetisch: Komponenten multiplizieren und addieren",
             detail=f"a^T b = {summe} = {tex_number(wert)}",
             items=[("a", a), ("b", b)]),
        Step("Längen", detail=f"|a| = {_zahl(la)}, \\quad |b| = {_zahl(lb)}",
             note="" if is_exact(la) and is_exact(lb) else
             "Mindestens eine Länge ist irrational, hier auf vier Stellen gerundet."),
    ]
    if not nullvektor:
        cos = max(-1.0, min(1.0, float(wert) / (float(la) * float(lb))))
        out.steps.append(Step(
            "Geometrisch: Winkel",
            detail=(r"\cos\varphi = \frac{a \cdot b}{|a|\,|b|} = "
                    f"{cos:.4f}, \\quad \\varphi = {grad:.4f}^\\circ")))
        out.steps.append(Step(
            "Projektionslängen (Zahlen, keine Vektoren)",
            detail=(f"a_b = \\frac{{a \\cdot b}}{{|b|}} = {_zahl(pab)}, \\quad "
                    f"b_a = \\frac{{a \\cdot b}}{{|a|}} = {_zahl(pba)}"),
            note="Es gilt a·b = a_b·|b| = b_a·|a| = |a|·|b|·cos φ (Folie 12)."))
    out.steps.append(Step("Einordnung", note=art))
    return out


# ==========================================================================
# Orthogonale Abbildungen (Folie 17)
# ==========================================================================

class OrthogonalResult(Result):
    title = "Ist die Abbildung orthogonal?"

    def __init__(self, A: Matrix, ist: bool, d: Num | None, art: str,
                 decimal: bool = False):
        super().__init__(decimal or _naeherung_matrix(A))
        self.A, self.ist_orthogonal, self.det, self.art = A, ist, d, art
        self.summary = art
        self.highlights = [("A^T A", A.T @ A)] if A.is_square() else []

    def __bool__(self) -> bool:
        return self.ist_orthogonal


def _naeherung_matrix(A: Matrix) -> bool:
    return any(v.denominator > 10 ** 6 for r in A.rows for v in r)


def pruefe_orthogonal(A, decimal: bool = False) -> OrthogonalResult:
    """
    Prüft, ob A eine orthogonale Abbildung ist (Folie 17): Spalten normiert und
    paarweise senkrecht, also AᵀA = E, A⁻¹ = Aᵀ und det A = ±1.

    Bei Erfolg die Einordnung: det = 1 Drehung, det = −1 Spiegelung (in der
    Ebene; im Raum Drehspiegelung). Bei Misserfolg die Begründung.
    """
    A = A if isinstance(A, Matrix) else Matrix(A)
    if A.augmented:
        A = A.coefficients()
    if not A.is_square():
        raise ValueError("Orthogonal kann nur eine quadratische Matrix sein")
    n = A.n
    spalten = [A.column(j) for j in range(n)]
    steps = []

    laengen = [s.norm() for s in spalten]
    ok_laenge = all(abs(float(l) - 1) < 1e-9 for l in laengen)
    steps.append(Step(
        "Längen der Spalten", items=[("A", A)],
        detail=", \\quad ".join(f"|a_{{{j + 1}}}| = {_zahl(l)}"
                                for j, l in enumerate(laengen)),
        note="Alle Spalten haben die Länge 1." if ok_laenge
        else "Nicht alle Spalten sind auf 1 normiert."))

    paare = [(i, j, spalten[i].dot(spalten[j]))
             for i in range(n) for j in range(i + 1, n)]
    ok_senkrecht = all(abs(float(p)) < 1e-9 for _, _, p in paare)
    if paare:
        steps.append(Step(
            "Spalten paarweise senkrecht?",
            detail=", \\quad ".join(f"a_{{{i + 1}}} \\cdot a_{{{j + 1}}} = {_zahl(p)}"
                                    for i, j, p in paare),
            note="Alle Skalarprodukte sind 0." if ok_senkrecht
            else "Mindestens zwei Spalten stehen nicht senkrecht aufeinander."))

    ATA = A.T @ A
    gleich_E = _nah(ATA, Matrix.identity(n))
    steps.append(Step("Kontrolle: AᵀA = E", items=[("A^T A", ATA)],
                      note="Dann ist A⁻¹ = Aᵀ." if gleich_E
                      else "AᵀA ist nicht die Einheitsmatrix."))

    d = det(A).value
    ok_det = abs(float(d) * float(d) - 1) < 1e-9
    steps.append(Step("Determinante", detail=f"\\det A = {_zahl(d)}",
                      note="Eine orthogonale Matrix hat Determinante 1 oder −1."
                      if ok_det else "Die Determinante ist weder 1 noch −1."))

    ist = ok_laenge and ok_senkrecht and gleich_E and ok_det
    if ist:
        wie = ("eine Drehung (det = 1, Drehsinn bleibt)" if float(d) > 0 else
               "eine Spiegelung (det = −1, Drehsinn kehrt um)" if n == 2 else
               "eine Drehspiegelung (det = −1, Drehsinn kehrt um)")
        art = f"A ist orthogonal: längen- und winkeltreu, {wie}."
    else:
        grund = ("Spalten nicht normiert" if not ok_laenge else
                 "Spalten nicht senkrecht" if not ok_senkrecht else "AᵀA ≠ E")
        art = f"A ist nicht orthogonal ({grund})."
    steps.append(Step("Ergebnis", note=art))
    out = OrthogonalResult(A, ist, d, art, decimal)
    out.steps = steps
    return out
