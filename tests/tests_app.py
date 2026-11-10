#!/usr/bin/env python3
"""
Tests für app/lialkit_qt.py (Fenster ohne Bildschirm). Start: python3 tests/tests_app.py

Läuft mit QT_QPA_PLATFORM=offscreen und braucht kein Netz. Ohne PySide6 wird
übersprungen (SKIP, Exit-Code 0).
"""
import os
from fractions import Fraction
import sys

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("MPLBACKEND", "Agg")
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(_here)))   # Elternordner des Pakets lialkit
sys.path.insert(0, os.path.join(os.path.dirname(_here), "app"))

try:
    import PySide6  # noqa: F401
except ImportError:
    print("SKIP: PySide6 nicht installiert")
    sys.exit(0)

import lialkit_qt as Q  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import QApplication, QMainWindow  # noqa: E402

_app = QApplication.instance() or QApplication([])
if Q.FONTS is None:                                   # main() setzt das sonst
    Q.FONTS = Q.Fonts()


def test_import():
    assert hasattr(Q, "MainWindow") and issubclass(Q.MainWindow, QMainWindow)
    assert callable(Q.main)


def test_main_window():
    w = Q.MainWindow()
    try:
        assert w.windowTitle() and w.width() > 0
        assert w.rows_n == 3 and w.cols_n == 3 and w.editing
        assert w.draft[0] == ["2", "1", "-1", "8"]     # Beispiel aus __init__.py
        w.show()
        _app.processEvents()
        assert w.isVisible()
    finally:
        w.close()
        w.deleteLater()


SHOTS = "/tmp/shots_app2"


def _shot(w, name):
    os.makedirs(SHOTS, exist_ok=True)
    for _ in range(4):                       # Layout setzt sich erst nach ein paar Runden
        _app.processEvents()
        QTest.qWait(80)
    w.grab().save(os.path.join(SHOTS, name + ".png"))


def test_maps_page():
    """Seite »Abbildungen«: alle drei Rechnungen, Zeichnung, Film-Auftrag, hell und dunkel."""
    w = Q.MainWindow()
    try:
        w.resize(1240, 900)
        w.show()
        w.seg_page.set_value(3)
        w.set_page(3)
        page = w.page_maps
        assert w.seg_page.options[3] == "Abbildungen" and w.stack.currentIndex() == 3
        _app.processEvents()

        # Abbilden: Scherung, Einheitsquadrat -> Ecken (0,0) (1,0) (2,1) (1,1)
        page.compute()
        res = page.result()
        assert res.Q.rows == [[0, 1, 2, 1], [0, 0, 1, 1]], res.Q.rows
        # Typ Drehung 30 Grad mit Buchstabe F: Näherung, wird dezimal gezeigt
        page.slot_a.set_type("Drehung")
        page.seg_obj.set_value(1)
        page.set_obj(1)
        page.compute()
        assert page.result().decimal

        for theme in (0, 1):
            w.set_theme(theme)
            tag = "dunkel" if theme else "hell"
            page.set_op(0)
            page.compute()
            _shot(w, f"abbilden_rechenweg_{tag}")
            page.draw()
            assert page.plot.figure is not None
            _shot(w, f"abbilden_zeichnung_{tag}")
            job = page.build_job("", "low")               # Film-Auftrag ohne Render
            assert job.scene == "abbild" and len(job.vectors) == 11 and len(job.matrix) == 2
            Q.show_view(page, 2)
            _shot(w, f"abbilden_animation_{tag}")

            # Zusammensetzen: B·A mit B = Drehung 90 Grad
            page.slot_a.set_type("Eigene")
            page.set_op(1)
            page.compute()
            res = page.result()
            assert res.matrix.rows == [[0, -1], [1, 1]], res.matrix.rows
            _shot(w, f"zusammensetzen_rechenweg_{tag}")
            page.draw()
            _shot(w, f"zusammensetzen_zeichnung_{tag}")

            # Aus Bildern ablesen: lineares Beispiel, dann Verschiebung, dann nichts
            page.set_op(2)
            page.compute()
            assert page.result().A is not None
            _shot(w, f"ablesen_linear_{tag}")
            page.draw()
            _shot(w, f"ablesen_zeichnung_{tag}")
            page.q_fields[0][0].setText("1")            # (0,0) -> (1,0): nur homogen
            page.q_fields[0][1].setText("1")
            page.q_fields[1][0].setText("2")
            page.q_fields[1][1].setText("1")
            page.q_fields[2][0].setText("3")
            page.q_fields[2][1].setText("2")
            page.q_fields[3][0].setText("2")
            page.q_fields[3][1].setText("2")
            page.compute()
            r = page.result()
            assert r.A is None and r.H is not None
            _shot(w, f"ablesen_homogen_{tag}")
            page.q_fields[2][0].setText("7")            # kein Parallelogramm mehr
            page.compute()
            r = page.result()
            assert r.A is None and r.H is None
            assert isinstance(page.matrix_to_draw(), str)
            _shot(w, f"ablesen_keine_{tag}")
            for f, v in zip((page.q_fields[0][0], page.q_fields[0][1], page.q_fields[1][0],
                             page.q_fields[1][1], page.q_fields[2][0], page.q_fields[2][1],
                             page.q_fields[3][0], page.q_fields[3][1]),
                            "00103121"):
                f.setText(v)                              # zurück zum linearen Beispiel
            page.set_op(0)

        page.slot_a.set_type("Eigene")
        page.slot_a.fields[0].setText("x")
        page.compute()                                    # Fehler statt Absturz
        assert page.lbl_err.text()
    finally:
        w.close()
        w.deleteLater()


