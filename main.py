"""
Evolução Real - Plague Inc style evolution simulation
Multi-file version with world map
"""

import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2' if os.name == 'nt' else 'gl'

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.animation import Animation

from game.evolution import PathogenSpecies, GENE_DEFINITIONS, format_number
from game.world_data import REGIONS
from game.world_map import WorldMapWidget

import random

# ─── Colors ───────────────────────────────────────────────────
C_BG        = (0.03, 0.05, 0.12, 1)
C_PANEL     = (0.06, 0.10, 0.20, 1)
C_ACCENT    = (0.9, 0.3, 0.05, 1)
C_GREEN     = (0.1, 0.85, 0.3, 1)
C_RED       = (0.9, 0.1, 0.1, 1)
C_YELLOW    = (0.95, 0.85, 0.1, 1)
C_TEXT      = (0.92, 0.92, 0.92, 1)
C_SUBTEXT   = (0.60, 0.65, 0.75, 1)


def make_bg(widget, color):
    """Add dark background rectangle to widget."""
    with widget.canvas.before:
        Color(*color)
        widget._bg_rect = Rectangle(pos=widget.pos, size=widget.size)
    widget.bind(pos=lambda w, v: setattr(w._bg_rect, 'pos', v),
                size=lambda w, v: setattr(w._bg_rect, 'size', v))


class StatBox(BoxLayout):
    def __init__(self, label, value, color=C_TEXT, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.size_hint_y = None
        self.height = dp(52)
        make_bg(self, (0.05, 0.09, 0.18, 1))

        self.lbl_title = Label(text=label, font_size=sp(9),
                               color=C_SUBTEXT, size_hint_y=0.4)
        self.lbl_val = Label(text=value, font_size=sp(15),
                             bold=True, color=color, size_hint_y=0.6)
        self.add_widget(self.lbl_title)
        self.add_widget(self.lbl_val)

    def update(self, value, color=None):
        self.lbl_val.text = value
        if color:
            self.lbl_val.color = color


class GeneButton(BoxLayout):
    def __init__(self, gene_key, gene_obj, on_evolve, **kwargs):
        super().__init__(orientation='horizontal', spacing=dp(4), **kwargs)
        self.size_hint_y = None
        self.height = dp(46)
        self.gene_key = gene_key
        self.gene_obj = gene_obj
        self.on_evolve = on_evolve

        # Left: icon + name
        left = BoxLayout(orientation='vertical', size_hint_x=0.4)
        self.lbl_name = Label(text=f"{gene_obj.icon} {gene_obj.name}",
                              font_size=sp(10), color=C_TEXT,
                              halign='left', valign='middle')
        self.lbl_name.bind(size=self.lbl_name.setter('text_size'))
        left.add_widget(self.lbl_name)

        # Middle: progress bar
        mid = BoxLayout(orientation='vertical', size_hint_x=0.35,
                        padding=[0, dp(12)])
        self.bar = ProgressBar(max=1.0, value=gene_obj.value)
        mid.add_widget(self.bar)

        # Right: evolve button
        btn = Button(text=f"+2🧬", size_hint_x=0.25,
                     background_color=(0.1, 0.2, 0.4, 1),
                     color=(1, 0.85, 0.1, 1),
                     font_size=sp(10))
        btn.bind(on_press=lambda b: self.on_evolve(gene_key))

        self.add_widget(left)
        self.add_widget(mid)
        self.add_widget(btn)

    def refresh(self):
        self.bar.value = self.gene_obj.value


class TopBar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None,
                         height=dp(48), padding=[dp(8), dp(4)],
                         spacing=dp(8), **kwargs)
        make_bg(self, (0.02, 0.04, 0.10, 1))

        self.lbl_title = Label(
            text="🧬 EVOLUÇÃO REAL",
            font_size=sp(14), bold=True, color=C_ACCENT,
            size_hint_x=0.35
        )
        self.lbl_day = Label(text="Dia 0", font_size=sp(11), color=C_SUBTEXT, size_hint_x=0.15)
        self.lbl_infected = Label(text="🦠 0", font_size=sp(12), color=C_YELLOW, size_hint_x=0.2)
        self.lbl_dead = Label(text="💀 0", font_size=sp(12), color=C_RED, size_hint_x=0.2)
        self.lbl_dna = Label(text="🧬 10", font_size=sp(12), color=C_GREEN, size_hint_x=0.1)

        for w in [self.lbl_title, self.lbl_day, self.lbl_infected, self.lbl_dead, self.lbl_dna]:
            self.add_widget(w)

    def update(self, stats, day, dna):
        self.lbl_day.text = f"Dia {int(day)}"
        self.lbl_infected.text = f"🦠 {format_number(stats['infected'])}"
        self.lbl_dead.text = f"💀 {format_number(stats['dead'])}"
        self.lbl_dna.text = f"🧬 {dna}"


