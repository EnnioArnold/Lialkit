# lialkit

Lineare Algebra mit nachvollziehbarem Rechenweg, gebaut zum Modul
I.BA_LIAL_MM.20 der HSLU. Deckt die Semesterwochen 1 bis 9 ab: Gauss, LR-Zerlegung,
Inverse und Determinante, Vektorrechnung, lineare Abbildungen (SW5 und SW6),
Skalarprodukt, orthogonale Abbildungen und homogene Koordinaten (SW7) sowie
lineare Regression mit orthogonaler Projektion (SW8) und multiple lineare
Regression mit Bestimmtheitsmass (SW9).

## Installieren

Nötig ist nur Python. Für die Zeichnungen und die App kommt dazu:

```bash
pip install -r requirements.txt      # numpy, matplotlib, plotly, PySide6
pip install manimgx                  # Animationen, freiwillig (Python 3.13+)
```

manimgx rendert auf der GPU und schreibt das MP4 ohne ffmpeg. Als Rückfall
geht Manim CE (`brew install cairo pango pkg-config ffmpeg`, `pip install manim`).
Die Videos folgen dem App-Design: heller Canvas (oder Tinten-Grund im Dunkelmodus), Pastell-Akzente.

Der Ordner `lialkit/` liegt neben deinen Wochen-Ordnern. Aus einem
Notebook in `Week 3/` heraus:

```python
import sys
sys.path.insert(0, '..')
import lialkit as lk
```

## Aufbau

![Notebook und Fenster rechnen mit demselben Modul](docs/architektur.svg)

Notebook und Fenster teilen sich den Rechenkern, darum können ihre Ergebnisse
nicht auseinanderlaufen.

```
app/        das Fenster (lialkit_qt.py)
rechnen/    Rechenkern: core, render, solving, factor, inverse, determinant,
            vectors und abbildung (SW5/6), skalarprodukt und homogen_3d (SW7),
            regression (SW8), multiple_regression (SW9)
grafik/     Zeichnungen (plots, plots_abbildung, plots_projektion) und Animationen (anim)
aufgaben/   Übungsaufgaben (exercises) und Vorlage zum Selbstprüfen (uebung)
docs/       Architektur-Diagramm
tests/      ein Testskript je Modul
```

Im Notebook bleiben die kurzen Namen: `import lialkit as lk`,
`from lialkit.exercises import liste`, `lialkit.anim` und so weiter.

## Lineare Abbildungen (SW5, SW6)

```python
lk.drehung(30)                         # Matrix der Drehung um 30°
lk.spiegelung_achse(30)                # Spiegelung an der Achse bei 30°
lk.abbilden(lk.scherung(1), lk.BUCHSTABE_F_FOLIEN)   # Bildpunkte Q = A·P
lk.zusammensetzen(A, B)                # erst A, dann B, also B·A
lk.finde_abbildung([(0,0),(1,0),(1,1),(0,1),(0,0)])   # Matrix aus der Bildfigur
lk.plot_abbildung(A)                   # Original Lavendel, Bild Tinte
```

**SW6** behandelt denselben Stoff wie SW5 (gleiche Folien, gleiches Blatt, nur
das Datum ist ein anderes). Neu im Kit sind zwei Wünsche aus den Notizen:

```python
lk.transponierte_abbildung(A, P)       # was A^T mit denselben Punkten macht
lk.plot_abbildung(A, [(0,0),(2,1),(3,3)], transponiert=True)   # eigene Punkte, A^T gestrichelt
```

Die Zeilen von A sind die Spalten von A^T. Der Rechenweg ordnet ein: Ist A
symmetrisch, sind A und A^T dieselbe Abbildung; bei Drehungen und Spiegelungen
ist A^T die Umkehrung. Die Fläche (|det|) bleibt gleich. Im Fenster gibt es
unter »Abbildungen« die Rechnung »Transponierte« und das Objekt »Eigene«, in
das du Punkte wie `(0,0) (2,1) (3,3)` tippst.

`finde_abbildung` löst Aufgabe 1 vom Blatt: Es liest A aus den Bildern von e₁ und
e₂ ab, prüft die Ecke (1,1) und begründet sonst, warum es keine lineare Abbildung
gibt (der Nullpunkt bleibt nicht fest). Dann liefert es die 3×3-Matrix in
homogenen Koordinaten.

## Skalarprodukt, orthogonale Abbildungen, homogene Koordinaten (SW7)

