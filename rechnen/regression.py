#!/usr/bin/env python3
"""
Einfache lineare Regression und orthogonale Projektion (SW 8).

Ein unlösbares System Ax = b hat keine Lösung, aber eine beste: das x̂, für
das Ax̂ = p die orthogonale Projektion von b auf den Spaltenraum C(A) ist.
Dann steht der Fehler e = b − p senkrecht auf allen Spalten, AᵀAx̂ = Aᵀb
(Normalgleichung, Folie 17) und x̂ = (AᵀA)⁻¹Aᵀb. Die Projektionsmatrix ist
P = A(AᵀA)⁻¹Aᵀ, bei einem einzelnen Vektor a einfach aaᵀ / aᵀa (Folie 13).

Bei der Regressionsgeraden b = C + D·t ist A die Datenmatrix mit den Zeilen
(1, tᵢ) und x̂ = (Ĉ, D̂). Alles rechnet exakt mit Brüchen; die Summe der
Fehlerquadrate ist SQR = ‖e‖² (Folie 24).
"""

from __future__ import annotations

from fractions import Fraction

from .core import Matrix, Num, Vector, parse_number
from .inverse import inverse
from .render import Result, Step, tex_number


def _spaltenmatrix(A) -> Matrix:
    """Ein Vektor wird zur einen Spalte; eine Matrix bleibt."""
    if isinstance(A, Vector) or (isinstance(A, (list, tuple)) and A
                                 and not isinstance(A[0], (list, tuple))):
        return (A if isinstance(A, Vector) else Vector(A)).as_matrix()
    A = A if isinstance(A, Matrix) else Matrix(A)
    return A.coefficients() if A.augmented else A


def _invers_AtA(A: Matrix) -> tuple[Matrix, Matrix]:
    """(AᵀA, (AᵀA)⁻¹); ValueError, wenn die Spalten linear abhängig sind (Folie 22)."""
    AtA = A.T @ A
    if A.rank() < A.n:
        raise ValueError(
            "Die Spalten von A sind linear abhängig, darum ist AᵀA nicht "
            "invertierbar und es gibt keine eindeutige beste Lösung (Folie 22).")
    return AtA, inverse(AtA).inverse


# ==========================================================================
# Projektionsmatrix (Folien 13, 17, 19, 20)
# ==========================================================================

class ProjektionsmatrixResult(Result):
    title = "Projektionsmatrix"

    def __init__(self, A: Matrix, P: Matrix, decimal: bool = False):
        super().__init__(decimal)
        self.A, self.P = A, P
        self.summary = ("Pb ist die orthogonale Projektion von b auf den "
                        "Spaltenraum von A.")
        self.highlights = [("P", P)]


def projektionsmatrix(A, decimal: bool = False) -> ProjektionsmatrixResult:
    """
    Projektionsmatrix auf den Spaltenraum von A: P = A(AᵀA)⁻¹Aᵀ.

    Ein Vektor a (oder eine Matrix mit einer Spalte) gibt P = aaᵀ / aᵀa
    (Folie 13). Probe im Rechenweg: P² = P, Pᵀ = P und P lässt die Spalten
    von A fest (Pb = b für b in C(A), Folie 20).
    """
    A = _spaltenmatrix(A)
    AtA, inv = _invers_AtA(A)
    P = A @ inv @ A.T
    steps = []
    if A.n == 1:
        a = A.column(0)
        steps.append(Step("Projektion auf einen Vektor", detail=r"P = \frac{1}{a^T a}\, a\,a^T",
                          items=[("a", a), ("a^T a", AtA), ("a\\,a^T", A @ A.T)]))
    else:
        steps += [Step("Normalmatrix", detail=r"A^T A", items=[("A", A), ("A^T A", AtA)]),
                  Step("Invertieren", detail=r"(A^T A)^{-1}", items=[("(A^T A)^{-1}", inv)]),
                  Step("Zusammensetzen", detail=r"P = A\,(A^T A)^{-1} A^T", items=[("P", P)])]
    steps.append(Step(
        "Probe",
        detail=r"P^2 = P, \quad P^T = P",
        note=("P² = P und Pᵀ = P stimmen; P bildet jeden Vektor auf seine "
              "Projektion ab, Spaltenraumvektoren auf sich selbst."
              if P @ P == P and P.T == P else "ACHTUNG: P ist keine Projektionsmatrix.")))
    out = ProjektionsmatrixResult(A, P, decimal)
    out.steps = steps
    return out


# ==========================================================================
# Beste Lösung nach der Methode der kleinsten Quadrate (Folien 9–18, 24)
# ==========================================================================

class KleinsteQuadrateResult(Result):
    title = "Beste Lösung (kleinste Quadrate)"

    def __init__(self, A: Matrix, b: Vector, x: Vector, p: Vector, e: Vector,
                 P: Matrix, sqr: Num, loesbar: bool, decimal: bool = False):
        super().__init__(decimal)
        self.A, self.b, self.x, self.p, self.e = A, b, x, p, e
        self.P, self.sqr, self.exakt_loesbar = P, sqr, loesbar
        self.summary = ("Ax = b ist lösbar: der Fehler ist 0." if loesbar else
                        "Ax = b hat keine Lösung; x̂ macht ‖b − Ax‖² so klein wie möglich.")
        self.highlights = [(r"\hat{x}", x), ("p", p), ("e", e), ("SQR", sqr)]


