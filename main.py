# ==============================================================
# 🧬 EVOLUÇÃO REAL - Simulação Evolutiva Autônoma
# Engine: Kivy (Android/iOS/Desktop)
# Arquivo único - compila para APK via Buildozer
# ==============================================================

import kivy
kivy.require('2.3.0')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import (Color, Ellipse, Rectangle, Line,
                            RoundedRectangle, Triangle)
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp, sp

import random
import math
import json
import os
import time

# ─────────────────────────────────────────────────────────────
# CONSTANTES GLOBAIS
# ─────────────────────────────────────────────────────────────
SAVE_FILE       = 'evo_save.json'
TICK_INTERVAL   = 0.08   # segundos entre ticks em tempo real
OFFLINE_SPEED   = 20     # ticks por segundo enquanto offline
MAX_OFFLINE_TICKS = 50000

# Paleta de cores
C_BG       = (0.04, 0.04, 0.09, 1)
C_PANEL    = (0.07, 0.07, 0.14, 1)
C_PRIMARY  = (0.20, 0.85, 0.65, 1)
C_PURPLE   = (0.75, 0.30, 0.90, 1)
C_GOLD     = (1.00, 0.80, 0.20, 1)
C_RED      = (0.90, 0.25, 0.25, 1)
C_TEXT     = (0.88, 0.93, 1.00, 1)
C_DIM      = (0.45, 0.55, 0.65, 1)

# ─────────────────────────────────────────────────────────────
# SISTEMA DE DNA
# ─────────────────────────────────────────────────────────────

class Gene:
    NAMES = {
        'speed':        '⚡ Velocidade',
        'resistance':   '🛡 Resistência',
        'reproduction': '🔄 Reprodução',
        'intelligence': '🧠 Inteligência',
        'metabolism':   '⚙ Metabolismo',
        'camouflage':   '🫥 Camuflagem',
        'aggression':   '⚔ Agressividade',
        'aquatic':      '🌊 Aquático',
        'size':         '📏 Tamanho',
    }

    def __init__(self, name, value, lo=0.0, hi=10.0):
        self.name  = name
        self.value = max(lo, min(hi, float(value)))
        self.lo    = lo
        self.hi    = hi

    def mutate(self, radiation=1.0):
        if random.random() < min(0.9, 0.04 * radiation):
            delta = random.gauss(0, 0.6 * radiation)
            self.value = max(self.lo, min(self.hi, self.value + delta))

    def copy(self):
        return Gene(self.name, self.value, self.lo, self.hi)

    def display_name(self):
        return self.NAMES.get(self.name, self.name)


class DNA:
    GENE_KEYS = ['speed','resistance','reproduction','intelligence',
                 'metabolism','camouflage','aggression','aquatic','size']

    def __init__(self, **kwargs):
        defaults = dict(speed=3, resistance=2, reproduction=5,
                        intelligence=1, metabolism=3, camouflage=1,
                        aggression=2, aquatic=0, size=2)
        defaults.update(kwargs)
        self.genes = {k: Gene(k, defaults[k]) for k in self.GENE_KEYS}

    def get(self, key):
        return self.genes[key].value

    def copy(self):
        d = DNA()
        d.genes = {k: g.copy() for k, g in self.genes.items()}
        return d

    def mutate(self, radiation=1.0):
        child = self.copy()
        for g in child.genes.values():
            g.mutate(radiation)
        # Chance de "salto evolutivo" raro
        if random.random() < 0.008 * radiation:
            key = random.choice(self.GENE_KEYS)
            child.genes[key].value = min(10, child.genes[key].value +
                                         random.uniform(1.0, 3.0))
        return child

    def crossover(self, other):
        child = DNA()
        for k in self.GENE_KEYS:
            child.genes[k] = (self.genes[k] if random.random() < 0.5
                              else other.genes[k]).copy()
        return child

    def fitness(self, env):
        """Fitness de sobrevivência no ambiente (0..∞)"""
        score = 0.0
        temp  = env.get('temperature', 5)
        water = env.get('water', 5)
        rad   = env.get('radiation', 3)
        pred  = env.get('predator_pressure', 0)
        res   = env.get('resources', 5)

        # Temperatura extrema exige resistência
        if temp > 7 or temp < 3:
            score += self.get('resistance') * 2.0
        else:
            score += self.get('resistance') * 0.6

        # Ambiente aquático
        if water > 6:
            score += self.get('aquatic') * 2.5
            score -= max(0, 2 - self.get('aquatic')) * 0.8
        else:
            score -= self.get('aquatic') * 0.4

        # Radiação = mutações mas custo de resistência
        score -= rad * 0.15 * (10 - self.get('resistance')) * 0.1

        # Predadores → velocidade, camuflagem, inteligência salvam
        if pred > 0:
            score += (self.get('speed') * 1.5 +
                      self.get('camouflage') * 2.0 +
                      self.get('intelligence') * 1.0)

        # Escassez → metabolismo baixo e inteligência ajudam
        if res < 3:
            score -= self.get('metabolism') * 0.5
            score += self.get('intelligence') * 2.0
        else:
            score += res * 0.3

        # Inteligência sempre beneficia
        score += self.get('intelligence') * 0.8

        return max(0.05, score)

    def to_dict(self):
        return {k: g.value for k, g in self.genes.items()}

    @classmethod
    def from_dict(cls, d):
        return cls(**{k: d.get(k, 0) for k in cls.GENE_KEYS})


# ─────────────────────────────────────────────────────────────
# ESPÉCIE
# ─────────────────────────────────────────────────────────────

_SPECIES_COUNTER = 0

PHASE_ORDER = ['microscópica','aquática','terrestre','predatória',
               'inteligente','civilização','tecnológica']

PREFIXES = ['Evo','Proto','Neo','Alpha','Meta','Xeno','Cyto','Bio',
            'Omni','Ultra','Para','Hex','Arc','Nex','Geo','Vex']