```python
lk.skalarprodukt([1, 2], [3, -1])      # a·b, Längen, Winkel, Projektionslängen, parallel/senkrecht
lk.laenge([4, 3])                      # |a| = 5 (Folie 5)
lk.normieren([4, 3])                   # a⁰ = (4/5, 3/5) (Folie 6)
lk.senkrechter_vektor([4, 3])          # (−3, 4) und (3, −4) (Folie 15)
lk.pruefe_orthogonal(lk.drehung(30))   # längen- und winkeltreu? AᵀA = E, det = ±1 (Folie 17)
lk.drehung_um_zentrum(90, (2, 3))      # Übung Folie 23: M = T(c)·R·T(−c)
lk.abbildung_um_zentrum(A, (2, 3))     # dasselbe mit beliebiger 2×2-Matrix A
lk.drehung_3d("y", 90)                 # 4×4 in homogenen Koordinaten (Folie 25)
lk.verschiebung_3d(1, 2, 3)            # 4×4 (Folie 26)
lk.plot_skalarprodukt([4, 3], [1, 5])  # a, b und die Projektion von b auf a
```

`dot`, `angle` und `projection` aus SW1 bleiben, wie sie waren; `skalarprodukt`
zeigt zusätzlich alle Formen von Folie 15 auf einmal. Die 2D-Bausteine
(`homogen`, `verschiebung`, `zusammensetzen`) gab es schon aus SW5; wie auf
Folie 22 gilt T·R ≠ R·T, die zuerst wirkende Abbildung steht rechts.

## Regression und Projektion (SW8)

```python
r = lk.regression([(0, 6), (1, 0), (2, 0)])   # Folie 9
r.C, r.D, r.sqr                               # 5, −3, 6: b = 5 − 3t
r.p, r.e                                      # Projektion (5, 2, −1), Fehler (1, −2, 1)
r.vorhersage(3)                               # Wert der Geraden bei t = 3
lk.kleinste_quadrate(A, b)                    # x̂ = (AᵀA)⁻¹Aᵀb für beliebiges A
lk.projektionsmatrix(A)                       # P = A(AᵀA)⁻¹Aᵀ; ein Vektor a gibt aaᵀ/aᵀa
lk.plot_regression([(0, 6), (1, 0), (2, 0)])  # Gerade, Fehler; bei drei Punkten auch C(A) im Raum
```

Sind die Spalten von A linear abhängig, bricht die Rechnung mit der
Begründung von Folie 22 ab (AᵀA ist dann nicht invertierbar).

## Multiple lineare Regression (SW9)

```python
r = lk.mehrfachregression(lk.GEWICHTHEBER_X, lk.GEWICHTHEBER_Y)   # Folien 5 bis 21
r.b                                  # b̂ = (XᵀX)⁻¹Xᵀy, Einserspalte wird ergänzt
r.yhat, r.e                          # ŷ = Py, e = Qy
r.P, r.Q, r.M                        # Hut-Matrix, Residualmatrix, zentrierende Matrix
r.sqt, r.sqe, r.sqr, r.r2            # 3075.2, …, 288.70, R² = 1 − SQR/SQT ≈ 0.9061
r.vorhersage([3, 1.5])               # Zielgrösse zu einem Einflussvektor
lk.zentriermatrix(5)                 # M = I − 11ᵀ/m (Folie 21)
lk.residualmatrix(X)                 # Q = I − X(XᵀX)⁻¹Xᵀ (Folie 13)
lk.plot_mehrfachregression(X, y)     # y gegen ŷ und SQT = SQE + SQR
```

Sind die Einflussgrössen korreliert (Spalten von X linear abhängig), bricht die
Rechnung mit der Begründung von Folie 22 ab. Der Rechenweg prüft P² = P, Pᵀ = P
und Xᵀe = 0.

**Offen (TODO):** Für SW7 bis SW9 gibt es weder Animationen noch ein
Übungsblatt oder eine Musterlösung. Die Folien-Aufgaben (SW7.F23, SW8.F14,
F18, F19, SW9.F5) sind aufgenommen und im Hinweis als »ohne Musterlösung« gekennzeichnet;
ihre Lösungen rechnet das Kit selbst. Die 3D-Matrizen haben noch keine
Zeichnung. Auf Folie 23 steht kein Drehwinkel; SW7.F23 nimmt 90°. In den Notizen
zu SW8 steht »aᵀb transponiert anschauen«: das Skalarprodukt aᵀb ist in
`skalarprodukt` und in der Projektion (Folie 13) umgesetzt.

## Genauigkeit

Gerechnet wird exakt mit Brüchen. `1/3` bleibt `1/3` und wird nie zu
`0.33333`. Das ist in der linearen Algebra kein Luxus: der Unterschied
zwischen `0` und `1e-17` entscheidet darüber, ob eine Matrix singulär ist.