class CureBar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None,
                         height=dp(22), padding=[dp(8), 0], **kwargs)
        make_bg(self, (0.04, 0.02, 0.06, 1))

        lbl = Label(text="💊 Cura:", font_size=sp(9), color=(0.7, 0.4, 0.9), size_hint_x=0.2)
        self.add_widget(lbl)

        self.bar = ProgressBar(max=100, value=0, size_hint_x=0.8)
        self.add_widget(self.bar)

    def update(self, pct):
        self.bar.value = pct


class RegionPanel(BoxLayout):
    """Bottom panel showing selected region info."""
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None,
                         height=dp(90), padding=dp(8), spacing=dp(4), **kwargs)
        make_bg(self, (0.05, 0.08, 0.18, 1))

        self.lbl_name = Label(text="Toque em um país para ver detalhes",
                              font_size=sp(11), bold=True, color=C_ACCENT)
        self.lbl_stats = Label(text="", font_size=sp(10), color=C_TEXT)
        self.lbl_bar_label = Label(text="", font_size=sp(9), color=C_SUBTEXT)
        self.inf_bar = ProgressBar(max=100, value=0)

        self.add_widget(self.lbl_name)
        self.add_widget(self.lbl_stats)
        self.add_widget(self.lbl_bar_label)
        self.add_widget(self.inf_bar)

    def show_region(self, region_data, state):
        name = region_data["name"]
        pop = state["population"]
        inf = state["infected"]
        dead = state["dead"]
        disc = "✓ Detectada" if state["discovered"] else "⚠ Não detectada"

        self.lbl_name.text = f"📍 {name}  [{disc}]"
        inf_pct = inf / pop * 100 if pop > 0 else 0
        dead_pct = dead / pop * 100 if pop > 0 else 0
        self.lbl_stats.text = (
            f"🦠 {format_number(inf)} infectados ({inf_pct:.1f}%) | "
            f"💀 {format_number(dead)} mortos ({dead_pct:.2f}%)"
        )
        self.lbl_bar_label.text = f"Taxa de infecção: {inf_pct:.1f}%"
        self.inf_bar.value = min(100, inf_pct)


class GenePanel(ScrollView):
    def __init__(self, pathogen, **kwargs):
        super().__init__(**kwargs)
        self.pathogen = pathogen
        self.do_scroll_x = False

        self.container = GridLayout(cols=1, spacing=dp(3), padding=dp(4),
                                    size_hint_y=None)
        self.container.bind(minimum_height=self.container.setter('height'))

        # Header
        hdr = Label(text="⚡ EVOLUÇÃO DO PATÓGENO", font_size=sp(11),
                    bold=True, color=C_ACCENT, size_hint_y=None, height=dp(28))
        self.container.add_widget(hdr)

        self.gene_buttons = {}
        for gname, gkey, gdesc, gicon in GENE_DEFINITIONS:
            gb = GeneButton(gkey, pathogen.genes[gkey], self._on_evolve)
            self.container.add_widget(gb)
            self.gene_buttons[gkey] = gb

        self.add_widget(self.container)

    def _on_evolve(self, gene_key):
        success = self.pathogen.evolve_gene(gene_key)
        if success:
            self.gene_buttons[gene_key].refresh()

    def refresh(self):
        for gb in self.gene_buttons.values():
            gb.refresh()