def kleinste_quadrate(A, b, decimal: bool = False) -> KleinsteQuadrateResult:
    """
    Beste Lösung x̂ = (AᵀA)⁻¹Aᵀb des Systems Ax = b mit Rechenweg.

    Liefert auch p = Ax̂ (Projektion von b auf C(A)), den Fehler e = b − p
    mit der Probe Aᵀe = 0, die Projektionsmatrix P und SQR = ‖e‖².
    A darf ein Vektor sein (Projektion auf einen Vektor, n = 1).
    """
    A = _spaltenmatrix(A)
    b = b if isinstance(b, Vector) else Vector(b)
    if len(b) != A.m:
        raise ValueError("b braucht so viele Einträge, wie A Zeilen hat")
    AtA, inv = _invers_AtA(A)
    Atb = (A.T @ b.as_matrix()).column(0)
    x = (inv @ Atb.as_matrix()).column(0)
    P = A @ inv @ A.T
    p = (A @ x.as_matrix()).column(0)
    e = b - p
    sqr = e.norm_squared()
    Ate = (A.T @ e.as_matrix()).column(0)
    out = KleinsteQuadrateResult(A, b, x, p, e, P, sqr, e.is_zero(), decimal)
    out.steps = [
        Step("Gleichungssystem Ax = b", items=[("A", A), ("b", b)],
             note="Hat im Allgemeinen keine Lösung: b liegt nicht im Spaltenraum C(A)."
             if not e.is_zero() else "b liegt im Spaltenraum, das System ist lösbar."),
        Step("Normalgleichung", detail=r"A^T A\,\hat{x} = A^T b",
             items=[("A^T A", AtA), ("A^T b", Atb)],
             note="Folgt aus A^T e = 0: der Fehler steht senkrecht auf den Spalten (Folie 17)."),
        Step("Lösen", detail=r"\hat{x} = (A^T A)^{-1} A^T b",
             items=[("(A^T A)^{-1}", inv), ("\\hat{x}", x)]),
        Step("Projektion von b auf C(A)", detail=r"p = A\,\hat{x}", items=[("p", p)]),
        Step("Fehlervektor", detail=r"e = b - p", items=[("e", e)],
             note="Probe: Aᵀe = 0." if Ate.is_zero() else "ACHTUNG: Aᵀe ≠ 0."),
        Step("Summe der Fehlerquadrate", detail=f"SQR = \\|e\\|^2 = {tex_number(sqr, decimal)}"),
        Step("Projektionsmatrix", detail=r"P = A\,(A^T A)^{-1} A^T",
             items=[("P", P)], note="Es gilt p = P·b."),
    ]
    return out


# ==========================================================================
# Regressionsgerade (Folien 9, 24)
# ==========================================================================

class RegressionResult(KleinsteQuadrateResult):
    title = "Einfache lineare Regression"

    def __init__(self, base: KleinsteQuadrateResult, t: list, y: list):
        self.__dict__.update(base.__dict__)
        self.t, self.y = t, y
        self.C, self.D = base.x[0], base.x[1]
        self.summary = "Beste Gerade b = C + D·t im Sinn der kleinsten Quadrate."
        self.highlights = [("\\hat{C}", self.C), ("\\hat{D}", self.D), ("SQR", self.sqr)]

    def vorhersage(self, t) -> Num:
        """Der Wert der Regressionsgeraden an der Stelle t: Ĉ + D̂·t."""
        return self.C + self.D * parse_number(t)


def regression(t, b=None, decimal: bool = False) -> RegressionResult:
    """
    Regressionsgerade b = C + D·t durch die Datenpunkte (t₁, b₁), …, (tₘ, bₘ).

    Aufruf entweder regression([0, 1, 2], [6, 0, 0]) oder mit Punktpaaren
    regression([(0, 6), (1, 0), (2, 0)]). Folie 9: aus diesen drei Punkten
    wird Ĉ = 5, D̂ = −3, also b = 5 − 3t, mit SQR = 6.
    """
    if b is None:
        paare = [tuple(p) for p in t]
        t, b = [p[0] for p in paare], [p[1] for p in paare]
    t = [parse_number(v) for v in t]
    y = [parse_number(v) for v in b]
    if len(t) != len(y):
        raise ValueError("Zu jedem t gehört ein b")
    if len(t) < 2:
        raise ValueError("Für eine Gerade braucht es mindestens zwei Punkte")
    if len(set(t)) < 2:
        raise ValueError("Alle t-Werte sind gleich: die Gerade ist nicht eindeutig (A hat linear abhängige Spalten).")
    A = Matrix([[1, v] for v in t])
    base = kleinste_quadrate(A, Vector(y), decimal)
    out = RegressionResult(base, t, y)
    C, D = out.C, out.D
    out.steps.insert(0, Step(
        "Modell", detail=r"b = C + D\,t \;\Rightarrow\; A\binom{C}{D} = b",
        note="Jede Zeile von A ist (1, tᵢ); jeder Datenpunkt gibt eine Gleichung."))
    out.steps.append(Step(
        "Regressionsgerade",
        detail=f"b = {tex_number(C, decimal)} + {tex_number(D, decimal)}\\,t"))
    return out