Wo Wurzeln auftreten — Vektorlängen, Winkel — schaltet lialkit von selbst
auf Gleitkomma um und sagt es im Rechenweg. Geht die Wurzel auf, bleibt
sie exakt: `|(3,4)| = 5`, nicht `5.0000`.

## Die Übungsaufgaben

```python
from lialkit.exercises import liste, aufgabe, loese

liste('SW8')          # welche es gibt (SW1 bis SW9)
aufgabe('SW3.1a')     # die Angabe
loese('SW3.1a')       # durchgerechnet
```

Enthalten sind die Aufgaben der Wochen 1 bis 9, zuletzt SW5.1a–e und SW5.2a/b
(lineare Abbildungen). Das Blatt von SW6 ist dasselbe; es steht als
SW6.1a–e und SW6.2a/b mit denselben Daten und Lösungen noch einmal da.

Für SW7 und SW8 gibt es nur die Folien (kein Blatt, keine Musterlösung). Daraus
sind die gestellten Fragen als SW7.F23 (Drehung um ein Zentrum) und SW8.F14, F18,
F19 (Projektion, Regression, Projektionsmatrix) aufgenommen; `loese` rechnet sie,
eine Lösung der Dozierenden liegt aber nicht vor.

Auch SW9 hat nur Folien und stellt keine Frage. Das Beispiel der Gewichtheber
(Folien 5 bis 21) ist als SW9.F5 aufgenommen und im Hinweis als »keine
Musterlösung« gekennzeichnet; die Teilaufgaben (b̂, P, Q, SQT, SQR, R²) sind aus
dem Beispiel abgeleitet, die Zahlen der Folien dienen als Kontrolle.

**Eine Aufgabe ist bewusst offen gelassen:** SW3 Aufgabe 3 verlangt, dass
du den LR-Algorithmus selbst programmierst. Dafür gibt es ein Gerüst mit
Prüfstand:

```python
from lialkit.uebung import vorlage, pruefe_lr
print(vorlage())

def meine_lr(A):
    ...
    return L, R

pruefe_lr(meine_lr)
```

Der Prüfstand rechnet die Aufgaben vom Blatt und ein paar Fälle, die man
leicht übersieht — Einheitsmatrix, schon dreieckige Matrix, Null an der
Pivotstelle, singuläre Matrix.

## Das Fenster

Ordner von GitHub laden, entpacken, dann im Terminal:

```bash
cd lialkit-main                  # wie der Ordner bei dir heisst
pip install -r requirements.txt  # einmalig
python3 app/lialkit_qt.py
```

Der Ordnername ist egal. Das Fenster ist hell oder dunkel (Design siehe unten). Fünf Ansichten:

- **Gauss** — Elimination von Hand oder Schritt für Schritt, mit Animation
  und Prüfung über Wolfram|Alpha
- **Verfahren** — LR-Zerlegung, Inverse, Determinante und Rang
- **Vektoren** — Skalar-, Vektor- und Spatprodukt, Winkel, Projektion; Länge,
  Normieren und das Skalarprodukt mit Projektion (SW7)
- **Abbildungen** — Skalierung, Drehung, Spiegelung, Scherung, Zusammensetzung;
  aus der Bildfigur die Matrix ablesen; Transponierte (SW6); eigene Punkte statt
  Quadrat oder F; Orthogonal prüfen und Abbildung um ein Zentrum (SW7)
- **Regression** (SW8, SW9) — Regressionsgerade durch eigene Datenpunkte mit
  Vorhersage, Projektionsmatrix; die Zeichnung zeigt bei drei Punkten auch den
  Spaltenraum. Die Rechnung »Multiple Regression« nimmt Beobachtungen
  (x₁, …, xₙ, y) und zeigt b̂, P, Q, SQT, SQR und R²

Alle Seiten zeigen ihr Ergebnis als Karte mit drei Ansichten:
**Rechenweg**, **Zeichnung** und **Animation**.

**Zeichnung.** Das Bild steht im Fenster; räumliche Bilder drehst du mit
gedrückter Maustaste. Bei den Vektoren öffnet »Im Browser öffnen« dieselbe
Zeichnung mit Plotly, mit Zoom und Beschriftung beim Überfahren. Bei den
Verfahren sieht man, was die Matrix mit dem Raum macht: bei 2×2 das verzerrte
Einheitsquadrat mit der Fläche |det A|, bei 3×3 die drei Spalten samt Spat.