class GameScreen(FloatLayout):
    def __init__(self, pathogen, **kwargs):
        super().__init__(**kwargs)
        self.pathogen = pathogen
        self.game_speed = 1.0
        self.paused = False
        self._tick_acc = 0.0

        make_bg(self, C_BG)
        self._build_ui()

        Clock.schedule_interval(self._tick, 1 / 30)

    def _build_ui(self):
        # ── Top Bar ──────────────────────────────────────────
        self.top_bar = TopBar(
            pos_hint={"top": 1}, size_hint=(1, None)
        )
        self.add_widget(self.top_bar)

        # ── Cure Bar ─────────────────────────────────────────
        self.cure_bar = CureBar(
            pos_hint={"top": 0.93}, size_hint=(1, None)
        )
        self.add_widget(self.cure_bar)

        # ── Speed Buttons ────────────────────────────────────
        speed_row = BoxLayout(
            orientation='horizontal', size_hint=(0.5, None),
            height=dp(28), pos_hint={"top": 0.905, "right": 1},
            spacing=dp(2), padding=[dp(4), 0]
        )
        make_bg(speed_row, (0.04, 0.06, 0.15, 1))
        for label, speed in [("⏸", 0), ("▶", 1), ("⏩", 3), ("⏭", 8)]:
            b = Button(text=label, font_size=sp(11),
                       background_color=(0.08, 0.14, 0.28, 1))
            b.speed = speed
            b.bind(on_press=self._set_speed)
            speed_row.add_widget(b)
        self.add_widget(speed_row)

        # ── World Map (center) ───────────────────────────────
        self.world_map = WorldMapWidget(
            pathogen=self.pathogen,
            on_region_click=self._on_region_click,
            pos_hint={"x": 0, "top": 0.905},
            size_hint=(1, None),
            height=Window.height * 0.42
        )
        self.add_widget(self.world_map)

        # ── Region Info Panel ────────────────────────────────
        map_bottom = 1 - 0.905 + Window.height * 0.42 / Window.height
        self.region_panel = RegionPanel(
            pos_hint={"x": 0, "top": 1 - 0.905 + 0.42 + 0.12},
            size_hint=(1, None)
        )
        self.add_widget(self.region_panel)

        # ── Gene Evolution Panel (bottom) ────────────────────
        self.gene_panel = GenePanel(
            pathogen=self.pathogen,
            pos_hint={"x": 0, "y": 0},
            size_hint=(1, 0.30)
        )
        self.add_widget(self.gene_panel)

        # Update map height dynamically
        self.bind(size=self._on_resize)

    def _on_resize(self, *args):
        self.world_map.height = self.height * 0.40
        self.world_map.pos_hint = {"x": 0, "top": 0.905}

    def _set_speed(self, btn):
        speed = btn.speed
        if speed == 0:
            self.paused = True
        else:
            self.paused = False
            self.game_speed = speed

    def _on_region_click(self, region_id):
        region_data = next((r for r in REGIONS if r["id"] == region_id), None)
        if region_data and self.pathogen:
            state = self.pathogen.regions.get(region_id, {})
            if state:
                self.region_panel.show_region(region_data, state)

    def _tick(self, dt):
        if self.paused or not self.pathogen:
            return

        self._tick_acc += dt * self.game_speed * 0.5  # 0.5 = days per real second at speed 1

        if self._tick_acc >= 1.0:
            days = int(self._tick_acc)
            self._tick_acc -= days
            for _ in range(days):
                self.pathogen.tick(dt_days=1.0)

        stats = self.pathogen.get_stats()
        self.top_bar.update(stats, self.pathogen.age_days, self.pathogen.dna_points)
        self.cure_bar.update(stats["cure_pct"])
        self.gene_panel.refresh()

        # Win/lose checks
        if self.pathogen.cured:
            self._show_result(won=False, reason="💊 A humanidade desenvolveu a cura!")
        elif stats["dead"] > 7_500_000_000:
            self._show_result(won=True, reason="☠️ Toda a humanidade foi exterminada!")

    def _show_result(self, won, reason):
        if not self.paused:
            self.paused = True
            color = C_GREEN if won else C_RED
            title = "🏆 VITÓRIA!" if won else "❌ DERROTA"
            content = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
            content.add_widget(Label(text=reason, font_size=sp(14), color=color))
            stats = self.pathogen.get_stats()
            content.add_widget(Label(
                text=f"Dias: {int(stats['age_days'])} | Mortos: {format_number(stats['dead'])}",
                font_size=sp(12), color=C_TEXT
            ))
            btn = Button(text="Jogar novamente", size_hint_y=None, height=dp(44),
                         background_color=(0.1, 0.3, 0.6, 1))
            content.add_widget(btn)
            popup = Popup(title=title, content=content, size_hint=(0.85, 0.5),
                          background_color=C_PANEL)
            btn.bind(on_press=lambda b: App.get_running_app().restart())
            popup.open()


