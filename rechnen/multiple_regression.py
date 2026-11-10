#!/usr/bin/env python3
"""
Multiple lineare Regression (SW 9).

Modell mit n Einflussgrössen (Folie 8): y = b₀ + b₁x₁ + … + bₙxₙ + e, für m
Beobachtungen in Matrixform y = Xb + e mit der m×(n+1)-Datenmatrix X (erste
Spalte lauter Einsen, Folien 6 und 23). Der Fehler e = y − Xb̂ ist minimal,
wenn er senkrecht auf dem Spaltenraum C(X) steht: Xᵀe = 0, also die
Normalgleichung XᵀXb̂ = Xᵀy (Folie 10) und b̂ = (XᵀX)⁻¹Xᵀy (Folie 11).

Projektionsmatrix (Hut-Matrix) P = X(XᵀX)⁻¹Xᵀ mit ŷ = Py (Folien 11, 13),
Residualmatrix Q = I − P mit e = Qy; beide symmetrisch und idempotent (Folie 13).
Zentrierende Matrix M = I − (1/m)·11ᵀ mit y − ȳ = My (Folie 21).
Fehlerquadrate (Folien 19 bis 21): SQT = yᵀMy, SQR = yᵀQy = eᵀe,
SQE = SQT − SQR, Bestimmtheitsmass R² = 1 − SQR/SQT, 0 ≤ R² ≤ 1.
Alles rechnet exakt mit Brüchen. Die einfache Regression (SW 8) bleibt in
`regression.py`; hier wird deren Normalgleichung wiederverwendet.
"""

from __future__ import annotations

from .core import Matrix, Num, Vector, parse_number
from .regression import _invers_AtA
from .render import Result, Step, tex_number

__all__ = ["MehrfachRegressionResult", "mehrfachregression", "residualmatrix",
           "zentriermatrix", "GEWICHTHEBER_X", "GEWICHTHEBER_Y"]

# Folie 5: Training (h/Woche) und Protein (g/kg/Tag) -> maximales Gewicht (kg)
GEWICHTHEBER_X = [[2, "1.1"], [2, "1.9"], [4, 2], [5, "1.5"], [7, "2.1"]]
GEWICHTHEBER_Y = [93, 106, 146, 140, 158]


def zentriermatrix(m: int) -> Matrix:
    """Zentrierende Matrix M = I − (1/m)·11ᵀ der Grösse m×m (Folie 21)."""
    if m < 1:
        raise ValueError("m muss mindestens 1 sein")
    return Matrix.identity(m) - Matrix([[1] * m for _ in range(m)]).scaled(parse_number(f"1/{m}"))


def residualmatrix(X) -> Matrix:
    """Residualmatrix Q = I − X(XᵀX)⁻¹Xᵀ (Folie 13); X ist die volle Datenmatrix."""
    X = X if isinstance(X, Matrix) else Matrix(X)
    _, inv = _invers_AtA(X)
    return Matrix.identity(X.m) - X @ inv @ X.T


class MehrfachRegressionResult(Result):
    title = "Multiple lineare Regression"

    def __init__(self, d: dict, decimal: bool = False):
        super().__init__(decimal)
        self.__dict__.update(d)
        self.summary = ("Beste Hyperebene y = b₀ + b₁x₁ + … + bₙxₙ im Sinn der kleinsten "
                        "Quadrate; R² sagt, wie gut sie die Daten erklärt.")
        self.highlights = [(r"\hat{b}", self.b), (r"\hat{y}", self.yhat), ("e", self.e),
                           ("SQT", self.sqt), ("SQR", self.sqr), ("SQE", self.sqe),
                           ("R^2", self.r2)]

    def vorhersage(self, x) -> Num:
        """Zielgrösse b̂ᵀ(1, x₁, …, xₙ) zu einem Einflussvektor x (Folie 23)."""
        x = [parse_number(v) for v in x]
        if len(x) != len(self.b) - 1:
            raise ValueError(f"x braucht {len(self.b) - 1} Einträge")
        return self.b[0] + sum((bi * xi for bi, xi in zip(list(self.b)[1:], x)), 0)


