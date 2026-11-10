"""
Design-Tokens für App, Zeichnungen und Animationen: EINE Stelle für Farben,
Radien, Abstände und Schriften.

Look angelehnt an eine unabhängige Analyse des ElevenLabs-Designsystems
(getdesign.md, DESIGN.md): warmes Off-White, Tinte, weisse Karten mit Hairline,
Pillen-Buttons, Pastell-Orbs nur als Atmosphäre. Waldenburg ist nicht frei
verfügbar; als Ersatz dient EB Garamond Light. Keine Fontdateien im Repo:
die Schriften werden nur benutzt, wenn sie auf dem Rechner installiert sind.
Reines Python, kein Qt/Matplotlib/Manim-Import.
"""

from __future__ import annotations

# --- Rohfarben ---------------------------------------------------------
INK = "#0c0a09"
INK_SOFT = "#292524"          # primary
BODY = "#4e4e4e"
MUTED = "#777169"
MUTED_SOFT = "#a8a29e"
HAIRLINE = "#e7e5e4"
HAIRLINE_STRONG = "#d6d3d1"
CANVAS = "#f5f5f5"
CANVAS_SOFT = "#fafafa"
SURFACE = "#ffffff"
SURFACE_STRONG = "#f0efed"
DARK = "#0c0a09"
DARK_ELEVATED = "#1c1917"
ON_DARK_SOFT = "#a8a29e"

# Pastell nur als Atmosphäre (Orbs, Flächen), nie als Schriftfarbe
MINT, PEACH, LAVENDER, SKY, ROSE = "#a7e5d3", "#f4c5a8", "#c8b8e0", "#a8c8e8", "#e8b8c4"
ORBS = (MINT, PEACH, LAVENDER, SKY, ROSE)

ERROR = "#dc2626"
SUCCESS = "#16a34a"

# --- Radien, Abstände (px) ---------------------------------------------
RADIUS = dict(input=8, card=16, pill=999)
SPACE = dict(xxs=4, xs=8, sm=12, base=16, md=20, lg=24, xl=32, xxl=48, section=96)

# --- Schriften: Kandidaten in Reihenfolge, danach Fallback --------------
FONT_UI = ["Inter", "Inter Variable", "Helvetica Neue", "Helvetica", "Arial",
           "SF Pro Text", ".AppleSystemUIFont", "Segoe UI Variable Text", "Segoe UI",
           "DejaVu Sans"]
FONT_DISPLAY = ["EB Garamond", "Waldenburg", "Georgia", "Times New Roman",
                "Times", "DejaVu Serif"]
FONT_MONO = ["SF Mono", "Menlo", "Cascadia Mono", "Consolas", "DejaVu Sans Mono"]
DISPLAY_WEIGHT = 300          # Light
DISPLAY_SPACING = 99          # Prozent; leicht enger wie die Vorlage
UI_SPACING = 101              # Prozent; leicht geweitet

# --- App-Paletten (Schlüssel wie bisher in lialkit_qt.T) ----------------
APP_LIGHT = dict(
    bg=CANVAS, nav=CANVAS, card=SURFACE, text=INK, sec=BODY, ter=MUTED,
    line=HAIRLINE, hair=HAIRLINE, fill=SURFACE_STRONG, fill2=CANVAS_SOFT,
    seg=SURFACE, blue=INK_SOFT, blue_hi=INK, blue_soft=SURFACE_STRONG,
    on_blue="#ffffff", green=SUCCESS, green_soft="#e7f5ec", red=ERROR,
    red_soft="#fdecec", amber="#92600a", amber_soft="#fbf0dc", flash="#fbe9dc",
    entry=SURFACE, shadow=1, dark=False)

APP_DARK = dict(
    bg=DARK, nav=DARK, card=DARK_ELEVATED, text="#ffffff", sec="#d6d3d1",
    ter=MUTED_SOFT, line="#2e2a28", hair="#2e2a28", fill="#292524", fill2="#151211",
    seg="#3a3532", blue="#ffffff", blue_hi="#e7e5e4", blue_soft="#292524",
    on_blue=INK, green="#4ade80", green_soft="#10281a", red="#f87171",
    red_soft="#331616", amber="#e0a93b", amber_soft="#33280f", flash="#3a2c20",
    entry="#151211", shadow=0, dark=True)

# --- Zeichnungen (Matplotlib/Plotly) -----------------------------------
# Mittlere Töne: tragen auf Weiss wie auf der dunklen Karte.
PLOT_ACCENT = "#8a72c8"       # Original/Hervorhebung (Lavendel)
PLOT_COLORS = [INK_SOFT, PLOT_ACCENT, "#5b8fc4", "#3fa58a", "#d98a52", "#c4708a"]
PLOT_GRID = HAIRLINE
PLOT_MUTED = "#8c857f"

# --- Animationen (Manim) -----------------------------------------------
ANIM = dict(background=CANVAS, text=INK, muted=MUTED, accent="#8a72c8",
            highlight="#e6dff0", pivot="#5b8fc4", good="#2f8f6f")
ANIM_VECTORS = ["#5b8fc4", "#8a72c8", "#2f8f6f", "#d0703a"]
