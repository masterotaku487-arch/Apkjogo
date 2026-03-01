import random
import math
from game.world_data import REGIONS, WORLD_TOTAL_POP


class Gene:
    def __init__(self, name, key, min_val=0.0, max_val=1.0, desc="", icon="🧬"):
        self.name = name
        self.key = key
        self.value = 0.0
        self.min_val = min_val
        self.max_val = max_val
        self.desc = desc
        self.icon = icon

    def mutate(self, amount=0.05):
        self.value = max(self.min_val, min(self.max_val, self.value + random.uniform(-amount, amount * 2)))

    def evolve(self, points=0.1):
        self.value = min(self.max_val, self.value + points)


GENE_DEFINITIONS = [
    ("Transmissão", "transmission", "Velocidade de contágio entre hospedeiros", "🦠"),
    ("Letal", "lethality", "Dano ao hospedeiro (alta = mais morte, menos spread)", "💀"),
    ("Resistência", "resistance", "Resistência a remédios e curas", "🛡️"),
    ("Furtividade", "stealth", "Dificulta detecção e pesquisa de cura", "👁️"),
    ("Mutação", "mutation", "Taxa de evolução espontânea", "🔬"),
    ("Calor", "heat_resist", "Adaptação a climas quentes", "🔥"),
    ("Frio", "cold_resist", "Adaptação a climas frios", "❄️"),
    ("Aquático", "water_spread", "Spread via água e costeiros", "🌊"),
    ("Ar", "air_spread", "Spread via ar e aerossóis", "💨"),
    ("Animal", "animal_host", "Pode usar animais como vetores", "🐀"),
]