class MenuScreen(FloatLayout):
    def __init__(self, on_start, **kwargs):
        super().__init__(**kwargs)
        self.on_start_cb = on_start
        make_bg(self, C_BG)
        self._build()

    def _build(self):
        layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(16),
                           pos_hint={"center_x": 0.5, "center_y": 0.5},
                           size_hint=(0.9, 0.85))
        make_bg(layout, C_PANEL)

        # Title
        layout.add_widget(Label(
            text="🧬 EVOLUÇÃO REAL",
            font_size=sp(28), bold=True, color=C_ACCENT,
            size_hint_y=0.2
        ))
        layout.add_widget(Label(
            text="Evolua seu patógeno.\nInfecte o mundo. Sobreviva à cura.",
            font_size=sp(13), color=C_SUBTEXT,
            halign='center', size_hint_y=0.15
        ))

        # Select origin
        layout.add_widget(Label(text="📍 Escolha o país de origem:",
                                font_size=sp(12), color=C_TEXT, size_hint_y=0.1))

        # Region grid
        scroll = ScrollView(size_hint_y=0.45)
        grid = GridLayout(cols=2, spacing=dp(6), padding=dp(8),
                          size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        self.selected_origin = REGIONS[0]["id"]
        self.origin_buttons = {}

        for r in REGIONS:
            btn = Button(
                text=f"{r['name']}\n🌍 {r['continent']}",
                font_size=sp(10), size_hint_y=None, height=dp(50),
                background_color=(0.08, 0.15, 0.30, 1)
            )
            btn.region_id = r["id"]
            btn.bind(on_press=self._select_origin)
            grid.add_widget(btn)
            self.origin_buttons[r["id"]] = btn

        scroll.add_widget(grid)
        layout.add_widget(scroll)

        # Pathogen name
        from kivy.uix.textinput import TextInput
        self.name_input = TextInput(
            text="Patógeno X",
            hint_text="Nome do patógeno",
            multiline=False, size_hint_y=None, height=dp(40),
            background_color=(0.08, 0.14, 0.25, 1),
            foreground_color=C_TEXT,
            font_size=sp(13)
        )
        layout.add_widget(self.name_input)

        # Start button
        start_btn = Button(
            text="🦠  INICIAR EVOLUÇÃO",
            font_size=sp(15), bold=True, size_hint_y=None, height=dp(52),
            background_color=(*C_ACCENT[:3], 1)
        )
        start_btn.bind(on_press=self._start)
        layout.add_widget(start_btn)

        self.add_widget(layout)
        self._select_origin_id(REGIONS[0]["id"])

    def _select_origin(self, btn):
        self._select_origin_id(btn.region_id)

    def _select_origin_id(self, rid):
        # Deselect previous
        if self.selected_origin in self.origin_buttons:
            self.origin_buttons[self.selected_origin].background_color = (0.08, 0.15, 0.30, 1)
        self.selected_origin = rid
        self.origin_buttons[rid].background_color = (0.2, 0.5, 0.1, 1)

    def _start(self, btn):
        name = self.name_input.text.strip() or "Patógeno X"
        self.on_start_cb(name, self.selected_origin)


class EvolucaoRealApp(App):
    def build(self):
        Window.clearcolor = C_BG
        self.title = "Evolução Real"
        self.root_layout = FloatLayout()

        self.menu = MenuScreen(on_start=self._start_game)
        self.root_layout.add_widget(self.menu)

        return self.root_layout

    def _start_game(self, name, origin_id):
        self.pathogen = PathogenSpecies(name, origin_id)
        self.root_layout.clear_widgets()

        self.game_screen = GameScreen(
            pathogen=self.pathogen,
            size_hint=(1, 1)
        )
        self.root_layout.add_widget(self.game_screen)

    def restart(self):
        self.root_layout.clear_widgets()
        self.menu = MenuScreen(on_start=self._start_game)
        self.root_layout.add_widget(self.menu)


if __name__ == "__main__":
    EvolucaoRealApp().run()