def mehrfachregression(X, y, konstante: bool = True, decimal: bool = False) -> MehrfachRegressionResult:
    """
    Multiple lineare Regression mit Rechenweg (Folien 5 bis 24).

    X hat eine Zeile je Beobachtung und eine Spalte je Einflussgrösse; bei
    `konstante=True` wird die Einserspalte (Folie 23) vorne ergänzt, sonst
    gilt X als volle Datenmatrix. Folie 5 bis 21: mehrfachregression(
    GEWICHTHEBER_X, GEWICHTHEBER_Y) gibt b̂ = (6956/127, 2551/254, 2485/127), SQT = 3075.2, R² ≈ 0.9061.
    """
    X = X if isinstance(X, Matrix) else Matrix(X)
    X = X.coefficients() if X.augmented else X
    y = y if isinstance(y, Vector) else Vector(y)
    if len(y) != X.m:
        raise ValueError("y braucht so viele Einträge, wie X Zeilen hat")
    if konstante:
        X = Matrix([[1] + list(r) for r in X.rows])
    if X.m < X.n:
        raise ValueError("Es braucht mindestens so viele Beobachtungen wie Parameter")
    m = X.m
    XtX, inv = _invers_AtA(X)           # ValueError bei korrelierten Spalten (Folie 22)
    Xty = (X.T @ y.as_matrix()).column(0)
    b = (inv @ Xty.as_matrix()).column(0)
    P = X @ inv @ X.T
    Q = Matrix.identity(m) - P
    M = zentriermatrix(m)
    yhat = (P @ y.as_matrix()).column(0)
    e = (Q @ y.as_matrix()).column(0)
    ym = y.as_matrix()
    sqt = (ym.T @ M @ ym)[0][0]
    sqr = (ym.T @ Q @ ym)[0][0]
    sqe = sqt - sqr
    if sqt == 0:
        raise ValueError("Alle y-Werte sind gleich (SQT = 0): R² ist nicht definiert.")
    r2 = 1 - sqr / sqt
    d = dict(X=X, y=y, b=b, P=P, Q=Q, M=M, yhat=yhat, e=e, sqt=sqt, sqr=sqr, sqe=sqe, r2=r2)
    out = MehrfachRegressionResult(d, decimal)
    t = lambda v: tex_number(v, decimal)
    Xte = (X.T @ e.as_matrix()).column(0)
    out.steps = [
        Step("Modell", detail=r"y = X\,b + e",
             items=[("X", X), ("y", y)],
             note="Jede Zeile von X ist (1, xᵢ₁, …, xᵢₙ); das System ist überbestimmt (Folie 6)."),
        Step("Normalgleichung", detail=r"X^T X\,\hat{b} = X^T y",
             items=[("X^T X", XtX), ("X^T y", Xty)],
             note="Folgt aus Xᵀe = 0: der Fehler steht senkrecht auf C(X) (Folie 10)."),
        Step("Parametervektor", detail=r"\hat{b} = (X^T X)^{-1} X^T y",
             items=[("(X^T X)^{-1}", inv), (r"\hat{b}", b)],
             note="XᵀX ist invertierbar, weil die Spalten linear unabhängig sind (Folie 11)."),
        Step("Projektionsmatrix (Hut-Matrix)", detail=r"P = X\,(X^T X)^{-1} X^T",
             items=[("P", P)],
             note="P² = P und Pᵀ = P" + (" stimmen." if P @ P == P and P.T == P else ": ACHTUNG, Probe schlägt fehl.")),
        Step("Vorhergesagte Zielgrössen", detail=r"\hat{y} = P\,y = X\hat{b}", items=[(r"\hat{y}", yhat)]),
        Step("Residualmatrix und Fehler", detail=r"Q = I - P,\quad e = Q\,y = y - \hat{y}",
             items=[("Q", Q), ("e", e)],
             note="Probe: Xᵀe = 0." if Xte.is_zero() else "ACHTUNG: Xᵀe ≠ 0."),
        Step("Zentrierende Matrix", detail=r"M = I - \tfrac{1}{m}\,\mathbf{1}\mathbf{1}^T",
             items=[("M", M)], note="My = y − ȳ (Folie 21)."),
        Step("Fehlerquadrate",
             detail=f"SQT = y^T M y = {t(sqt)},\\quad SQR = y^T Q y = {t(sqr)},\\quad SQE = SQT - SQR = {t(sqe)}"),
        Step("Bestimmtheitsmass", detail=f"R^2 = 1 - \\frac{{SQR}}{{SQT}} = {t(r2)}",
             note=f"R² ≈ {float(r2):.4f}: {float(r2) * 100:.1f} % der Streuung von y erklärt das Modell."),
    ]
    return out