class PathogenSpecies:
    def __init__(self, name, origin_region_id):
        self.name = name
        self.origin_id = origin_region_id
        self.age_days = 0
        self.dna_points = 10
        self.evolved_traits = []
        self.total_infected = 0
        self.total_dead = 0
        self.cured = False
        self.cure_progress = 0.0

        # Genes
        self.genes = {}
        for gname, gkey, gdesc, gicon in GENE_DEFINITIONS:
            self.genes[gkey] = Gene(gname, gkey, desc=gdesc, icon=gicon)

        # Starter: slight transmission
        self.genes["transmission"].value = 0.15
        self.genes["stealth"].value = 0.20

        # Region infection states
        self.regions = {}
        for r in REGIONS:
            self.regions[r["id"]] = {
                "infected": 0,
                "dead": 0,
                "population": r["pop"] * 1_000_000,
                "healthy": r["pop"] * 1_000_000,
                "infection_rate": 0.0,
                "discovered": False,
            }

        # Seed origin
        origin = self.regions[origin_region_id]
        seed = max(1, int(origin["population"] * 0.0001))
        origin["infected"] = seed
        origin["healthy"] -= seed
        origin["discovered"] = False

    def tick(self, dt_days=1.0):
        """Advance simulation by dt_days."""
        self.age_days += dt_days

        # Auto-mutate based on mutation gene
        if random.random() < self.genes["mutation"].value * 0.1 * dt_days:
            key = random.choice(list(self.genes.keys()))
            self.genes[key].mutate(0.03)
            if self.dna_points < 50:
                self.dna_points += 1

        # Spread within and between regions
        self._spread(dt_days)

        # Cure research
        self._cure_research(dt_days)

        # Tally
        self.total_infected = sum(s["infected"] for s in self.regions.values())
        self.total_dead = sum(s["dead"] for s in self.regions.values())

    def _spread(self, dt):
        trans = self.genes["transmission"].value
        lethal = self.genes["lethality"].value
        resist = self.genes["resistance"].value
        stealth = self.genes["stealth"].value
        air = self.genes["air_spread"].value
        water = self.genes["water_spread"].value
        animal = self.genes["animal_host"].value

        region_map = {r["id"]: r for r in REGIONS}

        for region_id, state in self.regions.items():
            if state["infected"] == 0:
                continue

            rdata = region_map[region_id]
            pop = state["population"]
            infected = state["infected"]
            healthy = state["healthy"]
            dead = state["dead"]

            if healthy <= 0:
                continue

            # Climate modifier
            climate = rdata.get("climate", "temperate")
            climate_mod = 1.0
            if climate == "tropical":
                climate_mod = 1.0 + self.genes["heat_resist"].value * 0.5
            elif climate == "cold":
                climate_mod = 1.0 + self.genes["cold_resist"].value * 0.5
            elif climate == "arid":
                climate_mod = 0.7 + self.genes["heat_resist"].value * 0.6

            # Base spread rate
            spread_rate = trans * 0.08 * climate_mod
            spread_rate += air * 0.04
            spread_rate += water * rdata.get("ports", 0) * 0.01
            spread_rate += animal * 0.02

            # New infections
            new_inf = int(infected * spread_rate * (healthy / pop) * dt)
            new_inf = min(new_inf, healthy)
            new_inf = max(0, new_inf)

            # Deaths
            death_rate = lethal * 0.005 * dt
            new_dead = int(infected * death_rate)
            new_dead = max(0, new_dead)

            # Recoveries (lowered by resistance)
            recover_rate = max(0.002, 0.01 - resist * 0.009) * dt
            recovered = int(infected * recover_rate * (1 - stealth * 0.3))

            state["infected"] += new_inf - new_dead - recovered
            state["dead"] += new_dead
            state["healthy"] -= new_inf
            state["healthy"] = max(0, state["healthy"])
            state["infected"] = max(0, state["infected"])

            # Discovery
            if not state["discovered"]:
                discovery_chance = (infected / pop) * (1 - stealth * 0.8) * 0.3 * dt
                if random.random() < discovery_chance:
                    state["discovered"] = True

            state["infection_rate"] = infected / pop if pop > 0 else 0

        # Cross-region spread
        self._cross_region_spread(dt, region_map)

    def _cross_region_spread(self, dt, region_map):
        """Spread between neighboring/connected regions."""
        air = self.genes["air_spread"].value
        water = self.genes["water_spread"].value
        trans = self.genes["transmission"].value

        # List of infected regions
        infected_regions = [rid for rid, s in self.regions.items() if s["infected"] > 100]

        for src_id in infected_regions:
            src = self.regions[src_id]
            src_data = region_map[src_id]
            src_pop = src["population"]
            if src_pop == 0:
                continue

            inf_ratio = src["infected"] / src_pop

            # Spread chance based on genes
            spread_chance = (trans * 0.03 + air * 0.06 + water * src_data.get("ports", 0) * 0.02) * inf_ratio * dt

            if random.random() < spread_chance:
                # Pick random target region
                target_id = random.choice([r["id"] for r in REGIONS if r["id"] != src_id])
                target = self.regions[target_id]

                if target["healthy"] > 0 and target["infected"] == 0:
                    # Seed infection
                    seed = random.randint(1, max(1, int(target["population"] * 0.00005)))
                    target["infected"] = seed
                    target["healthy"] -= seed
                elif target["infected"] > 0:
                    extra = random.randint(1, max(1, int(target["healthy"] * 0.001)))
                    target["infected"] += extra
                    target["healthy"] -= extra
                    target["healthy"] = max(0, target["healthy"])

    def _cure_research(self, dt):
        """World cure research speeds up when regions discover pathogen."""
        discovered = sum(1 for s in self.regions.values() if s["discovered"])
        if discovered == 0:
            return

        stealth = self.genes["stealth"].value
        resist = self.genes["resistance"].value

        research_speed = (discovered / len(self.regions)) * 0.002 * dt
        research_speed *= (1 - stealth * 0.4) * (1 - resist * 0.5)

        self.cure_progress = min(1.0, self.cure_progress + research_speed)

        if self.cure_progress >= 1.0:
            self.cured = True

    def evolve_gene(self, gene_key, amount=0.1):
        cost = 2
        if self.dna_points >= cost:
            self.genes[gene_key].evolve(amount)
            self.dna_points -= cost
            return True
        return False

    def get_stats(self):
        world_pop = WORLD_TOTAL_POP * 1_000_000
        infected_pct = (self.total_infected / world_pop * 100) if world_pop > 0 else 0
        dead_pct = (self.total_dead / world_pop * 100) if world_pop > 0 else 0
        regions_hit = sum(1 for s in self.regions.values() if s["infected"] > 0)

        return {
            "infected": self.total_infected,
            "dead": self.total_dead,
            "infected_pct": infected_pct,
            "dead_pct": dead_pct,
            "regions_hit": regions_hit,
            "cure_pct": self.cure_progress * 100,
            "dna_points": self.dna_points,
            "age_days": self.age_days,
        }


def format_number(n):
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.0f}K"
    return str(int(n))