**Animation.** Manim rendert bei den Verfahren die Umformungen von
LR-Zerlegung, Inverse und Rang, bei den Vektoren eine räumliche Szene pro
Rechnung. Beim Vektorprodukt fährt u × v senkrecht aus der Fläche, beim
Spatprodukt füllt sich der Körper, bei der Projektion fällt das Lot. Die
Kamera dreht sich, weil man erst in der Bewegung sieht, dass etwas wirklich
senkrecht steht. Die Determinante hat keine Animation, Sarrus und Laplace
kommen ohne Zwischenmatrizen aus. Anschaulich wird sie unter »Zeichnung«.

Gerendert wird als MP4 in 720p30, 1080p60 oder 1440p60 und über
QtMultimedia abgespielt. Fehlt das, springt der Abspieler auf ein GIF mit nur
256 Farben.

**Prüfung mit Wolfram|Alpha.** Gibt es auf allen drei Seiten. Bei den
Verfahren vergleicht sie Determinante, Rang und je nach Verfahren Inverse und
Stufenform, bei den Vektoren die gewählte Verknüpfung. Bei der LR-Zerlegung
weichen beide ab: Wolfram wählt die Pivots nach Betrag, die Vorlesung nur bei
einer Null an der Pivotstelle. Beide L und R sind richtig, nur verschieden.
Die App rechnet darum `L · R = P · A` selbst exakt nach und schreibt das in
den Bericht.

Der Regler Gauss / Gauss-Jordan oben rechts gilt nur für die Gauss-Seite und
ist auf den anderen beiden ausgegraut.

## Geprüft gegen

SW7: Folie 5 und 6 (|(4,3)| = 5, a⁰ = (0.8, 0.6)), Folie 22 (T·R und R·T mit
den Matrizen der Folie) und Folie 25/26 (3D-Matrizen). SW8: Folie 9 mit den
Punkten (0,6), (1,0), (2,0): x̂ = (5, −3), p = (5, 2, −1), e = (1, −2, 1),
SQR = 6 und die Projektionsmatrix von Folie 19, P = ⅙·(5 2 −1; 2 2 2; −1 2 5).
Die Aufgaben SW7.F23 und SW8.F14/F18/F19 haben keine Musterlösung; ihre
Ergebnisse sind von Hand und mit dem Normalgleichungs-Test nachgerechnet.

SW9: Gewichtheber-Beispiel Folien 5 bis 21: P (Folie 14, z. B. P₁₁ = 0.76946632),
ŷ und e (Folien 14 und 15), SQT = 3075.2, SQR ≈ 288.7047 und R² ≈ 0.9061 (Folie 21);
dazu die Probe, dass eine Einflussgrösse die Gerade aus SW8 ergibt.

SW6: Folie 7 (Q = A·P mit f₁ = (3, −1)ᵀ, f₂ = (−1, 2)ᵀ) und die Musterlösung
lial-sw-06-loesungen.pdf (Aufgabe 1a, 1c, 1d). Neu hinzugekommen ist nur die
Transponierte.

Die Ergebnisse sind Zahl für Zahl mit `lial-sw-04-loesungen.pdf` verglichen
worden: Determinanten und Inversen der Aufgaben 1 und 2, einschliesslich
der beiden singulären Matrizen. Die LR-Zerlegungen aus SW3 sind über
`L · R = P · A` und `A · x = b` nachgerechnet.

## Design

Alle Farben, Radien, Abstände und Schriften stehen in `design.py` (eine Stelle);
App, Zeichnungen (Matplotlib) und Animationen (Manim) lesen daraus. Look: warmes
Off-White (`#f5f5f5`) mit Tinte, weisse Karten mit Hairline und 16 px Radius,
Pillen-Buttons, Pastell-Orbs nur als Atmosphäre; Dunkelmodus mit Tinten-Canvas
`#0c0a09` und Karten `#1c1917`. Schriften: Inter für die Oberfläche, EB Garamond
Light für Überschriften (Ersatz für Waldenburg); sie werden nur benutzt, wenn
installiert, sonst Helvetica/Georgia. Es liegen keine Fontdateien im Repo.

Quelle: getdesign.md, ElevenLabs DESIGN.md. Das ist eine unabhängige Analyse
und Nachbildung der Gestaltungsprinzipien, kein Produkt von und nicht verbunden
mit ElevenLabs.

## Tests

```bash
python3 tests/tests_abbildung.py    # ebenso sw6, sw7, sw8, sw9, core, gauss, factor, inverse,
python3 tests/tests_determinant.py  # vectors, exercises, plots, anim, app
```