SUFFIXES = ['morphus','ensis','vorus','sapiens','rex','forma',
            'genix','cyte','derm','phage','ptera','nex','thar','vax']

def _rnd_color():
    h = random.random()
    # Cores vibrantes via HSV→RGB manual
    s, v = 0.8, 0.95
    i = int(h * 6)
    f = h * 6 - i
    p, q, t = v*(1-s), v*(1-s*f), v*(1-s*(1-f))
    combos = [(v,t,p),(q,v,p),(p,v,t),(p,q,v),(t,p,v),(v,p,q)]
    r,g,b = combos[i % 6]
    return [r, g, b, 1.0]

def _gen_name():
    return random.choice(PREFIXES) + random.choice(SUFFIXES)


class Species:
    def __init__(self, dna, population=50, generation=0, name=None, color=None):
        global _SPECIES_COUNTER
        _SPECIES_COUNTER += 1
        self.sid        = _SPECIES_COUNTER
        self.dna        = dna
        self.population = int(population)
        self.generation = generation
        self.age        = 0
        self.name       = name or _gen_name()
        self.color      = color or _rnd_color()
        self.phase      = 'microscópica'
        self.adaptations = []
        self.history    = []   # snapshots de população
        self.extinct    = False
        # Posição no mapa (0..1)
        self.x  = random.uniform(0.08, 0.92)
        self.y  = random.uniform(0.08, 0.92)
        self.vx = random.uniform(-0.003, 0.003)
        self.vy = random.uniform(-0.003, 0.003)

    # ── Ciclo de vida ──────────────────────────────────────────

    def tick(self, env, all_species):
        if self.extinct:
            return

        self.age += 1

        # Mover no mapa
        self.x = max(0.03, min(0.97, self.x + self.vx))
        self.y = max(0.03, min(0.97, self.y + self.vy))
        if not (0.03 < self.x < 0.97): self.vx *= -1
        if not (0.03 < self.y < 0.97): self.vy *= -1

        fitness = self.dna.fitness(env)

        # ── Mortalidade natural ──
        death_rate = max(0.005, 0.20 - fitness * 0.012)
        deaths = int(self.population * death_rate * random.uniform(0.5, 1.5))

        # ── Catástrofes ──
        if random.random() < 0.0008 * env.get('catastrophes', 2):
            deaths += int(self.population * random.uniform(0.10, 0.55))
        if random.random() < 0.0004 * env.get('volcanic', 3):
            deaths += int(self.population * random.uniform(0.05, 0.30))

        self.population = max(0, self.population - deaths)
        if self.population == 0:
            self.extinct = True
            return

        # ── Reprodução ──
        repro = self.dna.get('reproduction') * 0.025
        births = int(self.population * repro * random.uniform(0.6, 1.4))

        # Cap de recursos
        res   = env.get('resources', 5)
        intel = self.dna.get('intelligence')
        cap   = int(res * 120 * (1 + intel * 0.25))
        self.population = min(cap, self.population + births)

        # ── Predação entre espécies ──
        for other in all_species:
            if other.sid == self.sid or other.extinct:
                continue
            dist = math.hypot(self.x - other.x, self.y - other.y)
            if dist < 0.18:
                agg_diff = other.dna.get('aggression') - self.dna.get('aggression')
                if agg_diff > 1.5:
                    prey_d = int(self.population * 0.04 * agg_diff / 10)
                    self.population  = max(0, self.population - prey_d)
                    other.population = min(cap, other.population + prey_d // 2)
                    if self.population == 0:
                        self.extinct = True
                        return

        # ── Snapshot ──
        if self.age % 60 == 0:
            self.history.append(self.population)
            if len(self.history) > 120:
                self.history.pop(0)

        # ── Mutação contínua ──
        rad = env.get('radiation', 3)
        if self.age % 80 == 0 and random.random() < 0.12 + rad * 0.04:
            self.dna = self.dna.mutate(rad)
            self.generation += 1
            self._check_adaptations()

        self._update_phase()

    def _check_adaptations(self):
        for key in DNA.GENE_KEYS:
            if self.dna.get(key) >= 8.5:
                label = f"Mestre em {Gene.NAMES.get(key, key)}"
                if label not in self.adaptations:
                    self.adaptations.append(label)
        if (self.dna.get('intelligence') > 7 and
                'Consciência emergente' not in self.adaptations):
            self.adaptations.append('Consciência emergente')
        if (self.dna.get('aquatic') > 7 and self.dna.get('speed') > 6
                and 'Domínio dos oceanos' not in self.adaptations):
            self.adaptations.append('Domínio dos oceanos')

    def _update_phase(self):
        intel = self.dna.get('intelligence')
        aqua  = self.dna.get('aquatic')
        agg   = self.dna.get('aggression')
        if intel >= 9:
            self.phase = 'tecnológica'
        elif intel >= 7.5:
            self.phase = 'civilização'
        elif intel >= 5.5:
            self.phase = 'inteligente'
        elif agg >= 7 and self.dna.get('speed') >= 6:
            self.phase = 'predatória'
        elif aqua >= 5:
            self.phase = 'aquática'
        elif self.age > 200:
            self.phase = 'terrestre'
        else:
            self.phase = 'microscópica'

    def split(self, env):
        """Especiação: cria nova espécie divergente."""
        rad      = env.get('radiation', 3)
        new_dna  = self.dna.mutate(rad * 2.0)
        new_pop  = self.population // 4
        self.population -= new_pop
        child    = Species(new_dna, new_pop, self.generation + 1)
        child.x  = max(0.03, min(0.97, self.x + random.uniform(-0.12, 0.12)))
        child.y  = max(0.03, min(0.97, self.y + random.uniform(-0.12, 0.12)))
        return child

    # ── Serialização ──────────────────────────────────────────
    def to_dict(self):
        return dict(sid=self.sid, dna=self.dna.to_dict(),
                    population=self.population, generation=self.generation,
                    age=self.age, name=self.name, color=self.color,
                    phase=self.phase, adaptations=self.adaptations,
                    history=self.history, extinct=self.extinct,
                    x=self.x, y=self.y, vx=self.vx, vy=self.vy)

    @classmethod
    def from_dict(cls, d):
        global _SPECIES_COUNTER
        s = cls(DNA.from_dict(d['dna']), d['population'],
                d['generation'], d['name'], d['color'])
        s.sid         = d['sid']
        s.age         = d['age']
        s.phase       = d['phase']
        s.adaptations = d['adaptations']
        s.history     = d['history']
        s.extinct     = d['extinct']
        s.x, s.y      = d['x'], d['y']
        s.vx, s.vy    = d['vx'], d['vy']
        _SPECIES_COUNTER = max(_SPECIES_COUNTER, s.sid)
        return s


# ─────────────────────────────────────────────────────────────
# MUNDO / ENGINE DE SIMULAÇÃO
# ─────────────────────────────────────────────────────────────

class World:
    def __init__(self):
        self.env = dict(temperature=5, water=5, volcanic=3,
                        radiation=3, catastrophes=2, resources=5,
                        predator_pressure=0)
        self.species          = []
        self.tick_count       = 0
        self.year             = 0
        self.influence_pts    = 10
        self.events           = []
        self.mode             = 'scientist'   # scientist | god | hardcore
        self.total_extinct    = 0
        self.last_save_time   = time.time()
        self.paused           = False

    # ── Eventos ──────────────────────────────────────────────

    def log(self, msg):
        self.events.insert(0, f"[Ano {self.year:,}] {msg}")
        if len(self.events) > 60:
            self.events.pop()

    # ── Tick principal ────────────────────────────────────────

    def tick(self, n=1):
        for _ in range(n):
            if self.paused:
                return

            self.tick_count += 1
            self.year        = self.tick_count * 10   # 1 tick = 10 anos

            # Mudança climática lenta
            if self.tick_count % 300 == 0:
                key = random.choice(['resources','radiation','temperature'])
                self.env[key] = max(0.5, min(10, self.env[key] +
                                              random.uniform(-0.3, 0.3)))

            new_species = []
            for sp in self.species:
                if sp.extinct:
                    continue

                sp.tick(self.env, self.species)

                if sp.extinct:
                    self.log(f"💀 {sp.name} foi extinta!")
                    self.total_extinct += 1
                    continue

                # Especiação
                if (sp.population > 150 and sp.age % 250 == 0
                        and len(self.species) < 22
                        and random.random() < 0.06):
                    child = sp.split(self.env)
                    new_species.append(child)
                    self.log(f"🧬 Nova espécie: {child.name} divergiu de {sp.name}!")

            self.species.extend(new_species)

            # Remover extintas antigas (manter últimas 5 para história)
            alive    = [s for s in self.species if not s.extinct]
            extinct  = [s for s in self.species if s.extinct]
            self.species = alive + extinct[-5:]

            # Ganho passivo de pontos de influência
            if self.tick_count % 80 == 0:
                alive_count = len(alive)
                self.influence_pts += max(1, alive_count // 2)

    # ── Influência evolutiva ──────────────────────────────────

    INFLUENCE_COSTS = {
        'force_mutation':    5,
        'catastrophe':       8,
        'virus':            10,
        'boost_intel':      15,
        'climate':          12,
        'food_bloom':        6,
        'rad_pulse':         8,
        'mass_extinction':  25,
        'seed_life':        20,
    }

    def apply_influence(self, action, target=None):
        cost = self.INFLUENCE_COSTS.get(action, 5)
        if self.influence_pts < cost:
            return False, f"Precisa de {cost} ⚡ (você tem {self.influence_pts})"

        self.influence_pts -= cost

        if action == 'force_mutation' and target:
            target.dna = target.dna.mutate(radiation=6.0)
            target.generation += 1
            target._check_adaptations()
            self.log(f"⚡ Mutação forçada em {target.name}!")
            return True, f"Mutação aplicada em {target.name}!"

        elif action == 'catastrophe':
            killed = 0
            for sp in self.species:
                if sp.extinct: continue
                d = int(sp.population * random.uniform(0.25, 0.65))
                sp.population = max(0, sp.population - d)
                killed += d
            self.log(f"🌋 CATÁSTROFE GLOBAL! {killed:,} criaturas pereceram!")
            return True, f"Catástrofe global! {killed:,} mortes."

        elif action == 'virus' and target:
            d = int(target.population * random.uniform(0.35, 0.75))
            target.population = max(0, target.population - d)
            self.log(f"🦠 Vírus devastou {target.name}! -{d:,} indivíduos")
            return True, f"Vírus lançado! -{d:,} de {target.name}"

        elif action == 'boost_intel' and target:
            target.dna.genes['intelligence'].value = min(
                10, target.dna.get('intelligence') + 2.5)
            target._update_phase()
            self.log(f"🧠 Inteligência de {target.name} amplificada!")
            return True, "Inteligência amplificada!"

        elif action == 'climate':
            self.env['temperature'] = random.uniform(1, 9)
            self.env['water']       = random.uniform(1, 9)
            self.log("🌪 Evento climático massivo! Planeta transformado!")
            return True, "Evento climático lançado!"

        elif action == 'food_bloom':
            self.env['resources'] = min(10, self.env['resources'] + 3)
            self.log("🌿 Explosão de recursos! Vida prospera por toda parte!")
            return True, "Recursos aumentados!"

        elif action == 'rad_pulse':
            old = self.env['radiation']
            self.env['radiation'] = min(10, old + 4)
            Clock.schedule_once(lambda dt: self.env.update(radiation=old), 15)
            self.log("☢ Pulso de radiação! Mutações em massa!")
            return True, "Pulso de radiação ativo por 15 ticks!"

        elif action == 'mass_extinction':
            survivor = max((s for s in self.species if not s.extinct),
                          key=lambda s: s.dna.fitness(self.env), default=None)
            for sp in self.species:
                if sp.extinct: continue
                if survivor and sp.sid == survivor.sid: continue
                sp.population = max(0, sp.population // 10)
            self.log("☄ EXTINÇÃO EM MASSA! Apenas os mais fortes sobreviveram!")
            return True, "Extinção em massa executada!"

        elif action == 'seed_life':
            # Adiciona nova espécie aleatória
            new_dna = DNA(
                speed=random.uniform(1,5),
                resistance=random.uniform(1,5),
                reproduction=random.uniform(3,8),
                intelligence=random.uniform(0,3),
                metabolism=random.uniform(2,6),
                camouflage=random.uniform(0,4),
                aggression=random.uniform(0,4),
                aquatic=random.uniform(0,5),
                size=random.uniform(1,4),
            )
            new_sp = Species(new_dna, population=30)
            self.species.append(new_sp)
            self.log(f"🌱 Nova espécie {new_sp.name} introduzida ao planeta!")
            return True, f"Vida introduzida: {new_sp.name}!"

        return False, "Ação inválida"

    # ── Helpers ───────────────────────────────────────────────

    def alive_species(self):
        return [s for s in self.species if not s.extinct]

    def total_population(self):
        return sum(s.population for s in self.alive_species())

    def dominant(self):
        alive = self.alive_species()
        return max(alive, key=lambda s: s.population) if alive else None

    def simulate_offline(self):
        """Simula ticks que passaram enquanto o app estava fechado."""
        elapsed = time.time() - self.last_save_time
        n = int(min(MAX_OFFLINE_TICKS, elapsed * OFFLINE_SPEED))
        if n > 0:
            self.log(f"⏰ Offline: {n} épocas simuladas ({elapsed:.0f}s ausente)")
            self.tick(n)
        return n

    # ── Serialização ──────────────────────────────────────────

    def to_dict(self):
        return dict(
            env=self.env,
            species=[s.to_dict() for s in self.species],
            tick_count=self.tick_count,
            year=self.year,
            influence_pts=self.influence_pts,
            events=self.events[:30],
            mode=self.mode,
            total_extinct=self.total_extinct,
            last_save_time=time.time(),
        )

    @classmethod
    def from_dict(cls, d):
        w = cls()
        w.env           = d['env']
        w.tick_count    = d['tick_count']
        w.year          = d['year']
        w.influence_pts = d['influence_pts']
        w.events        = d.get('events', [])
        w.mode          = d.get('mode', 'scientist')
        w.total_extinct = d.get('total_extinct', 0)
        w.last_save_time= d.get('last_save_time', time.time())
        w.species       = [Species.from_dict(s) for s in d['species']]
        return w


# ─────────────────────────────────────────────────────────────
# ESTADO GLOBAL
# ─────────────────────────────────────────────────────────────

world: World = None   # type: ignore

def save_game():
    if world is None:
        return
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(world.to_dict(), f)
    except Exception as e:
        print(f"[SAVE ERROR] {e}")

def load_game():
    global world
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r') as f:
                world = World.from_dict(json.load(f))
            return True
    except Exception as e:
        print(f"[LOAD ERROR] {e}")
    return False


# ─────────────────────────────────────────────────────────────
# WIDGETS REUTILIZÁVEIS
# ─────────────────────────────────────────────────────────────

def add_bg(widget, color=C_PANEL):
    with widget.canvas.before:
        Color(*color)
        rect = Rectangle(pos=widget.pos, size=widget.size)
    widget.bind(pos=lambda i,v: setattr(rect,'pos',v),
                size=lambda i,v: setattr(rect,'size',v))


class EvoLabel(Label):
    def __init__(self, text='', font_size='14sp', color=C_TEXT,
                 bold=False, halign='left', valign='top', **kw):
        super().__init__(text=text, font_size=font_size, color=color,
                         bold=bold, halign=halign, valign=valign,
                         markup=True, **kw)
        self.bind(size=self.setter('text_size'))


class EvoButton(Button):
    def __init__(self, text='', bg=C_PRIMARY, fg=C_BG, fs='15sp', **kw):
        super().__init__(text=text, background_normal='',
                         background_color=bg, color=fg,
                         font_size=fs, **kw)


class ParamRow(BoxLayout):
    """Linha: Label | Slider | ValorLabel"""
    def __init__(self, label, key, lo, hi, default, callback=None, **kw):
        super().__init__(orientation='horizontal',
                         size_hint_y=None, height=dp(52), **kw)
        self.key      = key
        self.callback = callback

        lbl = EvoLabel(text=label, font_size='12sp', color=C_TEXT,
                       size_hint_x=0.38, valign='middle')
        self.add_widget(lbl)

        self.sl = Slider(min=lo, max=hi, value=default,
                         cursor_size=(dp(20), dp(20)),
                         size_hint_x=0.44)
        self.sl.bind(value=self._on_val)
        self.add_widget(self.sl)

        self.val_lbl = EvoLabel(text=str(int(default)), font_size='14sp',
                                color=C_GOLD, size_hint_x=0.18,
                                halign='center', valign='middle')
        self.add_widget(self.val_lbl)

    def _on_val(self, inst, val):
        self.val_lbl.text = str(int(val))
        if self.callback:
            self.callback(self.key, val)

    @property
    def value(self):
        return self.sl.value


# ─────────────────────────────────────────────────────────────
# TELA: MENU PRINCIPAL
# ─────────────────────────────────────────────────────────────

class MenuScreen(Screen):
    def on_enter(self):
        self.canvas.clear()
        self.clear_widgets()
        self._build()

    def _build(self):
        root = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(16))
        add_bg(root, C_BG)

        root.add_widget(Widget(size_hint_y=0.08))

        root.add_widget(EvoLabel(
            text='[b][color=33dd99]🧬 EVOLUÇÃO REAL[/color][/b]',
            font_size='34sp', bold=True, halign='center', valign='middle',
            size_hint_y=None, height=dp(70)))

        root.add_widget(EvoLabel(
            text='[color=aabbcc]Simulação Evolutiva Autônoma[/color]',
            font_size='15sp', halign='center', valign='middle',
            size_hint_y=None, height=dp(35)))

        root.add_widget(Widget(size_hint_y=0.06))

        btn_new = EvoButton('🌍  Novo Planeta', bg=(0.18,0.62,0.45,1),
                            size_hint_y=None, height=dp(58))
        btn_new.bind(on_press=lambda *a: setattr(self.manager,'current','planet'))
        root.add_widget(btn_new)

        btn_cont = EvoButton('▶  Continuar Evolução', bg=(0.25,0.40,0.80,1),
                             size_hint_y=None, height=dp(58))
        btn_cont.bind(on_press=self._continue)
        root.add_widget(btn_cont)

        root.add_widget(Widget(size_hint_y=0.05))

        root.add_widget(EvoLabel(
            text='[color=667788]Controle o DNA. Molde o ambiente.\nVeja a vida encontrar um caminho.[/color]',
            font_size='13sp', halign='center', valign='middle',
            size_hint_y=None, height=dp(55)))

        root.add_widget(Widget())
        self.add_widget(root)

    def _continue(self, *a):
        if load_game():
            n = world.simulate_offline()
            if n > 0:
                self._popup(f"Bem-vindo de volta!\n\n"
                            f"{n} épocas passaram.\n"
                            f"Pop total: {world.total_population():,}",
                            "⏰ O Mundo Continuou")
            self.manager.current = 'sim'
        else:
            self._popup("Nenhum save encontrado.\nCrie um novo planeta!", "Sem save")

    @staticmethod
    def _popup(text, title):
        p = Popup(title=title,
                  content=EvoLabel(text=text, halign='center', valign='middle'),
                  size_hint=(0.82, 0.38))
        p.open()


# ─────────────────────────────────────────────────────────────
# TELA: CONFIGURAR PLANETA
# ─────────────────────────────────────────────────────────────

class PlanetScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.rows  = {}
        self.mode  = 'scientist'
        self._build()

    def _build(self):
        sv = ScrollView()
        inner = BoxLayout(orientation='vertical', padding=dp(18),
                          spacing=dp(8), size_hint_y=None)
        inner.bind(minimum_height=inner.setter('height'))
        add_bg(inner, C_BG)

        inner.add_widget(EvoLabel(
            text='[b][color=33dd99]🌍 Configure Seu Planeta[/color][/b]',
            font_size='22sp', bold=True, halign='center', valign='middle',
            size_hint_y=None, height=dp(55)))

        params = [
            ('🌡 Temperatura',    'temperature',  0, 10, 5),
            ('🌊 Quantidade de Água','water',     0, 10, 5),
            ('🌋 Vulcões',        'volcanic',     0, 10, 3),
            ('☢ Radiação',       'radiation',    0, 10, 3),
            ('🌪 Catástrofes',   'catastrophes', 0, 10, 2),
            ('🌿 Recursos',      'resources',    1, 10, 5),
        ]
        for (label, key, lo, hi, default) in params:
            row = ParamRow(label, key, lo, hi, default)
            self.rows[key] = row
            inner.add_widget(row)

        inner.add_widget(EvoLabel(
            text='[b]Modo de Jogo[/b]', font_size='14sp',
            halign='center', valign='middle',
            size_hint_y=None, height=dp(35)))

        mode_box = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(6))
        self.mode_btns = {}
        for label, key in [('🔬 Cientista','scientist'),
                           ('⚡ Deus','god'),
                           ('💀 Hardcore','hardcore')]:
            btn = EvoButton(label, bg=(0.12,0.12,0.20,1), fg=C_TEXT, fs='13sp')
            btn.bind(on_press=lambda inst, k=key: self._sel_mode(k))
            self.mode_btns[key] = btn
            mode_box.add_widget(btn)
        self._sel_mode('scientist')
        inner.add_widget(mode_box)

        inner.add_widget(Widget(size_hint_y=None, height=dp(10)))

        btn = EvoButton('➡  Criar DNA Inicial', bg=(0.55,0.22,0.85,1),
                        size_hint_y=None, height=dp(58))
        btn.bind(on_press=self._next)
        inner.add_widget(btn)

        sv.add_widget(inner)
        self.add_widget(sv)

    def _sel_mode(self, key):
        self.mode = key
        for k, b in self.mode_btns.items():
            b.background_color = (0.25,0.55,0.30,1) if k == key else (0.12,0.12,0.20,1)

    def _next(self, *a):
        global world
        world = World()
        for key, row in self.rows.items():
            world.env[key] = row.value
        world.mode = self.mode
        self.manager.current = 'dna'


# ─────────────────────────────────────────────────────────────
# TELA: EDITOR DE DNA
# ─────────────────────────────────────────────────────────────

class DNAScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.rows = {}
        self._build()

    def _build(self):
        sv = ScrollView()
        inner = BoxLayout(orientation='vertical', padding=dp(18),
                          spacing=dp(6), size_hint_y=None)
        inner.bind(minimum_height=inner.setter('height'))
        add_bg(inner, C_BG)

        inner.add_widget(EvoLabel(
            text='[b][color=bb44ff]🧬 DNA da Primeira Espécie[/color][/b]',
            font_size='22sp', bold=True, halign='center', valign='middle',
            size_hint_y=None, height=dp(55)))

        self.tip_lbl = EvoLabel(
            text='Distribua os atributos como quiser.',
            font_size='12sp', color=C_DIM, halign='center', valign='middle',
            size_hint_y=None, height=dp(30))
        inner.add_widget(self.tip_lbl)

        dna_params = [
            ('⚡ Velocidade',     'speed',        1, 9, 3),
            ('🛡 Resistência',    'resistance',   1, 9, 2),
            ('🔄 Reprodução',     'reproduction', 1, 9, 5),
            ('🧠 Inteligência',   'intelligence', 0, 9, 1),
            ('⚙ Metabolismo',     'metabolism',   1, 9, 3),
            ('🫥 Camuflagem',     'camouflage',   0, 9, 1),
            ('⚔ Agressividade',   'aggression',   0, 9, 2),
            ('🌊 Aquático',       'aquatic',      0, 9, 0),
            ('📏 Tamanho',        'size',         1, 9, 2),
        ]
        for label, key, lo, hi, default in dna_params:
            row = ParamRow(label, key, lo, hi, default, self._on_change)
            self.rows[key] = row
            inner.add_widget(row)

        inner.add_widget(Widget(size_hint_y=None, height=dp(10)))

        btn = EvoButton('🚀  Iniciar Evolução!', bg=(0.75,0.25,0.90,1),
                        size_hint_y=None, height=dp(60))
        btn.bind(on_press=self._start)
        inner.add_widget(btn)

        sv.add_widget(inner)
        self.add_widget(sv)

    def _on_change(self, key, val):
        pass  # podemos adicionar validação futuramente

    def _start(self, *a):
        global world
        kwargs = {k: row.value for k, row in self.rows.items()}
        dna    = DNA(**kwargs)
        sp     = Species(dna, population=60, generation=0)
        world.species.append(sp)
        world.log(f"🌱 {sp.name} surgiu no planeta primitivo!")
        save_game()
        self.manager.current = 'sim'


# ─────────────────────────────────────────────────────────────
# CANVAS DO MUNDO
# ─────────────────────────────────────────────────────────────

PHASE_COLORS = {
    'microscópica': (0.5,  0.9,  0.5),
    'aquática':     (0.2,  0.5,  1.0),
    'terrestre':    (0.8,  0.7,  0.2),
    'predatória':   (1.0,  0.3,  0.3),
    'inteligente':  (0.9,  0.9,  0.2),
    'civilização':  (1.0,  0.6,  0.1),
    'tecnológica':  (0.8,  0.3,  1.0),
}


class WorldMap(Widget):
    def redraw(self):
        self.canvas.clear()
        if world is None:
            return
        w, h  = self.size
        px, py = self.pos

        with self.canvas:
            # Fundo do mapa tingido pelo ambiente
            temp  = world.env.get('temperature', 5) / 10
            water = world.env.get('water', 5) / 10
            Color(0.03 + temp*0.08, 0.06 + water*0.08, 0.12, 1)
            Rectangle(pos=self.pos, size=self.size)

            # Grid de pontos atmosférico
            Color(0.12, 0.18, 0.14, 0.4)
            for gi in range(0, int(w)+1, int(dp(35))):
                for gj in range(0, int(h)+1, int(dp(35))):
                    Ellipse(pos=(px+gi-1, py+gj-1), size=(dp(2), dp(2)))

            # Desenhar espécies
            for sp in world.species:
                if sp.extinct:
                    continue

                sx = px + sp.x * w
                sy = py + sp.y * h

                pop    = max(1, sp.population)
                radius = max(dp(9), min(dp(38),
                             math.log10(pop + 1) * dp(9)))

                cr, cg, cb, _ = sp.color

                # Aura / glow
                Color(cr*0.25, cg*0.25, cb*0.25, 0.45)
                Ellipse(pos=(sx - radius*1.7, sy - radius*1.7),
                        size=(radius*3.4, radius*3.4))

                # Corpo principal
                Color(cr, cg, cb, 0.88)
                Ellipse(pos=(sx - radius, sy - radius),
                        size=(radius*2, radius*2))

                # Anel de fase
                pr, pg, pb = PHASE_COLORS.get(sp.phase, (1,1,1))
                width = 2.5 if sp.phase in ('inteligente','civilização','tecnológica') else 1.5
                Color(pr, pg, pb, 0.85)
                Line(circle=(sx, sy, radius + dp(3)), width=width)

                # Estrela para civilizações
                if sp.phase in ('civilização','tecnológica'):
                    Color(1.0, 0.8, 0.2, 0.9)
                    star_r = radius * 0.55
                    for angle_i in range(5):
                        ang = math.radians(angle_i * 72 - 90)
                        lx = sx + math.cos(ang)*star_r
                        ly = sy + math.sin(ang)*star_r
                        Ellipse(pos=(lx-dp(3), ly-dp(3)),
                                size=(dp(6), dp(6)))


# ─────────────────────────────────────────────────────────────
# TELA: SIMULAÇÃO PRINCIPAL
# ─────────────────────────────────────────────────────────────

class SimScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._built      = False
        self.selected_sp = None
        self._tick_ev    = None

    # ── Ciclo de vida da tela ─────────────────────────────────

    def on_enter(self):
        if not self._built:
            self._build()
            self._built = True
        self._restart_tick()

    def on_leave(self):
        self._stop_tick()
        save_game()

    def _restart_tick(self):
        self._stop_tick()
        self._tick_ev = Clock.schedule_interval(self._game_tick, TICK_INTERVAL)

    def _stop_tick(self):
        if self._tick_ev:
            self._tick_ev.cancel()
            self._tick_ev = None

    # ── UI ───────────────────────────────────────────────────

    def _build(self):
        root = BoxLayout(orientation='vertical')
        add_bg(root, C_BG)

        # ── TOP BAR ──
        topbar = BoxLayout(size_hint_y=None, height=dp(50),
                           padding=(dp(8),dp(4)), spacing=dp(6))
        add_bg(topbar, (0.06, 0.06, 0.12, 1))

        self.lbl_year = EvoLabel('[color=33dd99]Ano: 0[/color]',
                                 font_size='13sp', size_hint_x=0.28,
                                 valign='middle')
        self.lbl_pop  = EvoLabel('Pop: 0', font_size='13sp',
                                 size_hint_x=0.25, valign='middle')
        self.lbl_ip   = EvoLabel('[color=ffcc33]⚡ 10[/color]',
                                 font_size='13sp', size_hint_x=0.20,
                                 valign='middle')
        self.lbl_sp_count = EvoLabel('Esp: 0', font_size='12sp',
                                      color=C_DIM, size_hint_x=0.15,
                                      valign='middle')

        btn_menu = EvoButton('☰', bg=(0.18,0.18,0.30,1), fg=C_TEXT,
                             fs='18sp', size_hint_x=0.12)
        btn_menu.bind(on_press=self._show_menu)

        for w in [self.lbl_year, self.lbl_pop, self.lbl_ip,
                  self.lbl_sp_count, btn_menu]:
            topbar.add_widget(w)
        root.add_widget(topbar)

        # ── ÁREA CENTRAL: mapa + painel direito ──
        mid = BoxLayout(size_hint_y=0.55)

        self.world_map = WorldMap()
        self.world_map.bind(on_touch_down=self._map_touch)
        mid.add_widget(self.world_map)

        rpanel = BoxLayout(orientation='vertical', size_hint_x=0.36,
                           padding=dp(5), spacing=dp(4))
        add_bg(rpanel, (0.06, 0.06, 0.11, 1))

        rpanel.add_widget(EvoLabel('[b][color=33dd99]Espécies[/color][/b]',
                                   font_size='12sp', bold=True, halign='center',
                                   valign='middle', size_hint_y=None, height=dp(24)))

        sv = ScrollView()
        self.sp_list = BoxLayout(orientation='vertical', spacing=dp(3),
                                  size_hint_y=None)
        self.sp_list.bind(minimum_height=self.sp_list.setter('height'))
        sv.add_widget(self.sp_list)
        rpanel.add_widget(sv)
        mid.add_widget(rpanel)
        root.add_widget(mid)

        # ── PAINEL INFERIOR ──
        bot = BoxLayout(orientation='vertical', size_hint_y=0.45,
                        padding=dp(6), spacing=dp(4))
        add_bg(bot, (0.05, 0.05, 0.10, 1))

        # Detalhe da espécie selecionada
        self.lbl_detail = EvoLabel(
            'Toque em uma espécie no mapa ou na lista →',
            font_size='12sp', color=C_DIM,
            size_hint_y=None, height=dp(72))
        bot.add_widget(self.lbl_detail)

        # Painel de influência
        self.inf_panel = BoxLayout(orientation='vertical',
                                    size_hint_y=None, height=dp(108))
        bot.add_widget(self.inf_panel)

        # Log de eventos
        self.lbl_log = EvoLabel('', font_size='11sp', color=(0.55,0.78,0.65,1),
                                 size_hint_y=None, height=dp(55))
        bot.add_widget(self.lbl_log)

        root.add_widget(bot)
        self.add_widget(root)
        self._build_inf_panel()

    def _build_inf_panel(self):
        self.inf_panel.clear_widgets()
        if world is None or world.mode == 'scientist':
            self.inf_panel.add_widget(EvoLabel(
                '👁  Modo Cientista — apenas observe e registre.',
                font_size='12sp', color=(0.50,0.72,0.60,1),
                halign='center', valign='middle'))
            return

        row1 = BoxLayout(spacing=dp(4), size_hint_y=0.5)
        row2 = BoxLayout(spacing=dp(4), size_hint_y=0.5)

        actions = [
            ('🧬 Mutação\n(5⚡)',   'force_mutation', True),
            ('🌋 Catástrofe\n(8⚡)','catastrophe',    False),
            ('🦠 Vírus\n(10⚡)',    'virus',           True),
            ('🧠 Intel\n(15⚡)',    'boost_intel',     True),
            ('🌪 Clima\n(12⚡)',    'climate',         False),
            ('🌿 Recursos\n(6⚡)',  'food_bloom',      False),
            ('☢ Radiação\n(8⚡)',  'rad_pulse',       False),
            ('☄ Extinção\n(25⚡)', 'mass_extinction', False),
            ('🌱 Semear\n(20⚡)',   'seed_life',       False),
        ]

        for i, (label, action, needs) in enumerate(actions):
            btn = EvoButton(label, bg=(0.12,0.20,0.30,1), fg=C_TEXT, fs='10sp')
            btn.bind(on_press=lambda inst, ac=action, nt=needs:
                     self._do_influence(ac, nt))
            (row1 if i < 5 else row2).add_widget(btn)

        self.inf_panel.add_widget(row1)
        self.inf_panel.add_widget(row2)

    # ── Toque no mapa ─────────────────────────────────────────

    def _map_touch(self, widget, touch):
        if not widget.collide_point(*touch.pos) or world is None:
            return
        wx = (touch.x - widget.x) / max(1, widget.width)
        wy = (touch.y - widget.y) / max(1, widget.height)

        best, best_d = None, 0.12
        for sp in world.alive_species():
            d = math.hypot(sp.x - wx, sp.y - wy)
            if d < best_d:
                best_d, best = d, sp
        if best:
            self.selected_sp = best
            self._update_detail(best)

    # ── Influência ───────────────────────────────────────────

    def _do_influence(self, action, needs_target):
        if world is None:
            return
        target = self.selected_sp if needs_target else None
        if needs_target and target is None:
            Popup(title='Selecione uma espécie',
                  content=EvoLabel('Toque em uma espécie\nno mapa primeiro.',
                                   halign='center', valign='middle'),
                  size_hint=(0.7, 0.28)).open()
            return
        ok, msg = world.apply_influence(action, target)
        Popup(title='✅ Ação' if ok else '❌ Falhou',
              content=EvoLabel(msg, halign='center', valign='middle'),
              size_hint=(0.75, 0.25)).open()

    # ── Atualização da UI ─────────────────────────────────────

    def _update_detail(self, sp):
        if sp is None:
            return
        g = sp.dna.genes
        self.lbl_detail.text = (
            f"[b][color=88ffcc]{sp.name}[/color][/b]  [{sp.phase}]\n"
            f"👥 Pop: {sp.population:,}  |  Gen: {sp.generation}  |  "
            f"Idade: {sp.age:,}\n"
            f"⚡{g['speed'].value:.1f}  🛡{g['resistance'].value:.1f}  "
            f"🔄{g['reproduction'].value:.1f}  🧠{g['intelligence'].value:.1f}  "
            f"⚔{g['aggression'].value:.1f}\n"
            f"Adaptações: {', '.join(sp.adaptations) if sp.adaptations else 'nenhuma'}"
        )

    def _update_sp_list(self):
        self.sp_list.clear_widgets()
        alive = sorted(world.alive_species(),
                       key=lambda s: s.population, reverse=True)
        for sp in alive[:12]:
            cr, cg, cb, _ = sp.color
            btn = Button(
                text=f"{sp.name}\n{sp.population:,}  [{sp.phase}]",
                size_hint_y=None, height=dp(46),
                font_size='10sp',
                background_normal='',
                background_color=(cr*0.28, cg*0.28, cb*0.28, 1),
                color=(min(1,cr*1.5), min(1,cg*1.5), min(1,cb*1.5), 1),
                halign='left', valign='middle',
            )
            btn.text_size = btn.size
            btn.bind(size=btn.setter('text_size'))
            btn.bind(on_press=lambda inst, s=sp: self._sel_sp(s))
            self.sp_list.add_widget(btn)

    def _sel_sp(self, sp):
        self.selected_sp = sp
        self._update_detail(sp)

    # ── Tick do jogo ─────────────────────────────────────────

    def _game_tick(self, dt):
        if world is None:
            return

        world.tick()

        # Labels topo
        self.lbl_year.text = (f'[color=33dd99]Ano: {world.year:,}[/color]')
        self.lbl_pop.text  = f'Pop: {world.total_population():,}'
        self.lbl_ip.text   = f'[color=ffcc33]⚡ {world.influence_pts}[/color]'
        alive_count        = len(world.alive_species())
        self.lbl_sp_count.text = f'Esp: {alive_count}'

        # Mapa e lista
        self.world_map.redraw()
        if world.tick_count % 6 == 0:
            self._update_sp_list()

        # Log de eventos
        if world.events:
            self.lbl_log.text = '\n'.join(world.events[:3])

        # Detalhe da espécie selecionada
        if self.selected_sp and not self.selected_sp.extinct:
            self._update_detail(self.selected_sp)
        elif self.selected_sp and self.selected_sp.extinct:
            self.lbl_detail.text = (
                f"[color=ff4444]{self.selected_sp.name} foi EXTINTA.[/color]")
            self.selected_sp = None

        # Salvar automaticamente a cada ~500 ticks
        if world.tick_count % 500 == 0:
            save_game()

        # Hardcore: verificar extinção total
        if world.mode == 'hardcore' and alive_count == 0:
            self._game_over_hardcore()

        # Reconstruir painel de influência na 1ª vez
        if world.tick_count == 1:
            self._build_inf_panel()

    def _game_over_hardcore(self):
        self._stop_tick()
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
        p = Popup(
            title='💀 EXTINÇÃO TOTAL',
            content=EvoLabel(
                f"Todas as espécies foram extintas.\n\n"
                f"Anos vividos: {world.year:,}\n"
                f"Extinções totais: {world.total_extinct}\n\n"
                f"[color=ff4444]Modo Hardcore: fim de jogo.[/color]",
                halign='center', valign='middle'),
            size_hint=(0.85, 0.52))
        p.open()
        Clock.schedule_once(
            lambda dt: setattr(self.manager, 'current', 'menu'), 6)

    # ── Menu de status ────────────────────────────────────────

    def _show_menu(self, *a):
        if world is None:
            return
        dom = world.dominant()
        content = BoxLayout(orientation='vertical', spacing=dp(10),
                            padding=dp(10))
        content.add_widget(EvoLabel(
            f"[b]🌍 Status do Planeta[/b]\n\n"
            f"Ano: {world.year:,}\n"
            f"Espécies vivas: {len(world.alive_species())}\n"
            f"Total extintas: {world.total_extinct}\n"
            f"Pop total: {world.total_population():,}\n"
            f"Dominante: {dom.name if dom else '—'}\n"
            f"Modo: {world.mode}\n"
            f"⚡ Influência: {world.influence_pts}",
            font_size='13sp', halign='left', valign='top',
            size_hint_y=None, height=dp(190)))

        btn_pause = EvoButton(
            '⏸ Pausar' if not world.paused else '▶ Retomar',
            bg=(0.30,0.45,0.55,1), size_hint_y=None, height=dp(46))

        btn_save  = EvoButton('💾 Salvar', bg=(0.22,0.48,0.30,1),
                              size_hint_y=None, height=dp(46))
        btn_exit  = EvoButton('🏠 Menu Principal', bg=(0.55,0.20,0.20,1),
                              size_hint_y=None, height=dp(46))

        popup = Popup(title='Painel de Controle',
                      content=content, size_hint=(0.88, 0.78))

        def toggle_pause(*_):
            world.paused = not world.paused
            btn_pause.text = '▶ Retomar' if world.paused else '⏸ Pausar'

        btn_pause.bind(on_press=toggle_pause)
        btn_save.bind(on_press=lambda *_: save_game())
        btn_exit.bind(on_press=lambda *_: (
            popup.dismiss(),
            setattr(self.manager, 'current', 'menu')
        ))
        content.add_widget(btn_pause)
        content.add_widget(btn_save)
        content.add_widget(btn_exit)
        popup.open()


# ─────────────────────────────────────────────────────────────
# APLICAÇÃO KIVY
# ─────────────────────────────────────────────────────────────

class EvolucaoRealApp(App):
    title = '🧬 Evolução Real'

    def build(self):
        Window.clearcolor = C_BG

        sm = ScreenManager(transition=FadeTransition(duration=0.25))
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(PlanetScreen(name='planet'))
        sm.add_widget(DNAScreen(name='dna'))
        sm.add_widget(SimScreen(name='sim'))
        return sm

    def on_pause(self):
        save_game()
        return True          # Mantém o app em memória

    def on_resume(self):
        if world is not None:
            world.simulate_offline()

    def on_stop(self):
        save_game()


if __name__ == '__main__':
    EvolucaoRealApp().run()