def test_maps_week6():
    """SW6: Transponierte und eigene Punkte auf der Seite »Abbildungen«."""
    w = Q.MainWindow()
    try:
        w.resize(1240, 900)
        w.show()
        w.set_page(3)
        page = w.page_maps
        assert "Transponierte" in Q.MAP_OPS
        assert Q.parse_points("(0,0) (2,1) (3,3)") == [(0, 0), (2, 1), (3, 3)]
        try:
            Q.parse_points("nix")
            raise AssertionError("parse_points hätte scheitern müssen")
        except ValueError:
            pass
        page.set_obj(2)                                   # eigene Punkte
        page.pts_edit.setText("(0,0) (2,0) (2,1)")
        page.set_op(list(Q.MAP_OPS.values()).index("transpose"))   # A = Scherung (1 1; 0 1)
        page.compute()
        r = page.result()
        assert r.Q.rows == [[0, 2, 3], [0, 0, 1]] and r.Qt.rows == [[0, 2, 2], [0, 2, 3]]
        page.draw()
        assert page.plot.figure is not None
        assert len(page.points(True).rows[0]) == 4        # geschlossen: erster Punkt am Ende
        page.pts_edit.setText("kaputt")
        page.compute()                                    # Fehlertext statt Absturz
        assert page.lbl_err.text()
    finally:
        w.close()
        w.deleteLater()


def test_week7_8():
    """SW7: Vektoren-Rechnungen, Abbildungen (orthogonal, um Zentrum); SW8: Seite »Regression«."""
    w = Q.MainWindow()
    try:
        w.resize(1240, 900)
        w.show()
        # Navigation: neue Seite hinten, die alten Indizes bleiben
        assert w.stack.count() == 5

        # Vektoren: Skalarprodukt mit allem, Länge, Normieren
        w.set_page(2)
        v = w.page_vectors
        assert list(Q.VECTOR_OPS)[:8] == ["Skalarprodukt", "Vektorprodukt", "Spatprodukt", "Winkel",
                                          "Projektion", "Addition", "Ortsvektor / Verbindung", "Skalar · Vektor"]
        v.set_dim(0)                                         # zwei Einträge
        v.fields[0][0].setText("4"); v.fields[0][1].setText("3")
        v.fields[1][0].setText("1"); v.fields[1][1].setText("5")
        for name, key in (("Länge (Norm)", "laenge"), ("Normieren", "normieren"),
                          ("Skalarprodukt mit Winkel und Projektion", "skalarprodukt")):
            v.set_op(name)
            assert v.op == key
            v.compute()
            assert v.figure(False) is not None
            assert isinstance(v.build_job("full", "Schnell"), str)      # ohne Animation, mit Erklärung
        # Abbildungen: Orthogonal prüfen und Um Zentrum
        w.set_page(3)
        m = w.page_maps
        assert list(Q.MAP_OPS)[:4] == ["Abbilden", "Zusammensetzen", "Aus Bildern ablesen", "Transponierte"]
        assert Q.parse_center("(2, 3)") == (2, 3) and Q.parse_center("2,3") == (2, 3)
        try:
            Q.parse_center("2")
            raise AssertionError("parse_center hätte scheitern müssen")
        except ValueError:
            pass
        m.slot_a.set_type("Drehung")
        m.slot_a.vals["Drehung"] = ["90"]
        m.slot_a._build()
        m.set_op(list(Q.MAP_OPS.values()).index("orthogonal"))
        assert bool(m.result()) and "Drehung" in m.result().art
        m.set_op(list(Q.MAP_OPS.values()).index("center"))
        m.center_edit.setText("2,3")
        m.set_obj(1)                                         # Buchstabe F
        assert m.result().matrix.rows == [[0, -1, 5], [1, 0, 1], [0, 0, 1]]
        m.compute()
        m.draw()
        assert m.plot.figure is not None
        m.center_edit.setText("x")
        m.compute()
        assert m.lbl_err.text()

        # Regression
        w.set_page(4)
        r = w.page_regression
        r.compute()
        assert r.result().C == 5 and r.result().D == -3
        assert "-4" in r.lbl_pred.text().replace("\u2212", "-")     # Vorhersage bei t = 3
        r.draw()
        assert r.plot.figure is not None
        r.set_op("Projektionsmatrix")
        r.compute()
        assert r.result().P.rows[0][0] == Fraction(5, 6)
        assert isinstance(r.build_job("full", "Schnell"), str)
        r.pts_edit.setText("(1,2) (1,5)")                    # gleiche t: keine eindeutige Lösung
        r.compute()
        assert r.lbl_err.text()
        r.pts_edit.setText("nix")
        r.compute()
        assert r.lbl_err.text()
        # SW9: multiple Regression (Gewichtheber, Folie 21)
        r.set_op("Multiple Regression")
        r.t_edit.setText("3, 1.5")
        r.compute()
        assert abs(float(r.result().r2) - 0.9061183908658075) < 1e-9 and not r.lbl_err.text()
        assert "R²" in r.lbl_pred.text()
        r.draw()
        assert r.plot.figure is not None
        r.multi_edit.setText("(1,2) (2,3)")
        r.compute()
        assert r.lbl_err.text()
        w.set_theme(1)                                       # restyle aller Seiten
        w.set_theme(0)
    finally:
        w.close()
        w.deleteLater()


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok  ", name)
            except Exception as e:  # noqa: BLE001
                import traceback
                fails += 1
                print("FAIL", name, repr(e))
                traceback.print_exc()
    print("alle Tests bestanden" if not fails else f"{fails} Test(s) fehlgeschlagen")
    sys.exit(1 if fails else 0)
